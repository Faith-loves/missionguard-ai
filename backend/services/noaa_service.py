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

        if not data:
            return {
                "available": False,
                "latest": None,
                "history": [],
                "error": "NOAA returned no Kp data",
            }

        # NOAA may return either dictionaries
        # or a header row followed by data rows.
        if isinstance(data[0], dict):
            valid_rows = [
                row
                for row in data
                if row.get("Kp") is not None
            ]

        else:
            headers = data[0]

            valid_rows = [
                dict(zip(headers, row))
                for row in data[1:]
            ]

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
    ) as exc:
        return {
            "available": False,
            "latest": None,
            "history": [],
            "error": str(exc),
        }