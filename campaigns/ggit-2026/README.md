# GGIT 2026 annual update campaign

Country-by-country gas-tracker update. Per country: an **in-dev status sweep** (deep
sweep in annual-update mode → per-row status verdicts) + a **discovery run** (new +
missing projects). Researchers rely on the packet for those two legs and research
operating pipelines themselves. Recipe: `docs/workflows.md §7`; rules:
`docs/sops/annual_update.md`.

## roster.csv

Generated + refreshed by:

```bash
python scripts/build_campaign_roster.py --tracker gas --campaign ggit-2026
```

Count columns are recomputed from the latest snapshot on every run (multi-country rows
count once per country, so `indev_total` sums above the tracker's row count). The manual
tracking columns **survive refreshes** — edit them freely:

- `priority` — batch ordering (blank = unscheduled)
- `indev_status` / `discovery_status` — blank → `running` → `delivered`
- `packet_file` — the `batches/…_annual-indev.xlsx` / `…_discovery.xlsx` stamp(s)
- `applied` — date Baird finished pasting the packet into the live Sheet
- `notes` — anything else (e.g. "chunk by province", "needs Arabic search")
