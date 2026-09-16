from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_explainer import (
    explain_assessment,
)


router = APIRouter(
    prefix="/ai-explanation",
    tags=["AI Explanation"],
)


class MissionResult(BaseModel):
    risk_score: int | None = None
    mission_readiness: int | None = None
    risk_level: str
    recommendation: str


class RiskFactors(BaseModel):
    geomagnetic: int = 0
    solar_flare: int = 0
    cme: int = 0
    storm: int = 0


class SolarActivity(BaseModel):
    total_flares: int | None = None
    strongest_flare: str | None = None


class CMEActivity(BaseModel):
    total_cmes: int | None = None
    earth_directed_cmes: int | None = None
    fastest_speed_km_s: float | None = None


class GeomagneticActivity(BaseModel):
    latest_kp: float | None = None
    storm_count: int | None = None


class SpaceWeather(BaseModel):
    solar_activity: SolarActivity
    cme_activity: CMEActivity
    geomagnetic_activity: GeomagneticActivity


class ExplanationRequest(BaseModel):
    mode: Literal[
        "live",
        "simulation",
    ] = "live"

    mission: MissionResult
    risk_factors: RiskFactors
    space_weather: SpaceWeather


@router.post("/explain")
def explain(
    request: ExplanationRequest,
):
    assessment = {
        "mission":
            request.mission.model_dump(),

        "risk_factors":
            request.risk_factors.model_dump(),

        "space_weather":
            request.space_weather.model_dump(),
    }


    result = explain_assessment(
        assessment=assessment,
        mode=request.mode,
    )


    return {
        "status": "success",

        "mode":
            request.mode,

        **result,

        "decision_source":
            "MissionGuard deterministic risk engine",

        "notice":
            (
                "The explanation layer does not "
                "calculate or modify the mission "
                "risk decision."
            ),
    }
