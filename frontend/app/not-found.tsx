import Link from "next/link";

export default function NotFound() {
  return (
    <div className="p-10 text-center">
      <h1 className="text-2xl font-semibold text-white">Page not found</h1>
      <Link href="/overview" className="btn mt-4">Back to overview</Link>
    </div>
  );
}
