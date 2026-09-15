# AI Jobs Dashboard - weekend starter kit
A v0 of the instrument Mat Honan's "The era of AI malaise" asks for: public, occupation-level AI exposure
weighted by real employment, plus a measured (not vibes) feed of AI-attributed layoff events.

## Already done for you (verified 12 Sep 2026)
- Primary exposure datasets **bundled**: Felten AIOE + Eloundou occ-level beta (see DATA_SOURCES.md, ATTRIBUTION in data/raw)
- OEWS dev copy bundled; the join **runs end-to-end now**: `python src/build_dataset.py`
- Classifier + Cohen's-kappa harness ready; full chain plumbing-tested offline via `--mock` (try: `python src/classify_ai_attribution.py gold/events_demo.csv --mock` then `python src/eval_kappa.py gold/events_demo_labeled.csv`)
- WARN ingestion via Big Local News scraper (`src/ingest_warn.py oh ny ca`)
- Dashboard contract + spec + sample Recharts component in `dashboard/`

## Saturday
1. `pip install -r requirements.txt`
2. Swap OEWS vintage: download latest National file from bls.gov/oes/tables.htm, run `python src/build_dataset.py --oews <file>`
3. `python src/ingest_warn.py oh ny ca tx` (start with a few states) -> `gold/events.csv`
4. Hand-label 30-60 events (`human_label`: yes/no/unclear) - this is the gold set
5. `ANTHROPIC_API_KEY=... python src/classify_ai_attribution.py gold/events.csv`
6. `python src/eval_kappa.py gold/events_labeled.csv` -> the kappa you publish

## Sunday
7. `npx create-next-app@latest dashboard-app`; copy `dashboard/ExposureScatter.jsx`; build the three views per DASHBOARD_SPEC.md
8. Put `dashboard_data.json` + labeled events in `public/data/`; render METHODS.md as the footer page
9. Deploy to Vercel; sanity-pass every number against the CSVs; add Challenger's latest monthly figure manually
10. Screenshot + 3-sentence description for the Monday email

## Monday
Send Honan the single email with the live URL. This repo also becomes declared pre-existing scaffolding
for the Open Agent Hackathon (Track 06 shape) - keep the git history clean from day one.
