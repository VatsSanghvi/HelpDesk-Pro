# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary buyer and user: the in-house IT team of a small or mid-sized company
(roughly 20-500 employees). Confirmed by the owner.

Three roles use the product, each with a different job:

- **Admin** (IT lead): triages every new ticket, sets priority, assigns it to
  an agent, rejects what is out of scope, manages users and categories, and
  watches SLA health across the whole queue.
- **Manager** (IT agent; the code and UI call this role "Manager"): works the
  tickets assigned to them through Scoping, In Progress and Completed, and
  records work notes.
- **Viewer** (employee): raises a ticket, follows its progress, comments on
  it, and rates the resolution.

## Product Purpose

HelpDesk Pro is an internal IT helpdesk: employees raise tickets, the IT team
triages and resolves them against SLA deadlines, and the IT lead sees service
health at a glance. The owner is turning it from a portfolio project into a
product to sell to businesses; success means a business evaluating it sees a
finished, trustworthy tool rather than a student project.

## Positioning

SLA accountability and reporting are built in, not add-ons: every ticket gets
a deadline from its priority, breaches are flagged automatically, every change
is written to an audit trail, and the same data feeds an in-app dashboard, CSV
and Excel export, a REST API, and a Power BI report.

## Operating Context

- Desktop browser at a work desk is the main setting; agents keep the ticket
  queue open through the working day.
- Ticket lifecycle: Pending, Assigned, Scoping, In Progress, Completed, plus
  Cancelled and Rejected.
- Priority is empty until an Admin triages the ticket ("Untriaged").
- SLA windows by priority: High 4h, Moderate 24h, Low 72h (configurable).
- Email and WhatsApp notifications go out on creation and status change.
- A separate four-page Power BI report reads a key-authenticated feed. It is
  out of scope for app design work.

## Capabilities and Constraints

- Django 5.1 server-rendered templates, Bootstrap 4, Chart.js 4, plain CSS in
  `static/css/main.css`. No JS build step.
- Role-based access: each role sees a different queryset and navigation.
- Dashboard KPIs and charts load from `/api/v1/analytics/dashboard/` after
  page load.
- Ticket list has status tabs, search, bulk actions, CSV and Excel export.
- Single-tenant: one company per installation. No sign-up, plans or billing.
- **Undecided:** pricing model (subscription versus one-time purchase). The
  owner chose to decide later; nothing billing-related is designed or built.
- **Undecided:** hosted versus self-hosted delivery.

## Brand Commitments

- Product name: **HelpDesk Pro**.
- No logo, wordmark or brand assets beyond the name have been made binding.

## Evidence on Hand

- Seeded demo dataset for a fictional company, Vats Financial Services
  (`python manage.py seed_data`): 5 categories, 9 users, about 30 tickets.
- 30-second demo video and stills: `brag-output/`.
- Before and after screenshots of the previous redesign: `docs/ui-before/`,
  `docs/ui-after/`.
- No customers, testimonials, benchmarks or published pricing exist. Future
  work must not invent them.

## Product Principles

1. The queue is the product: what needs attention next must be obvious
   without reading every row.
2. SLA state is never ambiguous: on time, at risk, late and breached are
   distinct at a glance.
3. Each role sees only what its job needs.
4. Every change is traceable to a person and a time.
5. Honest states: untriaged, unassigned and no-data are shown as what they
   are, never as blanks.
