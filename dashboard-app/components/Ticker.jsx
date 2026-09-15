"use client";
import { useEffect, useState } from "react";

function useCountUp(target, ms = 1800) {
  const [v, setV] = useState(0);
  useEffect(() => {
    if (!target) return;
    let raf; const t0 = performance.now();
    const step = t => {
      const p = Math.min(1, (t - t0) / ms), e = 1 - (1 - p) * (1 - p);
      setV(Math.round(target * e));
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, ms]);
  return v;
}

const S = {
  band: { background: "#122437", color: "#fff", borderRadius: 8, padding: "18px 22px", margin: "0 0 26px",
          display: "flex", flexWrap: "wrap", gap: "18px 40px", alignItems: "baseline", justifyContent: "space-between" },
  big: { fontSize: 52, fontWeight: 700, fontVariantNumeric: "tabular-nums", lineHeight: 1 },
  label: { fontSize: 13, color: "#c9d6e2", maxWidth: 300, lineHeight: 1.4, marginTop: 8 },
  src: { fontSize: 11, color: "#8fa3b5", marginTop: 4 }
};

export default function Ticker({ timeline, events }) {
  const t = timeline?.ticker;
  const n = useCountUp(t?.value || 0);
  const withReason = events ? events.filter(e => e.excerpt).length : null;
  const aiNamed = events ? events.filter(e => e.ai_mention).length : null;
  if (!t) return null;
  return (
    <div style={S.band}>
      <div>
        <div style={S.big}>{n.toLocaleString()}</div>
        <div style={S.label}>announced U.S. cuts <b>citing AI</b>, Jan&ndash;May 2026</div>
        <div style={S.src}>Challenger &middot; announcements; some counts global</div>
      </div>
      {timeline?.macro && (
        <div>
          <div style={S.big}>{timeline.macro.total_change > 0 ? "+" : ""}{timeline.macro.total_change.toLocaleString()}</div>
          <div style={S.label}>net U.S. payroll change, {new Date(timeline.macro.month + "-15").toLocaleString("en-US", { month: "short", year: "numeric" })} &mdash; <b>all causes</b></div>
          <div style={S.src}>BLS &middot; Information {timeline.macro.info_change > 0 ? "+" : ""}{timeline.macro.info_change?.toLocaleString()} &middot; unemployment {timeline.macro.unemp_rate}%</div>
        </div>
      )}
      {withReason != null && (
        <div>
          <div style={S.big}>{aiNamed.toLocaleString()} <span style={{ fontSize: 20, fontWeight: 400 }}>in {withReason.toLocaleString()}</span></div>
          <div style={S.label}>WARN Act layoff notices <b>cite AI as the cause</b></div>
          <div style={S.src}>(Federal law requires state filings for mass layoffs)</div>
        </div>
      )}
    </div>
  );
}
