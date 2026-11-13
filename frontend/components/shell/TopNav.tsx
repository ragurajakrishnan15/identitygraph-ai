"use client";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export const REPO_URL = "https://github.com/ragurajakrishnan15/identitygraph-ai";

const NAV = [
  { href: "/overview", label: "Overview" },
  { href: "/score", label: "Score" },
  { href: "/applications", label: "Applications" },
  { href: "/network", label: "Network" },
  { href: "/models", label: "Models" },
  { href: "/monitoring", label: "Monitoring" },
  { href: "/features", label: "Features" },
  { href: "/reports", label: "Reports" },
];

export function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2 text-[15px] font-semibold tracking-tight text-ink" aria-label="IdentityGraph AI home">
      <span className="grid h-7 w-7 place-items-center rounded-lg bg-ink text-bg"><ShieldCheck size={16} /></span>
      IdentityGraph
    </Link>
  );
}

/** Frosted, sticky app bar used by every dashboard page. */
export function TopNav() {
  const path = usePathname();
  return (
    <header className="glass sticky top-0 z-40">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-6 px-5 md:px-8">
        <Brand />
        <nav aria-label="Primary" className="-mx-1 flex flex-1 items-center gap-1 overflow-x-auto">
          {NAV.map(({ href, label }) => {
            const active = path === href || path.startsWith(href + "/");
            return (
              <Link key={href} href={href} aria-current={active ? "page" : undefined}
                className={cn("whitespace-nowrap rounded-full px-3 py-1.5 text-[13px] transition",
                  active ? "bg-fill font-medium text-ink" : "text-muted hover:text-ink")}>
                {label}
              </Link>
            );
          })}
        </nav>
        <span className="hidden whitespace-nowrap rounded-full bg-warn/10 px-2.5 py-1 text-[11px] font-medium text-warn lg:inline">Synthetic data</span>
        <a href={REPO_URL} target="_blank" rel="noreferrer" className="hidden items-center gap-1 text-[13px] text-muted hover:text-ink md:inline-flex">
          GitHub <ArrowUpRight size={13} />
        </a>
      </div>
    </header>
  );
}
