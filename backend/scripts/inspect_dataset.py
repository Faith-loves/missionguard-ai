import pandas as pd

DATA_PATH = "data/space_weather_unified.csv"

df = pd.read_csv(DATA_PATH)

print("\nDATASET SHAPE")
print(df.shape)

print("\nCOLUMNS")
for column in df.columns:
    print("-", column)

print("\nFIRST 5 ROWS")
print(df.head())

print("\nDATA TYPES")
print(df.dtypes)

print("\nMISSING VALUES")
print(df.isnull().sum())
