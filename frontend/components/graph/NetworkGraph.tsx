"use client";
import { useMemo } from "react";
import ReactFlow, { Background, Controls, MarkerType, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";
import type { NetworkResponse } from "@/types/graph";

export const KIND_COLOR: Record<string, string> = {
  application: "#7c6cf6", applicant: "#94a3b8", device: "#fb7185", ip: "#fbbf24",
  email: "#2dd4bf", phone: "#38bdf8", address: "#c084fc",
};

function layout(data: NetworkResponse): Node[] {
  const focus = data.nodes.find((n) => n.is_focus) ?? data.nodes[0];
  const adj = new Map<string, string[]>();
  data.edges.forEach((e) => {
    adj.set(e.source, [...(adj.get(e.source) ?? []), e.target]);
    adj.set(e.target, [...(adj.get(e.target) ?? []), e.source]);
  });
  // BFS rings around the focus node
  const depth = new Map<string, number>([[focus.id, 0]]);
  const q = [focus.id];
  while (q.length) {
    const c = q.shift()!;
    (adj.get(c) ?? []).forEach((n) => { if (!depth.has(n)) { depth.set(n, depth.get(c)! + 1); q.push(n); } });
  }
  const rings = new Map<number, string[]>();
  data.nodes.forEach((n) => { const d = depth.get(n.id) ?? 3; rings.set(d, [...(rings.get(d) ?? []), n.id]); });
  // Ring radius grows with node count so 130px-wide nodes never overlap on a ring.
  const pos = new Map<string, { x: number; y: number }>();
  let prevR = 0;
  [...rings.keys()].sort((a, b) => a - b).forEach((d) => {
    const ids = rings.get(d)!;
    const r = d === 0 ? 0 : Math.max(prevR + 140, (ids.length * 100) / (2 * Math.PI));
    prevR = r;
    ids.forEach((id, i) => {
      const a = (2 * Math.PI * i) / ids.length + d * 0.5;
      pos.set(id, { x: Math.cos(a) * r, y: Math.sin(a) * r });
    });
  });
  return data.nodes.map((n) => ({
    id: n.id,
    position: pos.get(n.id) ?? { x: 0, y: 0 },
    data: { label: `${n.type}\n${n.label.length > 22 ? n.label.slice(0, 20) + "…" : n.label}` },
    style: {
      background: "#111a33", color: "#e2e8f0", fontSize: 10, whiteSpace: "pre-line", textAlign: "center", width: 120,
      border: `2px solid ${n.flagged ? "#fb7185" : KIND_COLOR[n.type] ?? "#64748b"}`,
      borderRadius: n.type === "application" ? 8 : 24,
      boxShadow: n.is_focus ? "0 0 0 4px rgba(124,108,246,.5)" : n.flagged ? "0 0 14px rgba(251,113,133,.6)" : "none",
    },
  }));
}

export function NetworkGraph({ data, onSelect }: { data: NetworkResponse; onSelect: (id: string) => void }) {
  const nodes = useMemo(() => layout(data), [data]);
  const edges: Edge[] = useMemo(() => data.edges.map((e) => ({
    id: e.id, source: e.source, target: e.target, style: { stroke: "#475569" },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#475569" },
  })), [data]);
  return (
    <div className="h-[560px] w-full rounded-xl border border-navy-600/60 bg-navy-900">
      <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.15 }} minZoom={0.1} onNodeClick={(_, n) => onSelect(n.id)} proOptions={{ hideAttribution: true }}>
        <Background color="#1a2547" />
        <Controls />
      </ReactFlow>
    </div>
  );
}

export function Legend() {
  return (
    <div className="flex flex-wrap gap-3 text-xs text-slate-400">
      {Object.entries(KIND_COLOR).map(([k, c]) => (
        <span key={k} className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: c }} />{k}</span>
      ))}
      <span className="flex items-center gap-1"><span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-danger" />shared identifier (degree ≥ 4)</span>
    </div>
  );
}
