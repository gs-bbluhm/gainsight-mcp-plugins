#!/usr/bin/env python3
"""Stage 1 of the today list: report configs, scoring, shortlist, ledger.

Implements the engine in references/action-priority.md (stakes x urgency x attention, one item per
account, triggers, attention states, suppression that needs no thread read). Standard library only.
Run with `python3 -I`. Prints markdown for the model; never prints revenue figures.

  score.py pulls  --role-field customer.<field> [--role-field ...] --user-id N [--user-id N] --today YYYY-MM-DD
                  [--since YYYY-MM-DD] [--drop ID ...] [--split-a]
      Prints the stage-1 ReportConfigs as JSON (A or A1+A2, B, C1, C2, EV, COUNT). Columns carry
      label == key, so every CSV header is the key this script reads.

  score.py rank   --today YYYY-MM-DD --a A.csv [A2.csv] --b B.csv --c1 C1.csv --c2 C2.csv
                  [--ev EV.csv] [--ledger FILE] [--scope-id N] [--mode today|week|since|takeover]
                  [--lane waiting|quiet|stakeholder|risk|renewal] [--since YYYY-MM-DD]
                  [--now YYYY-MM-DDTHH:MM] [--weights 0.40,0.35,0.25] [--shortlist 14]
      Joins the pulls on account id, scores every trigger, prints the ranked candidates, the
      meetings strip, the stage-2 shortlist and what was left out (ledger, live, no trigger).

  score.py ledger --ledger FILE --today YYYY-MM-DD --fp FP --state done|dismissed|snoozed|lifted
                  --reason done|not_mine|wrong|not_now|do_not_contact [--until YYYY-MM-DD] [--scope-id N]
      Appends one line. do_not_contact (fp <account_id>|*|*) drops customer-facing items on the account
      and keeps internal ones; lifted cancels earlier lines with the same fp (and reason, when given).

  score.py check  --ledger FILE --today YYYY-MM-DD [--scope-id N] --fp FP [--fp FP ...]
      Prints which fingerprints the ledger suppresses (for stage-2 keys such as reply threads).
"""
import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone

INSIGHTS = ["ChurnRisk", "Farewell", "CustomerDark", "NoRenewalDiscussion"]
EVENTS = {"ev_churn_risk": "churn_risk", "ev_churn": "churn", "ev_farewell": "farewell",
          "ev_neg": "exceptional_negative", "ev_renewal_disc": "renewal_discussion",
          "ev_pos": "exceptional_positive"}
EV_TYPES = ["farewell", "organization_personnel_change", "churn", "churn_risk", "churn_status",
            "exceptional_negative", "exceptional_positive", "renewal_discussion"]
REACTIVE = {"reply_needed", "meeting_followup", "meeting_prep", "fresh_risk", "renewal_decision"}
LANES = {
    "waiting": {"reply_needed", "meeting_followup"},
    "quiet": {"quiet", "one_sided_chase"},
    "stakeholder": {"stakeholder_change"},
    "risk": {"fresh_risk", "open_situation", "renewal_decision", "renewal_checkpoint"},
    "renewal": {"renewal_decision", "renewal_checkpoint", "record_check"},
}
LANE_OF = {"reply_needed": "customer waiting", "meeting_followup": "customer waiting",
           "meeting_prep": "meeting", "quiet": "gone quiet", "one_sided_chase": "gone quiet",
           "stakeholder_change": "stakeholder change", "fresh_risk": "risk",
           "open_situation": "risk", "renewal_decision": "renewal",
           "renewal_checkpoint": "renewal", "record_check": "renewal",
           "expansion_ready": "grow"}
# Ledger entries the renewals skill writes hide only their own family here, at account level.
FAMILY = {"renewal_plan": {"renewal_checkpoint", "renewal_decision"},
          "expansion_plan": {"expansion_ready"}}
# Do not contact: these triggers put a message in front of the customer, so they drop; the rest
# stay as internal actions (a Slack to the renewal owner, a close-out, a CRM fix).
CUSTOMER_FACING = {"quiet", "one_sided_chase", "expansion_ready", "renewal_checkpoint", "stakeholder_change"}
# A live two-way account drops only the items the live conversation already answers. A contact
# change, an expansion signal or an open risk stays (attention 0.75): raise it in that conversation.
LIVE_DROP = {"quiet", "one_sided_chase", "renewal_checkpoint"}


# ---------------------------------------------------------------- configs

def col(fid, key, args=None):
    f = {"id": fid}
    if args:
        f["arguments"] = args
    return {"field": f, "key": key, "label": key}


def book_filter(roles, ids, prefix="customer"):
    """Active accounts where any of the role fields holds any of the user ids."""
    pre = "" if prefix == "customer" else prefix + "."
    leaves = [{"field": {"id": pre + rf}, "operator": "In", "values": ids} for rf in roles]
    who = leaves[0] if len(leaves) == 1 else {"operator": "Or", "conditions": leaves}
    return {"operator": "And", "conditions": [
        who, {"field": {"id": pre + "customer.status"}, "operator": "In", "values": ["Active"]}]}


def cmd_pulls(a):
    today = date.fromisoformat(a.today)
    start30 = today - timedelta(days=29)
    start = start30
    if a.since:
        s = date.fromisoformat(a.since)
        start = max(min(s, start30), today - timedelta(days=89))
    win = [start.isoformat(), today.isoformat()]
    drop = set(a.drop or [])
    flt = book_filter(a.role_field, a.user_id)
    # One page holds the whole book: sorting on customer.id is silently ignored, so paging on it can
    # drop or repeat rows. Check complete is true and the COUNT matches.
    page = {"sortBy": [], "pagination": {"from": 0, "to": 1000}}
    a_cols = [col("customer.id", "id"), col("customer.name", "name"),
              col("customer.renewal_date", "renewal"), col("customer.risk.risk_level", "risk"),
              col("customer.buckets.health_score", "health"),
              col("customer.revenue_converted", "value"), col("customer.last_touch", "last_touch"),
              col("customer.last_engagement", "last_eng"),
              col("customer.last_reach_out", "last_reach"),
              col("customer.email.customer_last_sent", "cust_email"),
              col("customer.email.organization_last_sent", "org_email"),
              col("customer.event.last_event", "last_mtg"),
              col("customer.event.next_event", "next_mtg")]
    out = {}
    if a.split_a:
        out["A1"] = dict(entity="customer", columns=a_cols[:8], filter=flt, **page)
        out["A2"] = dict(entity="customer", columns=[a_cols[0]] + a_cols[8:], filter=flt, **page)
    else:
        out["A"] = dict(entity="customer", columns=a_cols, filter=flt, **page)
    out["B"] = dict(entity="customer", arguments={"dateRange": win},
                    columns=[col("customer.id", "id"),
                             col("customer.email.customer_open_threads", "cust_open"),
                             col("customer.email.organization_open_threads", "org_open"),
                             col("customer.buckets.health", "health_band"),
                             # static columns ride on the light pull: the parent's id (a Reference
                             # column returns the id; a parent and child both in scope make one
                             # item) and the account's page in Staircase (links on items and the board)
                             col("customer.parent", "parent"), col("customer.url", "url")],
                    filter=flt, **page)
    c1 = [col("customer.id", "id")]
    keys = {"ChurnRisk": "i_churn", "Farewell": "i_farewell", "CustomerDark": "i_dark",
            "NoRenewalDiscussion": "i_norenew"}
    for ins in INSIGHTS:
        if ins not in drop:
            c1.append(col("customer.insight_detected", keys[ins], {"insightType": ins}))
    c1 += [col("customer.expansion.readiness_level", "exp"),
           col("customer.expansion.momentum_indicator", "mom"),
           {"field": {"rootEntityPath": "customer", "childEntity": "expansion_opportunity",
                      "referenceField": "expansion_opportunity.customer", "aggregation": "COUNT",
                      "condition": {"operator": "And", "conditions": [
                          {"field": {"id": "expansion_opportunity.confidence_level"},
                           "operator": "In", "values": ["High"]},
                          {"field": {"id": "expansion_opportunity.momentum_state"},
                           "operator": "In", "values": ["Heating"]}]}},
            "key": "exp_hot", "label": "exp_hot"}]
    out["C1"] = dict(entity="customer", columns=c1, filter=flt, **page)
    c2 = [col("customer.id", "id")]
    for k, ev in EVENTS.items():
        if ev not in drop:
            c2.append(col("customer.last_lifecycle_event_date", k, {"eventType": ev}))
    out["C2"] = dict(entity="customer", columns=c2, filter=flt, **page)
    out["EV"] = {"entity": "lifecycle_event", "arguments": {"dateRange": win},
                 "columns": [col("lifecycle_event.id", "event_id"),
                             col("lifecycle_event.customer", "id"),
                             col("lifecycle_event.customer.name", "name"),
                             col("lifecycle_event.type", "type"),
                             col("lifecycle_event.date", "date")],
                 "filter": {"operator": "And", "conditions":
                            book_filter(a.role_field, a.user_id, "lifecycle_event")["conditions"] +
                            [{"field": {"id": "lifecycle_event.type"}, "operator": "In",
                              "values": [t for t in EV_TYPES if t not in drop]}]},
                 "sortBy": [{"columnKey": "date", "direction": "Desc"}],
                 "pagination": {"from": 0, "to": 1000}}
    out["COUNT"] = {"entity": "customer", "columns": [
        {"field": {"aggregation": "COUNT"}, "key": "n", "label": "n"}], "filter": flt, "sortBy": []}
    out["_windows"] = {"threads_and_events": win, "today": today.isoformat()}
    print(json.dumps(out, indent=1))


# ---------------------------------------------------------------- parsing

def read_rows(paths):
    rows = {}
    for p in paths or []:
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                rid = (r.get("id") or "").strip()
                if not rid:
                    continue
                rows.setdefault(rid, {}).update({k: (v or "").strip() for k, v in r.items()})
    return rows


def pdt(s, now):
    """Parse a DateTime cell ('2026-10-28 21:05 UTC' or ISO). Future values clamp to now."""
    if not s:
        return None
    s = s.replace(" UTC", "").replace("Z", "").replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            d = datetime.strptime(s[:19], fmt).replace(tzinfo=timezone.utc)
            return d
        except ValueError:
            continue
    return None


def pd(s):
    try:
        return date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


TODAY_YEAR = [date.today().year]


def dm(d):
    """Day and month; the year too when it is not the current year."""
    if not d:
        return "never"
    return d.strftime("%-d %b") if d.year == TODAY_YEAR[0] else d.strftime("%-d %b %Y")


# ---------------------------------------------------------------- engine

def R(days):
    if days is None or days < -29:  # blank, or a stale date (passed over 30 days ago)
        return 0.3
    if days <= 30:
        return 1.0
    if days <= 60:
        return 0.8
    if days <= 90:
        return 0.6
    if days <= 180:
        return 0.35
    if days <= 365:
        return 0.15
    return 0.05


def attention(lt, le, org_open, ce):
    if lt is None or lt > 30:
        return 1.3, "dark"
    if lt <= 14 and (le is None or le > 30):
        return 1.15, "chasing"
    if org_open >= 2 and (ce is None or ce > 7):
        return 1.15, "chasing"
    if lt > 14 or le is None or le > 21:
        return 1.15, "drifting"
    if lt <= 3 and le is not None and le <= 7:
        return 0.75, "live"
    if lt <= 7:
        return 0.9, "recent"
    return 1.0, "normal"


def load_ledger(path, today, scope):
    active = []
    if not path or not os.path.exists(path):
        return active
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            if scope and e.get("scope") and str(e["scope"]) != str(scope):
                continue
            if e.get("state") == "lifted":
                # a lift ("undo 2", "ok to contact X") cancels earlier entries with the same
                # fingerprint; with a reason, only the entries that carry that reason
                active = [x for x in active if not (x.get("fp") == e.get("fp") and
                                                    (not e.get("reason") or x.get("reason") == e["reason"]))]
                continue
            if e.get("state") == "snoozed" and e.get("until") and e["until"] < today.isoformat():
                continue
            active.append(e)
    return active


def as_dt(v, end_of_day=False):
    """A date becomes a UTC datetime (start of day, or its last minute); a datetime passes through."""
    if isinstance(v, datetime):
        return v
    t = datetime.max.time() if end_of_day else datetime.min.time()
    return datetime.combine(v, t).replace(tzinfo=timezone.utc)


def when(s, end_of_day=False):
    """Parse a ledger or key timestamp: YYYY-MM-DD, or YYYY-MM-DDTHH:MM[:SS][Z]."""
    if not s:
        return None
    if len(s) <= 10:
        d = pd(s)
        return as_dt(d, end_of_day) if d else None
    return pdt(s, None)


def ledger_match(fp, entries, evdate=None):
    """exact: the same fingerprint, or the whole account marked not mine.
    account: a dismissal of any item on this account, and nothing newer than it has happened
    (evdate is the date of the evidence behind this candidate; None means no newer evidence).
    check: a reply row whose thread key stage 2 must compare.
    Do-not-contact entries never hide an item here (cmd_rank drops only customer-facing ones), and
    another skill's entry covers only its own family of triggers."""
    acct, trig, key = (fp.split("|") + ["", ""])[:3]
    best = (None, None)
    for e in entries:
        if e.get("reason") == "do_not_contact" or e.get("state") == "linked":
            continue
        ea, et, ek = (e.get("fp", "").split("|") + ["", ""])[:3]
        if ea != acct:
            continue
        if et == "*" or (et == trig and (ek == "*" or ek == key)):
            return "exact", e
        if et in FAMILY:
            if trig not in FAMILY[et]:
                continue
        elif et not in LANE_OF:
            continue
        at = when(e.get("at", ""), end_of_day=True)
        if at and (evdate is None or as_dt(evdate) <= at):
            best = ("account", e)
        elif et == trig and key == "?" and best[0] is None:
            best = ("check", e)
    return best


def cmd_rank(a):
    today = date.fromisoformat(a.today)
    TODAY_YEAR[0] = today.year
    now = (datetime.strptime(a.now, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
           if a.now else datetime.now(timezone.utc))
    wr, wk, wv = [float(x) for x in a.weights.split(",")]
    rows = read_rows(a.a)
    for part in (a.b, a.c1, a.c2):
        for rid, r in read_rows(part).items():
            rows.setdefault(rid, {}).update(r)
    rows = {k: v for k, v in rows.items() if v.get("name")}
    events = {}
    if a.ev:
        seen = set()
        with open(a.ev, newline="") as f:
            for r in csv.DictReader(f):
                eid = (r.get("event_id") or "").strip()
                if not eid or eid in seen:
                    continue
                seen.add(eid)
                events.setdefault(r.get("id", "").strip(), []).append(
                    (pd(r.get("date", "")), r.get("type", "").strip(), eid))
    ledger = load_ledger(a.ledger, today, a.scope_id)
    dnc = {e.get("fp", "").split("|")[0] for e in ledger if e.get("reason") == "do_not_contact"}
    # the user joined two accounts Staircase does not link ("Lumen Freight and Lumen Group are one")
    linked = {e.get("fp", "").split("|")[0]: str(e["with"]) for e in ledger
              if e.get("state") == "linked" and e.get("with")}
    n = len(rows)

    def age(s):
        d = pdt(s, now)
        if d is None:
            return None
        return max(0.0, (now - d).total_seconds() / 86400)

    def hours_ahead(s):
        d = pdt(s, now)
        return None if d is None else (d - now).total_seconds() / 3600

    vals = sorted(v for v in (num(r.get("value")) for r in rows.values()) if v and v > 0)

    def pct(v):
        if not v or v <= 0 or len(vals) < 2:
            return None
        return sum(1 for x in vals if x < v) / (len(vals) - 1)

    # base rates for boolean and picklist flags
    def share(key, test):
        have = [r for r in rows.values() if r.get(key, "") != ""]
        return sum(1 for r in have if test(r[key])) / n if n else 0
    flags = {"i_churn": "ChurnRisk insight", "i_farewell": "Farewell insight",
             "i_dark": "CustomerDark insight", "i_norenew": "NoRenewalDiscussion insight"}
    dropped, usable = [], {}
    for k, label in flags.items():
        present = any(k in r for r in rows.values())
        if not present:
            dropped.append(f"{label}: not pulled")
            usable[k] = False
            continue
        s = share(k, lambda v: v.lower() == "true")
        usable[k] = 0 < s <= 0.8
        if not usable[k]:
            dropped.append(f"{label}: true on {round(s * 100)} percent of the book (does not separate)")
    s_heat = share("mom", lambda v: v == "Heating")
    use_heat = 0 < s_heat <= 0.8
    if not use_heat:
        dropped.append(f"expansion momentum Heating: {round(s_heat * 100)} percent of the book (does not separate)")

    items, strip, live_dropped, ledger_out, notrig, stale = [], [], [], {}, [], []
    dnc_dropped, folded = [], []
    prep_window = 168 if a.mode == "week" else 48
    for rid, r in rows.items():
        name = r.get("name", rid)
        ren = pd(r.get("renewal"))
        d = (ren - today).days if ren else None
        risk = num(r.get("risk"))
        health = num(r.get("health"))
        if health == 0:
            health = None
        if risk:
            k = {5: 1.0, 4: 0.8, 3: 0.5, 2: 0.25, 1: 0.1}.get(int(risk), 0.5)
            ksrc = f"risk {int(risk)}"
        elif health is not None:
            k = min(0.6, 0.2 + 0.5 * (1 - health / 100))
            ksrc = f"risk not assessed, health {int(health)} used"
        else:
            k, ksrc = 0.3, "risk not assessed, no health data"
        if usable.get("i_churn") and r.get("i_churn", "").lower() == "true":
            k = max(k, 0.8)
            ksrc += ", ChurnRisk insight"
        evr = pd(r.get("ev_churn_risk"))
        if evr and (today - evr).days <= 29:
            k = max(k, 0.7)
        p = pct(num(r.get("value")))
        v = 0.5 if p is None else p
        vsrc = ("revenue not set" if p is None else
                "top third of the book by revenue" if p >= 0.67 else
                "bottom third of the book by revenue" if p <= 0.33 else "middle of the book by revenue")
        S = wr * R(d) + wk * k + wv * v
        if d is None:
            rsrc = "no renewal date"
        elif d < -29:
            rsrc = f"renewal date {dm(ren)} passed over 30 days ago (stale date)"
        elif d < 0:
            rsrc = f"renewal date {dm(ren)} has passed"
        else:
            rsrc = f"renewal {dm(ren)} ({d} days)"
        lt, le = age(r.get("last_touch")), age(r.get("last_eng"))
        ce, oe = age(r.get("cust_email")), age(r.get("org_email"))
        lm = age(r.get("last_mtg"))
        nm = hours_ahead(r.get("next_mtg"))
        cust_open = int(num(r.get("cust_open")) or 0)
        org_open = int(num(r.get("org_open")) or 0)
        att, ast = attention(lt, le, org_open, ce)
        base = dict(id=rid, name=name, S=S, d=d, k=k, why=[rsrc, ksrc, vsrc], att=ast,
                    health_band=r.get("health_band", ""))
        evs = sorted(events.get(rid, []), key=lambda x: (x[0] or date.min), reverse=True)

        def last_event(types, days):
            for ed, et, eid in evs:
                if et in types and ed and (today - ed).days <= days - 1:
                    return ed, et, eid
            return None

        c = []
        # reply needed
        if cust_open >= 1:
            u = min(1.0, 0.6 + 0.1 * min(cust_open, 3) + (0.1 if ce is not None and ce > 2 else 0))
            handled = oe is not None and ce is not None and oe < ce
            mult = 0.6 if handled else 1.0
            sameday = ce is not None and ce < 1
            c.append(("reply_needed", u, mult,
                      f"{cust_open} customer thread(s) open in the read window; customer last wrote "
                      f"{dm(pdt(r.get('cust_email'), now))}"
                      + ("; someone on our side wrote after them (account level)" if handled else "")
                      + ("; the latest customer email is under 1 day old (account level: check the waiting thread's own date)" if sameday else ""), "?"))
        # meeting follow-up
        if lm is not None and lm <= 3:
            # an email from our side since the meeting may have gone to someone else: it lowers the
            # candidate (x 0.6) until stage 2 checks the meeting's participants, never drops it
            sent_after = oe is not None and oe < lm
            c.append(("meeting_followup", 0.9, 0.6 if sent_after else 1.0,
                      f"meeting held {dm(pdt(r.get('last_mtg'), now))}, "
                      + ("someone on our side emailed the account since (account level: check the meeting's participants)"
                         if sent_after else "no email from our side since"),
                      r.get("last_mtg", "")[:16]))
        # meeting prep and the strip: every meeting in the window is a candidate; stakes in the
        # reports raise it, and stage 2 raises it when the read shows what the meeting is for
        meets = nm is not None and 0 <= nm <= prep_window
        if meets:
            stake = []
            if d is not None and -29 <= d <= 180:
                stake.append(f"renewal in {d} days" if d >= 0 else "renewal date just passed")
            if risk and risk >= 4:
                stake.append(f"risk {int(risk)}")
            if usable.get("i_churn") and r.get("i_churn", "").lower() == "true":
                stake.append("ChurnRisk insight")
            if cust_open >= 1:
                stake.append(f"{cust_open} customer thread(s) open")
            hi = bool(stake)
            strip.append(dict(id=rid, name=name, when=r.get("next_mtg", ""), hi=hi, rsrc=rsrc, ksrc=ksrc))
            # today or tomorrow by the local calendar (this machine's zone), not a 48-hour clock: a
            # call this afternoon must not lose to one 47 hours out
            w = pdt(r.get("next_mtg"), now)
            soon = w is not None and (w.astimezone().date() - now.astimezone().date()).days <= 1
            u = (0.8 if hi else 0.5) if soon else (0.6 if hi else 0.4)
            c.append(("meeting_prep", u, 1.0, f"meeting {r.get('next_mtg', '')[:16]} UTC; "
                      + (", ".join(stake) if stake else "nothing else at stake in the reports: the read decides"),
                      r.get("next_mtg", "")[:16]))
        # fresh risk
        fr = last_event({"churn_risk", "exceptional_negative"}, 30)
        if fr is None:
            for key, et in (("ev_churn_risk", "churn_risk"), ("ev_neg", "exceptional_negative")):
                ed = pd(r.get(key))
                if ed and (today - ed).days <= 29:
                    fr = (ed, et, f"{et}@{ed.isoformat()}")
                    break
        if fr:
            ag = (today - fr[0]).days
            c.append(("fresh_risk", 0.85 if ag <= 13 else 0.6, 1.0,
                      f"{fr[1]} event {dm(fr[0])}", fr[2]))
        # renewal decision, record check, checkpoint
        quiet90 = (lt is None or lt > 90) and (le is None or le > 90)
        if d is not None and d < -29:
            # a stale date: an item only when nothing was heard in 90 days, else the record-check line
            if quiet90:
                c.append(("record_check", 0.7, 1.0, f"renewal date {dm(ren)} passed, no communications in 90 days",
                          ren.isoformat()))
            else:
                stale.append(name)
        elif d is not None and d <= 30:
            c.append(("renewal_decision", 0.9, 1.0,
                      (f"renewal date {dm(ren)} passed and the account is still Active" if d < 0
                       else f"renewal in {d} days"), ren.isoformat()))
        elif d is not None and d <= 180:
            rd = pd(r.get("ev_renewal_disc"))
            discussed = rd is not None and (today - rd).days <= 59
            label = "cp60" if d <= 60 else "cp90" if d <= 90 else "cp120" if d <= 120 else "cp180"
            flagged = (usable.get("i_norenew") and r.get("i_norenew", "").lower() == "true") or (risk and risk >= 4)
            if label == "cp180":
                # 121 to 180 days: time for the value review that sets up the renewal conversation
                u = 0.55 if flagged else 0.4
                why = f"renewal in {d} days: value review before the renewal conversation"
            else:
                u = 0.7 if flagged else 0.55 if d <= 60 else 0.45
                why = f"renewal in {d} days"
            if discussed:
                # a renewal conversation in 60 days lowers the checkpoint; it never closes it (the
                # event may be another product's, or a conversation that stalled)
                u *= 0.5
                why += f"; a renewal conversation {dm(rd)} (lowered, not closed: the read checks it)"
            else:
                why += f"; last renewal discussion {dm(rd)}"
            c.append(("renewal_checkpoint", u, 1.0, why, f"{label}@{ren.isoformat()}"))
        if num(r.get("value")) == 0 and r.get("value") != "":
            c.append(("record_check", 0.7, 1.0, "revenue reads 0 on an Active account", "revenue0"))
        # stakeholder change
        fw = last_event({"farewell"}, 30)
        if fw is None:
            ed = pd(r.get("ev_farewell"))
            if ed and (today - ed).days <= 29:
                fw = (ed, "farewell", f"farewell@{ed.isoformat()}")
        if fw:
            ag = (today - fw[0]).days
            c.append(("stakeholder_change", 0.75 if ag <= 13 else 0.5, 1.0,
                      f"personnel-change (farewell) event {dm(fw[0])}", fw[2]))
        # quiet and one-sided chase; a meeting in the window is the next touch, so the silence folds
        # into the prep item ("raise it in the meeting") instead of becoming its own item
        qc = None
        if (le is None or le > 21) and (lt is None or lt > 14):
            qc = ("quiet", 0.6, 1.0,
                  f"customer last engaged {dm(pdt(r.get('last_eng'), now))}; our last touch "
                  f"{dm(pdt(r.get('last_touch'), now))}", (r.get("last_eng") or "never")[:10])
        elif (lt is not None and lt <= 14 and (le is None or le > 30)) or \
                (org_open >= 3 and (ce is None or ce > 10) and (le is None or le > 10)):
            qc = ("one_sided_chase", 0.55, 1.0,
                  f"we touched {dm(pdt(r.get('last_touch'), now))}; customer last engaged "
                  f"{dm(pdt(r.get('last_eng'), now))}; {org_open} of our threads open",
                  (r.get("last_eng") or "never")[:10])
        if qc and meets:
            folded.append(f"{name} ({qc[0]})")
            c = [(t, u, m, (w + f"; {qc[3]}: raise it in the meeting") if t == "meeting_prep" else w, k)
                 for t, u, m, w, k in c]
        elif qc:
            c.append(qc)
        # expansion ready
        expl = num(r.get("exp"))
        hot = num(r.get("exp_hot")) or 0
        # Average health is neutral, not a block: only a Low band (or a score under 40 with no band) is
        band = (r.get("health_band") or "").lower()
        lowrisk = (risk is not None and risk <= 2) or (not risk and (
            band in ("average", "high") or (not band and health is not None and health >= 40)))
        if expl and expl >= 4 and hot >= 1 and lowrisk and cust_open == 0 and \
                (not use_heat or r.get("mom") == "Heating"):
            c.append(("expansion_ready", 0.35, 1.0, f"expansion readiness {int(expl)}, "
                      f"{int(hot)} high-confidence heating opportunit{'y' if hot == 1 else 'ies'}",
                      f"readiness{int(expl)}"))
        # open situation
        if (risk and risk >= 4) or (usable.get("i_churn") and r.get("i_churn", "").lower() == "true"):
            if not fr:
                c.append(("open_situation", 0.7 if d is not None and d <= 120 else 0.6, 1.0,
                          f"{ksrc}, no fresh risk event in 30 days",
                          f"risk{int(risk) if risk else 'churnrisk'}"))
        if a.lane:
            allowed = LANES[a.lane]
            c = [x for x in c if x[0] in allowed and
                 (a.lane != "risk" or x[0] in {"fresh_risk", "open_situation"} or k >= 0.7)]
        if not c:
            notrig.append(name)
            continue
        scored = []
        pinned = d is not None and -29 <= d <= 60 and k >= 0.8

        def evdate(trig, key):
            """Date of the evidence behind a candidate, for account-level dismissals."""
            def dd(col):
                return pdt(r.get(col), now)
            if trig == "reply_needed":
                return dd("cust_email")
            if trig == "meeting_followup":
                return dd("last_mtg")
            if trig == "meeting_prep":
                return dd("next_mtg")
            if trig in ("fresh_risk", "stakeholder_change"):
                if "@" in key:
                    return pd(key.split("@")[1])
                for ed, et, eid in evs:
                    if eid == key:
                        return ed
                return None
            if trig == "renewal_checkpoint" and ren:
                return ren - timedelta(days=int(key[2:5].rstrip("@")))
            if trig in ("quiet", "one_sided_chase"):
                return dd("last_eng")
            return None

        for trig, u, m, why, key in c:
            if rid in dnc and trig in CUSTOMER_FACING:
                dnc_dropped.append(f"{name} ({trig})")
                continue
            if trig in LIVE_DROP and ast == "live" and a.mode != "takeover" and a.lane != "risk" and not pinned:
                live_dropped.append(f"{name} ({trig})")
                continue
            fp = f"{rid}|{trig}|{key}"
            hit, e = ledger_match(fp, ledger, evdate(trig, key))
            if hit in ("exact", "account"):
                ledger_out.setdefault(name, [e, []])[1].append(trig)
                continue
            P = min(100.0, 100 * S * u * m * (1.0 if trig in REACTIVE else att))
            scored.append(dict(base, trigger=trig, U=u, P=P, trig_why=why, fp=fp, pin=pinned,
                               ledger="check" if hit == "check" else "",
                               dnc=rid in dnc, group=[], group_ids=[],
                               wait=ce if trig == "reply_needed" else None))
        if not scored:
            continue
        # a record check never outranks a live trigger on the same account
        scored.sort(key=lambda x: (x["trigger"] == "record_check", -x["P"]))
        top = scored[0]
        top["also"] = [f"{x['trigger']}: {x['trig_why']}" for x in scored[1:]]
        items.append(top)

    # Related accounts: a child whose parent is also in scope joins the parent's item. The member
    # that stands for the group is a pinned one first, then the highest priority; the others move to
    # its "also" line and are read with it.
    groups = {}
    for it in items:
        par = rows.get(it["id"], {}).get("parent", "") or linked.get(it["id"], "")
        groups.setdefault(par if par and par in rows else it["id"], []).append(it)
    related = []
    merged = []
    for root, its in groups.items():
        its.sort(key=lambda x: (not x["pin"], -x["P"]))
        top = its[0]
        for o in its[1:]:
            top["group"].append(o["name"])
            top["group_ids"].append(o["id"])
            top["also"].append(f"{o['name']} (related account, one item): {o['trigger']}: {o['trig_why']}")
            top["fps_more"] = top.get("fps_more", []) + [o["fp"]]
        if len(its) > 1:
            related.append(f"{top['name']} with {', '.join(top['group'])}")
        merged.append(top)
    items = merged

    if a.mode == "takeover":
        for it in items:
            bump = 0.15 if it["trigger"] == "reply_needed" else 0.1 if it["trigger"] in {
                "fresh_risk", "stakeholder_change", "renewal_decision"} else 0
            it["P"] = min(100.0, 100 * (it["S"] + bump))
    items.sort(key=lambda x: (-round(x["P"], 1), -(x["wait"] or 0), x["d"] if x["d"] is not None else 99999, x["name"]))
    # the customer-waiting slot ignores value: the longest wait among reply candidates
    waits = [i for i in items if i["trigger"] == "reply_needed"]
    slot = max(waits, key=lambda i: (i["U"], i["wait"] or 0), default=None)
    short = items[:a.shortlist]
    # Week mode reads every account that meets this week: the read is what tells an EBR or a
    # pricing call from a routine sync, and the reports cannot.
    meets_ids = {m["id"] for m in strip}
    week_meet = lambda i: a.mode == "week" and (i["id"] in meets_ids or any(g in meets_ids for g in i["group_ids"]))  # noqa: E731
    must = [i for i in items if i not in short and (i["trigger"] == "reply_needed" or i["pin"] or i["ledger"] == "check"
                                                    or week_meet(i))]
    cap = 26 if a.mode == "week" else 20
    short = sorted(short + must, key=lambda x: (not x["pin"], x["trigger"] != "reply_needed",
                                                not week_meet(x), -x["P"]))[:cap]
    short.sort(key=lambda x: -x["P"])

    pr = print
    pr(f"# Stage 1: {a.mode} mode" + (f", lane {a.lane}" if a.lane else "") + f", local today {a.today}")
    pr(f"\nBook: {n} accounts joined on id. Risk level on {sum(1 for r in rows.values() if num(r.get('risk')))}"
       f" of {n}; revenue set on {len(vals)} of {n}; health blank or 0 on "
       f"{sum(1 for r in rows.values() if not num(r.get('health')))} of {n}.")
    if dropped:
        pr("Base-rate drops: " + "; ".join(dropped) + ".")
    pr(f"\n## Meetings in the next {prep_window} hours ({len(strip)})")
    for m in sorted(strip, key=lambda x: x["when"]):
        w = pdt(m["when"], now)
        loc = w.astimezone().strftime("%a %-d %b %H:%M %Z") if w else ""
        pr(f"- {m['when']} ({loc} local) | {m['name']} ({m['id']}) | {m['rsrc']}; {m['ksrc']}"
           + (" | high stakes: prep item" if m["hi"] else ""))
    pr(f"\n## Ranked candidates ({len(items)} accounts with a trigger)")
    pr("| # | Account | id | Lane | Trigger | Priority | Stakes | Urgency | Attention | Why now (stage 1 words) | Also | Ledger | Shortlist |")
    pr("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, it in enumerate(items, 1):
        mark = "slot: customer waiting" if it is slot else ("yes" if it in short else "")
        if it["pin"]:
            mark += (" (pinned: risk 4 or 5 renewal inside 60 days, stays on the list; settled as closing,"
                     " it moves to the Closing line)")
        led = it["ledger"] + (" do not contact: internal actions only, no customer draft" if it["dnc"] else "")
        acct = it["name"] + (f" (one item with {', '.join(it['group'])}: related accounts)" if it["group"] else "")
        pr(f"| {i} | {acct} | {it['id']} | {LANE_OF[it['trigger']]} | {it['trigger']} | {round(it['P'])} | "
           f"{it['S']:.2f} | {it['U']:.2f} | {it['att']} | {it['trig_why']}; {'; '.join(it['why'])} | "
           f"{' / '.join(it['also']) or ''} | {led.strip()} | {mark} |")
    pr("\nFingerprints (for the ledger; a reply row's key is its thread key plus the date of the customer's last message, set in stage 2):")
    for i, it in enumerate(items, 1):
        pr(f"- #{i} {it['fp']}" + "".join(f"; {f}" for f in it.get("fps_more", [])))
    reply_ids = [int(i["id"]) for i in short if i["trigger"] == "reply_needed"]
    other_ids = [int(x) for i in short if i["trigger"] != "reply_needed" for x in [i["id"]] + i["group_ids"]]
    reply_ids += [int(x) for i in short if i["trigger"] == "reply_needed" for x in i["group_ids"]]
    pr("\n## Shortlist for stage 2")
    pr(f"- Reply rows (read 30 days): {json.dumps(reply_ids)}")
    pr(f"- Other rows (read 90 days, latest 6 threads each; up to 20 ids per call): {json.dumps(other_ids)}")
    pages = [(i["name"], rows.get(i["id"], {}).get("url", "")) for i in short]
    if any(u for _, u in pages):
        pr("- Account pages (link the account name on its item): "
           + "; ".join(f"{nm} {u}" for nm, u in pages if u))
    pr("\n## Left out")
    pr(f"- Hidden by the ledger ({len(ledger_out)} accounts): " + ("; ".join(
        f"{nm} ({e.get('state')}, {e.get('reason', '')}, {e.get('at')}"
        + (f", until {e['until']}" if e.get("until") else "") + f"; triggers hidden: {', '.join(t)})"
        for nm, (e, t) in sorted(ledger_out.items())) or "none")
       + ". An account comes back when something newer than the dismissal happens.")
    pr(f"- Do not contact, customer-facing item dropped ({len(dnc_dropped)}): " + ("; ".join(dnc_dropped) or "none")
       + ". Internal actions on these accounts stay; never draft to the customer.")
    pr(f"- Quiet or chase folded into this week's meeting ({len(folded)}): " + ("; ".join(folded) or "none"))
    pr(f"- Related accounts made one item ({len(related)}): " + ("; ".join(related) or "none"))
    pr(f"- Live two-way, proactive item dropped ({len(live_dropped)}): " + ("; ".join(live_dropped) or "none"))
    pr(f"- No trigger today ({len(notrig)}): " + ("; ".join(sorted(notrig)) or "none"))
    # an account with an item carries its stale date inside that item's why-now, not on the line
    stale = sorted(set(stale) - {i["name"] for i in items})
    pr(f"- Record-check line, renewal date passed over 30 days ago with threads in 90 days ({len(stale)}): "
       + ("; ".join(stale) or "none") + ". The date is never ranked: ask whether it closed and the date moved.")
    from collections import Counter
    cnt = Counter(i["trigger"] for i in items)
    pr("- Items by trigger: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    if a.mode in ("week", "since"):
        bands = Counter(r.get("health_band") or "blank" for r in rows.values())
        r4 = sum(1 for r in rows.values() if (num(r.get("risk")) or 0) >= 4)
        assessed = sum(1 for r in rows.values() if num(r.get("risk")))
        ren120 = sorted(((pd(r.get("renewal")), r.get("name"), r.get("ev_renewal_disc", ""))
                         for r in rows.values() if pd(r.get("renewal")) and
                         -1 < (pd(r.get("renewal")) - today).days <= 119), key=lambda x: x[0])
        passed = sorted(r.get("name") for r in rows.values()
                        if pd(r.get("renewal")) and pd(r.get("renewal")) < today)
        start = date.fromisoformat(a.since) if a.since else today - timedelta(days=6)
        recent = Counter(et for evl in events.values() for ed, et, _ in evl if ed and ed >= start)
        quiet = sum(1 for it in items if it["trigger"] in {"quiet", "one_sided_chase"})
        pr(f"\n## Book header facts (window from {start.isoformat()})")
        pr(f"- Health (stored band): " + ", ".join(f"{k} {v}" for k, v in sorted(bands.items())))
        pr(f"- Risk 4 or 5: {r4}, of {assessed} with a risk level ({n} accounts)")
        pr(f"- Renewals in the next 120 days ({len(ren120)}): " + "; ".join(
            f"{nm} {dm(rd)} (last renewal discussion {dm(pd(disc))})" for rd, nm, disc in ren120))
        if passed:
            pr(f"- Renewal date passed, still Active ({len(passed)}): " + ", ".join(passed))
        pr("- Events since the window start: " + (", ".join(f"{k} {v}" for k, v in sorted(recent.items())) or "none"))
        pr(f"- Gone quiet or one-sided items: {quiet}")
        if a.mode == "since":
            pr("\n## Since the start date, per account")
            for rid, r in sorted(rows.items(), key=lambda x: x[1].get("name", "")):
                bits = []
                for ed, et, eid in sorted(events.get(rid, []), key=lambda x: x[0] or date.min):
                    if ed and ed >= start:
                        bits.append(f"{et} {dm(ed)} (event {eid})")
                cm = pdt(r.get("cust_email"), now)
                if cm and cm.date() >= start:
                    bits.append(f"customer email {dm(cm)}")
                mt = pdt(r.get("last_mtg"), now)
                if mt and mt.date() >= start:
                    bits.append(f"last meeting {dm(mt)}")
                if bits:
                    pr(f"- {r.get('name')} ({rid}): " + "; ".join(bits))
    if a.lane == "risk":
        low = sorted(r.get("name") for r in rows.values()
                     if not num(r.get("risk")) and num(r.get("health")) and num(r.get("health")) < 40)
        pr(f"\n## Not assessed, health under 40 ({len(low)}): " + (", ".join(low) or "none"))


def cmd_ledger(a):
    at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    line = {"fp": a.fp, "state": a.state, "reason": a.reason, "at": at}
    if a.until:
        line["until"] = a.until
    if a.with_id:
        line["with"] = str(a.with_id)
    if a.scope_id:
        line["scope"] = str(a.scope_id)
    os.makedirs(os.path.dirname(os.path.abspath(a.ledger)), exist_ok=True)
    with open(a.ledger, "a") as f:
        f.write(json.dumps(line) + "\n")
    print("ledger +1:", json.dumps(line))


def cmd_check(a):
    entries = load_ledger(a.ledger, date.fromisoformat(a.today), a.scope_id)
    for fp in a.fp:
        key = (fp.split("|") + ["", ""])[2]
        evd = when(key.split("@", 1)[1]) if "@" in key else None
        hit, e = ledger_match(fp, entries, evd)
        print(f"{fp}: " + (f"SUPPRESSED ({e.get('state')}, {e.get('reason', '')}"
                           + (", account-level, nothing newer" if hit == "account" else "") + ")"
                           if hit in ("exact", "account") else "show"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pulls")
    p.add_argument("--role-field", action="append", required=True,
                   help="repeat for several role fields (the recipe's OR case)")
    p.add_argument("--user-id", type=int, action="append", required=True)
    p.add_argument("--today", required=True)
    p.add_argument("--since")
    p.add_argument("--drop", nargs="*")
    p.add_argument("--split-a", action="store_true")
    p.set_defaults(fn=cmd_pulls)
    r = sub.add_parser("rank")
    r.add_argument("--today", required=True)
    r.add_argument("--a", nargs="+", required=True)
    r.add_argument("--b", nargs="+", required=True)
    r.add_argument("--c1", nargs="+", required=True)
    r.add_argument("--c2", nargs="+", required=True)
    r.add_argument("--ev")
    r.add_argument("--ledger", default=os.path.expanduser("~/.staircase/ledger.jsonl"))
    r.add_argument("--scope-id")
    r.add_argument("--mode", default="today", choices=["today", "week", "since", "takeover"])
    r.add_argument("--lane", choices=sorted(LANES))
    r.add_argument("--since")
    r.add_argument("--now")
    r.add_argument("--weights", default="0.40,0.35,0.25")
    r.add_argument("--shortlist", type=int, default=14)
    r.set_defaults(fn=cmd_rank)
    lg = sub.add_parser("ledger")
    lg.add_argument("--ledger", default=os.path.expanduser("~/.staircase/ledger.jsonl"))
    lg.add_argument("--today", required=True)
    lg.add_argument("--fp", required=True)
    lg.add_argument("--state", required=True, choices=["done", "dismissed", "snoozed", "lifted", "linked"])
    lg.add_argument("--reason", required=True, choices=["done", "not_mine", "wrong", "not_now", "do_not_contact", ""])
    lg.add_argument("--until")
    lg.add_argument("--with", dest="with_id", help="linked: the account id this one joins (one item)")
    lg.add_argument("--scope-id")
    lg.set_defaults(fn=cmd_ledger)
    ck = sub.add_parser("check")
    ck.add_argument("--ledger", default=os.path.expanduser("~/.staircase/ledger.jsonl"))
    ck.add_argument("--today", required=True)
    ck.add_argument("--scope-id")
    ck.add_argument("--fp", nargs="+", action="extend", required=True)
    ck.set_defaults(fn=cmd_check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
