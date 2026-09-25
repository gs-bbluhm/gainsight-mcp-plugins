#!/usr/bin/env python3
"""
Team Manager / 1:1 Prep analysis engine (live Staircase MCP version).

Ports a validated team-effort methodology (percentiles, the overwhelmed test, book
rollup, account flags, org summary, load distribution, bandwidth/capacity read) onto
live `staircase_run_report` pulls instead of CSV exports. Same interpretive logic; the
input is MCP report CSVs, not manual exports.

Nothing here hardcodes a role/book-owner field: pass its column label via --role-col.
See ../../skills/staircase-mcp-expert/SKILL.md (step 0, the first-call contract) for
how that field is resolved per org (Owner is NOT always the CSM).

Inputs (CSV files saved from staircase_run_report; column labels are the contract):

  --roster (R1, entity=user, one row per teammate). Required columns (report `label`s):
    "First name","Last name","Title","Manager","Effort (hrs)","Sent emails",
    "Received emails","Response time to emails (hrs)","Emails with positive sentiment",
    "Emails with negative sentiment","Emails with neutral sentiment","Attended meetings",
    "Meetings time (hrs)","Assigned tickets"
    (all the stat columns take dateRange + filter.customer arguments; state the window
    once when rendering. See
    ../../skills/staircase-mcp-expert/references/analysis-methodology.md's timeframe
    caveat; the same caution applies here.)

  --book (R2, entity=customer, one row per account, filtered
    `customer.<book_owner_field>.full_name In [roster]`).
    Required columns: "Account","<role label>" (the book-owner column's label, passed
    via --role-col), "Tier","Revenue","Risk level","Health score","Renewal date",
    "Last engagement","Stakeholders count","Multi threaded","Team effort (hours)",
    "Time frame revenue","Owner effort (hours)","Owner","Expansion readiness level",
    "Expansion momentum"
    Optional (used when present, degrade gracefully when absent):
    "Last reach-out","Last email from them","Last meeting","Ticket count","Ticket comments"
    These are all live customer.* fields (see field-catalog.md §6: ticket
    submitted/comment counts ARE available at the customer level, contrary to the old
    "use the CRM" note, which was about ticket *status* only).

  --expansion (R3, optional, entity=expansion_opportunity, one row per opportunity).
    Required columns: "Account","<role label>","Offering","Category","Momentum"
    (never sum "Opportunity value": it is prose, not numeric)

Emits one JSON manifest to stdout (and --out if given). The SKILL renders from this
JSON; it does not re-derive the math.
"""
import argparse, json, sys
import pandas as pd
import numpy as np


def _num(s):
    return pd.to_numeric(s, errors="coerce") if s is not None else pd.Series(dtype=float)


def _team_member(df):
    """Combine First/Last name into the single display key used throughout."""
    return (df["First name"].fillna("").astype(str).str.strip() + " " +
            df["Last name"].fillna("").astype(str).str.strip()).str.strip()


def _clean(records):
    """Replace NaN/NaT with None in a list of dicts before they leave the engine.
    Pandas leaves real NaN floats in missing numeric cells; json.dumps happily
    emits a literal `NaN` token for those (valid inside a raw <script> tag, but
    invalid JSON, so it breaks the moment a consumer does JSON.parse on this output).
    Always route to_dict("records") output through this before returning."""
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and v != v:
                r[k] = None
    return records


def _with_renewal_window(d):
    """Shared renewal-date parsing: days_to_renewal + renewal_90d boolean.
    Every account-level view needs this, so it is computed once and reused everywhere."""
    d["Renewal date"] = pd.to_datetime(d.get("Renewal date"), errors="coerce", utc=True)
    now = pd.Timestamp.now("UTC")
    d["days_to_renewal"] = (d["Renewal date"] - now).dt.days
    d["renewal_90d"] = d["days_to_renewal"].between(0, 90)
    return d


# ---------------------------------------------------------------------------
# Roster / personal effort (R1): the Team Effort lens
# ---------------------------------------------------------------------------
def team_pulse(roster):
    """Percentiles, the overwhelmed test, per-manager rollup. Identical math to the
    validated effort methodology's team_pulse, fed by MCP columns."""
    roster = roster.copy()
    roster["Team member"] = _team_member(roster)
    num_cols = ["Effort (hrs)", "Sent emails", "Received emails",
                "Response time to emails (hrs)", "Attended meetings", "Meetings time (hrs)",
                "Emails with positive sentiment", "Emails with negative sentiment",
                "Emails with neutral sentiment"]
    for c in num_cols:
        if c in roster.columns:
            roster[c] = _num(roster[c])

    act = roster[roster["Effort (hrs)"].fillna(0) > 0].copy()
    if len(act) == 0:
        return {"active_members": 0}

    pos = act.get("Emails with positive sentiment", pd.Series(0, index=act.index))
    neg = act.get("Emails with negative sentiment", pd.Series(0, index=act.index))
    neu = act.get("Emails with neutral sentiment", pd.Series(0, index=act.index))
    denom = (pos.fillna(0) + neg.fillna(0) + neu.fillna(0)).replace(0, np.nan)
    act["neg_ratio"] = (neg / denom).round(3)

    p90 = act["Effort (hrs)"].quantile(0.9)
    resp = act.get("Response time to emails (hrs)")
    deg = pd.Series(False, index=act.index)
    if resp is not None:
        deg = deg | (_num(resp) > 24)
    deg = deg | (act["neg_ratio"] > 0.15)
    overwhelmed = act[(act["Effort (hrs)"] >= p90) & deg]

    def rows(df, cols):
        cols = [c for c in cols if c in df.columns]
        return _clean(df[cols].round(2).to_dict("records"))

    pulse = {
        "active_members": int(len(act)),
        "effort_percentiles": {k: round(float(v), 1) for k, v in
                               act["Effort (hrs)"].describe(
                                   percentiles=[.25, .5, .75, .9, .95]).items()},
        "overwhelmed_threshold_hrs": round(float(p90), 1),
        "overwhelmed": rows(overwhelmed.sort_values("Effort (hrs)", ascending=False),
                            ["Team member", "Title", "Manager", "Effort (hrs)",
                             "Attended meetings", "Response time to emails (hrs)", "neg_ratio"]),
        "top_effort": rows(act.sort_values("Effort (hrs)", ascending=False).head(25),
                           ["Team member", "Manager", "Effort (hrs)", "Sent emails",
                            "Attended meetings", "Response time to emails (hrs)", "neg_ratio"]),
        "all_members": rows(act.sort_values("Effort (hrs)", ascending=False),
                            ["Team member", "Title", "Manager", "Effort (hrs)", "Sent emails",
                             "Received emails", "Response time to emails (hrs)",
                             "Attended meetings", "Meetings time (hrs)", "Assigned tickets",
                             "neg_ratio"]),
    }
    if "Manager" in act.columns:
        mgr = act.groupby("Manager").agg(
            members=("Team member", "count"),
            total_effort=("Effort (hrs)", "sum"),
            median_effort=("Effort (hrs)", "median"),
            total_meetings=("Attended meetings", "sum"),
            median_response=("Response time to emails (hrs)", "median"),
        ).reset_index().round(1)
        pulse["by_manager"] = _clean(mgr.sort_values("total_effort", ascending=False).to_dict("records"))
    return pulse


# ---------------------------------------------------------------------------
# Book rollup (from R2, client-side group-by role_col: the proven "one flat pull,
# client-side lenses" pattern; server-side child-aggregation on a discovered custom
# referenceField is confirmed to work too and gives identical numbers, but computing
# all rollup metrics here in one place is simpler to maintain).
# ---------------------------------------------------------------------------
def book_rollup(book, role_col):
    for c in ["Revenue", "Team effort (hours)", "Team effort cost", "Time frame revenue",
              "Owner effort (hours)", "Risk level", "Health score"]:
        if c in book.columns:
            book[c] = _num(book[c])
    d = book.copy()
    d["Last engagement"] = pd.to_datetime(d.get("Last engagement"), errors="coerce", utc=True)
    now = pd.Timestamp.now("UTC")
    d["days_idle"] = (now - d["Last engagement"]).dt.days
    d["stale30"] = d["days_idle"] > 30
    d["high_risk"] = _num(d.get("Risk level")) >= 4
    d["neglected"] = (_num(d["Revenue"]) >= 150_000) & (d["Team effort (hours)"].fillna(0) < 3)
    if "Renewal date" in d.columns:
        d = _with_renewal_window(d)
    else:
        d["renewal_90d"] = False
    d = d[d[role_col].notna() & (d[role_col].astype(str).str.strip() != "")]
    if len(d) == 0:
        return []
    agg_spec = {
        "accounts": ("Account", "count"),
        "total_ARR": ("Revenue", "sum"),
        "team_hours": ("Team effort (hours)", "sum"),
        "owner_hours": ("Owner effort (hours)", "sum"),
        "at_risk": ("high_risk", "sum"),
        "stale": ("stale30", "sum"),
        "neglected_highvalue": ("neglected", "sum"),
        "avg_health": ("Health score", "mean"),
        "renewals_90d": ("renewal_90d", "sum"),
    }
    if "Total meetings" in d.columns:
        d["Total meetings"] = _num(d["Total meetings"])
        agg_spec["meetings"] = ("Total meetings", "sum")
    g = d.groupby(d[role_col].astype(str)).agg(**agg_spec).reset_index().rename(
        columns={role_col: "person"})
    g["renewals_90d"] = g["renewals_90d"].astype(int)
    g["at_risk"] = g["at_risk"].astype(int)
    g["stale"] = g["stale"].astype(int)
    g["neglected_highvalue"] = g["neglected_highvalue"].astype(int)
    # Round the raw sums/means to 1dp, but NOT the two ratio columns below. A blanket
    # round(1) over everything would corrupt small ratios (e.g. 0.05 -> 0.0), a bug
    # this exact hand-check step caught (also latent in the original CSV-based version).
    round1_cols = [c for c in ["total_ARR", "team_hours", "owner_hours", "meetings", "avg_health"]
                   if c in g.columns]
    g[round1_cols] = g[round1_cols].round(1)
    g["owner_share"] = (g["owner_hours"] / g["team_hours"].replace(0, np.nan)).round(2)
    g["hours_per_account"] = (g["team_hours"] / g["accounts"]).round(2)
    return _clean(g.sort_values("total_ARR", ascending=False).to_dict("records"))


# ---------------------------------------------------------------------------
# Account flags (from R2). One deliberate change from the original CSV-based version:
# the efficiency/overspend denominator is "Time frame revenue"
# (customer.effort.team_effort_time_range_revenue), NOT annual "Revenue" (validated
# internally). Annual Revenue is still used for the value-size flags
# (underspend/at-risk/stale), since those are about deal size, not effort efficiency.
#
# Every lens below carries the confirmed book-owner/CSM name ("CSM") and Tier, so a
# manager reading any account-lens table can see who owns it and where it sits in the
# portfolio without cross-referencing the roster. "at_risk_low_effort" and
# "renewals_90d" are intentionally NOT capped, by design: a manager needs the full
# list for these two, not a top-N sample.
# ---------------------------------------------------------------------------
def account_flags(book, role_col=None):
    for c in ["Revenue", "Team effort (hours)", "Team effort cost", "Time frame revenue",
              "Risk level", "Health score", "Stakeholders count", "Ticket count",
              "Ticket comments"]:
        if c in book.columns:
            book[c] = _num(book[c])
    d = book.copy()
    d["Last engagement"] = pd.to_datetime(d.get("Last engagement"), errors="coerce", utc=True)
    now = pd.Timestamp.now("UTC")
    d["days_idle"] = (now - d["Last engagement"]).dt.days
    d["cost_pct_range_rev"] = (d["Team effort cost"] /
                               d["Time frame revenue"].replace(0, np.nan) * 100).round(2)
    if "Renewal date" in d.columns:
        d = _with_renewal_window(d)
    if role_col and role_col in d.columns:
        d["CSM"] = d[role_col]

    base = ["Account", "Tier", "CSM", "Revenue", "Renewal date", "days_to_renewal",
            "Time frame revenue", "Team effort (hours)", "Team effort cost",
            "cost_pct_range_rev", "days_idle", "Health score", "Risk level",
            "Stakeholders count", "Multi threaded", "Last reach-out", "Last email from them",
            "Last meeting", "Ticket count", "Ticket comments"]
    base = [c for c in base if c in d.columns]

    def recs(df):
        num_cols = df.select_dtypes(include="number").columns
        return _clean(df[base].assign(**{c: df[c].round(1) for c in num_cols if c in base}
                                       ).to_dict("records"))

    overspend = d[(d["Time frame revenue"] > 0) & (d["Team effort cost"] > 0)].sort_values(
        "cost_pct_range_rev", ascending=False).head(40)
    underspend = d[(d["Revenue"] >= 100_000) & (d["Team effort (hours)"].fillna(0) < 3)
                   ].sort_values("Revenue", ascending=False).head(40)
    at_risk_low = d[(_num(d.get("Risk level")) >= 4) & (d["Revenue"] > 100_000)
                    & (d["Team effort (hours)"].fillna(0) < 5)].sort_values(
                    "Revenue", ascending=False)
    stale = d[(d["Revenue"] > 100_000) & (d["days_idle"] > 30)].sort_values(
        "days_idle", ascending=False).head(40)
    renewals_90d = d[d.get("renewal_90d", False) == True].sort_values("days_to_renewal") \
        if "renewal_90d" in d.columns else d.iloc[0:0]
    # "Multi threaded" measures whether recent COMMUNICATION is spread across contacts,
    # not how many named stakeholders are on file: an account can carry several
    # stakeholders in the CRM and still be single-threaded if only one of them actually
    # replies. That combination (multi_threaded=false + stakeholders_count high) is itself
    # a signal: engaged with the wrong single point of contact despite having other
    # options on file. Show both columns so a manager reads the real story, not a
    # contradiction.
    single_threaded_at_risk = d[(d.get("Multi threaded").astype(str).str.lower() == "false") &
                                 (_num(d.get("Risk level")).fillna(0) >= 4)].sort_values(
                                 "Revenue", ascending=False) \
        if "Multi threaded" in d.columns else d.iloc[0:0]

    return {
        "overspend": recs(overspend),
        "overspend_total_count": int(len(d[(d["Time frame revenue"] > 0) & (d["Team effort cost"] > 0)])),
        "underspend_highvalue": recs(underspend),
        "underspend_total_count": int(len(d[(d["Revenue"] >= 100_000) & (d["Team effort (hours)"].fillna(0) < 3)])),
        "at_risk_low_effort": recs(at_risk_low),
        "stale_highvalue": recs(stale),
        "stale_total_count": int(len(d[(d["Revenue"] > 100_000) & (d["days_idle"] > 30)])),
        "stale_revenue_at_stake": float(stale["Revenue"].sum()) if len(stale) else 0.0,
        "renewals_90d": recs(renewals_90d),
        "single_threaded_at_risk": recs(single_threaded_at_risk),
        "single_threaded_note": "Multi threaded reflects who actually replies in recent "
            "communications, not the named-stakeholder roster: an account can show several "
            "Stakeholders count and still be single-threaded. Read Stakeholders count alongside "
            "Last email from them / Last reach-out / Last meeting to see whether the extra "
            "contacts are actually engaged.",
    }


def org_summary(book, role_col):
    rev = _num(book["Revenue"]) if "Revenue" in book.columns else pd.Series(dtype=float)
    th = _num(book.get("Team effort (hours)"))
    oh = _num(book.get("Owner effort (hours)"))
    tc = _num(book.get("Team effort cost"))
    worked = book[th.fillna(0) > 0]
    owner_share = (oh / th.replace(0, np.nan))

    by_tier = []
    if "Tier" in book.columns:
        t = book.copy()
        t["Revenue"] = _num(t.get("Revenue"))
        t["Health score"] = _num(t.get("Health score"))
        t["high_risk"] = _num(t.get("Risk level")).fillna(0) >= 4
        tg = t.groupby("Tier").agg(
            accounts=("Account", "count"), total_revenue=("Revenue", "sum"),
            at_risk=("high_risk", "sum"), avg_health=("Health score", "mean"),
        ).reset_index()
        tg["at_risk"] = tg["at_risk"].astype(int)
        tg[["total_revenue", "avg_health"]] = tg[["total_revenue", "avg_health"]].round(1)
        by_tier = _clean(tg.sort_values("total_revenue", ascending=False).to_dict("records"))

    return {
        "total_accounts": int(len(book)),
        "worked_accounts": int(len(worked)),
        "total_revenue": float(rev.sum()),
        "total_team_hours": round(float(th.sum()), 1),
        "total_team_cost": round(float(tc.sum()), 0) if tc is not None else None,
        "median_owner_share_of_effort": round(float(owner_share.median()), 2)
            if owner_share.notna().any() else None,
        "accounts_owner_under_25pct": int((owner_share < 0.25).sum()),
        "book_owner_field": role_col,
        "by_tier": by_tier,
        "note": "'owner_share' is the standard `Owner` field's engagement (often a "
                "different role than the CSM; see R7b), not the confirmed book-owner "
                "field's own share. Read it as cross-functional (e.g. AM) engagement.",
    }


def load_distribution(book_rows):
    if not book_rows:
        return {}
    df = pd.DataFrame(book_rows)
    def pct(col):
        if col not in df.columns:
            return {}
        return {k: round(float(v), 1) for k, v in
                df[col].describe(percentiles=[.5, .9]).items()}
    return {"people": int(len(df)), "accounts": pct("accounts"),
            "total_ARR": pct("total_ARR"), "hours_per_account": pct("hours_per_account")}


def capacity_signals(roster, book_rows):
    """Bandwidth read: who has personal-effort headroom while their existing book
    carries risk exposure, vs. who simply isn't a book-carrier in this pull at all.

    Renamed from "under_utilization"/"coverage gap": the old name read to a manager as
    "these accounts are poorly covered" (low engagement), when the actual test is
    "this person's own workload is low relative to book-carrying peers, AND their book
    carries at-risk/stale/neglected exposure." Both readings can be true at once (room
    to help elsewhere, or under-serving their own at-risk book); the `reason` string on
    each row spells out which numbers drove the flag.

    "not_a_book_carrier" answers the question "why isn't <name> flagged either way?"
    Someone can have low personal effort and simply carry zero accounts as the
    confirmed book-owner field in this pull, which excludes them from the bandwidth
    test entirely (there's no book to weigh against). That's a data-scope fact, not a
    capacity judgment, so it is surfaced separately rather than silently dropped.
    """
    if roster is None or len(roster) == 0 or not book_rows:
        return {"note": "Roster and book rollup both required to compute this."}
    roster = roster.copy()
    roster["Team member"] = _team_member(roster)
    roster["Effort (hrs)"] = _num(roster["Effort (hrs)"])
    act = roster[roster["Effort (hrs)"].fillna(0) > 0].copy()
    if len(act) == 0:
        return {}
    owner_names = {str(b["person"]).strip().lower() for b in book_rows}
    carriers = act[act["Team member"].astype(str).str.strip().str.lower().isin(owner_names)].copy()
    if len(carriers) == 0:
        return {"note": "No roster member matched a book-carrier name; check the role-field label."}
    carriers["pctile"] = carriers["Effort (hrs)"].rank(pct=True)
    eff_by_name = {str(n).strip().lower(): (e, p) for n, e, p in
                   zip(carriers["Team member"], carriers["Effort (hrs)"], carriers["pctile"])}

    bandwidth, idle = [], []
    for b in book_rows:
        key = str(b["person"]).strip().lower()
        exposure = (b.get("at_risk", 0) or 0) + (b.get("neglected_highvalue", 0) or 0) + (b.get("stale", 0) or 0)
        if key in eff_by_name:
            eff, pctile = eff_by_name[key]
            if pctile <= 0.40 and exposure >= 1:
                bandwidth.append({
                    "person": b["person"], "personal_effort_hrs": round(float(eff), 1),
                    "effort_percentile": round(float(pctile), 2), "accounts": b["accounts"],
                    "book_ARR": b["total_ARR"], "at_risk": b.get("at_risk"),
                    "neglected_highvalue": b.get("neglected_highvalue"), "stale": b.get("stale"),
                    "reason": (f"Personal effort ({round(float(eff), 1)}h) sits at the "
                               f"{round(float(pctile) * 100)}th percentile among this team's "
                               f"book-carriers, while their book carries {int(exposure)} "
                               f"at-risk/stale/neglected-highvalue account(s): either room to "
                               f"take on more, or their own at-risk accounts need more attention "
                               f"than current effort suggests."),
                })
        elif b["accounts"] >= 5:
            idle.append({"person": b["person"], "accounts": b["accounts"], "book_ARR": b["total_ARR"]})
    bandwidth.sort(key=lambda x: x["book_ARR"], reverse=True)
    idle.sort(key=lambda x: x["book_ARR"], reverse=True)

    evaluated = set(eff_by_name.keys())
    not_carrier = act[~act["Team member"].astype(str).str.strip().str.lower().isin(evaluated)]
    not_a_book_carrier = [{"person": n, "personal_effort_hrs": round(float(e), 1)}
        for n, e in zip(not_carrier["Team member"], not_carrier["Effort (hrs)"])]
    not_a_book_carrier.sort(key=lambda x: x["personal_effort_hrs"])

    return {
        "bandwidth_candidates": bandwidth,
        "zero_effort_no_hours_logged": idle,
        "not_a_book_carrier": not_a_book_carrier,
        "method": "bandwidth_candidates = bottom-40% personal effort among this pull's "
                  "book-carriers AND book exposure>=1 (a real signal: room to help, or "
                  "under-serving their own at-risk book; read the `reason` field per row). "
                  "zero_effort_no_hours_logged = owns 5+ accounts but 0 hours logged (likely "
                  "a data-hygiene gap, not a person judgment). not_a_book_carrier = active "
                  "roster members who match zero accounts under the confirmed book-owner field "
                  "in this pull: not flagged either way, simply not evaluated for bandwidth "
                  "because there's no book to weigh against.",
    }


# ---------------------------------------------------------------------------
# Expansion pipeline rollup (NEW: the original CSV-based version has no equivalent,
# since the CSV Account Efficiency export never had opportunity-level data). Never sum
# "Opportunity value" (String, prose); count + momentum/category mix only.
# ---------------------------------------------------------------------------
def expansion_rollup(expansion, role_col):
    if expansion is None or len(expansion) == 0:
        return {}
    d = expansion.copy()
    d = d[d[role_col].notna() & (d[role_col].astype(str).str.strip() != "")]
    if len(d) == 0:
        return {}
    per_person = d.groupby(d[role_col].astype(str)).agg(
        opportunities=("Account", "count"),
        accounts_with_opps=("Account", "nunique"),
    ).reset_index().rename(columns={role_col: "person"})
    if "Momentum" in d.columns:
        heating = d[d["Momentum"] == "Heating"].groupby(d[role_col].astype(str)).size()
        per_person["heating"] = per_person["person"].map(heating).fillna(0).astype(int)
    multi_opp_accounts = (d.groupby("Account").size() > 1).sum()
    return {
        "per_person": _clean(per_person.sort_values("opportunities", ascending=False).to_dict("records")),
        "total_opportunities": int(len(d)),
        "multi_opportunity_accounts": int(multi_opp_accounts),
        "category_mix": d["Category"].value_counts().to_dict() if "Category" in d.columns else {},
        "momentum_mix": d["Momentum"].value_counts().to_dict() if "Momentum" in d.columns else {},
    }


def person_accounts(book, role_col, person_name):
    """Full account-level detail for one person's book: at-risk accounts, renewals
    inside 90 days, and single-threaded-at-risk accounts, each with the detail a
    manager needs (revenue, risk, health, renewal date, last engagement/reach-out/
    email-from-them/meeting, stakeholders, tickets). This is the piece `person_view`
    was missing: it only pulled the already-aggregated per-person totals, never the
    underlying account rows, so the 1:1/roster drill-down always rendered an empty
    account list even when the rollup showed real at-risk revenue."""
    d = book.copy()
    for c in ["Revenue", "Team effort (hours)", "Risk level", "Health score",
              "Stakeholders count", "Ticket count", "Ticket comments"]:
        if c in d.columns:
            d[c] = _num(d[c])
    if "Renewal date" in d.columns:
        d = _with_renewal_window(d)
    d["high_risk"] = _num(d.get("Risk level")).fillna(0) >= 4
    if role_col in d.columns:
        d["CSM"] = d[role_col]

    mine = d[d[role_col].astype(str).str.strip().str.lower() == person_name.strip().lower()].copy()
    if len(mine) == 0:
        return {"accounts": 0, "total_ARR": 0.0, "at_risk": [], "renewals_90d": [],
                "single_threaded_at_risk": [], "all": []}

    cols = ["Account", "Tier", "CSM", "Revenue", "Risk level", "Health score", "Renewal date",
            "days_to_renewal", "Last engagement", "Last reach-out", "Last email from them",
            "Last meeting", "Stakeholders count", "Multi threaded", "Ticket count",
            "Ticket comments", "Team effort (hours)", "Expansion readiness level",
            "Expansion momentum"]
    cols = [c for c in cols if c in mine.columns]

    def recs(df):
        num_cols = df.select_dtypes(include="number").columns
        return _clean(df[cols].assign(**{c: df[c].round(1) for c in num_cols if c in cols}
                                       ).to_dict("records"))

    at_risk = mine[mine["high_risk"]].sort_values("Revenue", ascending=False)
    renewals = mine[mine.get("renewal_90d", False) == True].sort_values("days_to_renewal") \
        if "renewal_90d" in mine.columns else mine.iloc[0:0]
    single_threaded = mine[(mine.get("Multi threaded").astype(str).str.lower() == "false") &
                            mine["high_risk"]] if "Multi threaded" in mine.columns else mine.iloc[0:0]

    # needs_attention = the FULL, uncapped union of at-risk accounts and accounts
    # renewing within 90 days (never just a top-N sample). This is what a manager's
    # 1:1/roster drill-down should default to, per UX review: showing only the top
    # 2-3 at-risk accounts silently hid the rest. A pure at-risk-AND-renews-soon
    # intersection is too narrow (the two conditions rarely overlap in practice;
    # validated internally, a CSM can carry many at-risk accounts with ZERO of them
    # renewing in the next 90 days), so this is the union, each row tagged with `why`
    # so the reason it's here is never ambiguous.
    attention_idx = list(at_risk.index)
    for i in renewals.index:
        if i not in attention_idx:
            attention_idx.append(i)
    needs_attention = mine.loc[attention_idx].copy() if attention_idx else mine.iloc[0:0]
    if len(needs_attention):
        why_map = {i: [] for i in attention_idx}
        for i in at_risk.index:
            why_map[i].append("at_risk")
        for i in renewals.index:
            why_map[i].append("renews_90d")
        needs_attention = needs_attention.sort_values(
            ["Risk level", "days_to_renewal"], ascending=[False, True], na_position="last")
        na_recs = recs(needs_attention)
        for rec, i in zip(na_recs, needs_attention.index):
            rec["why"] = why_map[i]
    else:
        na_recs = []

    return {
        "accounts": int(len(mine)),
        "total_ARR": float(mine["Revenue"].sum()) if "Revenue" in mine.columns else None,
        "at_risk": recs(at_risk),
        "renewals_90d": recs(renewals),
        "needs_attention": na_recs,
        "single_threaded_at_risk": recs(single_threaded),
        "all": recs(mine.sort_values("Revenue", ascending=False)),
    }


def person_view(result, person_name, book=None, role_col=None):
    """Extract the 1:1-mode slice for one person from an already-computed roster-mode
    result, PLUS (when the raw book DataFrame is passed) their real account-level
    detail via person_accounts(), not just the aggregated per-person totals."""
    key = person_name.strip().lower()
    out = {"person": person_name}
    for b in result.get("book", {}).get("rollup", []):
        if str(b["person"]).strip().lower() == key:
            out["book"] = b
            break
    for m in result.get("team_pulse", {}).get("all_members", []):
        if str(m.get("Team member", "")).strip().lower() == key:
            out["personal"] = m
            break
    out["overwhelmed"] = any(
        str(o.get("Team member", "")).strip().lower() == key
        for o in result.get("team_pulse", {}).get("overwhelmed", []))
    out["bandwidth_candidate"] = any(
        str(c.get("person", "")).strip().lower() == key
        for c in result.get("capacity_signals", {}).get("bandwidth_candidates", []))
    if "expansion" in result:
        out["expansion"] = next(
            (p for p in result["expansion"].get("per_person", [])
             if str(p["person"]).strip().lower() == key), {})
    if book is not None and role_col:
        out["accounts"] = person_accounts(book, role_col, person_name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", help="R1 CSV: user roster + personal effort")
    ap.add_argument("--book", help="R2 CSV: customer book/account signals")
    ap.add_argument("--expansion", help="R3 CSV: expansion_opportunity rows (optional)")
    ap.add_argument("--role-col", required=True,
                    help="Column label of the confirmed book-owner/CSM field (R7b). "
                         "Must match the label used in --book/--expansion exactly.")
    ap.add_argument("--person", help="If set, also emit a 1:1-mode slice for this person")
    ap.add_argument("--out")
    args = ap.parse_args()
    if not args.roster and not args.book:
        ap.error("provide --roster and/or --book")

    result = {"role_col": args.role_col}
    roster = pd.read_csv(args.roster) if args.roster else None
    book = pd.read_csv(args.book) if args.book else None
    expansion = pd.read_csv(args.expansion) if args.expansion else None

    if roster is not None:
        result["team_pulse"] = team_pulse(roster)

    if book is not None:
        rollup = book_rollup(book, args.role_col)
        result["book"] = {"rollup": rollup}
        result["org_summary"] = org_summary(book, args.role_col)
        result["account_flags"] = account_flags(book, args.role_col)
        result["load_distribution"] = load_distribution(rollup)
        if roster is not None:
            result["capacity_signals"] = capacity_signals(roster, rollup)

    if expansion is not None:
        result["expansion"] = expansion_rollup(expansion, args.role_col)

    if args.person:
        result["person_view"] = person_view(result, args.person, book=book, role_col=args.role_col)

    out = json.dumps(result, indent=2, default=str)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out)
        print(f"Wrote {args.out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
