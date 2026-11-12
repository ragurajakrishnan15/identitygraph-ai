"use client";
import { ErrorBox } from "@/components/ui";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-6">
      <ErrorBox message={error.message || "Something went wrong"} onRetry={reset} />
    </div>
  );
}
