import pandas as pd


INPUT_FILE = "data/missionguard_daily_ml.csv"
OUTPUT_FILE = "data/missionguard_forecast_ml.csv"


df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["date"],
)

df = df.sort_values(
    "date"
).reset_index(drop=True)


# -------------------------------------------------
# Forecast target
#
# 1 = A geomagnetic storm occurs during
#     any of the NEXT 3 days.
#
# Current day is excluded.
# -------------------------------------------------

storm = df["geomagnetic_storm"]

df["storm_next_3d"] = (
    (
        storm.shift(-1).fillna(0)
        + storm.shift(-2).fillna(0)
        + storm.shift(-3).fillna(0)
    ) > 0
).astype(int)


# Remove final 3 rows because their
# future 3-day outcome is incomplete.
df = df.iloc[:-3].copy()


# -------------------------------------------------
# Features available at forecast time
# -------------------------------------------------

feature_columns = [
    # Current observed activity
    "c_flare_count",
    "m_flare_count",
    "x_flare_count",
    "high_speed_stream_count",

    # Previous day
    "c_flare_count_lag_1",
    "m_flare_count_lag_1",
    "x_flare_count_lag_1",
    "high_speed_stream_count_lag_1",

    # Two days ago
    "c_flare_count_lag_2",
    "m_flare_count_lag_2",
    "x_flare_count_lag_2",
    "high_speed_stream_count_lag_2",

    # Three days ago
    "c_flare_count_lag_3",
    "m_flare_count_lag_3",
    "x_flare_count_lag_3",
    "high_speed_stream_count_lag_3",

    # Rolling activity
    "c_flare_3d",
    "m_flare_3d",
    "x_flare_3d",
    "hss_3d",
]


# Keep only what the model needs
output_columns = (
    ["date"]
    + feature_columns
    + ["storm_next_3d"]
)

forecast_df = df[
    output_columns
].copy()


forecast_df.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("\nMISSIONGUARD FORECAST DATASET")
print("------------------------------")

print(
    "Date range:",
    forecast_df["date"].min().date(),
    "to",
    forecast_df["date"].max().date(),
)

print(
    "Total days:",
    len(forecast_df),
)

print("\nTARGET DISTRIBUTION")

print(
    forecast_df[
        "storm_next_3d"
    ].value_counts()
)

print("\nTARGET PERCENTAGES")

print(
    (
        forecast_df[
            "storm_next_3d"
        ]
        .value_counts(
            normalize=True
        )
        * 100
    ).round(2)
)

print("\nSAMPLE POSITIVE DAYS")

print(
    forecast_df[
        forecast_df[
            "storm_next_3d"
        ] == 1
    ]
    .head(10)
    .to_string(index=False)
)

print(
    "\nSaved to:",
    OUTPUT_FILE,
)
