"use client";
import { Activity, BarChart3, FileText, Gauge, LayoutDashboard, List, Network, ShieldCheck, SlidersHorizontal } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/score", label: "Score Application", icon: Gauge },
  { href: "/applications", label: "Applications", icon: List },
  { href: "/network", label: "Identity Network", icon: Network },
  { href: "/models", label: "Model Performance", icon: BarChart3 },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/features", label: "Feature Analysis", icon: SlidersHorizontal },
  { href: "/reports", label: "Reports", icon: FileText },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="flex w-full shrink-0 flex-col border-b border-navy-600/60 bg-navy-900/80 p-3 md:min-h-screen md:w-60 md:border-b-0 md:border-r">
      <div className="mb-4 flex items-center gap-2 px-2 py-2">
        <ShieldCheck className="text-accent" />
        <div>
          <div className="text-sm font-semibold text-white">IdentityGraph AI</div>
          <div className="text-[10px] uppercase tracking-wider text-warn">Synthetic data · simulated</div>
        </div>
      </div>
      <nav className="flex gap-1 overflow-x-auto md:flex-col">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path === href || path.startsWith(href + "/");
          return (
            <Link key={href} href={href} className={cn("flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm transition",
              active ? "bg-accent/20 text-white" : "text-slate-400 hover:bg-navy-700 hover:text-white")}>
              <Icon size={16} /> {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
