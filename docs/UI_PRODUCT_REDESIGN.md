# Product redesign — the triage board

The third version of the interface, built when the project's goal changed from
a portfolio piece to a product for sale. Screenshots are in `ui-product/`.

| Screen | File |
|---|---|
| Sign-in | `ui-product/01-sign-in.png` |
| Dashboard (Admin) | `ui-product/02-dashboard.png` |
| Ticket list | `ui-product/03-ticket-list.png` |
| Ticket page | `ui-product/04-ticket.png` |
| Triage form | `ui-product/05-triage.png` |
| Dashboard (employee) | `ui-product/06-employee-dashboard.png` |
| Dashboard on a phone | `ui-product/07-phone-dashboard.png` |

The earlier redesign is described in [`UI_REDESIGN.md`](UI_REDESIGN.md).

---

## The brief

Buyer: the in-house IT team of a company with roughly 20 to 500 employees.
Within ten seconds of a demo they should think **"this team is in control"**
and **"my staff could use this today"**.

It must not look like a stock admin template, be playful, need training, or
resemble Zendesk or Jira. Every existing feature keeps working, and role names
and labels stay as they were.

## The idea

An emergency department and an IT desk run on the same mechanism: sort what
arrives by urgency, then work each case against a time limit. The product
already used the word *triage*. The design takes the rest of the department's
board with it.

| Borrowed | Becomes |
|---|---|
| Triage category (1, 2, 3) | Priority as a numbered square. The number carries the rank, so it survives colour blindness and a black-and-white printout. |
| The four-hour waiting standard | The **waiting clock** on every open ticket. |
| Theatre green | The room. Operating theatres are green because it rests eyes that keep looking at red. Here it keeps a breached ticket unmissable. |
| The observation chart's banded zones | The clock's track: clear, then amber for the last quarter of the SLA window, then red for overtime. |

Only four things come from that world: type, palette, density and the clock.
Navigation, tables, forms and buttons are the standard ones a person already
knows how to use.

## What changed, screen by screen

**Dashboard.** Six KPI tiles became one sentence that states the worst news
first, followed by the open tickets in order of urgency. Tickets waiting for
triage and team workload sit beside it, each with the action it leads to. The
totals moved below, where they are reference rather than headline.

**Employee dashboard.** Before, a Viewer's dashboard requested analytics from
an endpoint Viewers are not permitted to call, so its cards never filled. It
now shows each of their tickets on a five-step progress line, and what happens
after a ticket is raised.

**Navigation.** The sidebar's nine entries were five destinations and four
filters. The filters ("My Tickets", "Pending", "Assigned", "In Progress")
became controls on the ticket page, which leaves four destinations in a top
bar and gives the ticket table the full width.

**Ticket list.** Category moved into the summary line under the title, which
gave the subject column room. Status became a pill whose dot fills as the
ticket advances, so status and priority never look alike and neither relies on
colour.

**Ticket page.** The page now reads in the order a person asks: where is it,
what is it, what has happened. The next action for your role is in the header.

## Decisions worth explaining

- **No outside requests.** Bootstrap, jQuery, Popper, Google Fonts, an icon
  font and Chart.js all loaded from CDNs, so the app broke wherever those
  hosts were blocked. Everything now ships with the app, which matters to a
  business on a locked-down network and means no visitor data goes to third
  parties.
- **Tables that stop being tables.** Below a certain width a ticket table is
  unreadable however it scrolls. Container queries turn each row into a block
  when the table's own container is too narrow, not when the screen is, so the
  dashboard's short table and the full list each give up at the right moment.
- **Honest empty states.** "Starts at triage" where a ticket has no deadline
  yet. "No tickets rated yet" where there is no CSAT. A dash is not a state.
- **The clock's warning threshold.** Amber starts at the last quarter of the
  window *or* the last hour, whichever comes first. A flat one-hour rule would
  leave a 72-hour ticket silent until it was nearly lost.
- **Demo data dated from now.** The old seed stamped tickets a random 1 to 30
  days back, so every open ticket was weeks overdue: a demonstration of a
  failing desk. `seed_data --retime` gives two late, two close, the rest on
  time.

## How it was chosen

Five directions were drawn as working screens with the real ticket data and
shown side by side: this one with a side menu, a station departure board, an
air-traffic strip board, a transit-style service status board, and this one
with a top menu. The owner picked the green triage board and asked for the
menu at the top.

## Known limits

- Displayed times still add a fixed +5:30 offset (`get_created_at` and
  friends). A product sold outside one time zone needs a per-installation or
  per-user setting.
- The 30-second demo video in the README shows the previous interface.
- The email templates were not redesigned.
