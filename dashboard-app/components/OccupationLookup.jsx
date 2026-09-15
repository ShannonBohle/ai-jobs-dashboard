"use client";
import { useMemo, useState } from "react";

const S = {
  input: { padding: "7px 10px", fontSize: 14, width: 320, marginBottom: 10 },
  th: { textAlign: "left", borderBottom: "2px solid #999", padding: "6px 8px", fontSize: 13 },
  td: { borderBottom: "1px solid #e2e2e2", padding: "6px 8px", fontSize: 13 }
};

export default function OccupationLookup({ occupations }) {
  const [q, setQ] = useState("");
  const scored = useMemo(() => {
    const withBeta = occupations.filter(o => o.gpt_beta_model != null);
    const sorted = [...withBeta].sort((a, b) => b.gpt_beta_model - a.gpt_beta_model);
    const rank = new Map(sorted.map((o, i) => [o.soc, Math.round(100 * (1 - i / (sorted.length - 1)))]));
    return { rank, n: sorted.length };
  }, [occupations]);
  const ql = q.toLowerCase();
  const rows = ql
    ? occupations.filter(o => (o.title || "").toLowerCase().includes(ql) || (o.soc || "").includes(ql)).slice(0, 15)
    : [];
  return (
    <div>
      <input style={S.input} placeholder="Type an occupation title or SOC code…" value={q} onChange={e => setQ(e.target.value)} />
      {ql && rows.length === 0 && <p style={{ fontSize: 13, color: "#666" }}>No matches.</p>}
      {rows.length > 0 && (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead><tr>
            <th style={S.th}>Occupation</th><th style={S.th}>SOC</th><th style={S.th}>Employment</th>
            <th style={S.th}>Median wage</th><th style={S.th}>β (LLM)</th><th style={S.th}>AIOE</th><th style={S.th}>Exposure percentile</th>
          </tr></thead>
          <tbody>
            {rows.map(o => (
              <tr key={o.soc}>
                <td style={S.td}>{o.title}</td>
                <td style={S.td}>{o.soc}</td>
                <td style={S.td}>{o.employment != null ? o.employment.toLocaleString() : "–"}</td>
                <td style={S.td}>{o.median_wage != null ? `$${o.median_wage.toLocaleString()}` : "–"}</td>
                <td style={S.td}>{o.gpt_beta_model ?? "–"}</td>
                <td style={S.td}>{o.aioe ?? "–"}</td>
                <td style={S.td}>{scored.rank.has(o.soc) ? `${scored.rank.get(o.soc)}th` : "–"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
