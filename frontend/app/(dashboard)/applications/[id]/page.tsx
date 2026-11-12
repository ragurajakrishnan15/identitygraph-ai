"use client";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { CaseView } from "@/components/applications/CaseView";

export default function ApplicationDetail() {
  const { id } = useParams<{ id: string }>();
  return (
    <>
      <Link href="/applications" className="btn-ghost mb-4 w-fit"><ArrowLeft size={14} /> Back</Link>
      <CaseView id={decodeURIComponent(id)} />
    </>
  );
}
