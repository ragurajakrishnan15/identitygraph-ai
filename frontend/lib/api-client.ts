import type { Application, Overview, Page } from "@/types/application";
import type { EntityHit, NetworkResponse } from "@/types/graph";
import type { FeatureCatalog, ModelReport, Monitoring } from "@/types/metrics";
import type { ScoreRequest, ScoreResponse } from "@/types/scoring";
import { mock } from "./mock-api";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface ApiResult<T> {
  data: T;
  simulated: boolean; // true => backend unreachable, mock fallback used
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch {}
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

/** Network failure (not HTTP error) => fall back to clearly-labelled mock data. */
async function withFallback<T>(real: () => Promise<T>, fallback: () => T): Promise<ApiResult<T>> {
  try {
    return { data: await real(), simulated: false };
  } catch (e) {
    if (e instanceof ApiError) throw e;
    return { data: fallback(), simulated: true };
  }
}

const qs = (o: Record<string, string | number | undefined>) => {
  const p = new URLSearchParams();
  Object.entries(o).forEach(([k, v]) => v !== undefined && v !== "" && p.set(k, String(v)));
  return p;
};

export const api = {
  overview: () => withFallback(() => http<Overview>("/overview"), mock.overview),
  applications: (o: { q?: string; tier?: string; channel?: string; sort?: string; order?: string; page?: number; page_size?: number }) => {
    const p = qs(o);
    return withFallback(() => http<Page<Application>>(`/applications?${p}`), () => mock.applications(p));
  },
  application: (id: string) => withFallback(() => http<Application>(`/applications/${encodeURIComponent(id)}`), () => mock.application(id)),
  addNote: (id: string, note: string) =>
    http<{ notes: { id: number; note: string; created_at: string }[] }>(`/applications/${encodeURIComponent(id)}/notes`, { method: "POST", body: JSON.stringify({ note }) }),
  score: (r: ScoreRequest) => withFallback(() => http<ScoreResponse>("/score", { method: "POST", body: JSON.stringify(r) }), () => mock.score(r)),
  network: (id: string) => withFallback(() => http<NetworkResponse>(`/entities/${id}/network`), () => mock.network(id)),
  entities: (q: string) => withFallback(() => http<{ items: EntityHit[] }>(`/entities?q=${encodeURIComponent(q)}`), mock.entities),
  modelMetrics: () => withFallback(() => http<ModelReport>("/metrics/model"), mock.modelReport),
  monitoring: () => withFallback(() => http<Monitoring>("/metrics/monitoring"), mock.monitoring),
  features: () => withFallback(() => http<FeatureCatalog>("/features"), mock.features),
};
