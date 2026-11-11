---
name: HelpDesk Pro
description: A triage board for IT tickets, where every open ticket carries a clock against its SLA.
colors:
  green: "#0d5a41"
  green-deep: "#0a4634"
  green-wash: "#e2f0e9"
  room: "#d5e6dc"
  room-deep: "#bdd5c7"
  room-edge: "#a9c6b6"
  room-ink: "#17382b"
  room-ink-2: "#36574a"
  p1: "#c5162a"
  p1-wash: "#fdeaea"
  p1-edge: "#f0b9b9"
  p2: "#e39a00"
  p2-ink: "#7a4c00"
  p2-wash: "#fff4d1"
  p2-edge: "#edd08a"
  p3: "#22774a"
  zone-warn: "#ffe394"
  zone-over: "#f4aaa5"
  ink: "#0f211a"
  ink-2: "#3a4d44"
  ink-3: "#55675e"
  ground: "#f3f8f5"
  paper: "#ffffff"
  row-hover: "#f7fbf9"
  rule: "#d3e0d8"
  rule-strong: "#b3c7bb"
  field-edge: "#78938a"
typography:
  display:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "2.375rem"
    fontWeight: 700
    lineHeight: 1.12
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.012em"
  figure:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    fontFeature: "'tnum'"
  title:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.90625rem"
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.84375rem"
    fontWeight: 400
    lineHeight: 1.4
  label:
    fontFamily: "'Atkinson Hyperlegible Next', 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    fontSize: "0.78125rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  track: "2px"
  sm: "4px"
  md: "6px"
  lg: "8px"
  pill: "999px"
spacing:
  cell: "0.75rem"
  panel-inset: "1.125rem"
  gutter-small: "1.25rem"
  stack: "1.5rem"
  column-gap: "1.75rem"
  gutter: "2rem"
  section: "2.5rem"
components:
  button-primary:
    backgroundColor: "{colors.green}"
    textColor: "{colors.paper}"
    rounded: "{rounded.md}"
    height: "2.25rem"
    padding: "0 0.875rem"
  button-primary-hover:
    backgroundColor: "{colors.green-deep}"
    textColor: "{colors.paper}"
  button-secondary:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "2.25rem"
    padding: "0 0.875rem"
  button-secondary-hover:
    backgroundColor: "{colors.green-wash}"
    textColor: "{colors.ink}"
  button-quiet:
    textColor: "{colors.green}"
    rounded: "{rounded.md}"
    height: "2.25rem"
    padding: "0 0.625rem"
  button-quiet-hover:
    backgroundColor: "{colors.green-wash}"
    textColor: "{colors.green-deep}"
  button-danger:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.p1}"
    rounded: "{rounded.md}"
    height: "2.25rem"
    padding: "0 0.875rem"
  button-danger-hover:
    backgroundColor: "{colors.p1-wash}"
    textColor: "{colors.p1}"
  band:
    backgroundColor: "{colors.room}"
    textColor: "{colors.room-ink}"
    height: "3.5rem"
  nav-link:
    textColor: "{colors.room-ink}"
    rounded: "{rounded.md}"
    height: "2.25rem"
    padding: "0 0.75rem"
  nav-link-current:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.room-ink}"
  panel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    height: "2.5rem"
    padding: "0 0.75rem"
  priority-square-high:
    backgroundColor: "{colors.p1}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    size: "1.625rem"
  priority-square-moderate:
    backgroundColor: "{colors.p2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    size: "1.625rem"
  priority-square-low:
    backgroundColor: "{colors.p3}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    size: "1.625rem"
  status-pill:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.pill}"
    padding: "0.125rem 0.5625rem 0.125rem 0.4375rem"
  status-pill-completed:
    backgroundColor: "{colors.green-wash}"
    textColor: "{colors.room-ink}"
  clock-track:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.track}"
    height: "0.75rem"
    width: "7.5rem"
  tooltip:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "0.1875rem 0.5rem"
---

# Design System: HelpDesk Pro

## Overview

**Creative North Star: "The Triage Board"**

HelpDesk Pro looks like the board in an emergency department, applied to IT tickets. The room is a calm, pale theatre green so that red is unmissable. Priority is a triage category drawn as a numbered square, and every open ticket carries a clock against its SLA. The working surfaces are white chart paper divided by green-grey hairlines; deep green is reserved for the action you take next.

The system is dense and quiet. One typeface carries every voice. Depth is carried by tone and hairline, and the only things that float are menus and the tooltip. Colour is spent on urgency: red, amber and green belong to the triage scale and the clock zones, and ticket status is deliberately drawn in ink so it never competes with them. Page headings are sentences that state what is late and what is waiting.

The owner chose this direction and rejected four things by name: looking like a stock admin template (dark sidebar, white KPI cards, coloured icon tiles), being playful, needing training, and resembling Zendesk or Jira. Navigation sits in a top band at the owner's request.

**Key Characteristics:**
- A pale green room with white paper surfaces and green-grey hairlines.
- Priority as a numbered square: 1 High, 2 Moderate, 3 Low, dashed for Untriaged.
- A waiting clock on every open ticket: banded track, ink marker, plain-words label.
- Status in ink only: a pill whose dot fills in quarters.
- One typeface, Atkinson Hyperlegible Next, with fixed-width figures wherever numbers line up.
- Flat surfaces; one shadow, for things that float.
- One authored motion: each clock's marker travels to its position once on load.

## Colors

A green room built to make red loud: greens and green-greys everywhere, with red, amber and a mid green held back for the triage scale.

### Primary
- **Deep Action Green** (`green`): primary buttons, links, the brand mark, focus outlines, the current tab's underline, the current page in the pager, done steps in the lifecycle, workload and category meters. `green-deep` is its hover.
- **Green Wash** (`green-wash`): the pale reply to an action: hover on secondary and quiet buttons, unread notifications, the bulk-action bar, success alerts, the Completed status pill.

### Secondary
- **Theatre Green** (`room`): the top band, the sign-in side panel, the segmented control's trough, count chips and numbered-list bullets. `room-deep` is the count chip inside the band and the text selection; `room-edge` is the band's bottom border and the border of green-washed things; `room-ink` and `room-ink-2` are the text colours on the room.

### Tertiary
The triage scale. These three hues carry urgency and are not available for decoration.
- **Triage Red** (`p1`): the High square, late clock labels, breached and missed verdicts, the alert figure, the unread count, errors, required marks and the danger button. `p1-wash` and `p1-edge` are its alert and danger-hover surface and border.
- **Triage Amber** (`p2`): the Moderate square and its bar. On white it fails as text, so amber words use **Amber Ink** (`p2-ink`): the "soon" clock label and the warning icon. `p2-wash` and `p2-edge` are the warning alert. Amber also fills the satisfaction stars.
- **Triage Green** (`p3`): the Low square and its bar, the met-SLA tick, the active-user dot.
- **Clock Amber** and **Clock Red** (`zone-warn`, `zone-over`): the pale zones of the waiting clock's track. They appear nowhere else.

### Neutral
- **Board Ink** (`ink`): body text, the clock marker, the status dot, the tooltip background, the Admin role tag.
- **Ink 2** (`ink-2`) and **Ink 3** (`ink-3`): secondary text and metadata. Ink 3 is the lightest text colour in the system; it is also the dashed outline of anything Untriaged.
- **Ground** (`ground`): the page, table header rows, disabled fields, note blocks inside a panel.
- **Chart Paper** (`paper`): panels, fields, menus, the current navigation item.
- **Row Hover** (`row-hover`): the tint a table row or list row takes under the pointer.
- **Hairline** (`rule`) and **Strong Hairline** (`rule-strong`): panel borders and row dividers; the stronger one borders menus, pills, secondary buttons and the tab rail.
- **Field Edge** (`field-edge`): the border of every form field, darker than any hairline so a field reads as a field.

### Named Rules
**The Quiet Room Rule.** Red, amber and triage green mean urgency or outcome. They are never used for categories, charts of neutral data, avatars or emphasis. Avatar tints and neutral bars stay in the room's green-to-stone range.

**The Number Carries It Rule.** No state depends on colour alone. The priority square holds its rank as a digit, the clock has a written label, status has a dot fill or an icon, and Untriaged is dashed and unfilled.

**The Ink Status Rule.** A ticket in progress shows its status in ink on paper. Only an end state changes the pill: Completed takes the green wash and a tick, Cancelled and Rejected sit on the ground tint with an icon.

## Typography

**Display Font:** Atkinson Hyperlegible Next (with Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif)
**Body Font:** the same family
**Label/Mono Font:** none; labels use the same family with fixed-width figures

**Character:** One self-hosted variable face (weights 200 to 800, OFL) does every job. It was drawn for legibility, which suits a screen people read all day, and its open digits make ticket numbers and times easy to tell apart. Hierarchy comes from weight (400, 600, 700) and a tight size ramp, not from a second family.

### Hierarchy
- **Display** (700, 2.375rem, 1.12, -0.02em): the sign-in pitch only. 1.625rem below 44rem.
- **Headline** (700, 1.75rem, 1.2, -0.012em): one per page, written as a sentence. 1.5rem below 44rem. Its supporting line is 0.96875rem in Ink 2, at most 70ch.
- **Figure** (700, 1.5rem, 1.2, tabular): the number in a figures row.
- **Title** (700, 1.0625rem, 1.3): panel headings and the brand name.
- **Body** (400, 0.90625rem, 1.5): everything else. Row titles and names are the same size at 700. Long text (ticket description, notes) is 0.96875rem at 1.6, at most 72ch.
- **Body small** (0.84375rem): metadata lines, field labels (600), help text, status pills (600), small buttons.
- **Label** (600, 0.78125rem): table column heads in Ink 3, count chips (700), tooltip, timestamps. Sentence case, no letter-spacing.

### Named Rules
**The Tabular Where It Lines Up Rule.** Fixed-width figures are switched on only where numbers align or change in place: tables, figures, clocks, ticket numbers, counts, pagers, timestamps. Running text keeps proportional figures.

**The Sentence Head Rule.** Headings say what is true ("2 tickets are past their SLA deadline"), in sentence case. Nothing is set in capitals.

## Layout

A sticky top band (3.5rem) holds brand, navigation, the role's main action, notifications and the account menu. Below it a single centred page column, at most 86rem wide with 2rem gutters; forms and single-record pages narrow to 46rem or 64rem.

Inside the page: a heading row (sentence headline left, actions right), then panels. Two column patterns recur: a main column beside a fixed 22rem aside, and an uneven pair at 1.55 to 1. Related summaries share one panel divided by hairlines instead of sitting in separate cards. Vertical rhythm is 1.5rem between stacked panels, 1.75rem between columns and 2.5rem before a new section. Panels are inset 1.125rem; table cells 0.75rem, with the first and last cell aligned to the panel inset.

Responsive behaviour:
- Below 72rem the two-column patterns collapse to one column.
- Below 60rem the gutter drops to 1.25rem and navigation folds behind a menu button into a full-width sheet under the band, with 2.75rem rows.
- Below 44rem figures go two across, fact lists stack label over value, the lifecycle becomes a vertical list, the clock track shortens to 4.5rem, and buttons, icon buttons and tabs grow to a 2.75rem touch height.
- Ticket tables respond to their own container, not the viewport. The full list drops its Updated column below 84rem and becomes stacked rows below 70rem; the dashboard table stacks below 36rem. A stacked row puts the subject first, then priority and status, then the clock on its own line.

## Elevation & Depth

Flat. Depth is tonal: ground, then paper, separated by a 1px hairline. Panels have no shadow. A shadow means the thing is floating above the page and will go away.

### Shadow Vocabulary
- **Floating** (`box-shadow: 0 2px 6px rgb(15 33 26 / 0.08), 0 14px 28px -10px rgb(15 33 26 / 0.28)`): dropdown menus, the notification panel and the tooltip.
- **Sheet** (`box-shadow: 0 12px 20px -12px rgb(15 33 26 / 0.3)`): the navigation sheet on small screens.
- **Selected segment** (`box-shadow: 0 1px 2px rgb(15 33 26 / 0.12)`): the chosen option in a segmented control.
- **Field focus** (`box-shadow: 0 0 0 3px rgb(13 90 65 / 0.18)`): a ring, with the border turning Deep Action Green.

### Named Rules
**The Paper Stays Down Rule.** Panels, tables, figures and alerts are flat. Do not add a resting or hover shadow to a surface that is part of the page.

## Shapes

Small, consistent corners: 4px for squares, chips and tags; 6px for buttons, fields, navigation items and alerts; 8px for panels and menus. The clock track and chart bars use 2px so they read as instruments. Full rounding is kept for things that are round by nature: status pills, avatars, dots, the unread count.

Borders are 1px hairlines. The two exceptions are meaningful: a 3px underline marks the current tab, and a 1.5px dashed outline marks anything Untriaged (the square, its bar). Icons are Lucide outlines at 2px stroke, 1.125rem by default, inlined as a sprite.

## Components

### Buttons
Plain and firm; they change tone, not size or position.
- **Shape:** 6px corners, 2.25rem tall, 0.875rem bold label, optional leading icon. Small is 1.875rem, large 2.75rem.
- **Primary:** Deep Action Green with white text. One per view or panel.
- **Secondary:** paper with a strong hairline; hover washes green.
- **Quiet:** green text, no border; hover washes green.
- **Danger:** paper with a red-edge border and red text; hover fills with the red wash.
- **Hover / Focus:** colour transitions over 150ms; pressing moves the button down 1px; focus is a 2px green outline offset 2px. Disabled is ground-tinted with Ink 3 text.

### Chips
- **Status pill:** fully rounded, paper, strong hairline, 600 weight. Its dot is an ink ring that fills clockwise: empty for Pending, a quarter for Assigned, half for Scoping, three quarters for In Progress. Completed, Cancelled and Rejected replace the dot with a tick, ban or cross icon.
- **Count chip:** 4px corners, room green, bold label size; used in navigation, tabs and panel heads.
- **Role tag:** 4px corners; Admin is ink with white text, Manager is room green, Viewer is outlined.

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** paper on ground.
- **Shadow Strategy:** none; see Elevation & Depth.
- **Border:** 1px hairline. Sections inside a panel are divided by hairlines, not nested cards.
- **Internal Padding:** 1.125rem at the sides, 0.875rem above and below a panel head. A panel head is a title, an optional muted note or count chip, and an optional link pushed to the right.
- **Figures row:** one bordered strip of cells divided by hairlines, each a bold number with a plain-words label beside or under it. A missing value is a dash in Ink 3 with a label that says why. A figure that needs attention turns its number red.

### Tables and rows
- **Head:** label size, 600, Ink 3, on ground, hairline above and below.
- **Rows:** 0.5625rem by 0.75rem cells, hairline between rows, row-hover tint under the pointer. The subject is a bold ink link with one small metadata line beneath (ticket number, category, status).
- **Narrow:** rows restack by container width as described in Layout. Column heads stay available to screen readers.

### Inputs / Fields
- **Style:** paper, 1px field-edge border, 6px corners, 2.5rem tall; label above in small 600; help text below in Ink 3. Selects use an inline chevron.
- **Focus:** border turns Deep Action Green with the field-focus ring.
- **Error / Disabled:** red border with a small bold red message and icon beneath; disabled is ground-tinted and not editable.

### Navigation
- **Band:** room green, 3.5rem, sticky, hairline beneath. Links are 500 weight in room ink; hover lightens with translucent white; the current page is a paper tile in 700.
- **Tabs:** text tabs on a strong hairline; the current tab is ink, 700, with a 3px green underline. Each may carry a count chip.
- **Menus:** paper, 8px corners, strong hairline, floating shadow; they open with a 160ms drop.
- **Small screens:** a menu button opens the links as a sheet under the band; Escape closes it.

### Priority square
A 1.625rem square with 4px corners holding the rank as a bold digit, followed by the priority name in bold: red 1 High (white digit), amber 2 Moderate (ink digit), green 3 Low (white digit). Untriaged is a dashed, unfilled square with a question mark and a lighter label. The same colours and the same dashed treatment are used for priority bars.

### Waiting clock (signature)
Shown for every open, triaged ticket. A 0.75rem-high track with a strong hairline and 2px corners, in three bands: paper for the first 56.25%, Clock Amber to 75%, Clock Red to the end. The track spans the SLA window plus a third of overtime, so the deadline sits at the 75% line and amber is the last quarter of the window. A 3px ink marker, overhanging the track by 4px top and bottom, stands where the ticket is now. Beside it, a 600-weight label in words ("2h 11m remaining"); it turns Amber Ink and bold when soon, Triage Red and bold when late ("Breached (+24m)").
- **Width:** 7.5rem by default, 6rem in the ticket list, 12rem on a ticket page, 4.5rem below 44rem.
- **Motion:** on load the marker travels from the start of the track to its position over 900ms on an ease-out curve (`cubic-bezier(0.16, 1, 0.3, 1)`), staggered 45ms per row. Meters grow in over 700ms on the same curve. With reduced motion, both are at rest immediately.
- **Tooltip:** on hover and keyboard focus, one line directly under the clock: due time, window length, percentage used. Ink background, white label-size text, floating shadow.
- **No clock:** a closed ticket gets a verdict (icon and words: met or missed); an untriaged one says "Starts at triage".

### Lifecycle and activity
The lifecycle is five steps on a 2px rail: done steps are solid green, the current one is a green dot ringed in paper, a stopped ticket ends in red. The activity feed is a vertical rail of small ground-tinted icon dots, each with who, when and what changed; notes sit in a ground-tinted block.

### Alerts and empty states
Alerts are one bordered row: icon, message in 600, dismiss button. Success is green-washed, warning amber-washed, error red-washed. Empty states are centred text in the panel: a bold line, one sentence in Ink 2, and the action if there is one.

## Do's and Don'ts

### Do:
- **Do** put a waiting clock on every open, triaged ticket wherever it is listed, and a verdict on every closed one.
- **Do** show priority as the numbered square with its name. Use the dashed, unfilled treatment for anything Untriaged.
- **Do** keep red, amber and triage green for urgency and outcome, and pair each with a digit, word or icon.
- **Do** write page headings as sentences that state the situation, with counts.
- **Do** group related summaries in one panel divided by hairlines.
- **Do** use Amber Ink for amber words on a light surface; Triage Amber is for fills.
- **Do** switch on fixed-width figures for any new column or counter where numbers line up.
- **Do** give every hover explanation a keyboard-focus equivalent, and honour reduced motion.
- **Do** keep assets self-hosted: the font, Chart.js and the icon sprite ship with the app, which makes no outside requests.
- **Do** keep the role names Admin, Manager and Viewer and the existing labels as written.

### Don't:
- **Don't** build a dark sidebar, a row of separate white KPI cards, or coloured icon tiles. The owner rejected the stock admin template look.
- **Don't** make it playful: no illustration, mascots or celebratory motion.
- **Don't** borrow the look of Zendesk or Jira.
- **Don't** colour the status of a ticket in progress; the dot fill carries it.
- **Don't** use the triage colours for categories, avatars or neutral charts.
- **Don't** add shadows to panels, tables or figures.
- **Don't** add a second typeface, capitals or letter-spaced labels.
- **Don't** animate anything on load beyond the clock marker and the meters.
- **Don't** show a blank where a value is missing; say what is missing and why.
