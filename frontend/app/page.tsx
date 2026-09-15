"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [apiStatus, setApiStatus] = useState("Checking...");

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
      .then((res) => res.json())
      .then((data) => {
        setApiStatus(data.status);
      })
      .catch(() => {
        setApiStatus("offline");
      });
  }, []);

  return (
    <main className="min-h-screen bg-[#070B14] text-white">
      <header className="border-b border-white/10 px-8 py-5">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">
              MissionGuard AI
            </h1>

            <p className="text-sm text-gray-400">
              Space Mission Readiness & Risk Intelligence
            </p>
          </div>

          <div className="flex items-center gap-2 text-sm text-green-400">
            <span
              className={`h-2 w-2 rounded-full ${
                apiStatus === "healthy"
                  ? "bg-green-400"
                  : "bg-red-400"
              }`}
            />

            {apiStatus === "healthy"
              ? "System Online"
              : apiStatus === "Checking..."
              ? "Checking System..."
              : "System Offline"}
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-8 py-10">
        <div className="mb-8">
          <p className="mb-2 text-sm uppercase tracking-widest text-blue-400">
            Mission Control
          </p>

          <h2 className="text-4xl font-bold">
            Mission Readiness Dashboard
          </h2>

          <p className="mt-3 max-w-2xl text-gray-400">
            Monitor space-weather conditions, assess mission risk,
            and receive intelligent launch-readiness recommendations.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <DashboardCard
            title="Mission Readiness"
            value="--%"
            subtitle="Awaiting live data"
          />

          <DashboardCard
            title="Risk Level"
            value="--"
            subtitle="No assessment yet"
          />

          <DashboardCard
            title="Kp Index"
            value="--"
            subtitle="Geomagnetic activity"
          />

          <DashboardCard
            title="Recommendation"
            value="--"
            subtitle="Mission decision"
          />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 lg:col-span-2">
            <div className="mb-6">
              <h3 className="text-lg font-semibold">
                Space Weather Risk Trend
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Risk data will appear here once the data engine is connected.
              </p>
            </div>

            <div className="flex h-72 items-center justify-center rounded-xl border border-dashed border-white/10 text-sm text-gray-600">
              Risk visualization coming in Phase 4
            </div>
          </section>

          <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
            <h3 className="text-lg font-semibold">
              Current Space Conditions
            </h3>

            <div className="mt-6 space-y-5">
              <ConditionRow
                label="X-Class Flares"
                value="--"
              />

              <ConditionRow
                label="M-Class Flares"
                value="--"
              />

              <ConditionRow
                label="CME Activity"
                value="--"
              />

              <ConditionRow
                label="Geomagnetic Storms"
                value="--"
              />

              <ConditionRow
                label="Solar Wind"
                value="--"
              />
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function DashboardCard({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">
      <p className="text-sm text-gray-400">
        {title}
      </p>

      <p className="mt-3 text-3xl font-semibold">
        {value}
      </p>

      <p className="mt-2 text-xs text-gray-600">
        {subtitle}
      </p>
    </div>
  );
}

function ConditionRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-white/5 pb-4">
      <span className="text-sm text-gray-400">
        {label}
      </span>

      <span className="text-sm font-medium">
        {value}
      </span>
    </div>
  );
}