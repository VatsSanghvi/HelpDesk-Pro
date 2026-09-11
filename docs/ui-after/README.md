# UI — after the redesign

The same seven screens as `docs/ui-before/`, captured with the identical
method and viewport (1440px) so the two sets are directly comparable.

See `docs/UI_REDESIGN.md` for what changed and why.

Regenerate with `docs/ui-before/capture_ui_screenshots.py`, then screenshot
the rendered HTML with headless Chrome at 1440x1400.

Note: the dashboard screenshot shows empty charts and "Loading..." because
these are standalone `file://` renders with no server behind them — the
KPI numbers and charts arrive from `/api/v1/analytics/dashboard/` at runtime.
The before-set has the same limitation, so the comparison still holds.
