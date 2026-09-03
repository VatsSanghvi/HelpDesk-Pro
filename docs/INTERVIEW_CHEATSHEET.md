# HelpDesk Pro — Interview Cheat Sheet

Read this in the 5 minutes before an interview. Every answer here is short on
purpose — say the short version first, then only go deeper if they ask a
follow-up. This file gets a new entry at the bottom every time we ship a new
feature, so re-skim it before each interview even if you've read it before.

---

## 30-second elevator pitch (say this if asked "tell me about a project")

> "I built HelpDesk Pro, a full-stack IT ticketing system — Django backend,
> role-based access for Admins, Managers, and Viewers, with a REST API and a
> live analytics dashboard. I track SLA compliance, first response time, and
> customer satisfaction on every ticket, and I export the data straight into
> Power BI for reporting. It's built the way a real internal support tool
> would be — audit trail on every change, automated email/WhatsApp alerts,
> and CSV/Excel export for ad-hoc analysis."

---

## Core concepts — say it in one line

| Term | One-line definition | How to answer if asked |
|---|---|---|
| **SLA** (Service Level Agreement) | A promised time limit to resolve a ticket, based on how urgent it is. | "High-priority tickets have a 4-hour SLA, Moderate is 24 hours, Low is 72 hours. If a ticket isn't resolved in that window, I flag it as breached." |
| **SLA Breach** | A ticket that blew past its promised deadline and is still open. | "It's calculated automatically — if the current time is past the ticket's due date and the ticket isn't closed yet, `is_sla_breached` returns true." |
| **KPI** (Key Performance Indicator) | A single number that tells you how the operation is doing at a glance. | "My dashboard shows KPIs like total tickets, open tickets, SLA breach %, and average resolution time." |
| **CSAT** (Customer Satisfaction) | A 1-5 rating the customer gives after their ticket is resolved. | "Once a ticket is marked Completed, the person who raised it can rate their experience 1 to 5 and leave optional feedback. I average that into a CSAT KPI." |
| **First Response Time (FRT)** | How long it took before a support agent actually engaged with the ticket — not just got assigned to it. | "I measure the time between ticket creation and the first time a Manager moves it past 'Assigned' into active work, like Scoping." |
| **Resolution Time** | Total time from ticket creation to it being closed. | "Calculated as `resolved_at minus created_at`, shown in hours." |
| **RBAC** (Role-Based Access Control) | Different users see and can do different things based on their role. | "I have three roles — Admin, Manager, Viewer — each with a different queryset and different permissions enforced both in the views and the API." |
| **REST API** | A standard way for other programs (or a frontend) to read/write your data over HTTP. | "I built mine with Django REST Framework — full CRUD on tickets, filtering, search, and dedicated analytics endpoints." |
| **CRUD** | Create, Read, Update, Delete — the four basic things any data-backed app needs to do. | "Every entity — tickets, categories, users — supports all four, with role checks on each." |
| **ORM** (Object-Relational Mapper) | Lets you write Python instead of raw SQL to talk to the database. | "I use Django's ORM — models like `Ticket` map directly to database tables, and querysets like `Ticket.objects.filter(...)` generate the SQL for me." |
| **Foreign Key** | A field that links one database table to a row in another table. | "A Ticket has a foreign key to Category, Subcategory, and to the User who created it and the User it's assigned to." |
| **Migration** | A versioned, auto-generated script that changes the database schema safely. | "Whenever I add a model field, Django's `makemigrations` generates a migration file, and `migrate` applies it — so the schema stays in sync with the code, with a full history of every change." |
| **Audit Trail** | A permanent log of who changed what and when. | "My `Worknote` model logs every status change, comment, and field update on a ticket with a timestamp and the user who made it." |
| **Serializer** (DRF term) | Converts a Python/database object into JSON for the API, and back. | "I have separate serializers for the ticket list view (compact) and the ticket detail view (includes the full worknote history)." |

---

## Power BI / data terms

| Term | One-line definition | How to answer if asked |
|---|---|---|
| **Power BI** | Microsoft's business intelligence tool for turning raw data into interactive dashboards. | "I built a dedicated flat JSON feed so Power BI's Web connector can pull ticket data straight from my Django backend and refresh on demand." |
| **DAX** | The formula language Power BI uses for calculated fields (like Excel formulas, but for dashboards). | "I use DAX to calculate things like SLA compliance % and average resolution time directly inside the report." |
| **Data refresh** | Re-pulling the latest data from the source into the report. | "Since my feed hits the live database, refreshing in Power BI instantly reflects any new or updated tickets." |
| **Drillthrough** | Clicking a chart element to jump to a detail page filtered to just that item. | "Clicking a category on the overview page drills through to a page showing only that category's tickets." |
| **Flat/denormalized data** | Data with foreign keys already resolved into plain readable values, instead of IDs. | "My Power BI feed flattens `category`, `assigned_to`, etc. into plain text, since Power BI's JSON parser handles flat data far better than nested objects." |

---

## Likely follow-up questions

**"What was the hardest part of this project?"**
> "Getting the SLA and satisfaction metrics to be *automatic* rather than manually entered — I wanted the system to calculate breach status and resolution time itself based on timestamps, not rely on someone remembering to log it."

**"How would you scale this to more users?"**
> "Right now it's SQLite for development; the settings are already structured to swap in MySQL/Postgres for production. I'd also move the Power BI feed's shared-secret key auth to proper OAuth2 if this became multi-tenant."

**"Why did you separate the Power BI endpoint from the main API?"**
> "The main API uses session-based auth, which Power BI's scheduled refresh can't use interactively. So I built a separate flat endpoint secured with a single key from environment variables, meant specifically for reporting tools."

**"What would you add next?"**
> "Historical trend snapshots — right now the dashboard shows current state, so I'd add a daily job that stores point-in-time snapshots to chart trends over months, not just the last 7 days."

---

## Recently added (most recent first)

Keep this section updated every time a feature ships — it's your "what's new"
answer if an interviewer has seen this project before or asks what you've
been working on lately.

- **2026-09-03** — Added CSAT rating (1-5 + feedback) captured from the
  ticket creator once a ticket is Completed, and First Response Time
  (time until a Manager first actively engages with a ticket, not just gets
  assigned it). Both now feed the analytics dashboard KPIs and the Power BI
  export. Added a personal "My Tickets" queue (distinct from the full
  all-tickets table) for every role, and bulk actions (reject/delete for
  Admin, mark-completed for Manager) on the ticket list.
