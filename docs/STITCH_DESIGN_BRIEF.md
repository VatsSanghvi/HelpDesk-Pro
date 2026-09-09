# HelpDesk Pro — Design Brief for Stitch

> Paste this whole file into Stitch's **"existing design.md"** / design-context field.
> It replaces the need for Stitch to crawl the repo.

---

## 1. What the product is

**HelpDesk Pro** is an internal IT support ticketing system (an ITSM tool, in the
same family as ServiceNow, Jira Service Management, Freshservice). Employees raise
tickets for IT problems; support staff triage, assign, and resolve them; managers
watch SLA compliance and team workload on a dashboard.

It is a **desktop-first internal web app**. Users sit at it for hours. Density,
scannability and low visual fatigue matter far more than marketing polish.
There is no landing page, no signup flow, no pricing page.

---

## 2. Who uses it — three roles, three different apps

The navigation and the dashboard change per role. Design all three.

| Role | Mental model | Primary need |
|---|---|---|
| **Viewer** (employee) | "I have a problem" | Raise a ticket, watch its status, rate it when resolved |
| **Manager** (support engineer) | "What's on my plate" | Work the queue assigned to them, move tickets through statuses, add work notes |
| **Admin** (IT lead) | "Is the team keeping up" | Triage/approve incoming, assign owners, watch SLA breaches, manage users & categories, export data |

---

## 3. Domain vocabulary — use these exact words

**Ticket statuses** (this is the lifecycle, in order):
`Pending` → `Assigned` → `Scoping` → `In Progress` → `Completed`
Plus two terminal off-ramps: `Cancelled`, `Rejected`.

**Priorities:** `Critical`, `High`, `Medium`, `Low`.

**Other domain objects:** Ticket number (e.g. `TKT-000142`), Category →
Subcategory (two-level taxonomy), Work Notes (an append-only comment/audit
timeline on each ticket), SLA deadline (auto-calculated from priority) and
**SLA breach** (a hard warning state), CSAT rating (1–5 stars, given by the
Viewer after resolution), First Response Time.

---

## 4. Screens to design

Design these as a coherent set, not as isolated pages.

### 4.1 App shell (highest priority — everything inherits it)
- Fixed **left sidebar**: product brand block at top, then grouped nav sections
  with small uppercase section labels, then a footer with logout.
- **Top bar**: page title + one line of subtext on the left; on the right, the
  signed-in user's avatar initials, full name, and role label.
- Content area below the top bar.
- Show the sidebar in all three role variants (the nav groups differ per role).

### 4.2 Dashboard
- A row of **KPI cards**: Total Tickets, Open, Resolved, Avg Resolution (hours),
  Avg First Response Time, Avg CSAT.
  Each card has: small muted label, large number, a one-line sub-caption, and a
  tinted icon chip.
- **Ticket volume over the last 7 days** — line or bar chart.
- **Priority breakdown** — donut chart.
- **Category performance** — horizontal progress bars, one per category.
- **Team workload** — a compact table of Managers with open vs. resolved counts.
- Design an **empty state** and a **loading/skeleton state** for the KPI row
  (the numbers arrive by API after page load).

### 4.3 Ticket list
- Page header with title, and action buttons on the right
  (`New Ticket` for Viewers; `Export CSV` / `Export Excel` for Admin & Manager).
- A row of **status filter pills** — one per status, the active one highlighted.
- A **dense data table**: checkbox, ticket number, title, status badge, priority
  badge, category, assignee, created date, SLA state.
- A **bulk action bar** that appears above the table when rows are selected.
- Design the **empty state** ("no tickets match this filter").

### 4.4 Ticket detail — the most-used screen, give it the most attention
- Header: ticket title, ticket number, status badge, priority badge, and an
  `SLA Breached` warning badge when applicable.
- A row of contextual action buttons that varies by role and current status
  (Approve, Reject, Assign, Change Status, Edit, Back).
- Two-column body: **left** = description and the Work Notes timeline;
  **right** = a metadata panel (requester, assignee, category/subcategory,
  created, SLA deadline, CSAT).
- **Work Notes timeline**: each entry has author avatar, author name, timestamp,
  and the note body. Status-change entries should look visibly different from
  human comments. Include the "add a work note" composer at the bottom.

### 4.5 Ticket create / edit form
- Fields: Title, Description, Category (select), Subcategory (select, filtered by
  the chosen Category), Priority (select), and an attachment field.
- Show the form's **validation error state**.

### 4.6 Login
- Standalone centered card, no sidebar. Brand mark, email + password, error state.

### 4.7 Admin management screens
- **User list**: table of users with avatar, name, email, role badge, actions.
- **User detail / edit form**.
- **Category list** and **Subcategory list**: simple CRUD tables.

---

## 5. What I want you to change

Keep the **information architecture exactly as described above** — sidebar +
top bar, same screens, same data on each screen. I am not looking to reorganise
the product.

Give me a **new visual language** for it:

- A more considered color system than the current flat corporate blue. It should
  still read as trustworthy enterprise software.
- **Status and priority badges are the heart of this UI.** Seven statuses and four
  priorities need to be instantly distinguishable at a glance in a dense table,
  and must stay distinguishable for a colour-blind user — so lean on shape,
  weight, border and icon, not hue alone.
- Better **typographic hierarchy and rhythm**. The current UI is uniformly 14px
  and everything competes.
- Real **spacing and elevation scales**, consistently applied.
- **Replace every emoji** currently used as an icon with a proper icon set
  (Material Symbols preferred).
- A genuinely well-designed **data table** — this app lives or dies on its table.

---

## 6. Hard constraints — the output has to survive porting

The design will be hand-ported into **Django templates styled with Bootstrap 4
plus a custom CSS layer**. So:

- **Desktop-first**, 1440px reference width. Must stay usable down to 1024px.
  Mobile is a nice-to-have, not a requirement.
- **No dark mode.** Light theme only.
- Assume **server-rendered pages** with full page loads. No SPA transitions, no
  client-side routing, no drag-and-drop, no optimistic UI, no infinite scroll —
  use ordinary numbered pagination.
- Charts are rendered by **Chart.js**. Design chart styling that Chart.js can
  actually produce (colors, grid lines, legends, rounded bars) — no exotic
  custom-canvas visuals.
- Keep dependencies to CSS. No component library that requires a JS framework.

## 7. Deliverable I need back

Above all, a **design token set** — color scale, type scale, spacing scale,
radii, shadows, and the full badge matrix (7 statuses × 4 priorities) — because
those tokens are what I will actually port into the stylesheet. The screens are
how I check the tokens work.
