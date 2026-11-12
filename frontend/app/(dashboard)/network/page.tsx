"use client";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Legend, NetworkGraph } from "@/components/graph/NetworkGraph";
import { Card, Loading, PageHeader, State } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import type { EntityHit } from "@/types/graph";

function NetworkInner() {
  const params = useSearchParams();
  const [focus, setFocus] = useState<string | null>(params.get("focus"));
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<EntityHit[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  const hubs = useApi(() => api.entities(""), []);
  useEffect(() => {
    if (!focus && hubs.data?.items.length) setFocus(hubs.data.items[0].entity_id);
  }, [hubs.data, focus]);
  useEffect(() => {
    if (q.length < 2) { setHits([]); return; }
    const t = setTimeout(() => api.entities(q).then((r) => setHits(r.data.items)).catch(() => setHits([])), 250);
    return () => clearTimeout(t);
  }, [q]);

  const net = useApi(() => (focus ? api.network(focus) : Promise.resolve({ data: null as never, simulated: false })), [focus]);
  const node = net.data?.nodes.find((n) => n.id === selected);

  return (
    <>
      <PageHeader title="Identity Network" subtitle="Shared identifiers across applications. Connections are investigation signals, not proof of fraud." />
      <div className="grid gap-4 lg:grid-cols-[300px_1fr]">
        <div className="space-y-4">
          <Card title="Find entity">
            <input className="input" placeholder="device:, ip:, email:, phone:, APP…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Entity search" />
            <ul className="mt-2 max-h-48 space-y-1 overflow-y-auto text-sm">
              {hits.map((h) => (
                <li key={h.entity_id}><button className="w-full truncate text-left text-accent-soft hover:underline" onClick={() => { setFocus(h.entity_id); setSelected(null); }}>{h.kind}: {h.label} ({h.degree})</button></li>
              ))}
            </ul>
          </Card>
          <Card title="Most-shared identifiers (rings to investigate)">
            {hubs.loading ? <Loading /> : (
              <ul className="space-y-1 text-sm">
                {hubs.data?.items.map((h) => (
                  <li key={h.entity_id}><button className="w-full truncate text-left text-accent-soft hover:underline" onClick={() => { setFocus(h.entity_id); setSelected(null); }}>{h.kind}: {h.label} <span className="text-slate-500">({h.degree})</span></button></li>
                ))}
              </ul>
            )}
          </Card>
          <Card title="Selected node">
            {node ? (
              <div className="space-y-1 text-sm">
                <div className="break-all font-medium text-white">{node.label}</div>
                <div className="text-slate-400">type: {node.type} · degree {node.degree}</div>
                {node.flagged && <div className="text-danger">Shared by many applications (investigate)</div>}
                <button className="btn-ghost mt-2" onClick={() => setFocus(node.id)}>Focus on this node</button>
              </div>
            ) : <p className="text-sm text-slate-500">Click a node in the graph.</p>}
          </Card>
        </div>
        <div className="space-y-3">
          {focus ? (
            <State s={net}>
              {(d) => (
                <>
                  <div className="card flex flex-wrap gap-x-6 gap-y-1 text-sm">
                    <span><b className="text-white">{d.summary.label}</b> ({d.summary.kind})</span>
                    <span>{d.summary.linked_applications} linked applications</span>
                    <span>component size {d.summary.component_size}</span>
                  </div>
                  <NetworkGraph data={d} onSelect={setSelected} />
                  <Legend />
                  <p className="text-xs text-slate-500">{d.note}</p>
                </>
              )}
            </State>
          ) : <Loading label="Loading graph…" />}
        </div>
      </div>
    </>
  );
}

export default function NetworkPage() {
  return <Suspense fallback={<Loading />}><NetworkInner /></Suspense>;
}
