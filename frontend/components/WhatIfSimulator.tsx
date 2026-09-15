"use client";

import { FormEvent, useState } from "react";


type FlareClass =
  | "NONE"
  | "C"
  | "M"
  | "X";


type SimulationResult = {
  status: string;

  simulation_notice: string;

  mission: {
    risk_score: number;
    mission_readiness: number;
    risk_level: string;
    recommendation: string;
  };

  risk_factors: {
    geomagnetic: number;
    solar_flare: number;
    cme: number;
    storm: number;
  };
};


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


export default function WhatIfSimulator() {
  const [kpIndex, setKpIndex] =
    useState(2);

  const [flareClass, setFlareClass] =
    useState<FlareClass>("NONE");

  const [flareMagnitude, setFlareMagnitude] =
    useState(1);

  const [
    earthDirectedCmes,
    setEarthDirectedCmes,
  ] = useState(0);

  const [
    cmeSpeed,
    setCmeSpeed,
  ] = useState(0);

  const [
    stormCount,
    setStormCount,
  ] = useState(0);

  const [result, setResult] =
    useState<SimulationResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function runSimulation(
    event: FormEvent
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${API_URL}/simulator/evaluate`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            kp_index: kpIndex,

            flare_class:
              flareClass,

            flare_magnitude:
              flareMagnitude,

            earth_directed_cmes:
              earthDirectedCmes,

            fastest_cme_speed_km_s:
              cmeSpeed,

            storm_count:
              stormCount,
          }),
        }
      );


      if (!response.ok) {
        throw new Error(
          `Simulator returned ${response.status}`
        );
      }


      const data =
        (await response.json()) as SimulationResult;

      setResult(data);

    } catch (err) {
      console.error(err);

      setError(
        "Unable to run the simulation."
      );

    } finally {
      setLoading(false);
    }
  }


  function resetSimulation() {
    setKpIndex(2);
    setFlareClass("NONE");
    setFlareMagnitude(1);
    setEarthDirectedCmes(0);
    setCmeSpeed(0);
    setStormCount(0);
    setResult(null);
    setError(null);
  }


  return (
    <section className="mt-6 rounded-2xl border border-white/10 bg-white/[0.03] p-6">

      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">

        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-violet-400">
            What-If Simulator
          </p>

          <h3 className="mt-2 text-2xl font-semibold">
            Simulate Space-Weather Conditions
          </h3>

          <p className="mt-2 max-w-2xl text-sm text-gray-500">
            Adjust hypothetical conditions and
            evaluate how MissionGuard would respond.
            Simulations do not alter the live
            NASA or NOAA assessment.
          </p>
        </div>


        <span className="w-fit rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-semibold text-violet-300">
          SIMULATION MODE
        </span>

      </div>


      <form
        onSubmit={runSimulation}
        className="mt-8 grid gap-6 lg:grid-cols-2"
      >

        <SimulatorField
          label="Kp Index"
          value={kpIndex.toFixed(1)}
        >
          <input
            type="range"
            min="0"
            max="9"
            step="0.1"
            value={kpIndex}
            onChange={(event) =>
              setKpIndex(
                Number(
                  event.target.value
                )
              )
            }
            className="w-full accent-violet-400"
          />

          <div className="mt-2 flex justify-between text-xs text-gray-600">
            <span>0 Quiet</span>
            <span>5 Storm</span>
            <span>9 Extreme</span>
          </div>
        </SimulatorField>


        <SimulatorField
          label="Solar Flare"
          value={
            flareClass === "NONE"
              ? "None"
              : `${flareClass}${flareMagnitude.toFixed(
                  1
                )}`
          }
        >
          <div className="grid grid-cols-2 gap-3">

            <select
              value={flareClass}
              onChange={(event) =>
                setFlareClass(
                  event.target
                    .value as FlareClass
                )
              }
              className="rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm outline-none focus:border-violet-400/50"
            >
              <option value="NONE">
                None
              </option>

              <option value="C">
                C-Class
              </option>

              <option value="M">
                M-Class
              </option>

              <option value="X">
                X-Class
              </option>
            </select>


            <input
              type="number"
              min="1"
              max="9.9"
              step="0.1"
              disabled={
                flareClass === "NONE"
              }
              value={flareMagnitude}
              onChange={(event) =>
                setFlareMagnitude(
                  Number(
                    event.target.value
                  )
                )
              }
              className="rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm outline-none disabled:cursor-not-allowed disabled:opacity-40 focus:border-violet-400/50"
            />

          </div>
        </SimulatorField>


        <SimulatorField
          label="Earth-Directed CMEs"
          value={String(
            earthDirectedCmes
          )}
        >
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            value={
              earthDirectedCmes
            }
            onChange={(event) =>
              setEarthDirectedCmes(
                Number(
                  event.target.value
                )
              )
            }
            className="w-full accent-violet-400"
          />
        </SimulatorField>


        <SimulatorField
          label="Fastest CME Speed"
          value={`${cmeSpeed} km/s`}
        >
          <input
            type="range"
            min="0"
            max="3000"
            step="50"
            value={cmeSpeed}
            onChange={(event) =>
              setCmeSpeed(
                Number(
                  event.target.value
                )
              )
            }
            className="w-full accent-violet-400"
          />

          <div className="mt-2 flex justify-between text-xs text-gray-600">
            <span>0</span>
            <span>1500</span>
            <span>3000 km/s</span>
          </div>
        </SimulatorField>


        <SimulatorField
          label="Geomagnetic Storm Events"
          value={String(
            stormCount
          )}
        >
          <input
            type="range"
            min="0"
            max="5"
            step="1"
            value={stormCount}
            onChange={(event) =>
              setStormCount(
                Number(
                  event.target.value
                )
              )
            }
            className="w-full accent-violet-400"
          />
        </SimulatorField>


        <div className="flex items-end gap-3">

          <button
            type="submit"
            disabled={loading}
            className="flex-1 rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400 disabled:opacity-50"
          >
            {loading
              ? "Running..."
              : "Run Simulation"}
          </button>


          <button
            type="button"
            onClick={
              resetSimulation
            }
            className="rounded-xl border border-white/10 bg-white/5 px-5 py-3 text-sm transition hover:bg-white/10"
          >
            Reset
          </button>

        </div>

      </form>


      {error && (
        <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}


      {result && (
        <div className="mt-8 border-t border-white/10 pt-8">

          <div className="mb-5 flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Simulated Mission Assessment
              </p>

              <h4 className="mt-1 text-xl font-semibold">
                Scenario Result
              </h4>
            </div>


            <span
              className={`rounded-full border px-4 py-2 text-sm font-bold ${getRecommendationStyle(
                result.mission
                  .recommendation
              )}`}
            >
              {
                result.mission
                  .recommendation
              }
            </span>

          </div>


          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

            <ResultCard
              label="Risk Score"
              value={`${result.mission.risk_score}/100`}
              style={
                getRiskTextStyle(
                  result.mission
                    .risk_level
                )
              }
            />


            <ResultCard
              label="Readiness"
              value={`${result.mission.mission_readiness}%`}
              style={
                getReadinessStyle(
                  result.mission
                    .mission_readiness
                )
              }
            />


            <ResultCard
              label="Risk Level"
              value={
                result.mission
                  .risk_level
              }
              style={
                getRiskTextStyle(
                  result.mission
                    .risk_level
                )
              }
            />


            <ResultCard
              label="Decision"
              value={
                result.mission
                  .recommendation
              }
              style={
                getRiskTextStyle(
                  result.mission
                    .risk_level
                )
              }
            />

          </div>


          <div className="mt-6 grid gap-5 md:grid-cols-2">

            <SimulationFactor
              label="Geomagnetic"
              value={
                result.risk_factors
                  .geomagnetic
              }
              max={35}
            />

            <SimulationFactor
              label="Solar Flare"
              value={
                result.risk_factors
                  .solar_flare
              }
              max={25}
            />

            <SimulationFactor
              label="CME"
              value={
                result.risk_factors
                  .cme
              }
              max={30}
            />

            <SimulationFactor
              label="Storm"
              value={
                result.risk_factors
                  .storm
              }
              max={10}
            />

          </div>


          <p className="mt-6 text-xs text-gray-600">
            {result.simulation_notice}
          </p>

        </div>
      )}

    </section>
  );
}


function SimulatorField({
  label,
  value,
  children,
}: {
  label: string;
  value: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/10 p-5">

      <div className="mb-4 flex items-center justify-between gap-3">

        <label className="text-sm text-gray-400">
          {label}
        </label>

        <span className="text-sm font-semibold text-white">
          {value}
        </span>

      </div>

      {children}

    </div>
  );
}


function ResultCard({
  label,
  value,
  style,
}: {
  label: string;
  value: string;
  style: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/10 p-5">

      <p className="text-xs uppercase tracking-wider text-gray-500">
        {label}
      </p>

      <p
        className={`mt-2 text-2xl font-semibold ${style}`}
      >
        {value}
      </p>

    </div>
  );
}


function SimulationFactor({
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

      <div className="mb-2 flex justify-between text-sm">

        <span className="text-gray-400">
          {label}
        </span>

        <span>
          {value}/{max}
        </span>

      </div>


      <div className="h-2 overflow-hidden rounded-full bg-white/10">

        <div
          className={
            `h-full rounded-full ${
              percentage >= 75
                ? "bg-red-500"
                : percentage >= 50
                  ? "bg-orange-400"
                  : percentage >= 25
                    ? "bg-amber-400"
                    : "bg-emerald-400"
            }`
          }
          style={{
            width:
              `${percentage}%`,
          }}
        />

      </div>

    </div>
  );
}


function getRecommendationStyle(
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


function getRiskTextStyle(
  risk: string
) {
  switch (risk) {
    case "LOW":
      return "text-emerald-300";

    case "MODERATE":
      return "text-amber-300";

    case "HIGH":
      return "text-orange-300";

    case "CRITICAL":
      return "text-red-300";

    default:
      return "text-gray-300";
  }
}


function getReadinessStyle(
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
