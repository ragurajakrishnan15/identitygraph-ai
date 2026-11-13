import type { ReactNode } from "react";
import { TopNav } from "@/components/shell/TopNav";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <TopNav />
      <main className="mx-auto w-full max-w-7xl px-5 py-10 md:px-8 md:py-14">{children}</main>
    </>
  );
}
