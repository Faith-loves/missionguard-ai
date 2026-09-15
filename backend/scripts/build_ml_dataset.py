import pandas as pd


INPUT_FILE = "data/space_weather_unified.csv"
OUTPUT_FILE = "data/missionguard_daily_ml.csv"


df = pd.read_csv(INPUT_FILE)

df["date"] = pd.to_datetime(df["date"])


# -------------------------------------------------
# Create a continuous calendar
# -------------------------------------------------

start_date = df["date"].min()
end_date = df["date"].max()

calendar = pd.DataFrame({
    "date": pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )
})


# -------------------------------------------------
# Solar flare features
# -------------------------------------------------

flare_df = df[
    df["event_type"] == "Solar Flare"
].copy()

flare_df["flare_letter"] = (
    flare_df["class_type"]
    .fillna("")
    .str[0]
    .str.upper()
)


def count_flare_class(letter):
    result = (
        flare_df[
            flare_df["flare_letter"] == letter
        ]
        .groupby("date")
        .size()
        .rename(f"{letter.lower()}_flare_count")
    )

    return result


c_flares = count_flare_class("C")
m_flares = count_flare_class("M")
x_flares = count_flare_class("X")


# -------------------------------------------------
# High-speed stream activity
# -------------------------------------------------

hss = (
    df[
        df["event_type"]
        == "High Speed Stream"
    ]
    .groupby("date")
    .size()
    .rename("high_speed_stream_count")
)


# -------------------------------------------------
# Target: geomagnetic storm occurred that day
# -------------------------------------------------

storm_dates = set(
    df[
        df["event_type"]
        == "Geomagnetic Storm"
    ]["date"]
)


calendar["geomagnetic_storm"] = (
    calendar["date"]
    .isin(storm_dates)
    .astype(int)
)


# -------------------------------------------------
# Merge features
# -------------------------------------------------

daily = calendar.copy()

for feature in [
    c_flares,
    m_flares,
    x_flares,
    hss,
]:
    daily = daily.merge(
        feature,
        on="date",
        how="left",
    )


feature_columns = [
    "c_flare_count",
    "m_flare_count",
    "x_flare_count",
    "high_speed_stream_count",
]

daily[feature_columns] = (
    daily[feature_columns]
    .fillna(0)
    .astype(int)
)


# -------------------------------------------------
# Lagged features
#
# We use PREVIOUS activity to predict a storm,
# rather than using information from after a
# storm has already happened.
# -------------------------------------------------

for lag in [1, 2, 3]:
    for column in feature_columns:
        daily[
            f"{column}_lag_{lag}"
        ] = (
            daily[column]
            .shift(lag)
            .fillna(0)
            .astype(int)
        )


# Rolling 3-day solar activity
daily["m_flare_3d"] = (
    daily["m_flare_count"]
    .shift(1)
    .rolling(3)
    .sum()
    .fillna(0)
)

daily["x_flare_3d"] = (
    daily["x_flare_count"]
    .shift(1)
    .rolling(3)
    .sum()
    .fillna(0)
)

daily["c_flare_3d"] = (
    daily["c_flare_count"]
    .shift(1)
    .rolling(3)
    .sum()
    .fillna(0)
)

daily["hss_3d"] = (
    daily["high_speed_stream_count"]
    .shift(1)
    .rolling(3)
    .sum()
    .fillna(0)
)


# -------------------------------------------------
# Calendar features
# -------------------------------------------------

daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month
daily["day_of_year"] = (
    daily["date"].dt.dayofyear
)


# -------------------------------------------------
# Save
# -------------------------------------------------

daily.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("\nDAILY DATASET CREATED")
print("---------------------")

print(
    "Date range:",
    daily["date"].min(),
    "to",
    daily["date"].max(),
)

print(
    "Total days:",
    len(daily),
)

print(
    "Storm days:",
    int(
        daily[
            "geomagnetic_storm"
        ].sum()
    ),
)

print(
    "Non-storm days:",
    int(
        (
            daily[
                "geomagnetic_storm"
            ] == 0
        ).sum()
    ),
)

print("\nTARGET DISTRIBUTION")

print(
    daily[
        "geomagnetic_storm"
    ].value_counts()
)

print("\nFIRST 10 ROWS")

print(
    daily.head(10).to_string(
        index=False
    )
)

print(
    "\nSaved to:",
    OUTPUT_FILE,
)
