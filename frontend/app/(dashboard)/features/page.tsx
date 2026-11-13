"use client";
import { Card, PageHeader, State } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";

export default function Features() {
  const s = useApi(() => api.features(), []);
  return (
    <>
      <PageHeader title="Feature Analysis" subtitle="Feature groups used by the model. Importance shown for the graph-enhanced model's top-20 features." />
      <State s={s}>
        {(c) => (
          <div className="grid gap-4 md:grid-cols-2">
            {c.groups.map((g) => (
              <Card key={g.group} title={g.group}>
                <ul className="space-y-2 text-sm">
                  {g.features.map((f) => (
                    <li key={f.name}>
                      <div className="flex justify-between"><span>{f.name}</span><span className="text-muted">{f.importance != null ? f.importance.toFixed(3) : "-"}</span></div>
                      <div className="mt-1 h-1.5 rounded bg-fill"><div className="h-1.5 rounded bg-accent" style={{ width: `${Math.min(100, (f.importance ?? 0) * 250)}%` }} /></div>
                    </li>
                  ))}
                </ul>
              </Card>
            ))}
            {c.groups.length === 0 && <p className="text-sm text-muted">No feature catalog available.</p>}
          </div>
        )}
      </State>
    </>
  );
}
