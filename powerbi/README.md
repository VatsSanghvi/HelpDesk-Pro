# powerbi/

The Power BI report, stored as a **PBIP** (Power BI Project) — plain-text JSON,
not a binary `.pbix` — so every page, visual, and theme change is a reviewable
git diff.

## Opening it

Open `Ticketing Project Power BI File.pbip` in Power BI Desktop (PBIP preview
feature required). The Django server must be running at
`http://127.0.0.1:8000` for a data refresh to succeed — see the Power BI
section in the [root README](../README.md) for the feed endpoint, the DAX
measures, and what the data showed.

## Layout

```
Ticketing Project Power BI File.pbip
├── ...Report/            # pages, visuals, theme registration
└── ...SemanticModel/     # TMDL tables, 13 DAX measures, Power Query source
```

`theme-seed-original.json` is the hand-authored palette the live theme was
built from. It isn't registered anywhere in the report — the live theme lives
inside `...Report/StaticResources/RegisteredResources/` — kept here only as a
reference for the original colour choices.
