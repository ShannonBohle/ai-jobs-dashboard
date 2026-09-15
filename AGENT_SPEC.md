# AGENT_SPEC.md — Attribution Agent for the AI Jobs Dashboard
**Version 0.1 (specification) · 2026-09-14 · Shannon Bohle / Archivopedia LLC**
**Target: GenAI.works Open Agent Hackathon 2026 — build window Oct 15 (09:00 UTC) – Oct 20 (23:45 UTC)**
**Destination: repo root of `ai-jobs-dashboard`, beside HANDOVER.md and METHODS.md**

---

## 0 · Purpose

The dashboard's only remaining human bottleneck is finding and entering employer AI-attribution events. This weekend, each press row cost a search, a primary-source fetch, a hand-verified quote, and an `add_press_rows` entry. The agent automates everything in that loop except the judgment call:

> **Discover** AI-attribution announcements and filings → **Extract** the employer's stated words into the row schema → **Classify** with the frozen rubric-v3 judge → **Review** by a human (the only gate that can publish) → **Publish** through the existing daily Action, so the live site's dots, feed, ticker, and κ badge update themselves.

One-line pitch for judges: *an autonomous investigator that finds what employers actually say about AI and layoffs — across SEC filings, company newsrooms, and legal notices — and is structurally incapable of publishing an unverified claim.*

## 1 · Requirements

**Functional.** (1) Continuously discover candidate events from SEC EDGAR, news feeds, and company IR/newsroom feeds. (2) Auto-draft rows in the established schema: company, date, jobs, source_tag, url, stated_reason with a verbatim employer quote. (3) Deduplicate against everything already known. (4) Present drafts for human approval in a `label_gold_set`-style pass. (5) On approval, append via the `add_press_rows` logic, commit, and let the daily Action + Vercel redeploy carry the change to the live site. (6) Report κ on the growing gold set at every release.

**Non-functional.** Zero-cost default (local mistral:7b-instruct judge, free APIs, GitHub Actions free tier); polite to every upstream (SEC fair-access rules especially); graceful per-connector failure exactly like the WARN scrapers ("a failing state keeps its last committed copy"); everything reproducible from a clean clone; Windows-first dev (`python`, not `py`; UTF-8 with `errors="ignore"` everywhere — the curly-quote crash is the precedent).

**Constraints.** Solo builder; six-day window with Monday-night feature freeze (submission-timestamp tiebreak favors early); the dashboard repo is declared pre-existing scaffolding, so the agent itself must be the in-window work (see §11).

## 2 · Invariants (product requirements, not style)

These are the weekend's editorial stances, promoted to hard constraints. Any implementation that violates one is wrong even if it works.

1. **Claims-only rule.** `stated_reason` carries the employer's own words — never reporter framing. Canonical example: the Oracle row cites the company's filing language; reporter framings like "investor pressure" were rejected. Enforced twice: in the extraction prompt, and mechanically — the draft's `quote_verbatim` must appear as a substring of the fetched source text (after whitespace/curly-quote normalization) or the draft fails validation.
2. **κ-gate.** The rubric-v3 judge is advisory. A `yes` label is **never** auto-published. Every agent-produced row lands in a drafts queue; only a human approval writes to `gold/` or `events`. The judge's known failure modes are the reason the gate exists: vocabulary misses (Block "intelligence tools", Cloudflare's not-cost-cutting framing → `unclear`) and Rule-1 era-framing literalism (Cisco → `yes`, pre-registered disagreement). Approved human labels are ground truth; the judge is never "corrected" to match, and disagreements are data.
3. **Frozen rubric discipline.** The classifier prompt is rubric v3, frozen 2026-09-13, κ = 0.426 held-out (n = 14). At runtime the agent hashes the PROMPT constant and aborts if it differs from the recorded v3 hash. Any rubric change = new version number + full κ re-run on the current gold set **before** first use. (Precedent: the round-2 prompt over-correction that collapsed the judge to majority-class `no` — κ = 0.000 at 0.889 raw agreement.)
4. **Attribution records the claimed cause, never the true cause.** Wording in code comments, drafts UI, and docs must preserve this.
5. **Verified sample, not universe.** The dots are "a verified sample of the 87,714" (Challenger counts ~183 companies, publishes no list). The agent grows the sample; nothing it writes may imply completeness.
6. **Geographic passports travel with the row.** Press headcounts are often global workforce figures announced by U.S.-based companies (Snap, Cloudflare, Cisco); `geo_scope` is recorded per row and never silently merged with U.S.-only series.
7. **Stranger-reader test.** Any label, caption, or UI text the agent generates must parse cold, with no conversation context — the standard set on the ticker ("1 in 5,081 WARN Act layoff notices cite AI as the cause / (Federal law requires state filings for mass layoffs)").

## 3 · High-level design

```
 DISCOVER                    EXTRACT              CLASSIFY           REVIEW              PUBLISH
┌────────────────┐        ┌─────────────┐      ┌────────────┐    ┌─────────────┐    ┌──────────────┐
│ EDGAR full-text│───┐    │ fetch doc   │      │ rubric v3  │    │ human pass  │    │ append via   │
│ Google News RSS│───┼──▶ │ LLM → schema│ ───▶ │ judge      │──▶ │ y/n/u/edit  │──▶ │ add_press_   │
│ GDELT DOC 2.0  │───┤    │ validators  │      │ (advisory) │    │ (terminal,  │    │ rows logic → │
│ IR/newsroom RSS│───┘    │ dedupe      │      │ per-model  │    │  or /admin  │    │ git push →   │
│ (WARN: daily   │        └─────────────┘      │ cache      │    │  stretch)   │    │ daily Action │
│  Action, cross-│              │              └────────────┘    └─────────────┘    │ → Vercel →   │
│  link only)    │              ▼                                      │            │ dots/ticker/ │
└────────────────┘        rejected.jsonl ◀── validation fails          ▼            │ κ badge      │
                          (audited, never silent)              gold_set grows       └──────────────┘
                                                               (κ's n grows too)
```

New code lives in `src/agent/` (importable package, one CLI entry point). The existing pipeline is the substrate and is not forked: approved rows flow through `add_press_rows` logic and `make_web_data.py` unchanged, which is why publication needs **zero new frontend code** — the confirmed-marker layer, feed, and badge already regenerate from `gold_set_labeled.csv` and `events.csv`.

**Two update paths, kept distinct (do not double-build):** filings that literally name AI already auto-plot via the regex layer with no human touch (a second Nespresso appears the morning after it is filed). The agent covers the *press-verified* layer, whose value is precisely the human verification.

**Module layout.**
```
src/agent/
  run.py            # CLI: --once | --discover-only | --review | --mock
  connectors/
    edgar.py        # EDGAR full-text search
    news.py         # Google News RSS + GDELT
    ir_feeds.py     # watchlist company newsroom/IR RSS
    warn_xlink.py   # cross-link pass against gold/events.csv
  extract.py        # fetch + LLM extraction + validators
  dedupe.py
  queue.py          # drafts.jsonl / rejected.jsonl I/O
  review_drafts.py  # terminal approval pass
  publish.py        # imports append fn refactored out of add_press_rows.py
  state.py          # cursors.json, watchlist.csv
data/agent/
  cursors.json      # per-source watermarks (committed; small)
  watchlist.csv     # company, ir_feed_url, feed_type, added_date
  drafts.jsonl      # the queue (committed by the discover workflow)
  rejected.jsonl    # audit trail with rejection reasons
```

**Prerequisite #0:** the repo exists on GitHub with the Vercel import done (handover queue item 1). The agent publishes by committing; without the repo there is no publish surface.

## 4 · Discovery connectors

Each connector is independent; one failing degrades gracefully and logs, mirroring `ingest_warn.py`'s `continue-on-error` behavior.

**4a. SEC EDGAR full-text search** (highest signal density — filings *are* primary sources, so discovery and source are the same document). Query family: `"artificial intelligence"` co-occurring with workforce terms (`"reduction in force"`, `"workforce reduction"`, `restructuring`, `layoff`, `severance`), restricted to forms 8-K, 10-K, 10-Q. API: the EDGAR full-text search service at `efts.sec.gov` (UI at sec.gov/edgar/search); exact parameter names verified in-window, not assumed. Compliance is non-negotiable: declared `User-Agent` including a real contact email (SEC requires it), well under 10 requests/second, exponential backoff on 429/503. Cursor: `filedAt` watermark plus a set of seen accession numbers. The hit's actual filing document is fetched for extraction.

**4b. News (leads only).** Google News RSS query URLs — per-watchlist-company (`"<company>" layoffs`) and generic (`layoffs "artificial intelligence"`) — plus the GDELT DOC 2.0 API as a broad free recall net (params confirmed at build time). **A news article is never a source; it is a pointer.** The extractor must reach the primary document (filing, letter, blog post) or, failing that, an employer-voice quote attributed in the article; a lead with no employer-voice text routes to a `needs-source` bucket, not to drafts. Precedent: the Cloudflare row was built from the founders' letter itself, not the Reuters summary of it.

**4c. IR / newsroom RSS.** `watchlist.csv` rows polled with conditional GETs (ETag / Last-Modified). Seeds: the five verified companies' newsrooms and investor pages (Cloudflare blog, Cisco blogs, Snap investor news, Block shareholder letters, Oracle press), extended with major employers recurrent in Challenger coverage. Founders'-letter-style posts (the Cloudflare pattern) are the target class.

**4d. WARN cross-link (no new scraping).** The daily Action already refreshes WARN. The agent adds only a pass that matches drafts and gold rows on `(normalized_company, month)` against `events.csv` and attaches a `warn_ref` for provenance enrichment — one event, two disclosure regimes, documented on the row.

## 5 · Extraction

Fetch (requests + a readability extractor for HTML; EDGAR documents as filed), then an LLM pass producing **strict JSON** validated by a pydantic model (`allow_nan=False` end to end — the NaN-serialization failure is the precedent).

**Draft record schema:**

| field | type | rule |
|---|---|---|
| company | str | as stated by the employer |
| event_date | `YYYY-MM-DD` or `YYYY-MM` | the layoff/announcement's own date |
| announced_date | `YYYY-MM-DD` | when the source document is dated |
| jobs_affected | int \| null | as stated; "more than 1,100" → `1100` + `jobs_qualifier=">"`; never invented |
| jobs_qualifier | `=`, `>`, `~`, null | preserves "more than / about" |
| source_tag | enum | `press-sec`, `press-filing`, `press-shareholder-letter`, `press-blog`, `press-earnings`, `press-release` |
| url | str | the primary document |
| doc_type | str | e.g. "8-K", "founders' letter", "CEO blog post" |
| stated_reason | str ≤ ~50 words | employer voice, containing one direct quote |
| quote_verbatim | str | exact substring of the source text |
| geo_scope | `global` \| `us` \| `unstated` | invariant 6 |
| warn_ref | str \| null | cross-link id when found |
| judge_label / judge_rationale | attached after §6 | advisory only |
| discovered_via / discovered_at | provenance | connector + timestamp |

**Mechanical validators (run before anything queues; failures go to `rejected.jsonl` with a reason — nothing is silently dropped):**
1. `quote_verbatim` is a substring of the normalized source text (whitespace collapsed, curly quotes straightened). This is the claims-only rule made mechanical.
2. Placeholder-contamination check: reject drafts containing template artifacts (`your-key`, `lorem`, `N/A`, `TBD`, empty company). Precedents: the literal `your-key` env variable incident; the blank-company gold row that became a known judge leak.
3. Date sanity: within 2015 → today + 18 months (NY-style future-dated notices allowed, flagged).
4. `jobs_affected` numeric or null; no unit words, no ranges collapsed without a qualifier.
5. Strict-JSON round trip (`parse_constant` trap for `NaN`/`Infinity`), the same test that diagnosed the dashboard bug.

## 6 · Classification

`classify_ai_attribution.py` is reused as-is: rubric v3, per-model caches keyed on row id, `--ollama mistral:7b-instruct` default, Anthropic API optional for cloud runs, `--mock` for CI. The label and ≤25-word rationale attach to the draft as a **suggestion** displayed at review. Runtime guard per invariant 3: sha256 of the PROMPT constant checked against the recorded v3 hash before any batch; mismatch aborts with "rubric changed — bump the version and re-run κ on the gold set before use."

## 7 · Review — the human gate

**v0 (ship this): `python src/agent/run.py --review`** — a `label_gold_set.py`-style terminal pass over `drafts.jsonl`. Per draft it shows company, date, jobs (+qualifier), source_tag, doc_type, the verbatim quote in context, and the judge's suggestion; keys: `y` / `n` / `u` / `e`(dit fields) / `o`(pen url) / `s`(kip) / `q`(uit). Approval calls the append function refactored out of `add_press_rows.py` (import, don't shell out): assigns the next `pNN` id, writes the row to `gold/gold_set.csv` **and** `gold_set_labeled.csv` with the human label, and to the events layer for the feed. Consequence worth advertising: **every approval grows the gold set, so κ's n grows with routine use** — the eval story compounds instead of staying frozen at n = 14.

**Stretch (demo polish): a local-only `/admin` queue** — a page in `dashboard-app` reading `drafts.json` with Approve/Reject buttons writing through a local API route. Never deployed (excluded from the Vercel build or env-gated); the terminal pass remains canonical. Build only if Days 1–4 run ahead of schedule.

## 8 · Publish

Approved rows → `git commit` → `git push` → the existing **Daily data update** Action (or a light on-approve `workflow_dispatch`) → `make_web_data.py` regenerates `timeline.confirmed`, `gold`, and `events` → Vercel redeploys → the new named dot, feed rows, and updated κ badge appear. This is the demo's money shot (§10): approve one draft in the terminal, push, and watch the live site change.

## 9 · Dedupe (before queueing)

1. Exact URL against `events.csv`, `gold_set.csv`, `drafts.jsonl`, and `rejected.jsonl`.
2. `(normalized_company, month)` key — lowercase, punctuation stripped, corporate suffixes removed (Inc, Corp, LLC, Ltd, plc).
3. Fuzzy company match: rapidfuzz `token_sort_ratio ≥ 90` against all known companies (catches "Cloudflare, Inc." vs "Cloudflare").
4. **Supersession, not duplication:** a newer *primary* source for an existing event (filing > shareholder letter > blog > press release) creates an UPDATE draft; on approval, the row's source upgrades and a provenance note records what it superseded. Superseded provenance is retained, never deleted.

## 10 · Eval, monitoring, and release discipline

- **κ on every release**, computed on the full current gold set, always reported with n ("κ = 0.426, n = 14" grows to "κ = …, n = 23" as approvals land).
- **Optional judge sweep** across installed models (mistral:7b-instruct, mistral:latest, llama3.2:3b) — per-model caches already isolate runs; output is a one-table "same rubric, different judge" exhibit.
- **Scraper-drift monitor:** per-connector candidate counts vs. a trailing 7-day mean; a >50% drop or a source-page schema-hash change logs a warning in the Action run. Precedents: WARN column-name drift across states, and Illinois's archive silently ending in July 2022.
- **Failure-modes writeup** (mandatory under rule 6.3, and the bonus engine — up to 30 points for open-sourcing + evals + documented failure modes): ships with the κ arc figure (0.031 hedger → 0.000 rubber stamp at 0.889 raw → 0.438 dev → 0.426 held-out), the four weekend failure IDs (silent NaN serialization; prompt over-correction → majority-class collapse; scraper drift; placeholder contamination of an eval set), plus whatever the agent build adds.

## 11 · Hackathon packaging and rule compliance

- **Rule 4.2 / 5.2 strategy:** the dashboard repo (pipeline, site, rubric v3, gold set, daily Action) is **declared pre-existing scaffolding**. To keep the judged contribution clean and large, the agent code itself (`src/agent/`, review flow, discover workflow, admin stretch) is written **inside the window**. This spec, the schema, and the watchlist seeds are prep and get declared. If external customization requests arrive before Oct 15, implement them in the *dashboard* (scaffolding side), not the agent — they strengthen the declared base without shrinking the in-window build.
- **Track:** 02 Autonomous Investigation or 06 Connected Data Agents — rule 3.2 allows switching until submission, so decide at the end. Impact framing (30 pts + tiebreaker): real work for real users — the instrument's maintainer, and journalists who need employer claims verified against primary documents.
- **Deliverables (rule 6):** public repo ✓; running deployment = the live Vercel site **plus** a Dockerfile / one-command run for the agent (`docker run … --once --mock` must work for judges with no keys); demo video ≤ 3 min = the approve-to-live loop; failure-modes writeup per §10.
- **Timing:** feature-freeze Monday night Oct 19 (EDT); submit early Tuesday at the latest — ties break on Impact, then submission timestamp.

## 12 · Configuration and operations

- **Secrets / env:** `SEC_USER_AGENT` (with a real contact email), optional `ANTHROPIC_API_KEY` for cloud judging. Local mistral default keeps marginal cost at $0 and matches the documented local-model choice.
- **Workflow:** new `agent-discover.yml`, daily 10:00 UTC (after the 09:17 data run), running discover → extract → classify and committing **`drafts.jsonl` only**. Publishing stays human-triggered, from the machine where review happens.
- **Rate limits:** SEC per fair-access policy; GDELT courteous polling; RSS via conditional GETs. All fetches time-boxed with retries + jitter.
- **Optional (S2, low priority):** monthly draft rows for `challenger_ai_monthly.csv` and `macro_context.csv` from the Challenger and BLS releases — currently a two-minute hand task per month, so automate last if at all.

## 13 · Build order (in-window)

| Day | Deliverable |
|---|---|
| 1 (Thu Oct 15) | Refactor `add_press_rows.py` → importable `append_row()` + CLI wrapper; pydantic schema + validators; `queue.py`; Dockerfile skeleton |
| 2 | EDGAR connector end-to-end with `--mock` judge; first real drafts in the queue |
| 3 | Extractor + verbatim-quote validator hardened; `review_drafts.py`; **first full approve → push → live-site update** |
| 4 | News RSS + GDELT + IR watchlist connectors; dedupe layer; `rejected.jsonl` audit complete |
| 5 (Sat/Sun) | Drift monitor; κ report + optional judge sweep; `/admin` stretch only if ahead |
| 6 (Mon Oct 19) | Freeze; failure-modes writeup; 3-min video; submission draft |

**Acceptance test for v0.1:** from a clean clone, `python -m src.agent.run --once` discovers ≥ 1 real EDGAR candidate, drafts it with a validated verbatim quote, `--review` approves it, the push triggers the Action, and the named dot appears on the live site.

## 14 · Trade-offs made explicit

- **Terminal review vs. web queue:** terminal ships in hours and reuses a proven interaction pattern; the web queue is nicer on camera but adds an auth/deployment surface. Decision: terminal canonical, web stretch.
- **Local judge vs. cloud:** mistral:7b-instruct is free, private, and already calibrated (κ = 0.426 is *its* number); a larger cloud model would likely score higher but would need its own κ run and a paid key in CI. Decision: local default, cloud optional behind the same cache interface.
- **Drafts committed to the repo vs. kept local:** committing makes the queue visible, auditable, and demo-able (judges can watch drafts arrive), at the cost of public visibility of unreviewed candidates. Decision: commit, with a README note that drafts are unverified by definition.
- **News as leads-only:** costs recall (some events have no reachable primary text) but is what keeps the claims-only rule honest. Decision: recall is sacrificed knowingly; the `needs-source` bucket preserves the leads.

## 15 · Revisit as it grows

The gold set outgrowing a single CSV (move to per-year files past a few hundred rows); rubric v4 once disagreement patterns justify distinguishing "AI named as cause" from "AI-era framing" (the Cisco class) — with the mandatory version bump + κ re-run; a second human labeler for a true inter-annotator κ; the adoption layer (Census BTOS, Anthropic Economic Index, Indeed Hiring Lab postings, JOLTS) as the paper's roadmap already states; and Challenger licensing or a media-request pipeline if the project earns a newsroom home.

---
*Companion documents: HANDOVER.md (state + queue), METHODS.md (measurement discipline the agent must not violate).*
