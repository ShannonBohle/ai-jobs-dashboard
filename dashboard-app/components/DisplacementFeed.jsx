"use client";
import { useState } from "react";

const S = {
  badge: { display: "inline-block", background: "#eef3ee", border: "1px solid #b9ccb9", borderRadius: 6, padding: "8px 12px", fontSize: 13, marginBottom: 12 },
  input: { padding: "7px 10px", fontSize: 14, width: 260, marginRight: 12 },
  th: { textAlign: "left", borderBottom: "2px solid #999", padding: "6px 8px", fontSize: 13 },
  td: { borderBottom: "1px solid #e2e2e2", padding: "6px 8px", fontSize: 13, verticalAlign: "top" },
  ai: { background: "#fff7e0" }
};

export default function DisplacementFeed({ events, gold }) {
  const [q, setQ] = useState("");
  const [aiOnly, setAiOnly] = useState(false);
  const ql = q.toLowerCase();
  const rows = events.filter(e =>
    (!aiOnly || e.ai_mention) &&
    (!ql || e.company.toLowerCase().includes(ql) || e.excerpt.toLowerCase().includes(ql)));
  const shown = rows.slice(0, 200);
  return (
    <div>
      <div style={S.badge}>
        Attribution classifier: {gold.judge} · Cohen&apos;s κ = <b>{gold.kappa}</b> vs human labels
        (n = {gold.n}, raw agreement {gold.agreement}). Attribution records the <i>claimed</i> cause.
      </div>
      <div style={{ marginBottom: 10 }}>
        <input style={S.input} placeholder="Search company or stated reason…" value={q} onChange={e => setQ(e.target.value)} />
        <label style={{ fontSize: 13 }}>
          <input type="checkbox" checked={aiOnly} onChange={e => setAiOnly(e.target.checked)} /> AI/automation mentions only
        </label>
        <span style={{ fontSize: 13, color: "#666", marginLeft: 14 }}>showing {shown.length} of {rows.length}</span>
      </div>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead><tr>
          <th style={S.th}>Date</th><th style={S.th}>Company</th><th style={S.th}>State</th>
          <th style={S.th}>Jobs</th><th style={S.th}>Stated reason</th>
        </tr></thead>
        <tbody>
          {shown.map((e, i) => (
            <tr key={i} style={e.ai_mention ? S.ai : undefined}>
              <td style={S.td}>{e.date}</td>
              <td style={S.td}>{e.company}</td>
              <td style={S.td}>{e.source}</td>
              <td style={S.td}>{e.jobs}</td>
              <td style={S.td}>{e.excerpt || <span style={{ color: "#999" }}>—</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
