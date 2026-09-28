# /brag plan: HelpDesk Pro (v2, production rebuild)

**Cut:** 30.6s · 1920×1080 · 30fps · H.264 + stereo AAC (-14 LUFS target). Scene changes sit on a 100 BPM grid (beat = 0.6s).

**Story:** problem → ticket workflow → SLA control → operational visibility → Power BI stakeholder analytics → technical architecture → capabilities → one real insight → brand.

**Direction:** premium internal-SaaS product film. Dark navy + teal (the app's own tokens), Inter / JetBrains Mono, restrained motion (ease-out / ease-in-out, no elastic), and 2–5% micro-scale on holds. Hard cuts, match cuts, pushes and card stacks replace cross-fades. The only cursor is the one meaningful click (Submit). The real UI is the evidence throughout.

## Shot list

| Time | Scene | On screen | Copy | Transition in |
|---|---|---|---|---|
| 0.0–1.2 | Cold open | 4 micro-shots, 0.3s each, cut on 8th notes: Power BI Overview → dashboard KPIs → SLA badges → new-ticket toast | HelpDesk Pro / *IT support, connected.* | Frame 0 is the poster (settled, no flash frame) |
| 1.2–4.2 | Ticket | Real create form (Viewer); title and description typed from 32 captures; Submit click | *Something broke? Raise a ticket.* | Hard cut |
| 4.2–7.2 | Logged | Success toast + new TKT000032 row highlighted | *Logged instantly.* + Role-based · Audited · Notified | Hard cut (page navigation) |
| 7.2–10.2 | SLA | Admin ticket list → push into the SLA State column, spotlight | *Every ticket gets an SLA clock.* + High 4h · Moderate 24h · Low 72h (app's own priority chips) | Zoom match |
| 10.2–13.2 | Dashboard | KPI tiles stagger in, then chart rows; callout ring on 24.3h avg resolution | *Live visibility for the support team.* | Push |
| 13.2–18.0 | Power BI | All 4 pages, 1.2s each, match cuts on the shared page skeleton | *From tickets to decisions.* + stepper: Overview (volume & priority), SLA & Aging (breaches & age), Category Deep-Dive (root causes), Agent Workload (team capacity) | Hard cut on the beat |
| 18.0–21.0 | Architecture | Window shrinks into node 04: Django → REST API → Power Query → Power BI, with beat-synced pulses | `/api/v1/powerbi/tickets/`, `Json.Document(Web.Contents…)`, 4 pages · 13 DAX measures / *Flat JSON feed · key-authenticated · refreshed by Power BI* | Match push |
| 21.0–24.0 | Capabilities | 4 cards from real UI crops: role badges, Activity log, email/WhatsApp notice, CSV/Excel buttons | *Built for real operations.* | Card stack (after a clean dip) |
| 24.0–27.0 | Insight | Count-up to 62.5% beside the SLA & Aging page; ring on the KPI cards, then spotlight on the Breached Tickets table | *62.5% SLA compliance. 12 of 32 tickets breached their SLA.* | Push |
| 27.0–30.6 | End card | Logo lockup, 2% drift; music resolves on F underneath | HelpDesk Pro · Django · REST API · Power BI · SLA Tracking · github.com/VatsSanghvi/HelpDesk-Pro | Out, then in |

## Honesty rules applied
- Every number is real: 62.5% / 12 of 32 come from the Power BI feed using the semantic model's DAX logic, 24.3h appears in both the app and the report, and the 4h/24h/72h SLA rules come from settings.
- The empty First-Response / CSAT row is left out of the dashboard shot (the seed data has no values), rather than shown as if it were a result.
- Power BI Desktop can't run on Linux, so the report pages are redrawn from the PBIP visual definitions and registered theme, using the same feed Power BI refreshes from. Fonts are slightly enlarged for readability.
- Capability claims match the code and README: RBAC roles, audit trail on status changes, Gmail SMTP + Twilio alerts, one-click CSV/Excel export with filters.

## Sound
100 BPM in F major: stabs on each cold-open cut → airy half-time groove → lift at Power BI → breakdown under the insight → resolves on Fmaj9 under the end card. One UI click (Submit) and soft whooshes on the major transitions only. No booms.
