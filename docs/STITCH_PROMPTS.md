# Stitch — what to type in each field

Companion to `STITCH_DESIGN_BRIEF.md`. Field names may differ slightly in
Stitch's UI; match by intent.

---

## Field: GitHub repository link

`https://github.com/VatsSanghvi/HelpDesk-Pro`

⚠️ Optional, and low value here — see "Why the repo link doesn't help much" at
the bottom. Fill in the design brief instead. If you do link it, read the
security note first.

---

## Field: existing design.md / design context

Paste **the entire contents of `docs/STITCH_DESIGN_BRIEF.md`**.

---

## Field: Additional instructions

Paste this verbatim:

```
Do not redesign the information architecture. The sidebar + top bar shell, the
screen list, and the data shown on each screen are fixed — treat them as given.
Your job is the visual system on top of them.

Optimise for an internal tool an IT support agent stares at for eight hours,
not for a marketing site. That means: high information density, restrained
colour used to carry meaning rather than decoration, generous but consistent
spacing, and a type scale with real hierarchy. No hero sections, no gradients
on large surfaces, no illustrations, no marketing copy.

Start with the design tokens and the badge matrix, then build the app shell,
then the ticket list and ticket detail. Those two screens are 80% of the
product's real usage — get them right before the rest.

Show every state, not just the happy path: loading, empty, validation error,
and SLA-breached. A design that only shows populated happy-path screens is not
usable to me.

Output plain semantic HTML plus a single stylesheet driven by CSS custom
properties. Keep class names descriptive and framework-agnostic. Do not emit
React, JSX, or any component-framework code.
```

---

## Prompt: the first screen to generate

Generate screens one at a time and iterate. Start here:

```
The ticket list screen for HelpDesk Pro, Admin role.

Full app shell: fixed dark left sidebar with the brand block, grouped nav
sections (Tickets: My Tickets / All Tickets / Pending; Manage: Users /
Categories; Account: My Profile / Logout), and the current item clearly active.
Top bar with page title "Tickets", the subtext "All tickets", and on the right
the signed-in user's avatar initials, name, and the role label "Admin".

Body: a page header with an "Export CSV" and "Export Excel" button on the right,
then a row of status filter pills (Pending, Assigned, Scoping, In Progress,
Completed, Cancelled, Rejected) with "Pending" active, then a dense data table
of about 12 tickets.

Table columns: select checkbox, ticket number, title, status badge, priority
badge, category, assignee (avatar + name), created date, SLA state. Two rows
must show an SLA-breached warning state. Show a bulk-action bar in the selected
state above the table. Numbered pagination at the bottom.

All seven status badges and all four priority badges must appear across the
rows, and each must be tellable apart at a glance without relying on colour
alone.
```

Then, in order: **ticket detail** → **dashboard** → **app shell for Viewer and
Manager roles** → **ticket create form** → **login** → **admin CRUD tables**.

---

## Why the repo link doesn't help much

HelpDesk Pro is **Django server-rendered templates** — the files are
`{% block %}`, `{% url %}`, `{% for %}` tags wrapped around Bootstrap 4 markup.
Stitch produces standalone HTML/Tailwind screens. It cannot read those templates
and hand back working Django templates, so what it gains from the repo is mostly
just the content and structure — which the design brief states more clearly and
more completely than the code does.

Give Stitch the brief. Treat whatever it returns as a **visual reference**, and
let Claude Code do the porting into the real templates.

## Note on the credentials file

`ID_passwords.txt` at the repo root is **intentional** — it holds fake seed
accounts so anyone cloning the project can log in as Admin / Manager / Viewer
without creating users first. Not real credentials, nothing sensitive, safe to
leave in a public repo.
