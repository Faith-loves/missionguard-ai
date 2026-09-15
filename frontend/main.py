from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.space_weather import (
    router as space_weather_router,
)

from routes.mission_risk import (
    router as mission_risk_router,
)


app = FastAPI(
    title="MissionGuard AI API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,

    # Allow localhost development frontend
    # regardless of whether Next.js uses
    # port 3000, 3001, etc.
    allow_origin_regex=(
        r"^http://(localhost|127\.0\.0\.1):\d+$"
    ),

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    space_weather_router
)

app.include_router(
    mission_risk_router
)


@app.get("/")
def root():
    return {
        "message": (
            "MissionGuard AI API is running"
        ),
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
