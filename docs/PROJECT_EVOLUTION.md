# Project Evolution — Before / After / Next

This is the document to open on a screen-share when an interviewer says
"walk me through how you improved this project." Full detail lives in
`CHANGELOG.md`; this is the summary table.

## Feature comparison

| Area | v1.0 — Original | v2.1 — Analytics Upgrade | v2.2 — This Session |
|---|---|---|---|
| **Data access** | Web UI only | + Full REST API (DRF), CSV/Excel export | + Power BI fields for CSAT & First Response Time |
| **Reporting** | None | Live dashboard: KPI cards, volume chart, priority/category breakdown, team workload | + Avg First Response Time & Avg CSAT KPIs |
| **SLA** | Not tracked | Auto-calculated deadline per priority, breach flag | Unchanged |
| **Customer feedback** | None | None | CSAT rating (1-5) + feedback captured at ticket close |
| **Response tracking** | Only full resolution time | Only full resolution time | First Response Time — time to first real engagement, not just assignment |
| **Personal workflow** | Role-wide lists only | Role-wide lists only | Dedicated "My Tickets" personal queue per role |
| **Bulk operations** | One ticket at a time | One ticket at a time | Bulk reject/delete (Admin), bulk complete (Manager) |
| **Secrets handling** | Twilio keys hardcoded in `models.py` (public repo) | Moved to `.env` | Unchanged |
| **Version tracking** | — | — | Git tag `v2.1-pre-csat-frt` marks this session's starting point |

## Why this progression makes sense to explain in an interview

1. **v1 → v2.1** is "make the data usable" — before this, the app could
   store tickets but couldn't tell you anything about how support was
   performing. This is the shift from a CRUD app to a reporting tool.
2. **v2.1 → v2.2** is "close the loop with the customer and the clock" —
   SLA told you if you were *late*, but not if the customer was *happy*, and
   not how long a ticket sat before anyone touched it. CSAT and First
   Response Time answer those two follow-up questions directly.
3. Each step maps to a real support-operations concept (SLA, FRT, CSAT),
   which is exactly the vocabulary a Data Analyst / Business Analyst /
   Support Analyst interview will probe — see `docs/INTERVIEW_CHEATSHEET.md`.

## Honest gap

The v1 → v2.1 jump happened before this repo's git history starts (the
first commit already contains the v2.1 code), so there's no git-diffable
"before" snapshot for that transition — only the written record above and
the original project report. Everything from v2.1 onward *is* fully
tracked, tagged, and diffable, which is the more important half since it's
what future interviews will actually ask about ("what have you shipped
recently").

## What's next (not yet built)

- Historical daily snapshots for real month-over-month trend charts
  (currently the dashboard only shows a 7-day window and current state).
- Power BI report layout itself — CSAT and FRT fields exist in the feed
  now; the dashboard pages/visuals for them still need to be built in
  Power BI Desktop.
- Seeded multi-month synthetic ticket history, to make SLA/CSAT trend
  analysis statistically meaningful (deferred by choice for now).
