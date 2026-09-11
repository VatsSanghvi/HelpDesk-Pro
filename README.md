# 🎫 HelpDesk Pro — IT Support Ticketing & Analytics System

A full-stack IT helpdesk and ticket management system built with **Django**, with two analytics surfaces on top of it: an in-application operational dashboard for the support team, and a four-page **Power BI** report for stakeholders. Role-based access control, a REST API, automated SLA tracking, and CSV/Excel export.

> The Power BI report is stored in **PBIP format** — plain-text JSON, version-controlled in this repository alongside the Django source. Every visual, measure and theme change is reviewable as a diff.

---

## 🚀 Features

### Core
- **Role-Based Access Control** — Admin, Manager, Viewer, each with a different queryset and different permissions
- **Ticket Lifecycle Management** — 7 stages: Pending → Assigned → Scoping → In Progress → Completed (plus Cancelled, Rejected)
- **Work Notes & Audit Trail** — every status change and field update logged with actor and timestamp
- **Automated SLA Tracking** — `due_by` calculated from priority on creation (High 4h / Moderate 24h / Low 72h); breach flagged automatically
- **Email & WhatsApp Notifications** — Gmail SMTP and Twilio on creation and status change

### Analytics
- **In-app dashboard** — KPI cards, 7-day volume chart, priority donut, category progress bars, team workload
- **Power BI report** — 4 pages, 13 DAX measures, cross-page slicers *(see below)*
- **CSV & Excel export** — all active filters carry through to the download

### Technical
- **REST API** (`/api/v1/`) — full CRUD, filtering, search, pagination, analytics endpoints
- **Dedicated reporting endpoint** — flat denormalised JSON feed for BI tools, key-authenticated
- **Secure config** — all secrets in `.env`, never committed

---

## 📊 Power BI Report

Four pages on a shared 1280×720 grid. Every page carries the same five slicers — created-date range, category, priority, status, assignee — so a filter applied anywhere holds across the whole report.

| Page | Question it answers | Key visuals |
|---|---|---|
| **Overview** | How is the service doing overall? | 5 KPI callouts, monthly volume trend, priority donut, status breakdown, resolution time by category, open-ticket queue by age |
| **SLA & Aging** | Where are we missing commitments? | Breaches over time / by category / by assignee, plus a breached-ticket table sorted oldest-first |
| **Category Deep-Dive** | Which problem areas cost us most? | Top-10 subcategories, resolution time by category, expandable category→subcategory matrix |
| **Agent Workload** | How is work distributed? | Open vs resolved by assignee, resolution time by assignee, agent scorecard by person and role |

### How the data gets there

```
Django ORM  →  /api/v1/powerbi/tickets/  →  Power Query (Web.Contents)  →  Tickets table  →  13 DAX measures
              flat JSON, key-authenticated        Import mode                 21 columns
```

Power BI never touches the database directly. The reporting endpoint returns one flat row per ticket with foreign keys already resolved to readable text — Power BI's JSON parser handles flat records far more reliably than nested objects, and it keeps the reporting contract decoupled from internal model changes.

### Selected DAX measures

```dax
SLA Compliance % =
DIVIDE(
    CALCULATE(COUNTROWS(Tickets), Tickets[is_sla_breached] = FALSE),
    COUNTROWS(Tickets),
    0
)

Avg Resolution Time (Hrs) = AVERAGE(Tickets[resolution_time_hours])

Unassigned Tickets =
CALCULATE(COUNTROWS(Tickets), Tickets[assigned_to] = "Unassigned")
```

Metrics are calculated in the model rather than pre-computed in Python, so they respond correctly to whatever the user filters to.

### Opening it

Requires **Power BI Desktop** with the PBIP preview feature enabled. Open `powerbi/Ticketing Project Power BI File.pbip`. The Django server must be running at `http://127.0.0.1:8000` for a refresh to succeed.

```
powerbi/
├── Ticketing Project Power BI File.pbip
├── ...Report/
│   ├── definition/pages/          # one folder per page, one folder per visual
│   ├── definition/report.json     # theme registration, report settings
│   └── StaticResources/           # custom theme JSON
└── ...SemanticModel/
    └── definition/tables/         # TMDL — columns, 13 measures, Power Query source
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 5.1 |
| REST API | Django REST Framework 3.15, django-filter |
| Frontend | Django templates, Bootstrap 4, Chart.js 4 |
| Business Intelligence | Power BI Desktop (PBIP/PBIR), DAX, Power Query (M) |
| Database | SQLite (dev) / MySQL (production-ready) |
| Notifications | Twilio (WhatsApp), Gmail SMTP |
| Data Export | openpyxl (Excel), Python `csv` |

---

## ⚙️ Setup

### 1. Clone
```bash
git clone https://github.com/VatsSanghvi/HelpDesk-Pro.git
cd HelpDesk-Pro
```

### 2. Virtual environment
```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux
```

### 3. Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment variables
```bash
cp .env.example .env
```
Fill in database, Gmail, Twilio, and the `POWERBI_API_KEY` used by the reporting endpoint.

### 5. Migrate and run
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/api/v1/tickets/` | List (role-filtered) or create |
| GET / PATCH | `/api/v1/tickets/<id>/` | Detail with activity log, or update |
| GET | `/api/v1/tickets/export/csv/` | Export filtered tickets as CSV |
| GET | `/api/v1/tickets/export/excel/` | Export filtered tickets as Excel |
| GET | `/api/v1/analytics/dashboard/` | KPI cards + chart data in one call |
| GET | `/api/v1/analytics/report/` | Date-range analytics report |
| GET | `/api/v1/powerbi/tickets/` | **Flat denormalised feed for Power BI** (key auth) |
| GET | `/api/v1/categories/` | Category list with ticket counts |
| GET | `/api/v1/users/managers/` | Active managers for assignment dropdowns |

---

## 👥 User Roles

| Role | Permissions |
|---|---|
| Admin | Create users, approve/reject tickets, manage categories, view all data |
| Manager | Handle assigned tickets (Scoping → In Progress → Completed), add work notes |
| Viewer | Raise tickets, track own tickets, comment on own tickets |

---

## 📁 Project Structure

```
├── tickit/                   # Django project config (settings, URLs, SLA config)
├── registration/             # Custom User model (email login, role field), auth views
├── vats/                     # Core ticketing app
│   ├── models.py             # Ticket, Category, Subcategory, Worknote + SLA fields
│   ├── api_views.py          # REST API, analytics, CSV/Excel export, Power BI feed
│   ├── serializers.py        # DRF serializers (compact list / full detail)
│   └── filters.py            # django-filter FilterSets
├── templates/                # Django templates — sidebar layout, dashboard, forms
├── static/css/main.css       # Custom design system over Bootstrap 4
├── docs/
│   ├── INTERVIEW_CHEATSHEET.md   # Concepts, talking points, trade-offs
│   ├── UI_REDESIGN.md            # The redesign write-up
│   └── ui-before/ ui-after/      # Before/after screenshots
├── docs/
│   ├── INTERVIEW_CHEATSHEET.md    # Concepts, talking points, trade-offs
│   ├── UI_REDESIGN.md             # The redesign write-up
│   ├── CHANGELOG.md               # Full version history
│   ├── PROJECT_EVOLUTION.md       # Before/after/next summary table
│   ├── ui-before/ ui-after/       # Before/after screenshots
│   ├── report/                    # Project report (.docx source + exported .pdf)
│   └── assets/                    # Project Demo.mp4
└── powerbi/
    └── Ticketing Project Power BI File.pbip   # Power BI report (PBIP, version-controlled)
```

---

## 🔍 What the data showed

Building the Power BI layer surfaced three things the in-app dashboard had been hiding. They're documented rather than papered over:

- **`csat_rating` and `first_response_at` are populated on 0 of 32 tickets.** Both fields are captured correctly by the application, but nothing in the sample dataset has been rated or given a first response yet. The three dependent measures return blank, so those visuals were removed rather than shipped empty.
- **Six tickets have no assignee — and all six are still open.** A triage gap no existing view made visible. This is why the Agent Workload page and the Unassigned Tickets KPI exist.
- **SLA compliance sits at 62.5%** (12 of 32 breached, concentrated in June). Average resolution time is 23.1 hours but ranges from 16.2h for Hardware to 34.5h for Network & Connectivity — a spread only visible once resolution time was broken out by category.

---

## 🔐 Security

- All credentials (Django secret key, Gmail, Twilio, Power BI feed key) live in `.env`, listed in `.gitignore`
- SLA hours per priority are configurable via `.env` with no code changes
- Role-based access enforced at both view level (decorators) and API level (DRF permissions)
- Session auth for the web UI; the Power BI feed uses a separate shared key, since scheduled refresh cannot complete an interactive login

---

*Built as a final-year project, extended with a REST API, an analytics dashboard, and a version-controlled Power BI reporting layer for portfolio use.*
