"use client";

import { useState } from "react";

import {
  addDoc,
  collection,
  serverTimestamp,
} from "firebase/firestore";

import {
  auth,
  db,
} from "../lib/firebase";


type Props = {
  periodDays: number;

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

  dataQuality: string;

  spaceWeather: {
    solar_activity: {
      total_flares: number | null;
      strongest_flare: string | null;
      x_class_flares: number | null;
      m_class_flares: number | null;
      c_class_flares: number | null;
    };

    cme_activity: {
      total_cmes: number | null;
      earth_directed_cmes: number | null;
      fastest_speed_km_s: number | null;
    };

    geomagnetic_activity: {
      latest_kp: number | null;
      storm_count: number | null;
      kp_time: string | null;
    };
  };
};


export default function SaveAssessment({
  periodDays,
  mission,
  riskFactors,
  dataQuality,
  spaceWeather,
}: Props) {
  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState<string | null>(null);

  const [error, setError] =
    useState<string | null>(null);


  async function saveAssessment() {
    const user =
      auth.currentUser;

    if (!user) {
      setError(
        "You must be signed in to save assessments."
      );

      return;
    }


    if (!riskFactors) {
      setError(
        "Risk-factor data is not available."
      );

      return;
    }


    try {
      setSaving(true);
      setError(null);
      setMessage(null);


      const assessmentsRef =
        collection(
          db,
          "users",
          user.uid,
          "assessments"
        );


      await addDoc(
        assessmentsRef,
        {
          type:
            "live_assessment",

          user_email:
            user.email ?? null,

          period_days:
            periodDays,

          mission: {
            risk_score:
              mission.risk_score,

            mission_readiness:
              mission.mission_readiness,

            risk_level:
              mission.risk_level,

            recommendation:
              mission.recommendation,
          },

          risk_factors: {
            geomagnetic:
              riskFactors.geomagnetic,

            solar_flare:
              riskFactors.solar_flare,

            cme:
              riskFactors.cme,

            storm:
              riskFactors.storm,
          },

          data_quality:
            dataQuality,

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

              x_class_flares:
                spaceWeather
                  .solar_activity
                  .x_class_flares,

              m_class_flares:
                spaceWeather
                  .solar_activity
                  .m_class_flares,

              c_class_flares:
                spaceWeather
                  .solar_activity
                  .c_class_flares,
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

              kp_time:
                spaceWeather
                  .geomagnetic_activity
                  .kp_time,
            },
          },

          saved_at:
            serverTimestamp(),
        }
      );


      setMessage(
        "Assessment saved successfully."
      );

    } catch (err) {
      console.error(err);

      setError(
        "Unable to save the assessment."
      );

    } finally {
      setSaving(false);
    }
  }


  return (
    <div className="mt-6 rounded-2xl border border-blue-400/20 bg-blue-400/[0.04] p-6">

      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

        <div>
          <p className="text-sm uppercase tracking-[0.18em] text-blue-400">
            Mission Record
          </p>

          <h3 className="mt-2 text-xl font-semibold">
            Save Current Assessment
          </h3>

          <p className="mt-2 text-sm text-gray-500">
            Store this live MissionGuard assessment
            in your personal account history.
          </p>
        </div>


        <button
          type="button"
          onClick={
            saveAssessment
          }
          disabled={saving}
          className="rounded-xl bg-blue-500 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : "Save Assessment"}
        </button>

      </div>


      {message && (
        <p className="mt-4 text-sm text-emerald-300">
          {message}
        </p>
      )}


      {error && (
        <p className="mt-4 text-sm text-red-300">
          {error}
        </p>
      )}

    </div>
  );
}
