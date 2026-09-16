"use client";
import { useEffect, useState } from "react";
import ExposureScatter from "../components/ExposureScatter";
import DisplacementFeed from "../components/DisplacementFeed";
import OccupationLookup from "../components/OccupationLookup";
import AttributionTimeline from "../components/AttributionTimeline";
import Ticker from "../components/Ticker";

const S = {
  wrap: { maxWidth: 1080, margin: "0 auto", padding: "28px 20px 60px", fontFamily: "Georgia, 'Times New Roman', serif", color: "#1a1a1a" },
  h1: { fontSize: 34, margin: "0 0 6px" },
  sub: { color: "#555", margin: "0 0 26px", fontSize: 16, lineHeight: 1.5 },
  stat: { display: "inline-block", marginRight: 28, marginBottom: 8 },
  statN: { fontSize: 26, fontWeight: 700 },
  statL: { fontSize: 13, color: "#666" },
  h2: { fontSize: 22, borderBottom: "1px solid #ccc", paddingBottom: 6, margin: "40px 0 12px" },
  note: { fontSize: 13, color: "#666", lineHeight: 1.5 },
  pre: { whiteSpace: "pre-wrap", fontSize: 13, background: "#f7f6f3", padding: 16, borderRadius: 6, lineHeight: 1.55 }
};

export default function Page() {
  const [dash, setDash] = useState(null);
  const [events, setEvents] = useState(null);
  const [gold, setGold] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [methods, setMethods] = useState("");

  useEffect(() => {
    fetch("/data/dashboard_data.json").then(r => r.json()).then(setDash);
    fetch("/data/events.json").then(r => r.json()).then(setEvents);
    fetch("/data/gold.json").then(r => r.json()).then(setGold);
    fetch("/data/timeline.json").then(r => r.json()).then(setTimeline).catch(() => setTimeline({ warn_monthly: [], challenger: [], retrieved: "" }));
    fetch("/data/methods.txt").then(r => r.text()).then(setMethods);
  }, []);

  if (!dash) return <main style={S.wrap}><p>Loading data…</p></main>;
  const c = dash.coverage, s = dash.summary;

  return (
    <main style={S.wrap}>
      <Ticker timeline={timeline} events={events} />
      <p style={{ ...S.note, marginTop: -14, marginBottom: 22, fontStyle: "italic" }}>
        Jobs <i>added</i> by AI? No symmetric tracker exists &mdash; the asymmetry is itself a finding (see methods).
      </p>
      <h1 style={S.h1}>AI Jobs Dashboard</h1>
      <p style={S.sub}>
        What can be measured about AI and U.S. jobs right now: published occupation-level
        exposure estimates weighted by real employment, and layoff filings with a
        calibrated reading of what employers actually claim. Exposure is not displacement;
        attribution records the claimed cause. See methods below.
      </p>
      <div>
        <span style={S.stat}><div style={S.statN}>{(c.employment_covered / 1e6).toFixed(1)}M</div><div style={S.statL}>jobs covered (of {(c.employment_total / 1e6).toFixed(1)}M)</div></span>
        <span style={S.stat}><div style={S.statN}>{s.emp_weighted_gpt_beta_model.toFixed(3)}</div><div style={S.statL}>employment-weighted LLM exposure (Eloundou β, model-rated)</div></span>
        <span style={S.stat}><div style={S.statN}>{s.aioe_gpt_spearman.toFixed(3)}</div><div style={S.statL}>Spearman, AIOE vs β (cross-measure check)</div></span>
        <span style={S.stat}><div style={S.statN}>{c.occupations_with_both_scores}</div><div style={S.statL}>occupations with both exposure scores</div></span>
      </div>

      <h2 style={S.h2}>1 · Exposure map</h2>
      <p style={S.note}>Each bubble is a detailed occupation (BLS OEWS, May 2025): LLM exposure (Eloundou et al., <i>Science</i> 2024) vs. median wage, sized by employment; hover for the Felten AIOE second measure.</p>
      <ExposureScatter data={dash} />

      <h2 style={S.h2}>2 · Displacement over time</h2>
      <p style={S.note}>
        Two different measures share this chart. <b>Gray bars</b>: every WARN layoff notice filed each month in four
        states, whatever the cause &mdash; the background rate of mass layoffs (the 2020 spike is the pandemic).
        <b> Red dots</b>: individual companies whose layoffs we verified as AI-attributed in primary documents &mdash; a verified sample of the 87,714 above (Challenger counts ~183 companies but publishes no list), placed by announced headcount. Almost none of these appear as AI in WARN filings
        (1 in 5,083, above). Blaming AI is rising fast in 2026; whether layoffs themselves are is a
        different question, and no peak is projected &mdash; see methods.
      </p>
      {timeline ? <AttributionTimeline timeline={timeline} /> : <p>Loading timeline…</p>}

      <h2 style={S.h2}>3 · Displacement feed</h2>
      <p style={S.note}>
        Scope: WARN events are U.S. worksite filings from four states' official archives (14,183 notices; 5,083 include a stated reason — Texas and Washington's archives omit that field). The curated employer
        statements (source tags beginning "press-") report company-wide headcounts as announced — several explicitly
        global — by U.S.-based companies; those figures are not U.S.-only job counts.
      </p>
      {events && gold ? <DisplacementFeed events={events} gold={gold} /> : <p>Loading events…</p>}

      <h2 style={S.h2}>4 · Occupation lookup</h2>
      {dash ? <OccupationLookup occupations={dash.occupations} /> : null}

      <h2 style={S.h2}>What this can and cannot measure</h2>
      <pre style={S.pre}>{methods}</pre>
    </main>
  );
}
