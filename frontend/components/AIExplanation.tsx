"use client";

import { useState } from "react";


type Props = {
  mission: {
    risk_score: number | null;
    mission_readiness: number | null;
    risk_level: string;
    recommendation: string;
  };

  riskFactors: {
    geomagnetic: number;
    solar_flare: number;
    cme: number;
    storm: number;
  } | null;

  spaceWeather: {
    solar_activity: {
      total_flares: number | null;
      strongest_flare: string | null;
    };

    cme_activity: {
      total_cmes: number | null;
      earth_directed_cmes: number | null;
      fastest_speed_km_s: number | null;
    };

    geomagnetic_activity: {
      latest_kp: number | null;
      storm_count: number | null;
    };
  };
};


type ExplanationResponse = {
  status: string;
  provider: string;
  model: string | null;
  ai_generated: boolean;
  explanation: string;
  warning?: string;
};


const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


export default function AIExplanation({
  mission,
  riskFactors,
  spaceWeather,
}: Props) {
  const [result, setResult] =
    useState<ExplanationResponse | null>(
      null
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function generateExplanation() {
    if (!riskFactors) {
      setError(
        "Risk factors are not available."
      );

      return;
    }


    try {
      setLoading(true);
      setError(null);


      const response = await fetch(
        `${API_URL}/ai-explanation/explain`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            mode: "live",

            mission,

            risk_factors:
              riskFactors,

            space_weather: {
              solar_activity: {
                total_flares:
                  spaceWeather
                    .solar_activity
                    .total_flares,

                strongest_flare:
                  spaceWeather
                    .solar_activity
                    .strongest_flare,
              },

              cme_activity: {
                total_cmes:
                  spaceWeather
                    .cme_activity
                    .total_cmes,

                earth_directed_cmes:
                  spaceWeather
                    .cme_activity
                    .earth_directed_cmes,

                fastest_speed_km_s:
                  spaceWeather
                    .cme_activity
                    .fastest_speed_km_s,
              },

              geomagnetic_activity: {
                latest_kp:
                  spaceWeather
                    .geomagnetic_activity
                    .latest_kp,

                storm_count:
                  spaceWeather
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
        (await response.json()) as ExplanationResponse;


      setResult(data);

    } catch (err) {
      console.error(err);

      setError(
        "Unable to generate the AI explanation."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <section className="mt-6 rounded-2xl border border-violet-400/20 bg-violet-400/[0.04] p-6">

      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">

        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-violet-400">
            IBM Granite AI
          </p>

          <h3 className="mt-2 text-xl font-semibold">
            Mission Risk Explanation
          </h3>

          <p className="mt-2 max-w-2xl text-sm text-gray-500">
            Generate a natural-language explanation
            of the current deterministic
            MissionGuard assessment.
          </p>
        </div>


        <button
          type="button"
          onClick={
            generateExplanation
          }
          disabled={loading}
          className="rounded-xl bg-violet-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading
            ? "Granite is analysing..."
            : result
              ? "Regenerate Explanation"
              : "Generate AI Explanation"}
        </button>

      </div>


      {error && (
        <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      )}


      {result && (
        <div className="mt-7">

          <div className="mb-4 flex flex-wrap items-center gap-3">

            <span className="rounded-full border border-violet-400/20 bg-violet-400/10 px-3 py-1 text-xs font-semibold text-violet-300">
              {
                result.ai_generated
                  ? "AI GENERATED"
                  : "FALLBACK"
              }
            </span>


            {result.model && (
              <span className="text-xs text-gray-500">
                {result.model}
              </span>
            )}

          </div>


          <div className="whitespace-pre-line text-sm leading-7 text-gray-300">
            {result.explanation}
          </div>


          {result.warning && (
            <p className="mt-4 text-xs text-amber-300">
              {result.warning}
            </p>
          )}


          <p className="mt-5 border-t border-white/10 pt-4 text-xs text-gray-600">
            Granite explains the assessment only.
            MissionGuard&apos;s deterministic risk
            engine remains responsible for the
            score, risk level, and recommendation.
          </p>

        </div>
      )}

    </section>
  );
}
