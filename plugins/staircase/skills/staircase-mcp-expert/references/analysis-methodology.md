# Staircase Analysis Methodology

Cross-person and cross-account rollups, rankings, and effort-efficiency ratios have a few ways to go quietly wrong. Read this before any analysis that compares people or accounts, ranks a book, or divides effort by revenue. These principles are enforced in `../../../_shared/scripts/team_engine.py`; this file states them so any skill (or any reader of that engine) can apply them without reverse-engineering the code.

## Contents
- Denominator matching (windowed revenue)
- Dual-signal thresholding (never flag on magnitude alone)
- Normalize before ranking
- Anti-libel framing
- Intersection vs union for compound views
- The negative-sentiment ratio

## Denominator matching (windowed revenue)
Any effort-efficiency, cost-as-percent-of-revenue, or ROI ratio must put revenue on the SAME time window as the effort. Use `customer.effort.team_effort_time_range_revenue` (the trailing-window figure), never the annual `customer.revenue` or `revenue_converted`. Mixing a quarterly effort figure over an annual revenue denominator silently distorts the ratio by roughly 4x and no error fires. (A server-computed `customer.effort.team_effort_efficiency` field also exists; verify its exact definition via `report_metadata` before trusting it as the ratio.)

## Dual-signal thresholding (never flag on magnitude alone)
Never call a person or account overloaded on a single raw magnitude. Require a load threshold AND an independent degradation signal. The engine's overwhelmed test is the model: effort at or above the p90 percentile AND (email response time > 24h OR negative-sentiment ratio > 0.15). High load alone is a busy person, not a drowning one; it is the co-occurring degradation that makes it real.

## Normalize before ranking
Compare rates and percentiles, never raw counts, across differently-sized books. A pooled 30-account book and a focused 3-account book are not comparable per-hour; segment by book size before ranking. When rounding, round only the raw sums, never the small per-book ratios (a blanket round to one decimal turns 0.05 into 0.0 and corrupts the ranking, a real bug caught by hand-check).

## Anti-libel framing
A low per-account effort number is meaningful only alongside book exposure and risk. Never present it as a standalone "this person is underperforming" claim. The engine renamed its "under-utilization / coverage gap" block to "bandwidth" and added a `not_a_book_carrier` bucket for exactly this reason: the numbers describe capacity, not worth, and a person with a small book may be carrying the org's hardest accounts.

## Intersection vs union for compound views
When a "needs attention" view combines two signals (for example at-risk AND renewing within 90 days), the intersection is often empirically near-empty even when each condition is individually common (verified: a CSM carrying 12 at-risk accounts with zero renewing in 90 days, so zero overlap). Default such views to the UNION, each row tagged with which condition fired, uncapped. An empty intersection is usually a modeling artifact, not a clean book.

## The negative-sentiment ratio
Compute negative sentiment as a ratio, neg / (pos + neg + neu), not a raw count, so a high-volume account does not dominate on volume alone. When the denominator is zero, treat the ratio as undefined (not zero), so a silent account is not mistaken for a happy one.

_Derived from the methodology enforced in `team_engine.py`; verified live during the team-manager / 1on1-prep builds, Aug-Sep 2026. Re-confirm field ids per org via `report_metadata`._
