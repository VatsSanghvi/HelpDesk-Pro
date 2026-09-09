# UI Redesign — before and after

Screenshots of the same seven screens, same viewport (1440px), same capture
method, before and after the redesign. Directly comparable.

| Screen | Before | After |
|---|---|---|
| Login | `ui-before/01-login.png` | `ui-after/01-login.png` |
| Dashboard | `ui-before/02-dashboard.png` | `ui-after/02-dashboard.png` |
| Ticket list | `ui-before/03-ticket-list.png` | `ui-after/03-ticket-list.png` |
| Ticket detail | `ui-before/04-ticket-detail.png` | `ui-after/04-ticket-detail.png` |
| My Tickets | `ui-before/05-my-tickets.png` | `ui-after/05-my-tickets.png` |
| User list | `ui-before/06-user-list.png` | `ui-after/06-user-list.png` |
| Ticket list (Manager) | `ui-before/07-manager-list.png` | `ui-after/07-manager-list.png` |

Code states:

```bash
git checkout ui-before-redesign   # the old UI
git checkout main                 # the new UI
```

---

## How the design was produced

The visual system came out of **Google Stitch**, driven by a written design
brief (`STITCH_DESIGN_BRIEF.md`) rather than by letting it read the repo —
Stitch generates standalone HTML/Tailwind screens and cannot return working
Django templates, so the brief describes the product more completely than the
code would have.

Stitch produced a **design system** (colour, type, spacing, elevation tokens)
plus reference screens. Those screens were reviewed in `design-preview/`, and
then the **tokens** — not the markup — were hand-ported into
`static/css/main.css`. The Django templates kept their structure.

That distinction matters: the port is a stylesheet rewrite plus four small
template edits, not a rebuild.

---

## What actually changed

### 1. The badge matrix — the substantive fix

The old UI styled status and priority badges the same way: both were tinted
pills from one loose set of `.sbadge-*` rules. In a dense table where the two
sit in adjacent columns, that meant a red "Rejected" status and a red "High"
priority looked like the same kind of object.

The two families are now deliberately **different shapes**, so they cannot be
confused even where they share a hue:

| Family | Shape | Treatment |
|---|---|---|
| **Status** (7) | Pill, fully rounded | Light tint, visible border, dot marker |
| **Priority** (4) | Chip, 6px radius | Saturated fill, white bold text, rank glyph |

Priority glyphs encode rank independently of colour — `keyboard_double_arrow_up`
for High, `drag_handle` for Moderate, `keyboard_arrow_down` for Low. The rank
is legible before colour registers, which is what makes it work for a
colour-blind user.

### 2. Untriaged is now a real state

Priority is `null` until an Admin triages a ticket, so a freshly-raised
`Pending` ticket genuinely has no priority. The old UI rendered that as a bare
em-dash (`—`), which read as "no value" rather than "not yet decided" —
visible on TKT000010, TKT000015 and TKT000023 in the before screenshot.

It now renders as an **"Untriaged" chip with a dashed border and a help
icon**. Dashed deliberately signals provisional. This was the single most
useful catch of the redesign, because it was a real gap in the data model's
visual representation, not a matter of taste.

### 3. Typography

The old UI was near-uniform 14px — page titles, table headers and cell text
all competed. Now there is a real scale: 36px tabular KPI numbers, 22px page
headings, 13px table rows, 11px uppercase labels, and **JetBrains Mono
reserved for ticket identifiers** so `TKT000142` reads as an ID rather than
prose.

### 4. Colour

`--primary` moved from `#185FA5` corporate blue to slate `#1E293B`, with
teal `#0F766E` taking over as the action colour. Chart.js colours were updated
in the same commit — a donut slice and its table badge must be the same
colour, or the palette reads as accidental.

### 5. Icons

Twenty emoji used as UI chrome were replaced with Material Symbols. Emoji
render differently on every OS and read as decorative rather than as
interface.

### 6. Motion, used sparingly

Row hover, card lift, focus rings for keyboard-only use, a skeleton shimmer
for the KPI row (those numbers arrive by API after page load, so there is a
real loading gap), and a slow low-amplitude pulse on SLA breach badges —
enough to draw the eye without being a blinking distraction. All of it is
wrapped in `prefers-reduced-motion`.

---

## Deliberate constraints

Everything is **plain CSS** — custom properties, gradients, `backdrop-filter`,
`box-shadow`, `transform`, `@keyframes`. No WebGL, no JS animation library, no
component framework. Not because those aren't impressive, but because they
cannot be hand-ported into Django templates, so anything built that way would
have been thrown away.

## Known trade-off

Rows are slightly taller than before, because priority chips carry more
padding and long category names now wrap. The table shows roughly 19 rows per
screen instead of ~25. Worth revisiting if density matters more than the badge
treatment.

---

## Round two — the mockup's layout and features

The first pass ported design *tokens* only, so the app looked correctly
styled but still had the old layout. This round closed the gap with the
Stitch mockup, building the elements as real functionality rather than
decoration:

| Element | Implementation |
|---|---|
| Notification bell | `Notification` model + `notify()` helper, fired from real events: ticket raised (Admins), assignment, reassignment, status change, rejection, cancellation, new work note. Unread badge, dropdown, click-to-open-and-mark-read, mark-all-read. |
| Filter pills with counts | Per-status counts from the role-scoped queryset, computed before status filtering so the pills show totals |
| Pagination | Django `Paginator`, 15/page — the view previously returned every ticket with no paging at all |
| Search | Over ticket number, title and description |
| Stat strip | Unassigned backlog, SLA breached, avg first response, resolution rate — real aggregates, role-scoped |
| Two-line subject | Title plus a description snippet, so a row carries enough to triage without opening it |
| Assignee avatars | Initials chip beside the name |
| Closed-row treatment | Strikethrough + reduced opacity on Cancelled/Rejected |
| Bulk action bar | Restyled to the dark selected-state treatment |

**Deliberately not faked.** Notifications are only ever created by real
lifecycle events — nothing is seeded. An empty bell honestly means nothing
has happened to your tickets yet. `notify()` also skips notifying someone
about their own action, since being told you did the thing you just did is
noise.

### A bug this surfaced

The bulk-reject action used a queryset `.update()`, which **bypasses
`Ticket.save()`** — the method that stamps `resolved_at`. Bulk-rejected
tickets were therefore left with no resolution timestamp, silently skewing
resolution-time metrics and the resolution-rate figure. Rewritten to iterate
and call `save()`.

That is worth knowing generally: `.update()` is faster because it goes
straight to SQL, but it skips `save()`, `auto_now`, and signals. If a model's
`save()` carries business logic, bulk `.update()` will quietly bypass it.
