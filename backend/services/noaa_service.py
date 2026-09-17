import math

import httpx


NOAA_KP_URL = (
    "https://services.swpc.noaa.gov/products/"
    "noaa-planetary-k-index.json"
)


async def get_kp_index():
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                NOAA_KP_URL,
                headers={
                    "User-Agent": "MissionGuardAI/1.0"
                },
            )

            response.raise_for_status()
            data = response.json()

        if not isinstance(data, list) or not data:
            return {
                "available": False,
                "latest": None,
                "history": [],
                "error": "NOAA returned no Kp data",
            }

        # NOAA may return either dictionaries
        # or a header row followed by data rows.
        if isinstance(data[0], dict):
            rows = data
        elif isinstance(data[0], list):
            headers = data[0]
            rows = [
                dict(zip(headers, row))
                for row in data[1:]
                if isinstance(row, list)
            ]
        else:
            rows = []

        valid_rows = []
        for row in rows:
            if not isinstance(row, dict) or not row.get("time_tag"):
                continue
            try:
                kp = float(row.get("Kp"))
            except (TypeError, ValueError):
                continue
            if math.isfinite(kp) and 0 <= kp <= 9:
                valid_rows.append({**row, "Kp": kp})

        if not valid_rows:
            return {
                "available": False,
                "latest": None,
                "history": [],
                "error": "No valid NOAA Kp readings found",
            }

        latest = valid_rows[-1]

        return {
            "available": True,
            "latest": latest,
            "history": valid_rows,
            "error": None,
        }

    except httpx.TimeoutException:
        return {
            "available": False,
            "latest": None,
            "history": [],
            "error": "NOAA request timed out",
        }

    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        ValueError,
    ) as exc:
        return {
            "available": False,
            "latest": None,
            "history": [],
            "error": f"NOAA data unavailable ({type(exc).__name__})",
        }
