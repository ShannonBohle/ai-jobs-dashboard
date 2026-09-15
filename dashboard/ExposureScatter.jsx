"use client";
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ExposureScatter({ data }) {
  const pts = data.occupations.filter(o => o.gpt_beta_model != null && o.median_wage != null);
  return (
    <ResponsiveContainer width="100%" height={440}>
      <ScatterChart margin={{ top: 12, right: 24, bottom: 28, left: 8 }}>
        <XAxis dataKey="gpt_beta_model" name="LLM exposure (beta)" type="number" domain={[0, 1]}
               label={{ value: "LLM exposure (Eloundou beta)", position: "bottom" }} />
        <YAxis dataKey="median_wage" name="Median wage" type="number"
               tickFormatter={v => `$${Math.round(v / 1000)}k`} />
        <ZAxis dataKey="employment" range={[20, 400]} name="Employment" />
        <Tooltip formatter={(v, n) => n === "Median wage" ? `$${v.toLocaleString()}` : v}
                 labelFormatter={() => ""} content={({ payload }) => payload?.[0] ?
                   <div style={{ background: "#fff", border: "1px solid #ccc", padding: 8 }}>
                     <b>{payload[0].payload.title}</b><br/>
                     emp {payload[0].payload.employment?.toLocaleString()} · beta {payload[0].payload.gpt_beta_model}
                   </div> : null} />
        <Scatter data={pts} fillOpacity={0.55} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
