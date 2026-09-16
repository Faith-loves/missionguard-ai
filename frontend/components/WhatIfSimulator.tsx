"use client";

import {
  FormEvent,
  ReactNode,
  useState,
} from "react";

import {
  addDoc,
  collection,
  serverTimestamp,
} from "firebase/firestore";

import {
  auth,
  db,
} from "../lib/firebase";


type FlareClass =
  | "NONE"
  | "C"
  | "M"
  | "X";


type SimulationScenario = {
  kp_index: number;
  flare_class: FlareClass;
  flare_magnitude: number;
  earth_directed_cmes: number;
  fastest_cme_speed_km_s: number;
  storm_count: number;
};


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

  simulated_space_weather: {
    solar_activity: {
      total_flares: number;
      strongest_flare: string | null;
    };

    cme_activity: {
      total_cmes: number;
      earth_directed_cmes: number;
      fastest_speed_km_s: number;
    };

    geomagnetic_activity: {
      latest_kp: number;
      storm_count: number;
    };
  };
};


type ExplanationResult = {
  provider: string;
  model: string | null;
  ai_generated: boolean;
  explanation: string;
  warning?: string;
};


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


export default function WhatIfSimulator() {
  const [kpIndex, setKpIndex] =
    useState(2);

  const [
    flareClass,
    setFlareClass,
  ] = useState<FlareClass>(
    "NONE"
  );

  const [
    flareMagnitude,
    setFlareMagnitude,
  ] = useState(1);

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


  const [
    result,
    setResult,
  ] =
    useState<SimulationResult | null>(
      null
    );


  const [
    lastScenario,
    setLastScenario,
  ] =
    useState<SimulationScenario | null>(
      null
    );


  const [
    explanation,
    setExplanation,
  ] =
    useState<ExplanationResult | null>(
      null
    );


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    explanationLoading,
    setExplanationLoading,
  ] = useState(false);


  const [
    saving,
    setSaving,
  ] = useState(false);


  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    );


  const [
    explanationError,
    setExplanationError,
  ] =
    useState<string | null>(
      null
    );


  const [
    saveMessage,
    setSaveMessage,
  ] =
    useState<string | null>(
      null
    );


  const [
    saveError,
    setSaveError,
  ] =
    useState<string | null>(
      null
    );


  async function runSimulation(
    event: FormEvent
  ) {
    event.preventDefault();


    const scenario: SimulationScenario = {
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
    };


    try {
      setLoading(true);

      setError(null);

      setExplanation(null);

      setExplanationError(null);

      setSaveMessage(null);

      setSaveError(null);


      const response =
        await fetch(
          `${API_URL}/simulator/evaluate`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify(
                scenario
              ),
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

      setLastScenario(
        scenario
      );

    } catch (err) {
      console.error(err);

      setError(
        "Unable to run the simulation."
      );

    } finally {
      setLoading(false);
    }
  }


  async function generateExplanation() {
    if (!result) {
      return;
    }


    try {
      setExplanationLoading(
        true
      );

      setExplanationError(
        null
      );


      const response =
        await fetch(
          `${API_URL}/ai-explanation/explain`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              mode:
                "simulation",

              mission:
                result.mission,

              risk_factors:
                result.risk_factors,

              space_weather: {
                solar_activity: {
                  total_flares:
                    result
                      .simulated_space_weather
                      .solar_activity
                      .total_flares,

                  strongest_flare:
                    result
                      .simulated_space_weather
                      .solar_activity
                      .strongest_flare,
                },

                cme_activity: {
                  total_cmes:
                    result
                      .simulated_space_weather
                      .cme_activity
                      .total_cmes,

                  earth_directed_cmes:
                    result
                      .simulated_space_weather
                      .cme_activity
                      .earth_directed_cmes,

                  fastest_speed_km_s:
                    result
                      .simulated_space_weather
                      .cme_activity
                      .fastest_speed_km_s,
                },

                geomagnetic_activity: {
                  latest_kp:
                    result
                      .simulated_space_weather
                      .geomagnetic_activity
                      .latest_kp,

                  storm_count:
                    result
                      .simulated_space_weather
                      .geomagnetic_activity
                      .storm_count,
                },
              },
            }),
          }
        );


      if (!response.ok) {
        throw new Error(
          `AI endpoint returned ${response.status}`
        );
      }


      const data =
        (await response.json()) as ExplanationResult;


      setExplanation(
        data
      );

    } catch (err) {
      console.error(err);

      setExplanationError(
        "Unable to generate the scenario explanation."
      );

    } finally {
      setExplanationLoading(
        false
      );
    }
  }


  async function saveSimulation() {
    const user =
      auth.currentUser;


    if (!user) {
      setSaveError(
        "You must be signed in to save simulations."
      );

      return;
    }


    if (
      !result ||
      !lastScenario
    ) {
      setSaveError(
        "Run a simulation before saving."
      );

      return;
    }


    try {
      setSaving(true);

      setSaveError(null);

      setSaveMessage(null);


      const simulationsRef =
        collection(
          db,
          "users",
          user.uid,
          "simulations"
        );


      await addDoc(
        simulationsRef,
        {
          type:
            "what_if_simulation",

          user_email:
            user.email ?? null,

          scenario: {
            kp_index:
              lastScenario.kp_index,

            flare_class:
              lastScenario.flare_class,

            flare_magnitude:
              lastScenario.flare_magnitude,

            earth_directed_cmes:
              lastScenario
                .earth_directed_cmes,

            fastest_cme_speed_km_s:
              lastScenario
                .fastest_cme_speed_km_s,

            storm_count:
              lastScenario.storm_count,
          },

          mission: {
            risk_score:
              result
                .mission
                .risk_score,

            mission_readiness:
              result
                .mission
                .mission_readiness,

            risk_level:
              result
                .mission
                .risk_level,

            recommendation:
              result
                .mission
                .recommendation,
          },

          risk_factors: {
            geomagnetic:
              result
                .risk_factors
                .geomagnetic,

            solar_flare:
              result
                .risk_factors
                .solar_flare,

            cme:
              result
                .risk_factors
                .cme,

            storm:
              result
                .risk_factors
                .storm,
          },

          simulated_space_weather: {
            solar_activity: {
              total_flares:
                result
                  .simulated_space_weather
                  .solar_activity
                  .total_flares,

              strongest_flare:
                result
                  .simulated_space_weather
                  .solar_activity
                  .strongest_flare,
            },

            cme_activity: {
              total_cmes:
                result
                  .simulated_space_weather
                  .cme_activity
                  .total_cmes,

              earth_directed_cmes:
                result
                  .simulated_space_weather
                  .cme_activity
                  .earth_directed_cmes,

              fastest_speed_km_s:
                result
                  .simulated_space_weather
                  .cme_activity
                  .fastest_speed_km_s,
            },

            geomagnetic_activity: {
              latest_kp:
                result
                  .simulated_space_weather
                  .geomagnetic_activity
                  .latest_kp,

              storm_count:
                result
                  .simulated_space_weather
                  .geomagnetic_activity
                  .storm_count,
            },
          },

          granite_explanation:
            explanation
              ? {
                  provider:
                    explanation.provider,

                  model:
                    explanation.model,

                  ai_generated:
                    explanation.ai_generated,

                  explanation:
                    explanation.explanation,

                  warning:
                    explanation.warning ??
                    null,
                }
              : null,

          simulation_notice:
            result.simulation_notice,

          saved_at:
            serverTimestamp(),
        }
      );


      setSaveMessage(
        "Simulation saved successfully."
      );

    } catch (err) {
      console.error(err);

      setSaveError(
        "Unable to save the simulation."
      );

    } finally {
      setSaving(false);
    }
  }


  function resetSimulation() {
    setKpIndex(2);

    setFlareClass(
      "NONE"
    );

    setFlareMagnitude(1);

    setEarthDirectedCmes(0);

    setCmeSpeed(0);

    setStormCount(0);

    setResult(null);

    setLastScenario(null);

    setExplanation(null);

    setError(null);

    setExplanationError(null);

    setSaveMessage(null);

    setSaveError(null);
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
            Simulations do not alter live NASA or
            NOAA data.
          </p>

        </div>


        <span className="w-fit rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-semibold text-violet-300">
          SIMULATION MODE
        </span>

      </div>


      <form
        onSubmit={
          runSimulation
        }
        className="mt-8 grid gap-6 lg:grid-cols-2"
      >

        <SimulatorField
          label="Kp Index"
          value={
            kpIndex.toFixed(1)
          }
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
              value={
                flareClass
              }
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
                flareClass ===
                "NONE"
              }
              value={
                flareMagnitude
              }
              onChange={(event) =>
                setFlareMagnitude(
                  Number(
                    event.target.value
                  )
                )
              }
              className="rounded-xl border border-white/10 bg-[#0C1220] px-4 py-3 text-sm outline-none disabled:opacity-40 focus:border-violet-400/50"
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
            value={
              cmeSpeed
            }
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
            value={
              stormCount
            }
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
            disabled={
              loading
            }
            className="flex-1 rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold transition hover:bg-violet-400 disabled:opacity-50"
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

          <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

            <div>

              <p className="text-sm text-gray-500">
                Simulated Mission Assessment
              </p>

              <h4 className="mt-1 text-xl font-semibold">
                Scenario Result
              </h4>

            </div>


            <div className="flex flex-wrap items-center gap-3">

              <span
                className={`w-fit rounded-full border px-4 py-2 text-sm font-bold ${getRecommendationStyle(
                  result
                    .mission
                    .recommendation
                )}`}
              >
                {
                  result
                    .mission
                    .recommendation
                }
              </span>


              <button
                type="button"
                onClick={
                  saveSimulation
                }
                disabled={
                  saving
                }
                className="rounded-xl border border-violet-400/30 bg-violet-400/10 px-4 py-2 text-sm font-semibold text-violet-200 transition hover:bg-violet-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {saving
                  ? "Saving..."
                  : "Save Simulation"}
              </button>

            </div>

          </div>


          {saveMessage && (
            <div className="mb-5 rounded-xl border border-emerald-400/20 bg-emerald-400/5 p-4 text-sm text-emerald-300">
              {saveMessage}
            </div>
          )}


          {saveError && (
            <div className="mb-5 rounded-xl border border-red-400/20 bg-red-400/5 p-4 text-sm text-red-300">
              {saveError}
            </div>
          )}


          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

            <ResultCard
              label="Risk Score"
              value={`${result.mission.risk_score}/100`}
              style={
                getRiskTextStyle(
                  result
                    .mission
                    .risk_level
                )
              }
            />


            <ResultCard
              label="Readiness"
              value={`${result.mission.mission_readiness}%`}
              style={
                getReadinessStyle(
                  result
                    .mission
                    .mission_readiness
                )
              }
            />


            <ResultCard
              label="Risk Level"
              value={
                result
                  .mission
                  .risk_level
              }
              style={
                getRiskTextStyle(
                  result
                    .mission
                    .risk_level
                )
              }
            />


            <ResultCard
              label="Decision"
              value={
                result
                  .mission
                  .recommendation
              }
              style={
                getRiskTextStyle(
                  result
                    .mission
                    .risk_level
                )
              }
            />

          </div>


          <div className="mt-6 grid gap-5 md:grid-cols-2">

            <SimulationFactor
              label="Geomagnetic"
              value={
                result
                  .risk_factors
                  .geomagnetic
              }
              max={35}
            />


            <SimulationFactor
              label="Solar Flare"
              value={
                result
                  .risk_factors
                  .solar_flare
              }
              max={25}
            />


            <SimulationFactor
              label="CME"
              value={
                result
                  .risk_factors
                  .cme
              }
              max={30}
            />


            <SimulationFactor
              label="Storm"
              value={
                result
                  .risk_factors
                  .storm
              }
              max={10}
            />

          </div>


          <div className="mt-8 rounded-xl border border-violet-400/20 bg-violet-400/[0.04] p-5">

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

              <div>

                <p className="text-sm font-semibold text-violet-300">
                  IBM Granite Scenario Explanation
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  Granite explains the simulated
                  result without changing it.
                </p>

              </div>


              <button
                type="button"
                onClick={
                  generateExplanation
                }
                disabled={
                  explanationLoading
                }
                className="rounded-xl bg-violet-500 px-4 py-2.5 text-sm font-semibold transition hover:bg-violet-400 disabled:opacity-50"
              >
                {explanationLoading
                  ? "Granite is analysing..."
                  : explanation
                    ? "Regenerate Explanation"
                    : "Explain Scenario with Granite"}
              </button>

            </div>


            {explanationError && (
              <p className="mt-4 text-sm text-red-300">
                {explanationError}
              </p>
            )}


            {explanation && (
              <div className="mt-6">

                <div className="mb-3 flex flex-wrap items-center gap-3">

                  <span className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-semibold text-violet-300">
                    {explanation.ai_generated
                      ? "AI GENERATED"
                      : "FALLBACK"}
                  </span>


                  {explanation.model && (
                    <span className="text-xs text-gray-500">
                      {explanation.model}
                    </span>
                  )}

                </div>


                <div className="whitespace-pre-line text-sm leading-7 text-gray-300">
                  {
                    explanation.explanation
                  }
                </div>


                {explanation.warning && (
                  <p className="mt-4 text-xs text-amber-300">
                    {
                      explanation.warning
                    }
                  </p>
                )}

              </div>
            )}

          </div>


          <p className="mt-6 text-xs text-gray-600">
            {
              result.simulation_notice
            }
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
  children: ReactNode;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/10 p-5">

      <div className="mb-4 flex items-center justify-between gap-3">

        <label className="text-sm text-gray-400">
          {label}
        </label>

        <span className="text-sm font-semibold">
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
  switch (
    recommendation
  ) {
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
  if (
    readiness >= 75
  ) {
    return "text-emerald-300";
  }

  if (
    readiness >= 50
  ) {
    return "text-amber-300";
  }

  if (
    readiness >= 25
  ) {
    return "text-orange-300";
  }

  return "text-red-300";
}
