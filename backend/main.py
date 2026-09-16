from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.space_weather import (
    router as space_weather_router,
)

from routes.mission_risk import (
    router as mission_risk_router,
)

from routes.simulator import (
    router as simulator_router,
)

from routes.ai_explanation import (
    router as ai_explanation_router,
)


app = FastAPI(
    title="MissionGuard AI API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    # Allowed MissionGuard frontend origins.
    allow_origins=[
        "https://missionguard-ai-one.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],

    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    space_weather_router
)

app.include_router(
    mission_risk_router
)

app.include_router(
    simulator_router
)

app.include_router(
    ai_explanation_router
)


@app.get("/")
def root():
    return {
        "message":
            "MissionGuard AI API is running",

        "status":
            "online",
    }


@app.get("/health")
def health():
    return {
        "status":
            "healthy",
    }

