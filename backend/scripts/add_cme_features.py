import json
from pathlib import Path

import pandas as pd


CME_FILE = Path(
    "data/historical_cmes.json"
)

FORECAST_FILE = Path(
    "data/missionguard_forecast_ml.csv"
)

OUTPUT_FILE = Path(
    "data/missionguard_forecast_ml_cme.csv"
)


# -------------------------------------------------
# Load existing forecast dataset
# -------------------------------------------------

forecast_df = pd.read_csv(
    FORECAST_FILE,
    parse_dates=["date"],
)


# -------------------------------------------------
# Load NASA CME history
# -------------------------------------------------

with CME_FILE.open(
    "r",
    encoding="utf-8",
) as file:
    cmes = json.load(file)


records = []


for cme in cmes:
    start_time = cme.get(
        "startTime"
    )

    if not start_time:
        continue

    event_date = pd.to_datetime(
        start_time,
        utc=True,
        errors="coerce",
    )

    if pd.isna(event_date):
        continue

    analyses = (
        cme.get("cmeAnalyses")
        or []
    )

    max_speed = 0.0
    earth_directed = False

    for analysis in analyses:
        speed = analysis.get(
            "speed"
        )

        if speed is not None:
            try:
                speed_value = float(
                    speed
                )

                max_speed = max(
                    max_speed,
                    speed_value,
                )

            except (
                ValueError,
                TypeError,
            ):
                pass

        enlil_list = (
            analysis.get(
                "enlilList"
            )
            or []
        )

        for enlil in enlil_list:
            if (
                enlil.get(
                    "isEarthGB"
                ) is True
                or
                enlil.get(
                    "isEarthMinorImpact"
                ) is True
            ):
                earth_directed = True


    records.append(
        {
            "date":
                event_date
                .tz_convert(None)
                .normalize(),

            "cme_speed":
                max_speed,

            "earth_directed":
                int(
                    earth_directed
                ),

            "fast_cme":
                int(
                    max_speed >= 1000
                ),
        }
    )


cme_df = pd.DataFrame(
    records
)


# -------------------------------------------------
# Aggregate CME features by day
# -------------------------------------------------

daily_cme = (
    cme_df
    .groupby("date")
    .agg(
        cme_count=(
            "date",
            "size",
        ),

        earth_directed_cme_count=(
            "earth_directed",
            "sum",
        ),

        max_cme_speed=(
            "cme_speed",
            "max",
        ),

        fast_cme_count=(
            "fast_cme",
            "sum",
        ),
    )
    .reset_index()
)


# -------------------------------------------------
# Merge into forecast dataset
# -------------------------------------------------

df = forecast_df.merge(
    daily_cme,
    on="date",
    how="left",
)


cme_columns = [
    "cme_count",
    "earth_directed_cme_count",
    "max_cme_speed",
    "fast_cme_count",
]


df[cme_columns] = (
    df[cme_columns]
    .fillna(0)
)


# -------------------------------------------------
# CME lag features
# -------------------------------------------------

for lag in [1, 2, 3]:
    for column in cme_columns:
        df[
            f"{column}_lag_{lag}"
        ] = (
            df[column]
            .shift(lag)
            .fillna(0)
        )


# -------------------------------------------------
# 3-day CME activity
#
# Current day + previous 2 days.
# Target begins tomorrow, so this does not
# use future information.
# -------------------------------------------------

df["cme_count_3d"] = (
    df["cme_count"]
    .rolling(3)
    .sum()
    .fillna(0)
)

df["earth_directed_cme_3d"] = (
    df[
        "earth_directed_cme_count"
    ]
    .rolling(3)
    .sum()
    .fillna(0)
)

df["fast_cme_3d"] = (
    df["fast_cme_count"]
    .rolling(3)
    .sum()
    .fillna(0)
)

df["max_cme_speed_3d"] = (
    df["max_cme_speed"]
    .rolling(3)
    .max()
    .fillna(0)
)


# -------------------------------------------------
# Save
# -------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False,
)


print(
    "\nCME FEATURES ADDED"
)

print(
    "=================================="
)

print(
    "Historical CME events:",
    len(cmes),
)

print(
    "Days with CME activity:",
    int(
        (
            df["cme_count"] > 0
        ).sum()
    ),
)

print(
    "Days with Earth-directed CME:",
    int(
        (
            df[
                "earth_directed_cme_count"
            ] > 0
        ).sum()
    ),
)

print(
    "Days with >=1000 km/s CME:",
    int(
        (
            df[
                "fast_cme_count"
            ] > 0
        ).sum()
    ),
)

print(
    "Maximum CME speed:",
    df[
        "max_cme_speed"
    ].max(),
)

print(
    "\nTARGET DISTRIBUTION"
)

print(
    df[
        "storm_next_3d"
    ].value_counts()
)

print(
    "\nSaved to:",
    OUTPUT_FILE,
)
