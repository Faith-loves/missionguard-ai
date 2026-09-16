import os
import re
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

Storm count:
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
            f"Earth-directed CME count: {earth_cmes}"
            f""
        )


    if cme_speed is not None:
        details.append(
            f"fastest CME speed: "
            f"{cme_speed} km/s"
        )


    if kp is not None:
        details.append(
            f"Kp index: {kp}"
        )


    if storms is not None:
        details.append(
            f"storm count: {storms}"
        )


    if flare:
        details.append(
            f"strongest flare: {flare}"
        )


    conditions = (
        "; ".join(details)
        if details
        else
        "available space-weather conditions"
    )


    second_paragraph = (
        f"The largest risk contribution comes "
        f"from {dominant_name}. Assessment "
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
    assessment: dict[str, Any],
) -> bool:
    text = explanation.lower()

    for term in DISALLOWED_EXPLANATION_TERMS:
        if term.lower() in text:
            return False

    extra_disallowed_terms = [
        "solar-wind hazards",
        "solar wind hazards",
        "other solar-wind",
        "other solar wind",
        "additional non-cme",
        "non-cme threats",
        "other threats",
        "cme onslaught",
        "aggressive series",
        "reassuring note",
    ]

    for term in extra_disallowed_terms:
        if term in text:
            return False

    if mode == "simulation":
        for term in [
            "recorded",
            "measured",
            "observed",
            "detected",
        ]:
            if term in text:
                return False

    # Reject ambiguous score assignments such as:
    # "18 and 10 points respectively".
    if (
        "respectively" in text
        and "point" in text
    ):
        return False

    mission = assessment.get(
        "mission",
        {},
    )

    factors = assessment.get(
        "risk_factors",
        {},
    )

    weather = assessment.get(
        "space_weather",
        {},
    )

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


    def numbers_equal(
        actual: str,
        expected: Any,
    ) -> bool:
        if expected is None:
            return True

        try:
            return abs(
                float(actual)
                - float(expected)
            ) < 0.001

        except (
            TypeError,
            ValueError,
        ):
            return False


    def validate_numeric_claims(
        patterns: list[str],
        expected: Any,
    ) -> bool:
        if expected is None:
            return True

        for pattern in patterns:
            matches = re.finditer(
                pattern,
                explanation,
                flags=re.IGNORECASE,
            )

            for match in matches:
                if not numbers_equal(
                    match.group(1),
                    expected,
                ):
                    return False

        return True


    # ---------------------------------------
    # Validate overall deterministic result.
    # ---------------------------------------

    if not validate_numeric_claims(
        [
            (
                r"risk score"
                r"(?:\s+of|\s+is|:)?"
                r"\s*(\d+(?:\.\d+)?)"
            ),
        ],
        mission.get(
            "risk_score"
        ),
    ):
        return False


    if not validate_numeric_claims(
        [
            (
                r"(?:mission\s+)?readiness"
                r"(?:\s+of|\s+is|:)?"
                r"\s*(\d+(?:\.\d+)?)"
                r"\s*%?"
            ),
            (
                r"(\d+(?:\.\d+)?)"
                r"\s*%\s+"
                r"(?:mission\s+)?readiness"
            ),
        ],
        mission.get(
            "mission_readiness"
        ),
    ):
        return False


    expected_level = str(
        mission.get(
            "risk_level",
            "",
        )
    ).lower()


    level_matches = re.findall(
        (
            r"risk level"
            r"(?:\s+is|:)?"
            r"\s*\**"
            r"(low|moderate|high|critical)"
            r"\**"
        ),
        explanation,
        flags=re.IGNORECASE,
    )


    for claimed_level in level_matches:
        if (
            expected_level
            and claimed_level.lower()
            != expected_level
        ):
            return False


    expected_recommendation = str(
        mission.get(
            "recommendation",
            "",
        )
    ).lower()


    recommendation_matches = re.findall(
        (
            r"(?:recommends?|recommended|"
            r"recommendation(?:\s+is|:)?)"
            r"\s+(?:a\s+)?"
            r"\**"
            r"(go|caution|delay|no-go)"
            r"\**"
        ),
        explanation,
        flags=re.IGNORECASE,
    )


    for claimed_recommendation in recommendation_matches:
        if (
            expected_recommendation
            and claimed_recommendation.lower()
            != expected_recommendation
        ):
            return False


    # ---------------------------------------
    # Validate individual factor scores.
    # ---------------------------------------

    factor_checks = [
        (
            [
                (
                    r"(?:kp(?:\s+index)?|"
                    r"geomagnetic(?:\s+factor)?)"
                    r"[^.!?;\n]{0,100}?"
                    r"(?:adds?|added|"
                    r"contributes?|contributed|"
                    r"reached|score(?:d)?"
                    r"(?:\s+is|:)?|"
                    r"component"
                    r"(?:\s+score)?"
                    r"(?:\s+of|\s+is|:)?)"
                    r"\s*(\d+(?:\.\d+)?)"
                    r"\s*(?:points?|/35)"
                ),
            ],
            factors.get(
                "geomagnetic"
            ),
        ),
        (
            [
                (
                    r"(?:solar\s+flare|"
                    r"x-class|m-class|c-class|"
                    r"\bflare\b)"
                    r"[^.!?;\n]{0,100}?"
                    r"(?:adds?|added|"
                    r"contributes?|contributed|"
                    r"reached|score(?:d)?"
                    r"(?:\s+is|:)?|"
                    r"component"
                    r"(?:\s+score)?"
                    r"(?:\s+of|\s+is|:)?)"
                    r"\s*(\d+(?:\.\d+)?)"
                    r"\s*(?:points?|/25)"
                ),
            ],
            factors.get(
                "solar_flare"
            ),
        ),
        (
            [
                (
                    r"(?:\bcme\b|"
                    r"coronal[-\s]mass ejection)"
                    r"[^.!?;\n]{0,100}?"
                    r"(?:adds?|added|"
                    r"contributes?|contributed|"
                    r"reached|score(?:d)?"
                    r"(?:\s+is|:)?|"
                    r"component"
                    r"(?:\s+score)?"
                    r"(?:\s+of|\s+is|:)?)"
                    r"\s*(\d+(?:\.\d+)?)"
                    r"\s*(?:points?|/30)"
                ),
            ],
            factors.get(
                "cme"
            ),
        ),
        (
            [
                (
                    r"(?:geomagnetic\s+storms?|"
                    r"\bstorm\b)"
                    r"[^.!?;\n]{0,100}?"
                    r"(?:adds?|added|"
                    r"contributes?|contributed|"
                    r"reached|score(?:d)?"
                    r"(?:\s+is|:)?|"
                    r"component"
                    r"(?:\s+score)?"
                    r"(?:\s+of|\s+is|:)?)"
                    r"\s*(\d+(?:\.\d+)?)"
                    r"\s*(?:points?|/10)"
                ),
            ],
            factors.get(
                "storm"
            ),
        ),
    ]


    for patterns, expected in factor_checks:
        if not validate_numeric_claims(
            patterns,
            expected,
        ):
            return False


    # ---------------------------------------
    # Validate scenario/input values.
    # ---------------------------------------

    if not validate_numeric_claims(
        [
            (
                r"kp index"
                r"(?:\s+of|\s+is|:)?"
                r"\s*(\d+(?:\.\d+)?)"
            ),
        ],
        geomagnetic.get(
            "latest_kp"
        ),
    ):
        return False


    if not validate_numeric_claims(
        [
            (
                r"earth[-\s]directed"
                r"\s+cme(?:s|\(s\))?"
                r"(?:\s+count)?"
                r"(?:\s+of|\s+is|:)?"
                r"\s*(\d+(?:\.\d+)?)"
            ),
            (
                r"(\d+(?:\.\d+)?)"
                r"\s+earth[-\s]directed"
                r"\s+cme"
            ),
        ],
        cme.get(
            "earth_directed_cmes"
        ),
    ):
        return False


    if not validate_numeric_claims(
        [
            (
                r"storm count"
                r"(?:\s+of|\s+is|:)?"
                r"\s*(\d+(?:\.\d+)?)"
            ),
        ],
        geomagnetic.get(
            "storm_count"
        ),
    ):
        return False


    expected_flare = solar.get(
        "strongest_flare"
    )


    if expected_flare:
        flare_matches = re.findall(
            (
                r"strongest flare"
                r"(?:\s+is|:)?"
                r"\s*"
                r"([a-z]\d+(?:\.\d+)?)"
            ),
            explanation,
            flags=re.IGNORECASE,
        )


        for claimed_flare in flare_matches:
            if (
                claimed_flare.upper()
                != str(
                    expected_flare
                ).upper()
            ):
                return False


    # ---------------------------------------
    # Validate dominant-factor claims.
    # ---------------------------------------

    numeric_factors = {
        name: value
        for name, value
        in factors.items()
        if isinstance(
            value,
            (int, float),
        )
    }


    if numeric_factors:
        dominant_factor = max(
            numeric_factors,
            key=numeric_factors.get,
        )


        aliases = {
            "geomagnetic":
                "geomagnetic",

            "solar_flare":
                "solar flare",

            "cme":
                "cme",

            "storm":
                "storm",
        }


        dominant_claim = re.search(
            (
                r"(?:largest|dominant|"
                r"most influential|biggest)"
                r"[^.!?]{0,100}?"
                r"(geomagnetic|solar flare|"
                r"cme|storm)"
            ),
            explanation,
            flags=re.IGNORECASE,
        )


        if dominant_claim:
            claimed = (
                dominant_claim
                .group(1)
                .lower()
            )

            expected = aliases.get(
                dominant_factor,
                dominant_factor,
            )


            if claimed != expected:
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
                assessment,
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








