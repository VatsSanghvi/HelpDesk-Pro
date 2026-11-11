---
version: 1
slug: "templates-base-html"
primary_target: "templates/base.html"
related_targets: ["static/css/main.css","templates/registration/home.html"]
---

# App shell and screens

Scope: every authenticated screen of the Django app plus sign-in and password
pages. Visitor mode: Operate. Power BI report is out of scope.

Audience and job: the IT lead triages and watches SLA health; agents work
their assigned tickets; employees raise and follow tickets. The owner wants a
buyer watching a demo to think "this team is in control" and "my staff could
use this today".

Constraints confirmed by the owner: screens and navigation may be rearranged;
every existing feature keeps working; labels and role names stay as they are.
It must not look like a stock admin template, be playful, need training, or
resemble Zendesk or Jira. The owner chose the green triage direction and asked
for navigation in a top bar instead of a side rail.

Unresolved: pricing model and hosted versus self-hosted delivery.

## Direction contract

THESIS: An emergency-department board for IT tickets. Priority is a triage
category and every open ticket carries a visible clock against its SLA. It
refuses the category default of dark sidebar, white KPI cards and icon tiles.

OWN-WORLD: A theatre-green room, pale green band and tints, so that red is
unmissable. White chart-paper surfaces with green-grey hairlines. Deep green
actions. Triage scale: red 1 High, amber 2 Moderate, green 3 Low, dashed for
Untriaged, always as a numbered square. Atkinson Hyperlegible Next for every
voice. The signature is the waiting clock: a banded track (clear, amber, red
zones) with an ink marker showing how much of the SLA window is used.

STORY: The IT lead reads one sentence saying what is late and what is waiting
for triage, then acts from the same screen. An employee sees where their
ticket stands without training.

FIRST VIEWPORT: Pale green top band holding brand, navigation, the Raise
ticket button, notifications and the user menu. Below it a sentence headline
with the late and untriaged counts. Left two thirds: open tickets, most urgent
first, as a table of priority square, ticket, owner and waiting clock. Right
third: Waiting for triage with its primary action, then Team workload. A
figures row closes the viewport. Signature interaction: each waiting clock's
marker travels to its position once on load, and the track explains its due
time and window on hover and focus.

FORM: Triage board, candidate 3 of 7 on the ordered list, steered by the owner
to top navigation. seed:954946ff7dc50c67

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
