# UI — before the redesign

Screenshots of HelpDesk Pro **as it looked before the Stitch redesign**,
captured 2026-09-09 at 1440px wide.

These are committed deliberately. They are the "before" half of the
before/after comparison, so the change is demonstrable later without needing
to check out old code and run it.

| File | Screen | Role |
|---|---|---|
| `01-login.png` | Login | — |
| `02-dashboard.png` | Dashboard (KPI cards, charts) | Admin |
| `03-ticket-list.png` | Ticket list — the main screen | Admin |
| `04-ticket-detail.png` | Ticket detail + work notes | Admin |
| `05-my-tickets.png` | My Tickets personal queue | Admin |
| `06-user-list.png` | User management | Admin |
| `07-manager-list.png` | Ticket list, manager's filtered view | Manager |

## The matching code state

Committed screenshots can drift from the code, so the same state is tagged:

```bash
git checkout ui-before-redesign   # the UI in these screenshots
git checkout main                 # the current UI
```

## How these were captured

Not by hand. Django's test client rendered each page as a logged-in user,
`static/css/main.css` was inlined into the HTML, and headless Chrome
screenshotted the result at 1440x1400. Repeatable — the same method captures
the "after" set so the two are directly comparable rather than being two
differently-cropped manual screenshots.

## What characterised the old design

Worth being able to name specifics rather than just "it looked older":

- **Flat type scale** — near-uniform 14px, so page titles, table headers and
  cell text all competed for attention.
- **`--primary: #185FA5`** corporate blue as the single accent.
- **Untriaged priority rendered as a bare em-dash** (`—`) — visible on
  TKT000010, TKT000015 and TKT000023 in `03-ticket-list.png`. A real state in
  the data with no real visual treatment.
- **Status badges as loose `.sbadge-*` rules** rather than a designed matrix,
  so status and priority badges shared one visual language.
- No skeleton/loading states; KPI cards popped in when the API returned.
