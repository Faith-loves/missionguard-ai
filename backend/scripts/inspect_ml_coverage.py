import pandas as pd

df = pd.read_csv("data/space_weather_unified.csv")

print("\nDATE RANGE")
print("Start:", df["date"].min())
print("End:", df["date"].max())

print("\nEVENT TYPES")
print(df["event_type"].value_counts(dropna=False))

print("\nKP DATA")
kp_rows = df[df["kp_index"].notna()]
print("Rows with Kp:", len(kp_rows))
print(kp_rows[["date", "kp_index"]].head(20))

print("\nKP RANGE")
if not kp_rows.empty:
    print("Minimum:", kp_rows["kp_index"].min())
    print("Maximum:", kp_rows["kp_index"].max())
    print("Average:", round(kp_rows["kp_index"].mean(), 2))

print("\nSOLAR FLARE CLASSES")
flare_rows = df[
    df["event_type"].str.contains(
        "flare",
        case=False,
        na=False
    )
]

print("Solar flare rows:", len(flare_rows))
print(
    flare_rows["class_type"]
    .fillna("UNKNOWN")
    .str[0]
    .value_counts()
)

print("\nUNIQUE DATES")
print("Total unique dates:", df["date"].nunique())
print(
    "Dates containing Kp:",
    kp_rows["date"].nunique()
)
