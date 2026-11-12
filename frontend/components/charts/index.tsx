"use client";
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { TIER_COLOR } from "@/lib/utils";
import type { Tier } from "@/types/application";

const AXIS = { stroke: "#64748b", fontSize: 11 };
const TT = { contentStyle: { background: "#111a33", border: "1px solid #26335e", borderRadius: 8, color: "#e2e8f0" } };

export function TrendChart({ data }: { data: { period: string; applications: number; avg_score: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7c6cf6" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#7c6cf6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1a2547" vertical={false} />
        <XAxis dataKey="period" {...AXIS} />
        <YAxis yAxisId="l" {...AXIS} />
        <YAxis yAxisId="r" orientation="right" domain={[0, 1]} {...AXIS} />
        <Tooltip {...TT} />
        <Legend />
        <Area yAxisId="l" dataKey="applications" name="Applications" stroke="#7c6cf6" fill="url(#g1)" />
        <Line yAxisId="r" dataKey="avg_score" name="Avg score" stroke="#fbbf24" dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function TierPie({ tiers }: { tiers: Partial<Record<Tier, number>> }) {
  const data = (["Low", "Medium", "High"] as Tier[]).map((t) => ({ name: t, value: tiers[t] ?? 0 }));
  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
          {data.map((d) => <Cell key={d.name} fill={TIER_COLOR[d.name as Tier]} />)}
        </Pie>
        <Tooltip {...TT} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function ChannelBars({ rows }: { rows: { channel: string; tier: Tier; count: number }[] }) {
  const byCh: Record<string, Record<string, number | string>> = {};
  rows.forEach((r) => {
    byCh[r.channel] ??= { channel: r.channel };
    byCh[r.channel][r.tier] = r.count;
  });
  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={Object.values(byCh)}>
        <CartesianGrid stroke="#1a2547" vertical={false} />
        <XAxis dataKey="channel" {...AXIS} />
        <YAxis {...AXIS} />
        <Tooltip {...TT} />
        <Legend />
        {(["Low", "Medium", "High"] as Tier[]).map((t) => <Bar key={t} dataKey={t} stackId="a" fill={TIER_COLOR[t]} />)}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HistBars({ data, xKey, yKey, color = "#7c6cf6", height = 240 }: { data: Record<string, unknown>[]; xKey: string; yKey: string; color?: string; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid stroke="#1a2547" vertical={false} />
        <XAxis dataKey={xKey} {...AXIS} interval="preserveStartEnd" />
        <YAxis {...AXIS} />
        <Tooltip {...TT} />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HBars({ data, xKey, yKey, color = "#7c6cf6" }: { data: Record<string, unknown>[]; xKey: string; yKey: string; color?: string }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 26)}>
      <BarChart data={data} layout="vertical" margin={{ left: 90 }}>
        <CartesianGrid stroke="#1a2547" horizontal={false} />
        <XAxis type="number" {...AXIS} />
        <YAxis type="category" dataKey={yKey} {...AXIS} width={170} />
        <Tooltip {...TT} />
        <Bar dataKey={xKey} fill={color} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function CurveChart({ series, xLabel, yLabel }: { series: { name: string; color: string; points: number[][] }[]; xLabel: string; yLabel: string }) {
  const rows: Record<string, number>[] = [];
  series.forEach((s) => s.points.forEach(([x, y]) => rows.push({ x, [s.name]: y })));
  rows.sort((a, b) => a.x - b.x);
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={rows}>
        <CartesianGrid stroke="#1a2547" />
        <XAxis dataKey="x" type="number" domain={[0, 1]} {...AXIS} label={{ value: xLabel, fill: "#64748b", fontSize: 11, position: "insideBottom", offset: -2 }} />
        <YAxis domain={[0, 1]} {...AXIS} label={{ value: yLabel, fill: "#64748b", fontSize: 11, angle: -90, position: "insideLeft" }} />
        <Tooltip {...TT} formatter={(v: number) => v.toFixed(3)} labelFormatter={(l: number) => `${xLabel}: ${Number(l).toFixed(3)}`} />
        <Legend />
        {series.map((s) => <Line key={s.name} dataKey={s.name} stroke={s.color} dot={false} connectNulls strokeWidth={2} />)}
      </LineChart>
    </ResponsiveContainer>
  );
}
