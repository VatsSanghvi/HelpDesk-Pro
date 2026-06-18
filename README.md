# 🎫 HelpDesk Pro — IT Support Ticketing System

A full-stack IT helpdesk and ticket management system built with **Django** and **Python**, featuring role-based access control, real-time analytics dashboard, REST API, and CSV/Excel data export.

---

## 🚀 Features

### Core Features
- **Role-Based Access Control** — Three roles: Admin, Manager, Viewer — each with different permissions
- **Ticket Lifecycle Management** — Full workflow: Pending → Assigned → Scoping → In Progress → Completed
- **Work Notes & Audit Trail** — Every status change and comment is logged with timestamps
- **Email Notifications** — Automated email on ticket creation and status change (Gmail SMTP)
- **WhatsApp Alerts** — Twilio-powered instant ticket notifications

### Analytics & Reporting (v2)
- **Live Analytics Dashboard** — KPI cards, ticket volume chart (7 days), priority breakdown donut chart
- **Category Performance** — Progress bars showing ticket distribution by category
- **Team Workload** — Manager performance and open vs. resolved counts
- **CSV & Excel Export** — One-click data export with filters for Data Analyst workflows
- **SLA Tracking** — Auto-calculated SLA deadlines per priority; breach alerts

### Technical Features
- **REST API** (`/api/v1/`) — Full CRUD, filtering, search, analytics endpoints
- **Django REST Framework** — Browsable API for easy testing
- **Dynamic Filtering** — Filter by status, priority, assignee, date range, SLA breach
- **Secure Config** — All secrets in `.env` (no hardcoded credentials)

---

## 🛠 Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.9+, Django 3.2             |
| REST API    | Django REST Framework 3.14          |
| Frontend    | HTML5, CSS3, Bootstrap 4, Chart.js  |
| Database    | SQLite (dev) / MySQL (production)   |
| Notifications | Twilio (WhatsApp), Gmail SMTP    |
| Data Export | openpyxl (Excel), Python csv (CSV)  |

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/VatsSanghvi/TickitGenerator-main.git
cd TickitGenerator-main
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your values (DB, email, Twilio)
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Start the development server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## 📡 API Endpoints

| Method | Endpoint                         | Description                     |
|--------|----------------------------------|---------------------------------|
| GET    | `/api/v1/tickets/`               | List tickets (role-filtered)    |
| POST   | `/api/v1/tickets/`               | Create ticket                   |
| GET    | `/api/v1/tickets/<id>/`          | Ticket detail + activity log    |
| PATCH  | `/api/v1/tickets/<id>/`          | Update ticket                   |
| GET    | `/api/v1/tickets/export/csv/`    | Export tickets as CSV           |
| GET    | `/api/v1/tickets/export/excel/`  | Export tickets as Excel         |
| GET    | `/api/v1/analytics/dashboard/`   | KPI cards + chart data          |
| GET    | `/api/v1/analytics/report/`      | Date-range analytics report     |
| GET    | `/api/v1/categories/`            | Category list                   |

---

## 👥 User Roles

| Role    | Permissions                                                    |
|---------|----------------------------------------------------------------|
| Admin   | Create users, approve/reject tickets, manage categories, view all data |
| Manager | Handle assigned tickets (Scoping → In Progress → Complete)     |
| Viewer  | Raise tickets, track own ticket status                         |

---

## 📁 Project Structure

```
├── tickit/              # Django project config
│   ├── settings.py      # Upgraded: env-based config, DRF, SLA settings
│   └── urls.py          # Routes: web views + /api/v1/
├── registration/        # User authentication app
│   ├── models.py        # Custom User model (email login, role field)
│   ├── views.py         # Login, user CRUD
│   └── urls.py
├── vats/                # Main ticketing app
│   ├── models.py        # Ticket, Category, Subcategory, Worknote + SLA fields
│   ├── views.py         # Web views (ticket CRUD, category management)
│   ├── api_views.py     # REST API views + analytics + CSV/Excel export
│   ├── serializers.py   # DRF serializers
│   ├── filters.py       # django-filter FilterSets
│   └── api_urls.py      # API URL routing
├── templates/           # HTML templates (redesigned)
│   ├── base.html        # Sidebar layout
│   ├── registration/    # Login, user, password templates
│   └── vats/            # Ticket, category, dashboard templates
└── static/
    └── css/main.css     # Custom design system
```

---

## 🔐 Security Notes

- All credentials (DB, email, Twilio) stored in `.env` — never committed to Git
- `.env` is listed in `.gitignore`
- Session-based authentication for the web UI
- Role-based access enforced at view level (decorators) and API level (permissions)

---

*Built as a final-year project — upgraded with REST API, analytics dashboard, and professional UI for portfolio showcase.*
