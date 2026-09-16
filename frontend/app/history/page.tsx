"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  collection,
  getDocs,
  Timestamp,
} from "firebase/firestore";

import {
  onAuthStateChanged,
} from "firebase/auth";

import {
  auth,
  db,
} from "../../lib/firebase";


type MissionResult = {
  risk_score?: number | null;
  mission_readiness?: number | null;
  risk_level?: string;
  recommendation?: string;
};


type RiskFactors = {
  geomagnetic?: number;
  solar_flare?: number;
  cme?: number;
  storm?: number;
};


type HistoryRecord = {
  id: string;

  recordType:
    | "assessment"
    | "simulation";

  saved_at?:
    | Timestamp
    | null;

  period_days?: number;

  data_quality?: string;

  mission?: MissionResult;

  risk_factors?: RiskFactors;

  scenario?: {
    kp_index?: number;

    flare_class?: string;

    flare_magnitude?: number;

    earth_directed_cmes?: number;

    fastest_cme_speed_km_s?: number;

    storm_count?: number;
  };

  granite_explanation?: {
    provider?: string;

    model?: string | null;

    ai_generated?: boolean;

    explanation?: string;

    warning?: string | null;
  } | null;
};


function formatDate(
  timestamp?:
    | Timestamp
    | null
) {
  if (!timestamp) {
    return "Timestamp unavailable";
  }

  return timestamp
    .toDate()
    .toLocaleString();
}


function timestampValue(
  timestamp?:
    | Timestamp
    | null
) {
  if (!timestamp) {
    return 0;
  }

  return timestamp
    .toMillis();
}


function riskStyle(
  level?: string
) {
  const value =
    level?.toUpperCase();

  if (value === "LOW") {
    return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";
  }

  if (
    value === "MODERATE"
  ) {
    return "border-yellow-400/30 bg-yellow-400/10 text-yellow-300";
  }

  if (value === "HIGH") {
    return "border-orange-400/30 bg-orange-400/10 text-orange-300";
  }

  if (
    value === "CRITICAL"
  ) {
    return "border-red-400/30 bg-red-400/10 text-red-300";
  }

  return "border-white/10 bg-white/5 text-gray-300";
}


export default function HistoryPage() {
  const [
    records,
    setRecords,
  ] =
    useState<HistoryRecord[]>(
      []
    );

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    );


  useEffect(() => {
    const unsubscribe =
      onAuthStateChanged(
        auth,
        async (user) => {
          if (!user) {
            return;
          }


          try {
            setLoading(
              true
            );

            setError(
              null
            );


            const assessmentRef =
              collection(
                db,
                "users",
                user.uid,
                "assessments"
              );


            const simulationRef =
              collection(
                db,
                "users",
                user.uid,
                "simulations"
              );


            const [
              assessmentSnapshot,
              simulationSnapshot,
            ] =
              await Promise.all([
                getDocs(
                  assessmentRef
                ),

                getDocs(
                  simulationRef
                ),
              ]);


            const assessments =
              assessmentSnapshot
                .docs
                .map(
                  (document) => ({
                    id:
                      document.id,

                    recordType:
                      "assessment" as const,

                    ...document.data(),
                  })
                ) as HistoryRecord[];


            const simulations =
              simulationSnapshot
                .docs
                .map(
                  (document) => ({
                    id:
                      document.id,

                    recordType:
                      "simulation" as const,

                    ...document.data(),
                  })
                ) as HistoryRecord[];


            const combined = [
              ...assessments,
              ...simulations,
            ].sort(
              (a, b) =>
                timestampValue(
                  b.saved_at
                ) -
                timestampValue(
                  a.saved_at
                )
            );


            setRecords(
              combined
            );

          } catch (err) {
            console.error(
              err
            );

            setError(
              "Unable to load your MissionGuard history."
            );

          } finally {
            setLoading(
              false
            );
          }
        }
      );


    return unsubscribe;

  }, []);


  return (
    <main className="min-h-screen bg-[#070B14] px-5 py-8 text-white md:px-10">

      <div className="mx-auto max-w-6xl">

        <div className="mb-10 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">

          <div>

            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">
              MissionGuard AI
            </p>

            <h1 className="mt-2 text-3xl font-bold md:text-4xl">
              Mission History
            </h1>

            <p className="mt-2 text-gray-500">
              Saved live assessments and what-if simulations.
            </p>

          </div>


          <Link
            href="/"
            className="w-fit rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm transition hover:bg-white/10"
          >
            Back to Dashboard
          </Link>

        </div>


        {loading && (
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-10 text-center">

            <div className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-white/10 border-t-blue-400" />

            <p className="mt-4 text-sm text-gray-500">
              Loading MissionGuard history...
            </p>

          </div>
        )}


        {error && (
          <div className="rounded-2xl border border-red-400/20 bg-red-400/5 p-6 text-red-300">
            {error}
          </div>
        )}


        {!loading &&
          !error &&
          records.length ===
            0 && (
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-10 text-center">

              <h2 className="text-xl font-semibold">
                No saved records yet
              </h2>

              <p className="mt-2 text-sm text-gray-500">
                Save a live assessment or simulation from the dashboard.
              </p>

              <Link
                href="/"
                className="mt-6 inline-block rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold hover:bg-blue-400"
              >
                Go to Dashboard
              </Link>

            </div>
          )}


        {!loading &&
          !error &&
          records.length >
            0 && (
            <div className="grid gap-5">

              {records.map(
                (record) => (
                  <article
                    key={`${record.recordType}-${record.id}`}
                    className="rounded-2xl border border-white/10 bg-white/[0.03] p-6"
                  >

                    <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">

                      <div>

                        <div className="flex flex-wrap items-center gap-3">

                          <span
                            className={
                              record.recordType ===
                              "simulation"
                                ? "rounded-full border border-violet-400/30 bg-violet-400/10 px-3 py-1 text-xs font-semibold text-violet-300"
                                : "rounded-full border border-blue-400/30 bg-blue-400/10 px-3 py-1 text-xs font-semibold text-blue-300"
                            }
                          >
                            {record.recordType ===
                            "simulation"
                              ? "SIMULATION"
                              : "LIVE ASSESSMENT"}
                          </span>


                          <span
                            className={`rounded-full border px-3 py-1 text-xs font-semibold ${riskStyle(
                              record
                                .mission
                                ?.risk_level
                            )}`}
                          >
                            {record
                              .mission
                              ?.risk_level ??
                              "UNKNOWN"}
                          </span>


                          <span className="text-xs text-gray-500">
                            {formatDate(
                              record.saved_at
                            )}
                          </span>

                        </div>


                        <h2 className="mt-4 text-xl font-semibold">
                          {record.recordType ===
                          "simulation"
                            ? "What-If Scenario"
                            : "Mission Risk Assessment"}
                        </h2>


                        <p className="mt-2 text-sm text-gray-400">
                          Decision:{" "}

                          <span className="font-semibold text-white">
                            {record
                              .mission
                              ?.recommendation ??
                              "Unavailable"}
                          </span>
                        </p>

                      </div>


                      <div className="grid grid-cols-2 gap-3">

                        <div className="rounded-xl bg-black/20 p-4">

                          <p className="text-xs text-gray-500">
                            Risk Score
                          </p>

                          <p className="mt-1 text-xl font-bold">
                            {record
                              .mission
                              ?.risk_score ??
                              "—"}
                          </p>

                        </div>


                        <div className="rounded-xl bg-black/20 p-4">

                          <p className="text-xs text-gray-500">
                            Readiness
                          </p>

                          <p className="mt-1 text-xl font-bold">
                            {record
                              .mission
                              ?.mission_readiness ??
                              "—"}
                            %
                          </p>

                        </div>

                      </div>

                    </div>


                    {record.recordType ===
                      "simulation" &&
                      record.scenario && (
                        <div className="mt-6 rounded-xl border border-violet-400/10 bg-violet-400/[0.03] p-5">

                          <p className="mb-4 text-sm font-semibold text-violet-300">
                            Simulated Inputs
                          </p>


                          <div className="grid grid-cols-2 gap-4 text-sm md:grid-cols-3 lg:grid-cols-6">

                            <HistoryValue
                              label="Kp"
                              value={
                                record
                                  .scenario
                                  .kp_index ??
                                "—"
                              }
                            />


                            <HistoryValue
                              label="Flare"
                              value={
                                record
                                  .scenario
                                  .flare_class ===
                                "NONE"
                                  ? "None"
                                  : `${
                                      record
                                        .scenario
                                        .flare_class ??
                                      ""
                                    }${
                                      record
                                        .scenario
                                        .flare_magnitude ??
                                      ""
                                    }`
                              }
                            />


                            <HistoryValue
                              label="Earth CMEs"
                              value={
                                record
                                  .scenario
                                  .earth_directed_cmes ??
                                "—"
                              }
                            />


                            <HistoryValue
                              label="CME Speed"
                              value={
                                record
                                  .scenario
                                  .fastest_cme_speed_km_s !=
                                null
                                  ? `${
                                      record
                                        .scenario
                                        .fastest_cme_speed_km_s
                                    } km/s`
                                  : "—"
                              }
                            />


                            <HistoryValue
                              label="Storms"
                              value={
                                record
                                  .scenario
                                  .storm_count ??
                                "—"
                              }
                            />


                            <HistoryValue
                              label="Mode"
                              value="What-If"
                            />

                          </div>

                        </div>
                      )}


                    {record.risk_factors && (
                      <div className="mt-6 grid grid-cols-2 gap-3 border-t border-white/10 pt-5 sm:grid-cols-4">

                        <HistoryValue
                          label="Geomagnetic"
                          value={
                            record
                              .risk_factors
                              .geomagnetic ??
                            0
                          }
                        />


                        <HistoryValue
                          label="Solar Flare"
                          value={
                            record
                              .risk_factors
                              .solar_flare ??
                            0
                          }
                        />


                        <HistoryValue
                          label="CME"
                          value={
                            record
                              .risk_factors
                              .cme ??
                            0
                          }
                        />


                        <HistoryValue
                          label="Storm"
                          value={
                            record
                              .risk_factors
                              .storm ??
                            0
                          }
                        />

                      </div>
                    )}


                    {record.recordType ===
                      "simulation" &&
                      record
                        .granite_explanation
                        ?.explanation && (
                        <details className="mt-6 rounded-xl border border-white/10 bg-black/10 p-5">

                          <summary className="cursor-pointer text-sm font-semibold text-violet-300">
                            Saved Granite Explanation
                          </summary>


                          <p className="mt-4 whitespace-pre-line text-sm leading-7 text-gray-400">
                            {
                              record
                                .granite_explanation
                                .explanation
                            }
                          </p>


                          {record
                            .granite_explanation
                            .warning && (
                            <p className="mt-4 text-xs text-amber-300">
                              {
                                record
                                  .granite_explanation
                                  .warning
                              }
                            </p>
                          )}

                        </details>
                      )}

                  </article>
                )
              )}

            </div>
          )}

      </div>

    </main>
  );
}


function HistoryValue({
  label,
  value,
}: {
  label: string;

  value:
    | string
    | number;
}) {
  return (
    <div>

      <p className="text-xs text-gray-500">
        {label}
      </p>

      <p className="mt-1 font-semibold text-gray-200">
        {value}
      </p>

    </div>
  );
}
