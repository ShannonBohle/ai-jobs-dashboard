"use client";
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ExposureScatter({ data }) {
  const pts = data.occupations.filter(o => o.gpt_beta_model != null && o.median_wage != null && o.employment != null);
  return (
    <ResponsiveContainer width="100%" height={440}>
      <ScatterChart margin={{ top: 12, right: 24, bottom: 34, left: 12 }}>
        <XAxis dataKey="gpt_beta_model" name="LLM exposure" type="number" domain={[0, 1]}
               label={{ value: "LLM exposure (Eloundou β, model-rated)", position: "bottom", offset: 18 }} />
        <YAxis dataKey="median_wage" name="Median wage" type="number"
               tickFormatter={v => `$${Math.round(v / 1000)}k`} width={64} />
        <ZAxis dataKey="employment" range={[16, 380]} name="Employment" />
        <Tooltip content={({ payload }) => payload && payload[0] ? (
          <div style={{ background: "#fff", border: "1px solid #ccc", padding: 8, fontSize: 13 }}>
            <b>{payload[0].payload.title}</b><br />
            employment {payload[0].payload.employment.toLocaleString()}<br />
            β {payload[0].payload.gpt_beta_model} · AIOE {payload[0].payload.aioe ?? "–"} · median ${payload[0].payload.median_wage.toLocaleString()}
          </div>) : null} />
        <Scatter data={pts} fill="#4a6b8a" fillOpacity={0.5} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
