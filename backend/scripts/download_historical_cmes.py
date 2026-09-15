from datetime import date, timedelta
from pathlib import Path
import json
import time

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NASA_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()


START_DATE = date(2023, 7, 11)
END_DATE = date(2025, 7, 9)

CHUNK_DAYS = 7

OUTPUT_FILE = Path(
    "data/historical_cmes.json"
)

PROGRESS_FILE = Path(
    "data/historical_cmes_progress.json"
)


DIRECT_CCMC_URL = (
    "https://kauai.ccmc.gsfc.nasa.gov/"
    "DONKI/WS/get/CME"
)

NASA_API_URL = (
    "https://api.nasa.gov/DONKI/CME"
)


def save_events(events_dict):
    events = list(events_dict.values())

    events.sort(
        key=lambda item:
            item.get("startTime", "")
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            events,
            file,
            indent=2,
        )


def save_progress(last_date):
    with PROGRESS_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "last_completed_date":
                    last_date.isoformat()
            },
            file,
            indent=2,
        )


def load_existing_events():
    if not OUTPUT_FILE.exists():
        return {}

    try:
        with OUTPUT_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            events = json.load(file)

        return {
            event["activityID"]: event
            for event in events
            if event.get("activityID")
        }

    except Exception:
        return {}


def get_resume_date():
    if not PROGRESS_FILE.exists():
        return START_DATE

    try:
        with PROGRESS_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            progress = json.load(file)

        last_completed = date.fromisoformat(
            progress[
                "last_completed_date"
            ]
        )

        return (
            last_completed
            + timedelta(days=1)
        )

    except Exception:
        return START_DATE


def fetch_from_endpoint(
    url,
    start_date,
    end_date,
    use_api_key=False,
):
    params = {
        "startDate":
            start_date.isoformat(),

        "endDate":
            end_date.isoformat(),
    }

    if use_api_key:
        params["api_key"] = (
            settings.NASA_API_KEY
        )

    timeout = httpx.Timeout(
        120.0,
        connect=20.0,
    )

    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers={
            "User-Agent":
                "MissionGuardAI/1.0"
        },
    ) as client:

        response = client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()


def download_chunk(
    start_date,
    end_date,
):
    endpoints = [
        (
            "NASA CCMC",
            DIRECT_CCMC_URL,
            False,
        ),
        (
            "NASA Open API",
            NASA_API_URL,
            True,
        ),
    ]

    errors = []

    for (
        name,
        url,
        use_api_key,
    ) in endpoints:

        for attempt in range(3):
            try:
                print(
                    f"  Trying {name} "
                    f"(attempt {attempt + 1})"
                )

                data = fetch_from_endpoint(
                    url,
                    start_date,
                    end_date,
                    use_api_key,
                )

                print(
                    f"  Success via {name}"
                )

                return data

            except httpx.HTTPStatusError as exc:
                status = (
                    exc.response.status_code
                )

                errors.append(
                    f"{name}: HTTP {status}"
                )

                if status == 429:
                    wait_time = (
                        10 * (attempt + 1)
                    )
                else:
                    wait_time = (
                        5 * (attempt + 1)
                    )

                print(
                    f"  {name} returned "
                    f"HTTP {status}. "
                    f"Waiting {wait_time}s..."
                )

                time.sleep(wait_time)

            except httpx.RequestError as exc:
                errors.append(
                    f"{name}: {exc}"
                )

                wait_time = (
                    5 * (attempt + 1)
                )

                print(
                    f"  {name} network error. "
                    f"Waiting {wait_time}s..."
                )

                time.sleep(wait_time)

    raise RuntimeError(
        "All NASA endpoints failed: "
        + " | ".join(errors)
    )


OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


all_events = load_existing_events()

current_date = get_resume_date()


print(
    "\nMISSIONGUARD HISTORICAL CME DOWNLOAD"
)

print(
    "====================================="
)

print(
    "Starting from:",
    current_date,
)

print(
    "Already saved events:",
    len(all_events),
)


while current_date <= END_DATE:
    chunk_end = min(
        current_date
        + timedelta(
            days=CHUNK_DAYS - 1
        ),
        END_DATE,
    )

    print(
        f"\nFetching "
        f"{current_date.isoformat()} "
        f"to "
        f"{chunk_end.isoformat()}"
    )

    try:
        events = download_chunk(
            current_date,
            chunk_end,
        )

    except Exception as exc:
        print(
            "\nDOWNLOAD PAUSED"
        )

        print(
            "Progress has been preserved."
        )

        print(
            "Error:",
            exc,
        )

        break


    new_count = 0

    for event in events:
        event_id = event.get(
            "activityID"
        )

        if (
            event_id
            and event_id
            not in all_events
        ):
            new_count += 1

        if event_id:
            all_events[
                event_id
            ] = event


    save_events(
        all_events
    )

    save_progress(
        chunk_end
    )


    print(
        "  Events returned:",
        len(events),
    )

    print(
        "  New events:",
        new_count,
    )

    print(
        "  Total saved:",
        len(all_events),
    )


    current_date = (
        chunk_end
        + timedelta(days=1)
    )

    time.sleep(0.5)


events = list(
    all_events.values()
)

events.sort(
    key=lambda item:
        item.get(
            "startTime",
            "",
        )
)


print(
    "\nCURRENT DOWNLOAD STATUS"
)

print(
    "====================================="
)

print(
    "Unique CME events:",
    len(events),
)

if events:
    print(
        "First event:",
        events[0].get(
            "startTime"
        ),
    )

    print(
        "Last event:",
        events[-1].get(
            "startTime"
        ),
    )

print(
    "Saved to:",
    OUTPUT_FILE,
)
