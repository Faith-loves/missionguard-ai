from datetime import date, timedelta
import asyncio

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NASA_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()


NASA_BASE_URL = "https://api.nasa.gov/DONKI"


async def fetch_nasa_data(
    endpoint: str,
    days: int = 7,
):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    url = f"{NASA_BASE_URL}/{endpoint}"

    params = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "api_key": settings.NASA_API_KEY,
    }

    last_error = None

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(
                timeout=30.0
            ) as client:

                response = await client.get(
                    url,
                    params=params,
                    headers={
                        "User-Agent": "MissionGuardAI/1.0"
                    },
                )

                response.raise_for_status()

                return {
                    "available": True,
                    "data": response.json(),
                    "error": None,
                }

        except (
            httpx.HTTPStatusError,
            httpx.RequestError,
        ) as exc:

            last_error = str(exc)

            if attempt < 2:
                await asyncio.sleep(
                    2 * (attempt + 1)
                )

    return {
        "available": False,
        "data": [],
        "error": last_error,
    }


async def get_solar_flares(
    days: int = 7,
):
    return await fetch_nasa_data(
        endpoint="FLR",
        days=days,
    )


async def get_cmes(
    days: int = 7,
):
    return await fetch_nasa_data(
        endpoint="CME",
        days=days,
    )


async def get_geomagnetic_storms(
    days: int = 7,
):
    return await fetch_nasa_data(
        endpoint="GST",
        days=days,
    )