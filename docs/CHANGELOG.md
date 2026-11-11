# Changelog

Every entry here is written for interview storytelling, not just as a commit
log: what changed, why it mattered, and what problem it solved. Newest first.

## [v3.0] — 2026-11-11 — Product redesign: the triage board

**Why:** The goal changed from "a portfolio project" to "something a business
would pay for". A buyer watching a demo should think two things in the first
ten seconds: *this team is in control* and *my staff could use this today*.
The previous UI was a tidy admin template (dark sidebar, white KPI cards,
tinted icon tiles) and said neither.

- Rebuilt every screen around one idea: an emergency-department triage board.
  Priority is a numbered square, and every open ticket carries a **waiting
  clock** showing how much of its SLA window is used.
- The Admin dashboard now opens with a sentence, not six KPI tiles, followed
  by open tickets most urgent first, tickets waiting for triage, and team
  workload with late counts per person.
- Employees get a dashboard that actually works for them: each ticket on a
  five-step progress line. (Before, the Viewer dashboard called an analytics
  API that Viewers are not allowed to use, so its cards stayed empty.)
- Navigation moved from a sidebar to a top bar, freeing the full width for
  the ticket table. The personal queue and status filters became controls on
  the ticket page rather than separate menu entries.
- Removed Bootstrap, jQuery, Popper and three CDNs. Fonts, icons, styles and
  Chart.js now ship with the app: it makes no outside requests.
- Works on a phone: ticket tables become stacked blocks through container
  queries, and the navigation collapses into a menu.
- The seed command now dates tickets relative to now (`seed_data --retime`),
  so a demo shows a working desk rather than 12 tickets a month overdue.
- Added a test suite (22 tests): the SLA clock, the dashboard summary, and
  every screen for every role.
- Fixed along the way: deleting a subcategory crashed on redirect; the SLA
  due time was shown in a different time offset from created and updated;
  assignee dropdowns listed email addresses instead of names.

Designed with the Impeccable plugin for Claude Code. The owner chose the
direction from five rendered options.

**Files touched:** `static/css/main.css` (rewritten), `static/js/app.js`,
`static/fonts/`, `static/vendor/`, every file in `templates/`,
`vats/dashboard.py` (new), `vats/models.py`, `vats/forms.py`,
`vats/templatetags/ui_extras.py`, `vats/context_processors.py`,
`vats/management/commands/seed_data.py`, `vats/tests.py`,
`registration/views.py`, `registration/forms.py`, `PRODUCT.md`, `DESIGN.md`.

---

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
project report ([`report/HelpDesk_Pro_Project_Report_Final.pdf`](report/HelpDesk_Pro_Project_Report_Final.pdf)) document it.

---

## [v1.0] — Original Ticketing App

Django ticketing system: three roles (Admin/Manager/Viewer), ticket
lifecycle (Pending → Assigned → Scoping → In Progress → Completed), work
notes as an audit trail, email notifications on create/status-change, and
Twilio WhatsApp alerts. No REST API, no analytics, no SLA concept.
