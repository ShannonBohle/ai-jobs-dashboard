"use client";
import { ComposedChart, Bar, Scatter, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function AttributionTimeline({ timeline }) {
  const byMonth = {};
  for (const c of (timeline.confirmed || [])) {
    const m = byMonth[c.month];
    byMonth[c.month] = m
      ? { jobs: Math.max(m.jobs, c.jobs), company: m.company + " · " + c.company }
      : { jobs: c.jobs, company: c.company };
  }
  const data = [...timeline.warn_monthly]
    .sort((a, b) => a.month.localeCompare(b.month))
    .map(d => ({ ...d, conf_jobs: byMonth[d.month]?.jobs ?? null, conf_company: byMonth[d.month]?.company ?? "" }));
  return (
    <div>
      <ResponsiveContainer width="100%" height={380}>
        <ComposedChart data={data} margin={{ top: 12, right: 56, bottom: 8, left: 8 }}>
          <XAxis dataKey="month" interval="preserveStartEnd" minTickGap={48}
                 tickFormatter={m => m.endsWith("-01") ? m.slice(0, 4) : m} />
          <YAxis yAxisId="left" width={54}
                 label={{ value: "WARN events / month", angle: -90, position: "insideLeft", style: { fontSize: 12 } }} />
          <YAxis yAxisId="right" orientation="right" width={56}
                 tickFormatter={v => `${Math.round(v / 1000)}k`}
                 label={{ value: "announced jobs cut (AI-confirmed)", angle: 90, position: "insideRight", style: { fontSize: 12 } }} />
          <Tooltip formatter={(v, name, p) => name.startsWith("AI-confirmed")
            ? [`${v?.toLocaleString?.() ?? v} — ${p.payload.conf_company}`, name]
            : [v?.toLocaleString?.() ?? v, name]} />
          <Legend />
          <Bar yAxisId="left" dataKey="events" name="All WARN notices, any cause (NY, IL, TX, WA)" fill="#7a8fa5" />
          <Scatter yAxisId="right" dataKey="conf_jobs" name="AI-confirmed cuts (company-verified)"
                   fill="#b3402a" isAnimationActive={false} />
        </ComposedChart>
      </ResponsiveContainer>
      <p style={{ fontSize: 12, color: "#666", lineHeight: 1.5, marginTop: 4 }}>
        Bars: all WARN notices from four state archives, any stated cause (retrieved {timeline.retrieved}); archive depth
        varies &mdash; Illinois's ends July 2022, and New York reports scheduled start dates, so some events are
        future-dated. Red dots: specific companies whose cuts are AI-confirmed in primary sources (SEC memos, regulatory filings,
        shareholder and founders' letters &mdash; verified in this project's gold set), placed at the announcement
        month and positioned by announced headcount (hover a dot for the company); several counts are global workforce figures. Bars show the legal
        record; dots show the confirmed cases &mdash; see methods.
      </p>
    </div>
  );
}
