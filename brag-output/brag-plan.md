# /brag plan — HelpDesk Pro

**What it is:** A Django IT support portal where employees raise tickets, admins and managers work them through a lifecycle, and every ticket is tracked against a priority-based SLA. A 4-page Power BI report reads from the app's own REST feed.

**Who it's for:** IT support teams (Admin / Manager / Viewer roles). It's also a portfolio piece for Data Analyst, BA and Support Analyst roles.

**What sets it apart:** SLA state is built into every row (Breached / Late / On time), and the analytics go all the way to a real Power BI report fed by `/api/v1/powerbi/tickets/`.

**Hook:** The real "Raise New Ticket" form being filled in: *"Something broke? Raise a ticket."*

**Tone:** `default` leaning polished. Clean and confident, soft transitions, recruiter-friendly.

**Visual identity:** App tokens from `static/css/main.css`: slate `#0F172A`/`#1E293B`, teal `#0F766E`→`#14B8A6`, Inter + JetBrains Mono, login-page gradient. Power BI scenes use the report's registered theme (`#12191E` page, `#1B262C` visuals, `#2E6A96` borders, `#3282B8` data, `#BBE1FA` text).

**Share caption:** see `share-copy.txt`.

## Storyboard (22.5s, 1920×1080, 30fps, cuts on a 120 BPM grid)

| # | Time | Scene | On screen |
|---|---|---|---|
| 1 | 0.0–3.5 | Hook | Real create-ticket form (Viewer: James Wilson), typed in live; cursor submits. "Something broke? / Raise a ticket." |
| 2 | 3.5–6.5 | Reveal | App logo mark + **HelpDesk Pro** + "The IT support portal that tracks every ticket against its SLA." Lifecycle badges pop in: Pending → Assigned → Scoping → In Progress → Completed |
| 3 | 6.5–11.0 | Highlight 1 | Success toast + new TKT000032 row ("Your ticket is logged instantly.") → Admin's All Tickets, camera onto the SLA State column ("Every ticket gets an SLA clock.") |
| 4 | 11.0–14.0 | Highlight 2 | Admin dashboard: KPI cards → volume and priority charts. "Live KPIs for the whole team." |
| 5 | 14.0–19.0 | Highlight 3 | The 4 Power BI pages rebuilt from the PBIP layout and theme with real feed data; cursor clicks through Overview → SLA & Aging → Category Deep-Dive → Agent Workload. "Plus a 4-page Power BI report / fed by the app's own REST API." |
| 6 | 19.0–22.5 | Outro | Logo, **HelpDesk Pro**, "Django · REST API · Power BI", repo link |

## Sourcing notes
- Web-app scenes are real screenshots of the running app (seeded demo data, 2× DPR), captured with Playwright. The typing sequence is 32 real captures of the form mid-entry.
- Power BI Desktop can't run on Linux, so the report pages are redrawn from `powerbi/…Report/definition/pages/*/visuals/*.json` (positions, visual types, titles, fields) and the registered theme JSON. The numbers come from the same feed endpoint Power BI refreshes from, with the DAX measure logic from the semantic model.
