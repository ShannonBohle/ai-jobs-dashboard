# Methods and limitations

**What this instrument measures.** (1) *Exposure*: for each detailed occupation, two independent published
estimates of how much of its task content large language models could materially accelerate - Felten's AIOE
and the Eloundou et al. beta - joined to BLS OEWS employment and wages so every score is weighted by how many
people actually hold the job. (2) *Claimed displacement*: layoff events from WARN filings and public reports,
with each event's stated cause labeled AI-attributed / not / unclear by a language-model classifier.

**What it deliberately does not claim.**
- **Exposure is not displacement.** A high beta means tasks overlap LLM capability, not that jobs are being lost.
- **Attribution is claimed cause, not true cause.** The classifier records what the filing or announcement *says*.
  Employers may over-attribute cuts to AI (cover for demand weakness) or under-attribute (avoid publicity).
- **WARN coverage is partial.** Thresholds (generally 50+ employees at larger firms), notice evasion, and state
  variation mean small and gradual cuts never appear. Challenger totals use their own methodology.
- **No causal identification.** Nothing here separates AI from macro conditions, rates, or ordinary churn.

**Measurement discipline.** The classifier is evaluated against a human-labeled gold set; Cohen's kappa,
the confusion matrix, and gold-set size are published on the dashboard itself, and every event view carries them.
Scores are point-in-time snapshots of 2021-24 vintage research; exposure estimates predate current model
capabilities and are best read as lower-bound orderings, not forecasts.

**Rate over time, and why no peak is projected.** The timeline pairs monthly WARN notice counts
(four states, archive depth varying) with Challenger, Gray & Christmas's national monthly counts of
announced job cuts citing AI as the stated reason. The AI-attribution rate is accelerating sharply in
2026, but stated-cause data cannot separate real displacement growth from attribution migrating toward
a newly acceptable public explanation; the same employers name AI to shareholders and omit it in legal
filings. No peak date is projected: fitting a saturating curve to a short, definition-shifting
announcement series yields peak estimates that move by years with each added month, and realized-
separation series (e.g., BLS JOLTS) long enough to show curvature are a future data layer, not a
present one.

**Geographic scope.** Three geographies coexist and are never merged: exposure and employment
figures are U.S.-only (BLS OEWS national). WARN events are U.S. worksite-level filings from four
states. The curated employer statements report company-wide headcounts as announced — several
explicitly global (Snap, Cloudflare, Cisco) — by U.S.-based companies, and Challenger's series
counts job cuts announced by U.S.-based employers; neither is a count of U.S. positions.

**The offset question (jobs created).** The strongest objection to any displacement count is that
AI also creates jobs. This instrument shows no creation-side ticker for a measurement reason, not an
editorial one: announced cuts have a systematic monthly stated-reason accountant (Challenger), while
announced AI-driven hiring has none — it surfaces only as scattered press releases and reassignment
memos (e.g., Meta redirecting 7,000 employees to AI initiatives, May 2026). Summing a hand-curated,
necessarily non-exhaustive additions list beside a systematic series would manufacture a false ratio.
Systematic creation-side signals are postings-based (e.g., Indeed Hiring Lab's published data on
AI-skill demand); postings measure demand, not net jobs, and are a planned layer. The disclosure
asymmetry itself — cuts itemized, additions unaggregated — is a finding of this project.

**Macro context (realized net change).** The band's third figure is BLS Current Employment
Statistics: total nonfarm payroll net change for the latest month (hires minus separations, all
causes, all industries, seasonally adjusted, preliminary and revised), with the Information
sector's change and the unemployment rate. It anchors scale and teaches the central distinction:
announced, AI-attributed cuts are not realized net losses — announcements span future dates,
attrition, and reassignment, while an economy can add jobs on net in the same months. Sectoral
net changes carry no cause attribution; Information's decline is context where AI-attributed
announcements concentrate, never a measurement of AI's effect. Hand-entered monthly from BLS
releases; API automation is a planned upgrade.

**Update cadence.** OEWS annually; WARN weekly per state scrape; Challenger monthly; exposure scores as literature updates.
