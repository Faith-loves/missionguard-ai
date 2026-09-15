import asyncio
import copy
import time

from fastapi import APIRouter, Query

from services.nasa_service import (
    get_cmes,
    get_geomagnetic_storms,
    get_solar_flares,
)

from services.noaa_service import (
    get_kp_index,
)

from services.space_weather_processor import (
    summarize_space_weather,
)

from services.risk_engine import (
    calculate_mission_risk,
)


router = APIRouter(
    prefix="/mission-risk",
    tags=["Mission Risk"],
)


CACHE_TTL_SECONDS = 300
STALE_FALLBACK_SECONDS = 1800

_cache = {}
_cache_lock = asyncio.Lock()


def format_risk_result(
    result,
):
    """
    Supports MissionGuard's flat risk-engine
    result and also a nested format if the
    engine is changed later.
    """

    if not result:
        return {
            "mission": {
                "risk_score": None,
                "mission_readiness": None,
                "risk_level": "UNKNOWN",
                "recommendation": "HOLD",
            },
            "risk_factors": None,
        }


    if "mission" in result:
        return {
            "mission":
                result.get("mission"),

            "risk_factors":
                result.get(
                    "risk_factors"
                ),
        }


    mission = {
        "risk_score":
            result.get(
                "risk_score"
            ),

        "mission_readiness":
            result.get(
                "mission_readiness"
            ),

        "risk_level":
            result.get(
                "risk_level",
                "UNKNOWN",
            ),

        "recommendation":
            result.get(
                "recommendation",
                "HOLD",
            ),
    }


    return {
        "mission": mission,

        "risk_factors":
            (
                result.get("risk_factors")
                or result.get("factors")
                or result.get("factor_scores")
            ),
    }


async def build_live_assessment(
    days: int,
):
    (
        flare_result,
        cme_result,
        storm_result,
        kp_result,
    ) = await asyncio.gather(
        get_solar_flares(days),
        get_cmes(days),
        get_geomagnetic_storms(days),
        get_kp_index(),
    )


    summary = summarize_space_weather(
        flares=flare_result.get(
            "data",
            [],
        ),

        cmes=cme_result.get(
            "data",
            [],
        ),

        storms=storm_result.get(
            "data",
            [],
        ),

        kp_result=kp_result,

        flare_available=flare_result.get(
            "available",
            False,
        ),

        cme_available=cme_result.get(
            "available",
            False,
        ),

        storm_available=storm_result.get(
            "available",
            False,
        ),
    )


    raw_risk_result = (
        calculate_mission_risk(
            summary
        )
    )


    formatted = format_risk_result(
        raw_risk_result
    )


    return {
        "status": "online",

        "period_days": days,

        "mission":
            formatted["mission"],

        "risk_factors":
            formatted[
                "risk_factors"
            ],

        "data_quality":
            summary.get(
                "data_quality"
            ),

        "space_weather":
            summary,

        "provider_status": {
            "nasa_flares":
                flare_result.get(
                    "available",
                    False,
                ),

            "nasa_cmes":
                cme_result.get(
                    "available",
                    False,
                ),

            "nasa_storms":
                storm_result.get(
                    "available",
                    False,
                ),

            "noaa_kp":
                kp_result.get(
                    "available",
                    False,
                ),
        },

        "provider_sources": {
            "nasa_flares":
                flare_result.get(
                    "provider"
                ),

            "nasa_cmes":
                cme_result.get(
                    "provider"
                ),

            "nasa_storms":
                storm_result.get(
                    "provider"
                ),
        },
    }


@router.get("")
async def get_mission_risk(
    days: int = Query(
        default=7,
        ge=1,
        le=30,
    ),
):
    now = time.monotonic()

    cached = _cache.get(days)


    if cached:
        age = (
            now
            - cached["timestamp"]
        )

        if age < CACHE_TTL_SECONDS:

            response = copy.deepcopy(
                cached["response"]
            )

            response[
                "cache_status"
            ] = "fresh"

            response[
                "cache_age_seconds"
            ] = round(
                age,
                1,
            )

            return response


    async with _cache_lock:

        now = time.monotonic()

        cached = _cache.get(days)


        if cached:
            age = (
                now
                - cached["timestamp"]
            )

            if age < CACHE_TTL_SECONDS:

                response = copy.deepcopy(
                    cached["response"]
                )

                response[
                    "cache_status"
                ] = "fresh"

                response[
                    "cache_age_seconds"
                ] = round(
                    age,
                    1,
                )

                return response


        live_response = (
            await build_live_assessment(
                days
            )
        )


        if (
            live_response[
                "data_quality"
            ]
            == "complete"
        ):

            _cache[days] = {
                "timestamp":
                    time.monotonic(),

                "response":
                    copy.deepcopy(
                        live_response
                    ),
            }


            live_response[
                "cache_status"
            ] = "live"

            live_response[
                "cache_age_seconds"
            ] = 0

            return live_response


        cached = _cache.get(days)


        if cached:

            age = (
                time.monotonic()
                - cached[
                    "timestamp"
                ]
            )

            if (
                age
                <= STALE_FALLBACK_SECONDS
            ):

                response = copy.deepcopy(
                    cached["response"]
                )

                response[
                    "cache_status"
                ] = (
                    "stale-fallback"
                )

                response[
                    "cache_age_seconds"
                ] = round(
                    age,
                    1,
                )

                response[
                    "live_provider_status"
                ] = (
                    live_response[
                        "provider_status"
                    ]
                )

                return response


        live_response[
            "cache_status"
        ] = "unavailable"

        live_response[
            "cache_age_seconds"
        ] = None

        return live_response

