from datetime import date, timedelta
import asyncio

import httpx
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    NASA_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


NASA_OPEN_API = (
    "https://api.nasa.gov/DONKI"
)

NASA_CCMC_LEGACY = (
    "https://kauai.ccmc.gsfc.nasa.gov/"
    "DONKI/WS/get"
)

NASA_CCMC_NEW = (
    "https://ccmc.gsfc.nasa.gov/"
    "DONKI-API/get"
)


async def request_endpoint(
    url: str,
    params: dict,
):
    timeout = httpx.Timeout(
        60.0,
        connect=15.0,
    )

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent":
                "MissionGuardAI/1.0"
        },
    ) as client:

        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()


async def fetch_nasa_data(
    endpoint: str,
    days: int = 7,
):
    end_date = date.today()

    start_date = (
        end_date
        - timedelta(days=days)
    )


    common_params = {
        "startDate":
            start_date.isoformat(),

        "endDate":
            end_date.isoformat(),
    }


    providers = [
        {
            "name":
                "NASA Open API",

            "url":
                f"{NASA_OPEN_API}/{endpoint}",

            "params": {
                **common_params,
                "api_key":
                    settings.NASA_API_KEY,
            },
        },

        {
            "name":
                "NASA CCMC Legacy",

            "url":
                (
                    f"{NASA_CCMC_LEGACY}/"
                    f"{endpoint}"
                ),

            "params":
                common_params,
        },

        {
            "name":
                "NASA CCMC New",

            "url":
                (
                    f"{NASA_CCMC_NEW}/"
                    f"{endpoint}"
                ),

            "params":
                common_params,
        },
    ]


    errors = []


    for provider in providers:

        for attempt in range(2):

            try:
                data = await request_endpoint(
                    provider["url"],
                    provider["params"],
                )

                return {
                    "available": True,

                    "data":
                        data
                        if isinstance(
                            data,
                            list,
                        )
                        else [],

                    "error": None,

                    "provider":
                        provider["name"],
                }


            except (
                httpx.HTTPStatusError,
                httpx.RequestError,
            ) as exc:

                errors.append(
                    (
                        f"{provider['name']}: "
                        f"{exc}"
                    )
                )

                if attempt == 0:
                    await asyncio.sleep(2)


    return {
        "available": False,
        "data": [],
        "error":
            " | ".join(errors),
        "provider": None,
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

