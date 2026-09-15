import asyncio

from fastapi import APIRouter

from services.nasa_service import (
    get_cmes,
    get_geomagnetic_storms,
    get_solar_flares,
)

from services.noaa_service import get_kp_index

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


@router.get("")
async def mission_risk(days: int = 7):
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

    risk = calculate_mission_risk(
        summary
    )

    return {
        "status": "online",
        "period_days": days,
        "mission": {
            "risk_score": risk[
                "risk_score"
            ],

            "mission_readiness": risk[
                "mission_readiness"
            ],

            "risk_level": risk[
                "risk_level"
            ],

            "recommendation": risk[
                "recommendation"
            ],
        },

        "risk_factors": risk[
            "factors"
        ],

        "data_quality": risk[
            "data_quality"
        ],

        "space_weather": summary,
    }