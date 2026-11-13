"use client";
import {
  Area, Bar, BarChart, CartesianGrid, Cell, ComposedChart, Legend, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { TIER_COLOR } from "@/lib/utils";
import type { Tier } from "@/types/application";

const AXIS = { stroke: "rgb(var(--subtle))", fontSize: 11, tickLine: false, axisLine: false };
const GRID = "rgb(var(--line))";
const LEGEND_FMT = (v: string) => <span style={{ color: "rgb(var(--muted))", fontSize: 12 }}>{v}</span>;
const BLUE = "#0a84ff";
const TT = { contentStyle: { background: "rgb(var(--surface))", border: "1px solid rgb(var(--line))", borderRadius: 14, color: "rgb(var(--ink))", boxShadow: "0 10px 40px rgb(0 0 0 / .12)", fontSize: 12 }, cursor: { stroke: "rgb(var(--line))" } };

export function TrendChart({ data }: { data: { period: string; applications: number; avg_score: number }[] }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <ComposedChart data={data}>
        <defs>
          <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#0a84ff" stopOpacity={0.5} />
            <stop offset="100%" stopColor="#0a84ff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="period" {...AXIS} />
        <YAxis yAxisId="l" {...AXIS} />
        <YAxis yAxisId="r" orientation="right" domain={[0, 1]} {...AXIS} />
        <Tooltip {...TT} />
        <Legend formatter={LEGEND_FMT} />
        <Area yAxisId="l" dataKey="applications" name="Applications" stroke="#0a84ff" fill="url(#g1)" />
        <Line yAxisId="r" dataKey="avg_score" name="Avg score" stroke="#ff9f0a" dot={false} />
      </ComposedChart>
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
        <Legend formatter={LEGEND_FMT} />
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
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey="channel" {...AXIS} />
        <YAxis {...AXIS} />
        <Tooltip {...TT} />
        <Legend formatter={LEGEND_FMT} />
        {(["Low", "Medium", "High"] as Tier[]).map((t) => <Bar key={t} dataKey={t} stackId="a" fill={TIER_COLOR[t]} />)}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HistBars({ data, xKey, yKey, color = BLUE, height = 240 }: { data: Record<string, unknown>[]; xKey: string; yKey: string; color?: string; height?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid stroke={GRID} vertical={false} />
        <XAxis dataKey={xKey} {...AXIS} interval="preserveStartEnd" />
        <YAxis {...AXIS} />
        <Tooltip {...TT} />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function HBars({ data, xKey, yKey, color = BLUE }: { data: Record<string, unknown>[]; xKey: string; yKey: string; color?: string }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 26)}>
      <BarChart data={data} layout="vertical" margin={{ left: 90 }}>
        <CartesianGrid stroke={GRID} horizontal={false} />
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
        <CartesianGrid stroke={GRID} />
        <XAxis dataKey="x" type="number" domain={[0, 1]} {...AXIS} label={{ value: xLabel, fill: "rgb(var(--subtle))", fontSize: 11, position: "insideBottom", offset: -2 }} />
        <YAxis domain={[0, 1]} {...AXIS} label={{ value: yLabel, fill: "rgb(var(--subtle))", fontSize: 11, angle: -90, position: "insideLeft" }} />
        <Tooltip {...TT} formatter={(v: number) => v.toFixed(3)} labelFormatter={(l: number) => `${xLabel}: ${Number(l).toFixed(3)}`} />
        <Legend formatter={LEGEND_FMT} />
        {series.map((s) => <Line key={s.name} dataKey={s.name} stroke={s.color} dot={false} connectNulls strokeWidth={2} />)}
      </LineChart>
    </ResponsiveContainer>
  );
}
