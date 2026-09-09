# design-preview/

Scratch space for **looking at** Stitch output. Nothing in here is wired into
Django. Nothing in here affects the running app.

## The rule

Stitch HTML never goes into `templates/` or `static/css/main.css` until we have
looked at it here first and agreed it's worth porting.

`templates/` is the live app. This folder is the sketchpad.

## Workflow

1. Generate a screen in Stitch.
2. Export / copy its HTML into this folder, one file per screen:
   `shell-admin.html`, `ticket-list.html`, `ticket-detail.html`, `dashboard.html`, …
3. Open the file directly in Chrome — `file:///…/design-preview/ticket-list.html`.
   These are standalone pages, so no `runserver` needed.
4. To compare against the real thing, run the app in a second tab:
   `python manage.py runserver` → http://127.0.0.1:8000/

## What we're judging

Not "is it pretty". Specifically:

- Do the **7 status badges** and **4 priority badges** stay tellable apart in a
  dense table? (Pending / Assigned / Scoping / In Progress / Completed /
  Cancelled / Rejected — and Critical / High / Medium / Low.)
- Does the **data table** read well with ~15 rows on screen?
- Is the **type hierarchy** actually better than the current flat 14px?
- Are the colours portable into CSS custom properties, or does the look depend
  on effects Bootstrap 4 + a stylesheet can't reproduce?
- Do the charts look like something **Chart.js** can actually render?

## If we decide to port

The unit of porting is **design tokens**, not markup — the colour scale, type
scale, spacing scale, radii, shadows, and the badge matrix. Those go into
`static/css/main.css`. The Django templates keep their structure and mostly just
change class names.

Porting happens on a branch, one screen at a time, starting with the app shell.

## Git

The HTML in here is gitignored on purpose — we're not committing Stitch output
until we've decided to keep it. Only this README is tracked. To start tracking a
screen, `git add -f design-preview/whatever.html`.
