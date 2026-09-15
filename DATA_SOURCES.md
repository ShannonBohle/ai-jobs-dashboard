# Data sources (verified 12 Sep 2026)

| Source | What | Where | License / terms | Status |
|---|---|---|---|---|
| Felten, Raj & Seamans AIOE | AI Occupational Exposure score per SOC (plus Language-Modeling and Image-Generation variants in same repo) | github.com/AIOE-Data/AIOE -> `AIOE_DataAppendix.xlsx` (Appendix A) | Free to use with citation: Felten, Raj & Seamans, *Strategic Management Journal* 42(12), 2021, doi 10.1002/smj.3286 | **Bundled** in data/raw |
| Eloundou et al. "GPTs are GPTs" | Occupation-level LLM exposure (alpha/beta/gamma, GPT-4 and human ratings), O*NET-SOC keyed | github.com/openai/GPTs-are-GPTs -> `data/occ_level.csv` | MIT (c) 2024 OpenAI. Cite: Eloundou, Manning, Mishkin & Rock, *Science* 384:1306-1308 (2024) | **Bundled** in data/raw |
| BLS OEWS | Employment + median wage per detailed SOC | Dev copy bundled (May 2021 national, from the OpenAI repo). Production: bls.gov/oes/tables.htm -> latest "National" XLSX/CSV | US public domain | Bundled (2021); swap in May 2025 file Saturday |
| WARN Act notices | Layoff events, state-by-state | `pip install warn-scraper` (Big Local News / Stanford; verified v1.2.143 on PyPI) or bulk archive at biglocalnews.org, free account | Public records; attribute Big Local News | Script ready (`src/ingest_warn.py`) |
| Challenger, Gray & Christmas | Monthly job-cut totals incl. AI-attributed category | challengergray.com press releases | Quote figures with attribution; no bulk redistribution | Manual: add monthly rows to gold/events or a totals CSV |
| layoffs.fyi | Crowdsourced tech layoffs tracker | layoffs.fyi (Airtable) | Personal-use viewing; do not scrape/redistribute - cite figures manually | Secondary/manual only |
| Census BTOS AI questions; Anthropic Economic Index | Adoption-side signals for the phase-2 "index of indices" | census.gov/hfp/btos ; huggingface.co/datasets/Anthropic/EconomicIndex | Public / open | Phase 2 pointers |

Crosswalk note: O*NET-SOC (`11-1011.00`) truncates to SOC (`11-1011`); `occupations_onet_bls_matched.csv` (bundled) covers edge cases.
