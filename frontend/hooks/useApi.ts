"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import type { ApiResult } from "@/lib/api-client";

export function useApi<T>(fn: () => Promise<ApiResult<T>>, deps: unknown[]) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [simulated, setSimulated] = useState(false);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const run = useCallback(() => {
    let live = true;
    setLoading(true);
    setError(null);
    fnRef.current()
      .then((r) => {
        if (!live) return;
        setData(r.data);
        setSimulated(r.simulated);
      })
      .catch((e: Error) => live && setError(e.message))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);
  return { data, loading, error, simulated, reload: run };
}
