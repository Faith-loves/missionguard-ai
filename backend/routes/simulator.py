from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.risk_engine import calculate_mission_risk


router = APIRouter(
    prefix="/simulator",
    tags=["What-If Simulator"],
)


class SimulationRequest(BaseModel):
    kp_index: float = Field(
        default=2.0,
        ge=0,
        le=9,
    )

    flare_class: Literal[
        "NONE",
        "C",
        "M",
        "X",
    ] = "NONE"

    flare_magnitude: float = Field(
        default=1.0,
        ge=1.0,
        le=9.9,
    )

    earth_directed_cmes: int = Field(
        default=0,
        ge=0,
        le=20,
    )

    fastest_cme_speed_km_s: float = Field(
        default=0,
        ge=0,
        le=5000,
    )

    storm_count: int = Field(
        default=0,
        ge=0,
        le=10,
    )


def build_simulated_summary(
    request: SimulationRequest,
):
    c_count = 0
    m_count = 0
    x_count = 0

    strongest_flare = None


    if request.flare_class != "NONE":
        strongest_flare = (
            f"{request.flare_class}"
            f"{request.flare_magnitude:.1f}"
        )


    if request.flare_class == "C":
        c_count = 1

    elif request.flare_class == "M":
        m_count = 1

    elif request.flare_class == "X":
        x_count = 1


    total_cmes = max(
        request.earth_directed_cmes,
        (
            1
            if request.fastest_cme_speed_km_s > 0
            else 0
        ),
    )


    return {
        "solar_activity": {
            "available": True,
            "total_flares":
                c_count
                + m_count
                + x_count,

            "x_class_flares":
                x_count,

            "m_class_flares":
                m_count,

            "c_class_flares":
                c_count,

            "strongest_flare":
                strongest_flare,
        },

        "cme_activity": {
            "available": True,

            "total_cmes":
                total_cmes,

            "earth_directed_cmes":
                request.earth_directed_cmes,

            "fastest_speed_km_s":
                request.fastest_cme_speed_km_s,
        },

        "geomagnetic_activity": {
            "storm_data_available": True,

            "storm_count":
                request.storm_count,

            "kp_available": True,

            "latest_kp":
                request.kp_index,

            "kp_time":
                "SIMULATION",
        },

        "data_quality": "complete",

        "sources": {
            "solar_flares": True,
            "cmes": True,
            "geomagnetic_storms": True,
            "kp_index": True,
        },
    }


def format_result(result):
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


    factors = (
        result.get("risk_factors")
        or result.get("factors")
        or result.get("factor_scores")
    )


    return {
        "mission": mission,
        "risk_factors": factors,
    }


@router.post("/evaluate")
def evaluate_simulation(
    request: SimulationRequest,
):
    summary = build_simulated_summary(
        request
    )

    raw_result = (
        calculate_mission_risk(
            summary
        )
    )

    result = format_result(
        raw_result
    )


    return {
        "status": "simulated",

        "simulation_notice":
            (
                "Educational what-if assessment. "
                "This does not modify live "
                "NASA or NOAA data."
            ),

        "inputs":
            request.model_dump(),

        "mission":
            result["mission"],

        "risk_factors":
            result[
                "risk_factors"
            ],

        "simulated_space_weather":
            summary,
    }
