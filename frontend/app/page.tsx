"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import WhatIfSimulator from "../components/WhatIfSimulator";
import AIExplanation from "../components/AIExplanation";
import UserAccount from "../components/UserAccount";
import HistoryButton from "../components/HistoryButton";
import SaveAssessment from "../components/SaveAssessment";


type MissionData = {
  status: string;
  period_days: number;

  mission: {
    risk_score: number | null;
    mission_readiness: number | null;
    risk_level: string;
    recommendation: string;
  };

  risk_factors: {
    geomagnetic: number;
    solar_flare: number;
    cme: number;
    storm: number;
  } | null;

  data_quality: string;

  space_weather: {
    solar_activity: {
      available: boolean;
      total_flares: number | null;
      x_class_flares: number | null;
      m_class_flares: number | null;
      c_class_flares: number | null;
      strongest_flare: string | null;
    };

    cme_activity: {
      available: boolean;
      total_cmes: number | null;
      earth_directed_cmes: number | null;
      fastest_speed_km_s: number | null;
    };

    geomagnetic_activity: {
      storm_data_available: boolean;
      storm_count: number | null;
      kp_available: boolean;
      latest_kp: number | null;
      kp_time: string | null;
    };
  };
};


type KpPoint = {
  time_tag: string;
  Kp: number;
};


type KpResponse = {
  available: boolean;
  latest: KpPoint | null;
  history: KpPoint[];
  error: string | null;
};


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


export default function Home() {
  const [data, setData] =
    useState<MissionData | null>(null);

  const [kpHistory, setKpHistory] =
    useState<KpPoint[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);


  const loadMissionData =
    useCallback(async () => {
      try {
        setLoading(true);
        setError(null);
        setKpHistory([]);

        // Mission assessment is the
        // required dashboard request.
        const missionResponse =
          await fetch(
            `${API_URL}/mission-risk`,
            {
              cache: "no-store",
            }
          );

        if (!missionResponse.ok) {
          throw new Error(
            `Mission API returned ${missionResponse.status}`
          );
        }

        const missionResult =
          (await missionResponse.json()) as MissionData;

        setData(
          missionResult
        );


        // Kp history is optional.
        // If NOAA temporarily fails,
        // the rest of MissionGuard
        // remains online.
        try {
          const kpResponse =
            await fetch(
              `${API_URL}/space-weather/kp-index`,
              {
                cache: "no-store",
              }
            );

          if (kpResponse.ok) {
            const kpResult =
              (await kpResponse.json()) as KpResponse;

            if (
              kpResult.available &&
              Array.isArray(
                kpResult.history
              )
            ) {
              setKpHistory(
                kpResult.history.slice(-24)
              );
            }
          }

        } catch (kpError) {
          console.warn(
            "Kp history temporarily unavailable:",
            kpError
          );
        }

      } catch (err) {
        console.error(err);

        setError(
          "MissionGuard backend is unavailable."
        );

      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    const initialLoad = setTimeout(loadMissionData, 0);

    const interval = setInterval(
      loadMissionData,
      60000
    );

    return () => {
      clearTimeout(initialLoad);
      clearInterval(interval);
    };
  }, [loadMissionData]);


  const mission =
    data?.mission;

  const solar =
    data?.space_weather
      ?.solar_activity;

  const cme =
    data?.space_weather
      ?.cme_activity;

  const geomagnetic =
    data?.space_weather
      ?.geomagnetic_activity;


  const readiness =
    mission?.mission_readiness ?? 0;

  const riskLevel =
    mission?.risk_level ?? "UNKNOWN";

  const recommendation =
    mission?.recommendation ?? "HOLD";


  return (
    <main className="min-h-screen bg-[#070B14] text-white">

      <header className="border-b border-white/10 bg-[#070B14]/90 px-6 py-5 backdrop-blur md:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

          <div>
            <h1 className="text-xl font-semibold">
              MissionGuard AI
            </h1>

            <p className="mt-1 text-sm text-gray-400">
              Space Mission Readiness & Risk Intelligence
            </p>
          </div>


          <div className="flex flex-wrap items-center gap-3">

            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm">

            <span
              className={`h-2.5 w-2.5 rounded-full ${
                error
                  ? "bg-red-400"
                  : data
                    ? "bg-emerald-400"
                    : "bg-amber-400"
              }`}
            />

            <span
              className={
                error
                  ? "text-red-300"
                  : data
                    ? "text-emerald-300"
                    : "text-amber-300"
              }
            >
              {error
                ? "System Offline"
                : data
                  ? "System Online"
                  : "Connecting..."}
            </span>

            </div>

            <HistoryButton />
            <UserAccount />

          </div>
        </div>
      </header>


      <section className="mx-auto max-w-7xl px-6 py-10 md:px-8">

        <div className="mb-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">

          <div>
            <p className="mb-2 text-sm uppercase tracking-[0.22em] text-blue-400">
              Mission Control
            </p>

            <h2 className="text-3xl font-bold md:text-4xl">
              Mission Readiness Dashboard
            </h2>

            <p className="mt-3 max-w-2xl text-gray-400">
              Live NASA and NOAA space-weather
              intelligence with MissionGuard
              mission-risk assessment.
            </p>
            <p className="mt-2 max-w-2xl text-sm text-amber-200/80">
              Educational prototype. Scores and GO / NO-GO labels are not
              operational launch guidance or official NASA/NOAA decisions.
            </p>
          </div>


          <button
            onClick={loadMissionData}
            disabled={loading}
            className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-medium transition hover:bg-white/10 disabled:opacity-50"
          >
            {loading
              ? "Updating..."
              : "Refresh Data"}
          </button>

        </div>


        {error && (
          <div className="mb-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
            {error}
          </div>
        )}


        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">

          <DashboardCard
            title="Mission Readiness"
            value={
              mission?.mission_readiness != null
                ? `${mission.mission_readiness}%`
                : "--"
            }
            subtitle="Current readiness score"
            tone={
              getReadinessTone(
                readiness
              )
            }
          />


          <DashboardCard
            title="Risk Level"
            value={riskLevel}
            subtitle={
              mission?.risk_score != null
                ? `Risk score ${mission.risk_score}/100`
                : "Awaiting assessment"
            }
            tone={
              getRiskTone(
                riskLevel
              )
            }
          />


          <DashboardCard
            title="Kp Index"
            value={
              geomagnetic?.latest_kp != null
                ? geomagnetic.latest_kp.toFixed(
                    2
                  )
                : "--"
            }
            subtitle="Planetary geomagnetic activity"
            tone={
              getKpTone(
                geomagnetic?.latest_kp ??
                  null
              )
            }
          />


          <DashboardCard
            title="Recommendation"
            value={recommendation}
            subtitle="Educational model classification"
            tone={
              getRecommendationTone(
                recommendation
              )
            }
          />

        </div>


        <div className="mt-8 grid gap-6 lg:grid-cols-3">

          <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 lg:col-span-2">

            <div>
              <div className="flex items-center justify-between gap-4">

                <div>
                  <h3 className="text-lg font-semibold">
                    Mission Readiness
                  </h3>

                  <p className="mt-1 text-sm text-gray-500">
                    Overall readiness based on
                    current space-weather risk.
                  </p>
                </div>


                <span
                  className={`text-3xl font-semibold ${getReadinessText(
                    readiness
                  )}`}
                >
                  {mission?.mission_readiness !=
                  null
                    ? `${mission.mission_readiness}%`
                    : "--"}
                </span>

              </div>


              <div className="mt-5 h-3 overflow-hidden rounded-full bg-white/10">

                <div
                  className={`h-full rounded-full transition-all duration-700 ${getReadinessBar(
                    readiness
                  )}`}
                  style={{
                    width: `${readiness}%`,
                  }}
                />

              </div>
            </div>


            <div className="mt-7 border-t border-white/10 pt-7">

              <h3 className="text-lg font-semibold">
                Risk Factor Breakdown
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Contribution of each factor
                to the current risk score.
              </p>


              <div className="mt-7 space-y-6">

                <RiskBar
                  label="Geomagnetic Activity"
                  value={
                    data?.risk_factors
                      ?.geomagnetic ?? 0
                  }
                  max={35}
                />


                <RiskBar
                  label="Solar Flare Activity"
                  value={
                    data?.risk_factors
                      ?.solar_flare ?? 0
                  }
                  max={25}
                />


                <RiskBar
                  label="CME Activity"
                  value={
                    data?.risk_factors
                      ?.cme ?? 0
                  }
                  max={30}
                />


                <RiskBar
                  label="Geomagnetic Storms"
                  value={
                    data?.risk_factors
                      ?.storm ?? 0
                  }
                  max={10}
                />

              </div>
            </div>

          </section>


          <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">

            <div className="flex items-start justify-between gap-3">

              <div>
                <h3 className="text-lg font-semibold">
                  Current Space Conditions
                </h3>

                <p className="mt-1 text-sm text-gray-500">
                  Last {data?.period_days ?? 7} days
                </p>
              </div>


              <span
                className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                  data?.data_quality ===
                  "complete"
                    ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300"
                    : "border-amber-400/20 bg-amber-400/10 text-amber-300"
                }`}
              >
                {data?.data_quality
                  ? data.data_quality.toUpperCase()
                  : "WAITING"}
              </span>

            </div>


            <div className="mt-6 space-y-5">

              <ConditionRow
                label="Total Flares"
                value={
                  solar?.total_flares != null
                    ? String(
                        solar.total_flares
                      )
                    : "--"
                }
              />


              <ConditionRow
                label="Strongest Flare"
                value={
                  solar?.strongest_flare ||
                  "None"
                }
              />


              <ConditionRow
                label="X-Class Flares"
                value={
                  solar?.x_class_flares != null
                    ? String(
                        solar.x_class_flares
                      )
                    : "--"
                }
              />


              <ConditionRow
                label="M-Class Flares"
                value={
                  solar?.m_class_flares != null
                    ? String(
                        solar.m_class_flares
                      )
                    : "--"
                }
              />


              <ConditionRow
                label="Total CMEs"
                value={
                  cme?.total_cmes != null
                    ? String(
                        cme.total_cmes
                      )
                    : "--"
                }
              />


              <ConditionRow
                label="Earth-Directed CMEs"
                value={
                  cme?.earth_directed_cmes !=
                  null
                    ? String(
                        cme.earth_directed_cmes
                      )
                    : "--"
                }
              />


              <ConditionRow
                label="Fastest CME"
                value={
                  cme?.fastest_speed_km_s != null
                    ? `${Math.round(
                        cme.fastest_speed_km_s
                      )} km/s`
                    : "--"
                }
              />


              <ConditionRow
                label="Storm Events"
                value={
                  geomagnetic?.storm_count !=
                  null
                    ? String(
                        geomagnetic.storm_count
                      )
                    : "--"
                }
              />

            </div>
          </section>

        </div>


        <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-6">

          <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">

            <div>
              <h3 className="text-lg font-semibold">
                Geomagnetic Activity
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Recent NOAA planetary Kp index
              </p>
            </div>


            <div className="text-sm text-gray-500">
              Latest Kp:{" "}
              <span className="font-semibold text-white">
                {geomagnetic?.latest_kp != null
                  ? geomagnetic.latest_kp.toFixed(
                      2
                    )
                  : "--"}
              </span>
            </div>

          </div>


          <KpChart
            data={kpHistory}
          />

        </section>


        {mission && solar && cme && geomagnetic && (
          <SaveAssessment
            periodDays={
              data?.period_days ?? 7
            }
            mission={mission}
            riskFactors={
              data?.risk_factors ?? null
            }
            dataQuality={
              data?.data_quality ?? "unknown"
            }
            spaceWeather={{
              solar_activity: {
                total_flares:
                  solar.total_flares,
                strongest_flare:
                  solar.strongest_flare,
                x_class_flares:
                  solar.x_class_flares,
                m_class_flares:
                  solar.m_class_flares,
                c_class_flares:
                  solar.c_class_flares,
              },

              cme_activity: {
                total_cmes:
                  cme.total_cmes,
                earth_directed_cmes:
                  cme.earth_directed_cmes,
                fastest_speed_km_s:
                  cme.fastest_speed_km_s,
              },

              geomagnetic_activity: {
                latest_kp:
                  geomagnetic.latest_kp,
                storm_count:
                  geomagnetic.storm_count,
                kp_time:
                  geomagnetic.kp_time,
              },
            }}
          />
        )}


        


        {mission && solar && cme && geomagnetic && (
          <AIExplanation
            key={JSON.stringify([mission, data?.risk_factors, solar, cme, geomagnetic])}
            mission={mission}
            riskFactors={
              data?.risk_factors ?? null
            }
            spaceWeather={{
              solar_activity: {
                total_flares:
                  solar.total_flares,

                strongest_flare:
                  solar.strongest_flare,
              },

              cme_activity: {
                total_cmes:
                  cme.total_cmes,

                earth_directed_cmes:
                  cme.earth_directed_cmes,

                fastest_speed_km_s:
                  cme.fastest_speed_km_s,
              },

              geomagnetic_activity: {
                latest_kp:
                  geomagnetic.latest_kp,

                storm_count:
                  geomagnetic.storm_count,
              },
            }}
          />
        )}


        <WhatIfSimulator />


        <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-6">

          <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">

            <div>
              <p className="text-sm text-gray-400">
                Current Mission Decision
              </p>


              <div className="mt-3">

                <span
                  className={`inline-flex rounded-full border px-4 py-2 text-sm font-bold tracking-wide ${getRecommendationBadge(
                    recommendation
                  )}`}
                >
                  {recommendation}
                </span>

              </div>
            </div>


            <p className="max-w-lg text-sm text-gray-500 md:text-right">
              MissionGuard automatically refreshes
              the live assessment every 60 seconds.
            </p>

          </div>
        </section>

      </section>
    </main>
  );
}


function KpChart({
  data,
}: {
  data: KpPoint[];
}) {
  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-dashed border-white/10 text-sm text-gray-500">
        Waiting for NOAA Kp history...
      </div>
    );
  }


  const width = 1000;
  const height = 260;

  const paddingLeft = 45;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 40;

  const chartWidth =
    width -
    paddingLeft -
    paddingRight;

  const chartHeight =
    height -
    paddingTop -
    paddingBottom;


  const points = data.map(
    (point, index) => {

      const x =
        paddingLeft +
        (
          index /
          Math.max(
            data.length - 1,
            1
          )
        ) *
          chartWidth;


      const kp =
        Math.min(
          Math.max(
            Number(point.Kp) || 0,
            0
          ),
          9
        );


      const y =
        paddingTop +
        chartHeight -
        (kp / 9) *
          chartHeight;


      return {
        x,
        y,
        kp,
        time: point.time_tag,
      };
    }
  );


  const polyline = points
    .map(
      (point) =>
        `${point.x},${point.y}`
    )
    .join(" ");


  return (
    <div className="overflow-x-auto">

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="min-w-[700px] w-full"
        role="img"
        aria-label="Recent NOAA Kp index chart"
      >

        {[0, 3, 5, 7, 9].map(
          (value) => {

            const y =
              paddingTop +
              chartHeight -
              (value / 9) *
                chartHeight;


            return (
              <g key={value}>

                <line
                  x1={paddingLeft}
                  x2={
                    width -
                    paddingRight
                  }
                  y1={y}
                  y2={y}
                  stroke="currentColor"
                  className="text-white/10"
                  strokeWidth="1"
                />


                <text
                  x={10}
                  y={y + 4}
                  fill="currentColor"
                  className="text-[12px] text-gray-500"
                >
                  {value}
                </text>

              </g>
            );
          }
        )}


        <line
          x1={paddingLeft}
          x2={
            width -
            paddingRight
          }
          y1={
            paddingTop +
            chartHeight -
            (5 / 9) *
              chartHeight
          }
          y2={
            paddingTop +
            chartHeight -
            (5 / 9) *
              chartHeight
          }
          stroke="currentColor"
          className="text-amber-400/50"
          strokeDasharray="7 7"
        />


        <polyline
          points={polyline}
          fill="none"
          stroke="currentColor"
          className="text-blue-400"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />


        {points.map(
          (point, index) => (

            <circle
              key={index}
              cx={point.x}
              cy={point.y}
              r="4"
              fill="currentColor"
              className={
                point.kp >= 5
                  ? "text-amber-400"
                  : "text-blue-400"
              }
            >
              <title>
                {`${point.time} — Kp ${point.kp.toFixed(
                  2
                )}`}
              </title>
            </circle>

          )
        )}


        {points.length > 0 && (
          <>
            <text
              x={paddingLeft}
              y={height - 10}
              fill="currentColor"
              className="text-[11px] text-gray-500"
            >
              {formatChartTime(
                points[0].time
              )}
            </text>


            <text
              x={
                width -
                paddingRight
              }
              y={height - 10}
              textAnchor="end"
              fill="currentColor"
              className="text-[11px] text-gray-500"
            >
              {formatChartTime(
                points[
                  points.length - 1
                ].time
              )}
            </text>
          </>
        )}

      </svg>


      <div className="mt-3 flex flex-wrap gap-5 text-xs text-gray-500">

        <span>
          Blue line = observed Kp
        </span>

        <span className="text-amber-300">
          Dashed line = Kp 5 threshold
        </span>

      </div>

    </div>
  );
}


function formatChartTime(
  value: string
) {
  const date = new Date(
    value
  );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }

  return date.toLocaleString(
    undefined,
    {
      month: "short",
      day: "numeric",
      hour: "numeric",
    }
  );
}


function DashboardCard({
  title,
  value,
  subtitle,
  tone,
}: {
  title: string;
  value: string;
  subtitle: string;
  tone: string;
}) {
  return (
    <div
      className={`rounded-2xl border bg-white/[0.03] p-6 ${tone}`}
    >
      <p className="text-sm text-gray-400">
        {title}
      </p>

      <p className="mt-3 text-3xl font-semibold">
        {value}
      </p>

      <p className="mt-2 text-xs text-gray-500">
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
    <div className="flex items-center justify-between gap-4 border-b border-white/5 pb-4 last:border-b-0">
      <span className="text-sm text-gray-400">
        {label}
      </span>

      <span className="text-right text-sm font-medium">
        {value}
      </span>
    </div>
  );
}


function RiskBar({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const percentage =
    Math.min(
      (value / max) * 100,
      100
    );

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">

        <span className="text-sm text-gray-400">
          {label}
        </span>

        <span className="text-sm font-medium">
          {value}/{max}
        </span>

      </div>


      <div className="h-2.5 overflow-hidden rounded-full bg-white/10">

        <div
          className={`h-full rounded-full transition-all duration-700 ${getFactorBar(
            percentage
          )}`}
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>
    </div>
  );
}


function getRiskTone(
  level: string
) {
  switch (level) {
    case "LOW":
      return "border-emerald-400/20 text-emerald-300";

    case "MODERATE":
      return "border-amber-400/30 text-amber-300";

    case "HIGH":
      return "border-orange-400/30 text-orange-300";

    case "CRITICAL":
      return "border-red-500/40 text-red-300";

    default:
      return "border-white/10 text-gray-300";
  }
}


function getRecommendationTone(
  recommendation: string
) {
  switch (recommendation) {
    case "GO":
      return "border-emerald-400/20 text-emerald-300";

    case "CAUTION":
      return "border-amber-400/30 text-amber-300";

    case "DELAY":
      return "border-orange-400/30 text-orange-300";

    case "NO-GO":
      return "border-red-500/40 text-red-300";

    default:
      return "border-white/10 text-gray-300";
  }
}


function getRecommendationBadge(
  recommendation: string
) {
  switch (recommendation) {
    case "GO":
      return "border-emerald-400/30 bg-emerald-400/10 text-emerald-300";

    case "CAUTION":
      return "border-amber-400/30 bg-amber-400/10 text-amber-300";

    case "DELAY":
      return "border-orange-400/30 bg-orange-400/10 text-orange-300";

    case "NO-GO":
      return "border-red-500/30 bg-red-500/10 text-red-300";

    default:
      return "border-gray-400/20 bg-gray-400/10 text-gray-300";
  }
}


function getReadinessTone(
  readiness: number
) {
  if (readiness >= 75) {
    return "border-emerald-400/20 text-emerald-300";
  }

  if (readiness >= 50) {
    return "border-amber-400/30 text-amber-300";
  }

  if (readiness >= 25) {
    return "border-orange-400/30 text-orange-300";
  }

  return "border-red-500/30 text-red-300";
}


function getReadinessText(
  readiness: number
) {
  if (readiness >= 75) {
    return "text-emerald-300";
  }

  if (readiness >= 50) {
    return "text-amber-300";
  }

  if (readiness >= 25) {
    return "text-orange-300";
  }

  return "text-red-300";
}


function getReadinessBar(
  readiness: number
) {
  if (readiness >= 75) {
    return "bg-emerald-400";
  }

  if (readiness >= 50) {
    return "bg-amber-400";
  }

  if (readiness >= 25) {
    return "bg-orange-400";
  }

  return "bg-red-500";
}


function getFactorBar(
  percentage: number
) {
  if (percentage >= 75) {
    return "bg-red-500";
  }

  if (percentage >= 50) {
    return "bg-orange-400";
  }

  if (percentage >= 25) {
    return "bg-amber-400";
  }

  return "bg-emerald-400";
}


function getKpTone(
  kp: number | null
) {
  if (kp == null) {
    return "border-white/10 text-gray-300";
  }

  if (kp >= 7) {
    return "border-red-500/40 text-red-300";
  }

  if (kp >= 5) {
    return "border-orange-400/30 text-orange-300";
  }

  if (kp >= 4) {
    return "border-amber-400/30 text-amber-300";
  }

  return "border-emerald-400/20 text-emerald-300";
}
















