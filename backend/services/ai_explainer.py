import os
from dotenv import load_dotenv

load_dotenv()
from typing import Any


GRANITE_MODEL_ID = (
    "ibm/granite-4-h-small"
)


def watsonx_configured() -> bool:
    return all(
        [
            os.getenv(
                "WATSONX_API_KEY"
            ),
            os.getenv(
                "WATSONX_PROJECT_ID"
            ),
            os.getenv(
                "WATSONX_URL"
            ),
        ]
    )


def build_prompt(
    assessment: dict[str, Any],
    mode: str,
) -> str:

    mission = assessment.get(
        "mission",
        {},
    )

    factors = assessment.get(
        "risk_factors",
        {},
    ) or {}

    weather = assessment.get(
        "space_weather",
        {},
    ) or assessment.get(
        "simulated_space_weather",
        {},
    ) or {}


    solar = weather.get(
        "solar_activity",
        {},
    )

    cme = weather.get(
        "cme_activity",
        {},
    )

    geomagnetic = weather.get(
        "geomagnetic_activity",
        {},
    )


    return f"""
You are the explanation layer for
MissionGuard AI, an educational
space-weather decision-support prototype.

IMPORTANT RULES:
- Use ONLY the facts supplied below.
- Do not change or recalculate the risk score.
- Do not change the risk level.
- Do not change the mission recommendation.
- Do not invent NASA, NOAA, spacecraft,
  mission, launch-site, or engineering data.
- Do not claim that this is an official
  NASA or NOAA launch decision.
- Do not say that a spacecraft, crew,
  electronics, launch vehicle, satellite,
  or mission is safe, unsafe, threatened,
  protected, or exposed to unacceptable risk.
- Do not refer to proceeding with or
  cancelling an actual launch unless that
  information was explicitly supplied.
- Treat GO, CAUTION, DELAY, and NO-GO only
  as MissionGuard prototype classifications.
- Do not convert the prototype recommendation
  into operational aerospace advice.
- Never tell the user to proceed with, delay,
  suspend, cancel, postpone, or approve a
  real launch or mission.
- Never say that launch plans should change.
- In simulation mode, call all supplied values
  simulated or hypothetical, never measured,
  observed, recorded, or detected.
- Use only MissionGuard's actual factor names:
  geomagnetic, solar flare, CME, and storm.
- Do not invent technical components such as
  solar-wind exposure, particle environment,
  spacecraft vulnerability, radiation dose,
  or hardware effects.
- Explain only how the supplied numerical
  factors contributed to the deterministic
  MissionGuard score.
- Explain why the deterministic MissionGuard
  risk engine reached its result.
- Be concise and professional.
- Write 2 short paragraphs.
- In the second paragraph, identify the
  most important risk driver and mention
  any reassuring conditions.
- If this is a simulation, clearly say that
  the scenario is hypothetical.

Assessment mode: {mode}

MISSION RESULT
Risk score:
{mission.get("risk_score")}/100

Mission readiness:
{mission.get("mission_readiness")}%

Risk level:
{mission.get("risk_level")}

Recommendation:
{mission.get("recommendation")}

RISK FACTORS
Geomagnetic:
{factors.get("geomagnetic")}/35

Solar flare:
{factors.get("solar_flare")}/25

CME:
{factors.get("cme")}/30

Geomagnetic storms:
{factors.get("storm")}/10

SPACE WEATHER
Kp index:
{geomagnetic.get("latest_kp")}

Recent storm count:
{geomagnetic.get("storm_count")}

Strongest flare:
{solar.get("strongest_flare")}

Total flares:
{solar.get("total_flares")}

Total CMEs:
{cme.get("total_cmes")}

Earth-directed CMEs:
{cme.get("earth_directed_cmes")}

Fastest CME speed:
{cme.get("fastest_speed_km_s")} km/s

Explain this assessment now.
""".strip()


def build_fallback_explanation(
    assessment: dict[str, Any],
    mode: str,
) -> str:

    mission = assessment.get(
        "mission",
        {},
    )

    factors = assessment.get(
        "risk_factors",
        {},
    ) or {}

    weather = assessment.get(
        "space_weather",
        {},
    ) or assessment.get(
        "simulated_space_weather",
        {},
    ) or {}


    solar = weather.get(
        "solar_activity",
        {},
    )

    cme = weather.get(
        "cme_activity",
        {},
    )

    geomagnetic = weather.get(
        "geomagnetic_activity",
        {},
    )


    factor_names = {
        "geomagnetic":
            "geomagnetic activity",

        "solar_flare":
            "solar flare activity",

        "cme":
            "CME activity",

        "storm":
            "geomagnetic storm activity",
    }


    dominant_key = None

    if factors:
        dominant_key = max(
            factors,
            key=lambda key:
                factors.get(
                    key,
                    0,
                ),
        )


    dominant_name = (
        factor_names.get(
            dominant_key,
            "space-weather activity",
        )
    )


    prefix = (
        "This hypothetical scenario"
        if mode == "simulation"
        else "The current assessment"
    )


    first_paragraph = (
        f"{prefix} has a MissionGuard risk "
        f"score of "
        f"{mission.get('risk_score')}/100, "
        f"with "
        f"{mission.get('mission_readiness')}% "
        f"mission readiness. The resulting "
        f"risk level is "
        f"{mission.get('risk_level')}, so "
        f"the deterministic risk engine "
        f"recommends "
        f"{mission.get('recommendation')}."
    )


    details = []


    earth_cmes = cme.get(
        "earth_directed_cmes"
    )

    cme_speed = cme.get(
        "fastest_speed_km_s"
    )

    kp = geomagnetic.get(
        "latest_kp"
    )

    storms = geomagnetic.get(
        "storm_count"
    )

    flare = solar.get(
        "strongest_flare"
    )


    if earth_cmes is not None:
        details.append(
            f"{earth_cmes} Earth-directed "
            f"CME(s) were recorded"
        )


    if cme_speed is not None:
        details.append(
            f"the fastest CME reached "
            f"{cme_speed} km/s"
        )


    if kp is not None:
        details.append(
            f"the Kp index is {kp}"
        )


    if storms is not None:
        details.append(
            f"recent storm count is {storms}"
        )


    if flare:
        details.append(
            f"the strongest flare is {flare}"
        )


    conditions = (
        "; ".join(details)
        if details
        else
        "available space-weather conditions"
    )


    second_paragraph = (
        f"The largest risk contribution comes "
        f"from {dominant_name}. Supporting "
        f"conditions include {conditions}. "
        f"This explanation describes the "
        f"MissionGuard educational risk model "
        f"and is not an official NASA or NOAA "
        f"mission decision."
    )


    return (
        first_paragraph
        + "\n\n"
        + second_paragraph
    )


def generate_granite_explanation(
    assessment: dict[str, Any],
    mode: str,
) -> str:

    from ibm_watsonx_ai import (
        APIClient,
        Credentials,
    )

    from ibm_watsonx_ai.foundation_models import (
        ModelInference,
    )


    credentials = Credentials(
        url=os.environ[
            "WATSONX_URL"
        ],

        api_key=os.environ[
            "WATSONX_API_KEY"
        ],
    )


    client = APIClient(
        credentials
    )


    model = ModelInference(
        model_id=GRANITE_MODEL_ID,

        api_client=client,

        project_id=os.environ[
            "WATSONX_PROJECT_ID"
        ],

        params={
            "time_limit": 10000,
            "max_new_token": 300,
        },
    )


    messages = [
        {
            "role": "system",

            "content": (
                "You explain deterministic "
                "MissionGuard space-weather "
                "risk assessments. Never alter "
                "the supplied score, level, or "
                "recommendation."
            ),
        },

        {
            "role": "user",

            "content": build_prompt(
                assessment,
                mode,
            ),
        },
    ]


    response = model.chat(
        messages=messages
    )


    return (
        response[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ].strip()
    )


DISALLOWED_EXPLANATION_TERMS = [
    "spacecraft electronics",
    "spacecraft avionics",
    "communications",
    "navigation systems",
    "orbital decay",
    "radiation dose",
    "particle flux",
    "hardware damage",
    "mission safety",
    "operational safety",
    "launch safety",
    "operational margin",
    "suspend",
    "cancel",
    "postpone",
    "proceed with the launch",
    "launch plans",
    "unacceptable risk",
]


def explanation_is_grounded(
    explanation: str,
    mode: str,
) -> bool:
    text = explanation.lower()

    for term in DISALLOWED_EXPLANATION_TERMS:
        if term.lower() in text:
            return False

    if mode == "simulation":
        simulation_disallowed = [
            "recorded",
            "measured",
            "observed",
            "detected",
        ]

        for term in simulation_disallowed:
            if term in text:
                return False

    return True


def explain_assessment(
    assessment: dict[str, Any],
    mode: str = "live",
):
    if mode not in {
        "live",
        "simulation",
    }:
        mode = "live"


    if watsonx_configured():
        try:
            explanation = (
                generate_granite_explanation(
                    assessment,
                    mode,
                )
            )

            if not explanation_is_grounded(
                explanation,
                mode,
            ):
                return {
                    "provider":
                        "fallback",

                    "model":
                        GRANITE_MODEL_ID,

                    "ai_generated":
                        False,

                    "explanation":
                        build_fallback_explanation(
                            assessment,
                            mode,
                        ),

                    "warning":
                        (
                            "Granite generated claims "
                            "outside MissionGuard's "
                            "available evidence, so "
                            "the response was rejected "
                            "and replaced with the "
                            "grounded explanation."
                        ),
                }

            return {
                "provider":
                    "watsonx",

                "model":
                    GRANITE_MODEL_ID,

                "ai_generated":
                    True,

                "explanation":
                    explanation,
            }

        except Exception as exc:
            fallback = (
                build_fallback_explanation(
                    assessment,
                    mode,
                )
            )

            return {
                "provider":
                    "fallback",

                "model":
                    None,

                "ai_generated":
                    False,

                "explanation":
                    fallback,

                "warning":
                    (
                        "IBM Granite was "
                        "unavailable, so "
                        "MissionGuard used its "
                        "deterministic explanation "
                        "fallback."
                    ),

                "error_type":
                    type(exc).__name__,
            }


    return {
        "provider":
            "fallback",

        "model":
            None,

        "ai_generated":
            False,

        "explanation":
            build_fallback_explanation(
                assessment,
                mode,
            ),

        "warning":
            (
                "watsonx credentials are not "
                "configured yet."
            ),
    }






