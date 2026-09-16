"use client";

import Link from "next/link";

export default function HistoryButton() {
  return (
    <Link
      href="/history"
      className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300 transition hover:bg-white/10 hover:text-white"
    >
      History
    </Link>
  );
}
