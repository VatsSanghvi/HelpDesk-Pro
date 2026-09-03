# Changelog

Every entry here is written for interview storytelling, not just as a commit
log: what changed, why it mattered, and what problem it solved. Newest first.

## [v2.2] — 2026-09-03 — CSAT, First Response Time, My Tickets, Bulk Actions

**Why:** After analytics/SLA tracking (v2.1) was in place, the two obvious
gaps left were "did the customer actually think we did a good job?" (no
satisfaction signal existed) and "how fast did we actually start working on
this?" (only total resolution time was tracked, which hides a ticket that
sat untouched before someone picked it up).

- Added `csat_rating` (1-5) and `csat_feedback` to `Ticket`. The ticket
  creator can rate their experience once the ticket is marked Completed.
  Feeds a new "Avg CSAT Rating" dashboard KPI and the Power BI export.
- Added `first_response_at` / `first_response_time_hours` to `Ticket`,
  auto-stamped the first time a Manager moves a ticket past "Assigned"
  (mirrors the existing `resolved_at` auto-stamp pattern). Feeds a new
  "Avg First Response Time" dashboard KPI.
- Added a personal **My Tickets** queue (`/my_tickets/`), distinct from the
  full role-wide table: Admin sees tickets pending their approval, Manager
  sees their open assigned tickets, Viewer sees their own open tickets.
- Added **bulk actions** to the ticket list: Admin can bulk Reject or Delete
  selected tickets, Manager can bulk mark selected In-Progress tickets
  Completed.
- Tagged the pre-existing codebase `v2.1-pre-csat-frt` before this work
  started, so there's a clean git reference point for "before" in interviews.

**Files touched:** `vats/models.py`, `vats/views.py`, `vats/urls.py`,
`vats/serializers.py`, `vats/api_views.py`, `vats/powerbi_views.py`,
`templates/vats/ticket_detail.html`, `templates/vats/ticket_list.html`,
`templates/registration/home.html`, `templates/base.html`,
`vats/migrations/0002_*.py`.

---

## [v2.1] — Analytics Dashboard, SLA Tracking, REST API (retroactive entry)

**Why:** The original ticketing app had no way to answer "how are we doing?"
— no dashboard, no SLA concept, no API for exporting data anywhere. This
upgrade turned it from a pure CRUD ticketing tool into something with actual
reporting value, which is what makes it relevant to a Data/Business Analyst
role rather than just a web dev portfolio piece.

- Added Django REST Framework: full CRUD API, filtering, search, and CSV/
  Excel export endpoints (`vats/api_views.py`, `vats/serializers.py`).
- Added `due_by` (SLA deadline, auto-set from priority on creation) and
  `resolved_at` (auto-set on close) to `Ticket`, plus `is_sla_breached` and
  `resolution_time_hours` computed properties.
- Added a live analytics dashboard: KPI cards, 7-day ticket volume chart,
  priority breakdown, category breakdown, team workload (Chart.js).
- Added a dedicated flattened Power BI feed (`vats/powerbi_views.py`),
  authenticated with a shared secret key since Power BI's scheduled refresh
  can't use session cookies.
- Moved Twilio WhatsApp credentials out of hardcoded values in `models.py`
  into environment variables — the originals had been committed in plain
  text to a public repo.

**Note:** this upgrade happened before the current git history began (the
very first commit in this repo already contains it), so there's no git tag
for the true "before" state — only this written record and the original
project report (`HelpDesk_Pro_Project_Report_Final.pdf`) document it.

---

## [v1.0] — Original Ticketing App

Django ticketing system: three roles (Admin/Manager/Viewer), ticket
lifecycle (Pending → Assigned → Scoping → In Progress → Completed), work
notes as an audit trail, email notifications on create/status-change, and
Twilio WhatsApp alerts. No REST API, no analytics, no SLA concept.
