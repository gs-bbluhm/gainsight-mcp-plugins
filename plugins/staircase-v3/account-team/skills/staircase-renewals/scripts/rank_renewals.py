#!/usr/bin/env python3
"""Rank renewals (plan, commit), the expansion ladder, or both, from Staircase report CSVs.

Deterministic scoring for staircase-renewals. The skill works without it (SKILL.md section 7,
reduced mode); this script only removes hand arithmetic. Standard library only.

Usage:
  rank_renewals.py renewals  --today D [--horizon N] [--lens csm] [--override O.csv] [--other OTHER.csv] [--totals] R1 R2 R3
  rank_renewals.py expansion --today D [--override O.csv] OPPS.csv R1 R2 R3
  rank_renewals.py combined  --today D [--window 120] [--horizon N] --me "<full name>" [--override O.csv] OPPS.csv R1 R2 R3
  rank_renewals.py ledger    --today D --fp FP --state done|dismissed|snoozed|lifted --reason R [--until D] [--scope-id N]

Every ranking mode reads the ledger (--ledger, default ~/.staircase/ledger.jsonl; --scope-id is the user id whose
book is ranked). Fingerprints: <account_id>|renewal_plan|<renewal_date> and <account_id>|expansion_plan|<lane>.
A clear covers the account's renewal (or expansion) row until something newer happens: an event in the pulls dated
after it, the renewal crossing 180, 120, 90, 60 or 30 days, or the snooze ending. "Not mine" on the account (<id>|*|*) hides
it until lifted. do_not_contact (<id>|*|*) keeps renewal rows as internal actions and drops expansion rows.

CSV headers are the column labels SKILL.md sections 4 and 11 give (account_id first); files join on
account_id. D is the user's local date. In combined mode the R pulls cover the whole book and R3
carries a renewal_owner column (full name); --me is the user's full name as it appears there.

Override file (after the stage 2 read), header account_id,action,value, one change per line:
  drop_gap / add_gap  engagement | buyer | risk | stakeholder   (drop_gap risk also downgrades the play)
  notice              true    (a read thread is a written non-renewal notice)
  due                 text    (a dated step inside the horizon that the read confirmed)
  play / bucket       text    (renewal rows: the read's play or Commit bucket)
  moving              true    (renewal rows: the read shows the renewal conversation moving; allows Commit)
  unread              true    (expansion rows: Ready but not read; sorts below read rows)
  lane / missing      text    (expansion rows: the read's lane, or its missing piece)
  note                text    (replaces the row note; empty clears it)
  exclude / covered   text    (a reason, or who works it: the row leaves the ranking; covered rows stay in
                               commit totals; a pinned row never leaves the list, only its action changes)
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

GAPS = ("engagement", "buyer", "risk", "stakeholder")
GAP_TEXT = {"engagement": "no commercial discussion in 90 days", "buyer": "no decision-maker touch in 180 days",
            "risk": "risk signal", "stakeholder": "stakeholder change in 30 days"}
DM_MISSING = ("not yet identified", "to be confirmed", "not named", "not identified", "unknown")
LANE_ORDER = {"Ready": 0, "Developing": 1, "Fix first": 2, "Blocked": 3, "Unassessed": 4}
CONF = {"High": 0, "Medium": 1, "Low": 2}
MOM = {"Heating": 0, "Steady": 1, "Cooling": 2}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{(k or "").strip(): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(f)]


def join(paths):
    rows, order = {}, []
    for p in paths:
        for r in read_csv(p):
            aid = r.get("account_id")
            if not aid:
                continue
            if aid not in rows:
                rows[aid] = {"account_id": aid}
                order.append(aid)
            rows[aid].update({k: v for k, v in r.items() if v != ""})
    return [rows[a] for a in order]


def day(v):
    try:
        return dt.date.fromisoformat(v[:10]) if v else None
    except ValueError:
        return None


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def truthy(v):
    return (v or "").lower() == "true"


def within(d, today, n):
    """True when date d falls in the last n days, both ends included."""
    return d is not None and today - dt.timedelta(days=n - 1) <= d <= today


def ahead(d, today, n):
    """True when date d falls in the next n days, both ends included."""
    return d is not None and today <= d <= today + dt.timedelta(days=n - 1)


def renewal_stakes(days):
    if days is None:
        return 0.3
    for limit, s in ((30, 1.0), (60, 0.8), (90, 0.6), (180, 0.35), (365, 0.15)):
        if days <= limit:
            return s
    return 0.05


def risk_stakes(r, today, f):
    lvl = num(r.get("risk_level"))
    if lvl:
        base, basis = {5: 1.0, 4: 0.8, 3: 0.5, 2: 0.25, 1: 0.1}.get(int(lvl), 0.2), f"risk {int(lvl)}"
    else:
        h = num(r.get("health_score"))
        if not h:
            base, basis = 0.3, "risk not assessed, no health data"
        else:
            base, basis = min(0.6, 0.2 + 0.5 * (1 - h / 100)), "risk not assessed, health used"
    if not f["downgraded"]:
        for on, floor, why in ((truthy(r.get("ins_churn_risk")), 0.8, "ChurnRisk insight"),
                               (within(day(r.get("ev_churn_risk")), today, 30), 0.7, "churn-risk event in 30 days"),
                               (f["notice"], 0.9, "non-renewal notice")):
            if on and floor > base:
                base, basis = floor, why
    return base, basis


def percentiles(rows):
    vals = sorted(v for v in (num(r.get("value")) for r in rows) if v and v > 0)
    out = {}
    for r in rows:
        v = num(r.get("value"))
        out[r["account_id"]] = 0.5 if (not v or v <= 0 or len(vals) < 2) else sum(1 for x in vals if x < v) / (len(vals) - 1)
    return out


def load_overrides(path):
    ov = {}
    if path:
        for r in read_csv(path):
            ov.setdefault(r.get("account_id", ""), []).append(((r.get("action") or "").lower(), r.get("value", "")))
    return ov


def has(o, action, value=None):
    return any(a == action and (value is None or v == value) for a, v in o)


def flags(r, today, o):
    rd = day(r.get("renewal_date"))
    days = (rd - today).days if rd else None
    notice = within(day(r.get("ev_churn_notice")), today, 90) or any(a == "notice" and truthy(v) for a, v in o)
    downgraded = has(o, "drop_gap", "risk") and not notice
    strong, fix = [], []
    lvl = num(r.get("risk_level"))
    if lvl and lvl >= 4:
        strong.append(f"risk {int(lvl)}")
    if truthy(r.get("ins_churn_risk")):
        strong.append("ChurnRisk insight")
    if within(day(r.get("ev_churn_risk")), today, 90):
        strong.append(f"churn-risk event {r['ev_churn_risk'][:10]}")
    if notice:
        strong.append("non-renewal notice " + (r.get("ev_churn_notice", "")[:10] or "(read)"))
    h = num(r.get("health_score"))
    if (r.get("health_label") or "").lower() == "low" and h:
        fix.append("health Low")
    if within(day(r.get("ev_very_negative")), today, 30):
        fix.append(f"very negative message {r['ev_very_negative'][:10]}")
    shown = strong + fix
    if downgraded:
        strong, fix = [], []
    many_open = (r.get("open_items") or "").lower() == "many" and (r.get("health_label") or "").lower() != "high"
    hot = num(r.get("exp_hot")) or 0
    ready = num(r.get("exp_readiness"))
    expansion = hot >= 1 or (ready is not None and ready >= 4 and r.get("exp_momentum") == "Heating")
    gaps = {"engagement": not within(day(r.get("ev_commercial")), today, 90),
            "buyer": not within(day(r.get("last_dm_touch")), today, 180),
            "risk": bool(strong or fix),
            "stakeholder": within(day(r.get("ev_personnel")), today, 30)}
    for a, v in o:
        if a in ("drop_gap", "add_gap") and v in GAPS:
            gaps[v] = a == "add_gap"
    return {"days": days, "notice": notice, "downgraded": downgraded, "strong": strong, "fix": fix,
            "shown": shown, "many_open": many_open, "expansion": expansion, "gaps": gaps,
            "waiting": (num(r.get("open_threads_customer")) or 0) >= 1,
            "renewed_recent": within(day(r.get("ev_renewal")), today, 60), "next_meeting": day(r.get("next_meeting"))}


def play(f, lens):
    if f["notice"]:
        return "Defend (notice: read first)"
    if f["strong"] and f["expansion"]:
        return "Defend then grow"
    if f["strong"]:
        return "Defend"
    if f["fix"]:
        if lens == "csm":
            return "Fix first (yours, before the renewal call)"
        return "Route to the CSM" + (" (hold the expansion)" if f["expansion"] else "")
    if f["expansion"]:
        if f["many_open"]:
            return "Grow (clear open items first)" if lens == "csm" else "Grow (check open items with the CSM first)"
        return "Grow"
    return "Steady"


def bucket(f, moving):
    g = f["gaps"]
    if f["strong"] or (f["days"] is not None and f["days"] < 0):
        return "At risk"
    if g["engagement"] and f["days"] is not None and f["days"] <= 60:
        return "At risk"
    if f["fix"] or g["engagement"] or g["buyer"]:
        return "Best case"
    return "Commit" if moving else "Best case"


def pin_text(r, today):
    """Pinned (action-priority.md, list shape): renewal inside 60 days or passed in the last 30,
    on a risk 4 or 5 or ChurnRisk account. Only the ledger removes it; the read changes its action."""
    d = day(r.get("renewal_date"))
    if d is None:
        return ""
    days = (d - today).days
    lvl = num(r.get("risk_level"))
    why = [f"risk {int(lvl)}"] if lvl and lvl >= 4 else []
    if truthy(r.get("ins_churn_risk")):
        why.append("ChurnRisk")
    if not why or not -30 <= days <= 60:
        return ""
    when = f"renews {d.isoformat()}" if days >= 0 else f"renewal date passed {d.isoformat()}"
    return "PINNED: " + ", ".join(why) + ", " + when


def hooks(f, today, horizon, o):
    """Dated steps inside the horizon: (boosting, shown-only)."""
    if not horizon:
        return [], []
    boost, shown = [], []
    if f["days"] is not None and 0 <= f["days"] < horizon:
        boost.append("renews inside the horizon")
    boost += [f"read: {v}" for a, v in o if a == "due"]
    if ahead(f["next_meeting"], today, horizon):
        shown.append(f"meeting {f['next_meeting'].isoformat()}")
    if f["waiting"]:
        shown.append("customer thread open (unconfirmed)")
    return boost, shown


def base_rate(fl):
    """Gaps true on more than 80 percent of 5 or more rows do not separate them."""
    n = len(fl)
    if n < 5:
        return []
    return [g for g in GAPS if sum(1 for f in fl.values() if f["gaps"][g]) > 0.8 * n]


def score_renewals(rows, today, horizon, ov, lens="", pct=None):
    pct = pct or percentiles(rows)
    fl = {r["account_id"]: flags(r, today, ov.get(r["account_id"], [])) for r in rows}
    dropped = base_rate(fl)
    out = []
    for r in rows:
        o, f = ov.get(r["account_id"], []), fl[r["account_id"]]
        days = f["days"]
        ks, kbasis = risk_stakes(r, today, f)
        stakes = 0.40 * renewal_stakes(max(days, 0) if days is not None else None) + 0.35 * ks + 0.25 * pct[r["account_id"]]
        gaps = [GAP_TEXT[g] for g in GAPS if f["gaps"][g] and g not in dropped]
        boost, shown = hooks(f, today, horizon, o)
        pr = 100 * stakes * (0.4 + 0.15 * len(gaps)) * (1.2 if boost else 1.0)
        x = {"kind": "renewal", "account_id": r["account_id"], "account": r.get("account", ""),
             "renewal_date": r.get("renewal_date", ""), "days": days, "priority": min(100, round(pr)),
             "play": play(f, lens), "bucket": bucket(f, has(o, "moving", "true")), "gaps": gaps, "risk_basis": kbasis,
             "pin": pin_text(r, today), "rank": "Ranked",
             "signals": f["shown"] + (["(risk downgraded by the read)"] if f["downgraded"] else [])
                        + (["open items Many"] if f["many_open"] else []) + (["expansion signal"] if f["expansion"] else []),
             "due_soon": boost + shown, "value": num(r.get("value")) or 0,
             "note": "; ".join(n for n in ("renewal event in 60 days: may already be renewed" if f["renewed_recent"] else "",
                                          f"renewal owner {r['renewal_owner']}" if lens == "csm" and r.get("renewal_owner") else "") if n)}
        if x["pin"]:
            x["rank"] = "Pinned"
        if days is not None and days < -30 and not x["pin"]:
            x.update(play="Record check: stale renewal date", bucket="Passed", priority=0, rank="Strip: record check")
        for a, v in o:
            if a in ("play", "bucket", "note"):
                x[a] = v
            elif a == "covered":
                x["note"] = (x["note"] + "; " if x["note"] else "") + f"worked by {v}"
                if not x["pin"]:
                    x.update(priority=0, rank="Strip: covered")
            elif a == "exclude":
                if x["pin"]:
                    x["play"] = f"{x['play']} ({v})"
                else:
                    x.update(bucket="Out", priority=0, note=v, rank="Strip: out")
        out.append(x)
    out.sort(key=sort_key)
    return out, dropped


def sort_key(x):
    """Pinned rows first, soonest renewal first; then the ranked rows by priority; then the strips."""
    if x["rank"] == "Pinned":
        return (0, x["renewal_date"] or "9999", 0, x["account"])
    if x["rank"] == "Ranked":
        return (1, "", -x["priority"], (x["renewal_date"] or "9999") + x["account"])
    return (2, x["rank"], 0, (x["renewal_date"] or "9999") + x["account"])


def other_owner_rows(rows, today):
    """The other-renewal-owner lane: pinned rows go to the top, flagged and routed; the rest stay a strip."""
    out = []
    for r in rows:
        pin = pin_text(r, today)
        who = r.get("renewal_owner") or "another renewal owner"
        out.append({"kind": "other owner", "account_id": r["account_id"], "account": r.get("account", ""),
                    "renewal_date": r.get("renewal_date", ""), "days": None, "priority": 0, "pin": pin,
                    "rank": "Pinned" if pin else "Strip: other renewal owner",
                    "play": (f"Run by {who}: Slack to {who}" if pin else f"Run by {who}"),
                    "bucket": "Out", "gaps": [], "risk_basis": "", "signals": [], "due_soon": [], "note": "", "value": 0})
    return out


def merge_lists(own, others):
    return sorted(own + others, key=sort_key)


def pick_row(rows):
    """The row that stands for the account: best confidence, then momentum, then the newest analysis."""
    def newest(o):
        d = day(o.get("analyzed_at"))
        return -d.toordinal() if d else 0
    return sorted(rows, key=lambda o: (CONF.get(o.get("confidence"), 3), MOM.get(o.get("momentum"), 3), newest(o)))[0]


def ladder(book, opps, today, ov):
    by = {}
    for o in opps:
        by.setdefault(o.get("account_id"), []).append(o)
    n = len(opps)
    tech_sep = n < 5 or sum(1 for o in opps if "validated" not in (o.get("technical") or "").lower()) <= 0.8 * n
    budget_sep = n < 5 or sum(1 for o in opps if "approved" not in (o.get("budget") or "").lower()) <= 0.8 * n
    out = []
    for r in book:
        o = ov.get(r["account_id"], [])
        f = flags(r, today, o)
        rows = by.get(r["account_id"], [])
        fix = f["strong"] + f["fix"]
        ready = [x for x in rows if x.get("confidence") == "High" and x.get("momentum") == "Heating"
                 and "blocked" not in (x.get("technical") or "").lower()]
        blocked = [x for x in rows if "blocked" in (x.get("technical") or "").lower()]
        missing, pick = "", None
        if not rows:
            lane = "Unassessed" if num(r.get("exp_readiness")) is None else "Developing"
            missing = "" if lane == "Unassessed" else "assessed, no offering rows"
        elif fix:
            lane, missing, pick = "Fix first", "; ".join(fix), pick_row(rows)
        elif ready:
            lane, pick = "Ready", pick_row(ready)
        elif len(blocked) == len(rows):
            lane, pick = "Blocked", pick_row(blocked)
            missing = (pick.get("timeline") or "")[:140]
        else:
            lane, pick = "Developing", pick_row(rows)
            dmv = (pick.get("decision_maker") or "").lower()
            if not dmv or any(m in dmv for m in DM_MISSING):
                missing = "buyer not named"
            elif pick.get("confidence") != "High":
                missing = f"signal not confirmed ({pick.get('confidence') or 'no'} confidence)"
            elif pick.get("momentum") != "Heating":
                missing = f"timing ({pick.get('momentum') or 'momentum unknown'})"
            elif tech_sep and "validated" not in (pick.get("technical") or "").lower():
                missing = "technical fit not validated"
            elif budget_sep and "approved" not in (pick.get("budget") or "").lower():
                missing = "budget unconfirmed"
            else:
                missing = "next step not stated"
        p = pick or {}
        fresh = within(day(p.get("analyzed_at")), today, 30)
        x = {"kind": "expansion", "account_id": r["account_id"], "account": r.get("account", ""), "lane": lane,
             "offering": p.get("offering", ""), "category": p.get("category", ""),
             "confidence": p.get("confidence", ""), "momentum": p.get("momentum", ""),
             "analyzed_at": p.get("analyzed_at", ""), "fresh": fresh, "missing_or_blocker": missing,
             "offerings": len(rows), "renewal_date": r.get("renewal_date", ""), "days": f["days"],
             "risk_note": "; ".join(f["shown"]) if lane == "Unassessed" else "",
             "timeline": p.get("timeline", ""), "value": num(r.get("value")) or 0, "note": "", "_f": f, "_r": r}
        x["unread"] = has(o, "unread", "true")
        if x["unread"]:
            x["note"] = "not verified by the read"
        for a, v in o:
            if a == "lane" and v in LANE_ORDER:
                x["lane"] = v
            elif a in ("missing", "note"):
                x["missing_or_blocker" if a == "missing" else "note"] = v
            elif a in ("exclude", "covered"):
                x.update(lane="Out", note=(f"covered by {v}" if a == "covered" else v))
        out.append(x)
    out.sort(key=lambda x: (LANE_ORDER.get(x["lane"], 9), x["unread"], CONF.get(x["confidence"], 3), not x["fresh"],
                            not (x["days"] is not None and 0 <= x["days"] <= 180),
                            x["days"] if x["days"] is not None else 9999, -x["value"], x["account"]))
    notes = [] if tech_sep else ["technical status not validated on more than 80 percent of rows: not used as a missing piece"]
    notes += [] if budget_sep else ["budget unconfirmed on more than 80 percent of rows: not used as a missing piece"]
    return out, notes


def combined(book, opps, today, window, horizon, me, ov):
    def in_window(r):
        d = day(r.get("renewal_date"))
        return d is not None and (today - dt.timedelta(days=60)) <= d <= today + dt.timedelta(days=window - 1)
    mine = lambda r: not me or "renewal_owner" not in r or r.get("renewal_owner") == me  # noqa: E731
    ren_rows = [r for r in book if in_window(r) and mine(r)]
    other = [r for r in book if in_window(r) and not mine(r)]
    pct = percentiles(book)
    ren, dropped = score_renewals(ren_rows, today, horizon, ov, pct=pct)
    lad, notes = ladder([r for r in book if r not in ren_rows], opps, today, ov)
    exp, outside_risk = [], []
    for x in lad:
        f, r = x["_f"], x["_r"]
        if f["strong"] and x["lane"] in ("Unassessed", "Blocked"):
            outside_risk.append(x)
        if x["lane"] not in ("Ready", "Developing", "Fix first"):
            continue
        ks, _ = risk_stakes(r, today, f)
        stakes = 0.40 * renewal_stakes(f["days"]) + 0.35 * ks + 0.25 * pct[r["account_id"]]
        urgent = x["fresh"] and any(w in (x["timeline"] or "").lower() for w in ("immediate", "this week", "within the next week"))
        u = {"Ready": 0.6 if urgent else 0.5, "Developing": 0.35, "Fix first": 0.4}[x["lane"]]
        boost, shown = hooks(f, today, horizon, ov.get(x["account_id"], []))
        pr = 100 * stakes * u * (1.2 if boost else 1.0)
        exp.append({"kind": "expansion", "account_id": x["account_id"], "account": x["account"],
                    "renewal_date": x["renewal_date"], "days": x["days"], "priority": min(100, round(pr)),
                    "play": {"Ready": "Grow (Ready)", "Developing": "Develop: " + x["missing_or_blocker"],
                             "Fix first": "Route to the CSM (fix first)"}[x["lane"]],
                    "bucket": "", "gaps": [], "signals": [x["offering"] + (" (analysis " + x["analyzed_at"] + ")" if x["analyzed_at"] else "")],
                    "due_soon": boost + shown + (["timeline says immediate"] if urgent else []),
                    "note": (x["note"] + "; " if x["note"] else "") + f"{x['offerings']} offering rows"
                            + ("; renewal run by " + (r.get("renewal_owner") or "another owner") if r in other else ""),
                    "value": x["value"], "pin": "", "rank": "Ranked"})
    strip = [{"kind": "outside, strong risk", "account_id": x["account_id"], "account": x["account"],
              "renewal_date": x["renewal_date"], "days": None, "priority": 0, "play": "For the CSM, not an expansion conversation",
              "bucket": "Out", "gaps": [], "signals": x["_f"]["shown"], "due_soon": [], "note": x["lane"], "value": 0,
              "pin": "", "rank": "Strip: outside the window, strong risk"} for x in outside_risk]
    allx = merge_lists(ren + exp, other_owner_rows(other, today)) + strip
    unassessed = sum(1 for x in lad if x["lane"] == "Unassessed")
    info = [f"book rows: {len(book)} (check against the COUNT)", f"renewal rows: {len(ren_rows)}",
            f"expansion rows ranked: {len(exp)}", f"unassessed accounts: {unassessed}"]
    if dropped:
        info.append("gaps dropped by the base rate: " + ", ".join(dropped))
    return allx, info + notes


# ---------------------------------------------------------------- ledger (action-priority.md, Ledger)

# A clear written by either skill on these triggers covers the matching row here, at account level.
FAMILY = {"renewal": {"renewal_plan", "renewal_checkpoint", "renewal_decision"},
          "expansion": {"expansion_plan", "expansion_ready"}}
EVIDENCE = ("ev_churn_risk", "ev_churn_notice", "ev_personnel", "ev_very_negative", "ev_commercial", "ev_renewal")


def load_ledger(path, today, scope):
    active = []
    if not path or not os.path.exists(path):
        return active
    with open(path, encoding="utf-8") as f:
        for ln in f:
            try:
                e = json.loads(ln)
            except ValueError:
                continue
            if scope and e.get("scope") and str(e["scope"]) != str(scope):
                continue
            if e.get("state") == "lifted":
                active = [x for x in active if not (x.get("fp") == e.get("fp") and
                                                    (not e.get("reason") or x.get("reason") == e["reason"]))]
                continue
            if e.get("state") == "snoozed" and e.get("until") and e["until"] < today.isoformat():
                continue
            active.append(e)
    return active


def fingerprint(x):
    if x["kind"] == "expansion":
        return f"{x['account_id']}|expansion_plan|{x.get('lane') or 'ladder'}"
    return f"{x['account_id']}|renewal_plan|{x.get('renewal_date') or 'none'}"


def newer(r, at, today):
    """Something happened after the clear: an event in the pulls, or the renewal crossed a checkpoint."""
    if any((d := day(r.get(c))) and d > at for c in EVIDENCE):
        return True
    rd = day(r.get("renewal_date"))
    if rd:
        then, now = (rd - at).days, (rd - today).days
        return any(then > t >= now for t in (180, 120, 90, 60, 30, 0))
    return False


def apply_ledger(res, raw, entries, today):
    """Hide cleared rows (pins too: only the ledger removes a pin); mark do-not-contact accounts."""
    dnc = {e.get("fp", "").split("|")[0] for e in entries if e.get("reason") == "do_not_contact"}
    hidden = []
    for x in res:
        if x["kind"] not in ("renewal", "expansion"):
            continue
        aid, fp = x["account_id"], fingerprint(x)
        x["fp"] = fp
        fam = FAMILY[x["kind"]]
        hit = None
        for e in entries:
            if e.get("reason") == "do_not_contact" or e.get("state") == "linked":
                continue
            ea, et, ek = (e.get("fp", "").split("|") + ["", ""])[:3]
            if ea != aid:
                continue
            if et == "*":
                hit = e
                break
            # a row's fingerprint stays the same from event to event, so even an exact match holds
            # only until something newer happens
            at = day(e.get("at", ""))
            if (e.get("fp") == fp or et in fam) and at and not newer(raw.get(aid, {}), at, today):
                hit = e
        if hit:
            hidden.append(f"{x['account']} ({hit.get('state')}, {hit.get('reason', '')}, {str(hit.get('at', ''))[:10]}"
                          + (f", until {hit['until']}" if hit.get("until") else "") + ")")
            x.update(priority=0, rank="Strip: hidden by your clears", pin="")
            if "lane" in x:
                x["lane"] = "Out"
        elif aid in dnc:
            if x["kind"] == "expansion":
                x.update(priority=0, rank="Strip: do not contact", lane="Out" if "lane" in x else x.get("lane", ""))
            x["note"] = (x.get("note", "") + "; " if x.get("note") else "") + \
                "do not contact: internal actions only, no customer draft"
    return hidden


def cmd_ledger(a):
    line = {"fp": a.fp, "state": a.state, "reason": a.reason,
            "at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}
    if a.until:
        line["until"] = a.until
    if a.scope_id:
        line["scope"] = str(a.scope_id)
    os.makedirs(os.path.dirname(os.path.abspath(a.ledger)), exist_ok=True)
    with open(a.ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")
    print("ledger +1:", json.dumps(line))


def table(res, cols):
    lines = ["| # | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for i, x in enumerate(res, 1):
        cells = ["; ".join(x.get(c) or []) if isinstance(x.get(c), list) else ("" if x.get(c) is None else str(x.get(c)))
                 for c in cols]
        lines.append(f"| {i} | " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["renewals", "expansion", "combined", "ledger"])
    ap.add_argument("--today", required=True, help="the user's local date, YYYY-MM-DD")
    ap.add_argument("--ledger", default=os.path.expanduser("~/.staircase/ledger.jsonl"))
    ap.add_argument("--scope-id", default="", help="the user id whose book is ranked (ledger scope)")
    ap.add_argument("--fp", default="", help="ledger mode: the fingerprint")
    ap.add_argument("--state", default="", choices=["", "done", "dismissed", "snoozed", "lifted"])
    ap.add_argument("--reason", default="", choices=["", "done", "not_mine", "wrong", "not_now", "do_not_contact"])
    ap.add_argument("--until", default="")
    ap.add_argument("--window", type=int, default=120, help="combined mode: the renewal window in days")
    ap.add_argument("--horizon", type=int, default=0, help="an action horizon the user named, in days")
    ap.add_argument("--me", default="", help="combined mode: the user's full name, as in renewal_owner")
    ap.add_argument("--lens", default="", choices=["", "csm"], help="csm: the user is the CSM, not the renewal owner")
    ap.add_argument("--override", default="")
    ap.add_argument("--other", default="", help="renewals mode: the other-renewal-owner lane CSV (pins and strip)")
    ap.add_argument("--totals", action="store_true", help="commit mode: print bucket counts and value sums")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    if a.mode == "ledger":
        if not (a.fp and a.state):
            sys.exit("ledger needs --fp and --state")
        cmd_ledger(a)
        return
    if not a.files:
        sys.exit(f"{a.mode} needs the pull CSVs")
    today = dt.date.fromisoformat(a.today)
    ov = load_overrides(a.override)
    entries = load_ledger(a.ledger, today, a.scope_id)
    info = []
    if a.mode == "renewals":
        raw = {r["account_id"]: r for r in join(a.files)}
        res, dropped = score_renewals(list(raw.values()), today, a.horizon, ov, a.lens)
        info = [f"rows: {len(res)} (check against the COUNT)"]
        if a.other:
            others = other_owner_rows(join([a.other]), today)
            res = merge_lists(res, others)
            info.append(f"other renewal owner lane: {len(others)} rows, {sum(1 for x in others if x['pin'])} pinned")
        if dropped:
            info.append("gaps dropped by the base rate (true on more than 80 percent): " + ", ".join(dropped))
        cols = ["rank", "pin", "priority", "kind", "account", "renewal_date", "days", "play", "bucket", "gaps",
                "signals", "risk_basis", "due_soon", "note", "fp", "account_id"]
    else:
        if len(a.files) < 2:
            sys.exit(f"{a.mode} needs OPPS.csv, then the book pulls (R1.csv R2.csv R3.csv)")
        opps, book = read_csv(a.files[0]), join(a.files[1:])
        raw = {r["account_id"]: r for r in book}
        if a.mode == "expansion":
            res, info = ladder(book, opps, today, ov)
            info = [f"book rows: {len(book)} (check against the COUNT)"] + info
            cols = ["lane", "account", "offering", "category", "confidence", "momentum", "analyzed_at",
                    "missing_or_blocker", "offerings", "renewal_date", "risk_note", "note", "fp", "account_id"]
        else:
            if not a.me:
                sys.exit("combined needs --me with the user's full name")
            res, info = combined(book, opps, today, a.window, a.horizon, a.me, ov)
            cols = ["rank", "pin", "priority", "kind", "account", "renewal_date", "play", "bucket", "gaps",
                    "signals", "due_soon", "note", "fp", "account_id"]
    hidden = apply_ledger(res, raw, entries, today)
    if a.mode == "expansion":
        res.sort(key=lambda x: x["lane"] == "Out")
    else:
        res.sort(key=sort_key)
    info.append(f"hidden by the user's clears ({len(hidden)}): " + ("; ".join(hidden) or "none")
                + ". A row comes back when something newer happens (an event, a checkpoint, the snooze ends).")
    for x in res:
        for k in [k for k in x if k.startswith("_")]:
            x.pop(k)
    if a.json:
        print(json.dumps({"rows": res, "info": info}, indent=1, default=str))
        return
    print(table(res, cols))
    print()
    for line in info:
        print(line)
    if a.totals and a.mode == "renewals":
        tot = {}
        for x in res:
            if x["kind"] != "renewal" or x["bucket"] in ("Out", "Passed"):
                continue
            t = tot.setdefault(x["bucket"], [0, 0.0])
            t[0] += 1
            t[1] += x["value"]
        print("Commit buckets (accounts, sum of the value column): "
              + "; ".join(f"{b} {n}, {v:.0f}" for b, (n, v) in sorted(tot.items())))


if __name__ == "__main__":
    main()
