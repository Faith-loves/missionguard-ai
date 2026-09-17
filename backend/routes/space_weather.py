import asyncio

from fastapi import APIRouter, Query

from services.nasa_service import (
    get_cmes,
    get_geomagnetic_storms,
    get_solar_flares,
)

from services.noaa_service import get_kp_index

from services.space_weather_processor import (
    summarize_space_weather,
)


router = APIRouter(
    prefix="/space-weather",
    tags=["Space Weather"],
)


@router.get("/solar-flares")
async def solar_flares(days: int = Query(default=7, ge=1, le=30)):
    result = await get_solar_flares(days)

    return {
        "source": "NASA DONKI",
        "available": result["available"],
        "count": len(result["data"]),
        "events": result["data"],
        "error": result.get("error"),
    }


@router.get("/cmes")
async def cmes(days: int = Query(default=7, ge=1, le=30)):
    result = await get_cmes(days)

    return {
        "source": "NASA DONKI",
        "available": result["available"],
        "count": len(result["data"]),
        "events": result["data"],
        "error": result.get("error"),
    }


@router.get("/geomagnetic-storms")
async def geomagnetic_storms(days: int = Query(default=7, ge=1, le=30)):
    result = await get_geomagnetic_storms(days)

    return {
        "source": "NASA DONKI",
        "available": result["available"],
        "count": len(result["data"]),
        "events": result["data"],
        "error": result.get("error"),
    }


@router.get("/kp-index")
async def kp_index():
    result = await get_kp_index()

    return {
        "source": "NOAA SWPC",
        "available": result["available"],
        "latest": result["latest"],
        "history": result["history"],
        "error": result["error"],
    }


@router.get("/current")
async def current_space_weather(days: int = Query(default=7, ge=1, le=30)):
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

    return {
        "status": "online",
        "period_days": days,

        "solar_flares": {
            "source": "NASA DONKI",
            "available": flare_result["available"],
            "count": len(flare_result["data"]),
            "events": flare_result["data"],
            "error": flare_result.get("error"),
        },

        "cmes": {
            "source": "NASA DONKI",
            "available": cme_result["available"],
            "count": len(cme_result["data"]),
            "events": cme_result["data"],
            "error": cme_result.get("error"),
        },

        "geomagnetic_storms": {
            "source": "NASA DONKI",
            "available": storm_result["available"],
            "count": len(storm_result["data"]),
            "events": storm_result["data"],
            "error": storm_result.get("error"),
        },

        "kp_index": {
            "source": "NOAA SWPC",
            "available": kp_result["available"],
            "latest": kp_result["latest"],
            "error": kp_result["error"],
        },
    }


@router.get("/summary")
async def space_weather_summary(days: int = Query(default=7, ge=1, le=30)):
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

    return {
        "status": "online",
        "period_days": days,
        "summary": summary,

        "provider_status": {
            "nasa_flares": flare_result.get(
                "available",
                False,
            ),

            "nasa_cmes": cme_result.get(
                "available",
                False,
            ),

            "nasa_storms": storm_result.get(
                "available",
                False,
            ),

            "noaa_kp": kp_result.get(
                "available",
                False,
            ),
        },
    }
