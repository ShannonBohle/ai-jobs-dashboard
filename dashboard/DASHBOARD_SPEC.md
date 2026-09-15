# Dashboard spec (three views, one JSON contract)
Data contract: `data/processed/dashboard_data.json` -> { coverage, summary, top_exposed[], occupations[] }.
Each occupation: { soc, title, employment, median_wage, aioe, gpt_beta_model, gpt_beta_human, soc_major }.

1. **Exposure map** - scatter: x = gpt_beta_model, y = median_wage, bubble = employment, color = soc_major.
   Headline stat: emp-weighted beta ("the share of US work an LLM could speed up by >=50%, weighted by who actually holds the jobs").
2. **Displacement feed** - table/timeline from `gold/events_labeled.csv`: date, company, excerpt, model_label chip,
   kappa badge in the header ("classifier agreement with human labels: kappa = X on n = Y gold set").
3. **Occupation lookup** - search by title/SOC -> employment, wage, both exposure scores, percentile ranks, matched events.

Stack: Next.js App Router + Recharts on Vercel; serve the JSON statically from /public/data or an API route.
Footer on every view: "What this can and cannot measure" -> METHODS.md rendered.
