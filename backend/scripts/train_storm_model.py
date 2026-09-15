from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


DATA_PATH = Path(
    "data/missionguard_daily_ml.csv"
)

MODEL_PATH = Path(
    "models/storm_probability_model.pkl"
)

FEATURES_PATH = Path(
    "models/storm_model_features.pkl"
)


# -------------------------------------------------
# Load data
# -------------------------------------------------

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

df = df.sort_values(
    "date"
).reset_index(drop=True)


# -------------------------------------------------
# Features
#
# We deliberately use PREVIOUS activity,
# not same-day activity, to reduce leakage.
# -------------------------------------------------

feature_columns = [
    "c_flare_count_lag_1",
    "m_flare_count_lag_1",
    "x_flare_count_lag_1",
    "high_speed_stream_count_lag_1",

    "c_flare_count_lag_2",
    "m_flare_count_lag_2",
    "x_flare_count_lag_2",
    "high_speed_stream_count_lag_2",

    "c_flare_count_lag_3",
    "m_flare_count_lag_3",
    "x_flare_count_lag_3",
    "high_speed_stream_count_lag_3",

    "c_flare_3d",
    "m_flare_3d",
    "x_flare_3d",
    "hss_3d",
]


target_column = "geomagnetic_storm"


X = df[feature_columns]
y = df[target_column]


# -------------------------------------------------
# Time-based split
#
# First 80% = training
# Last 20% = testing
# -------------------------------------------------

split_index = int(
    len(df) * 0.80
)

train_df = df.iloc[
    :split_index
]

test_df = df.iloc[
    split_index:
]


X_train = train_df[
    feature_columns
]

y_train = train_df[
    target_column
]

X_test = test_df[
    feature_columns
]

y_test = test_df[
    target_column
]


print("\nTIME SPLIT")
print("---------------------")

print(
    "Training:",
    train_df["date"].min().date(),
    "to",
    train_df["date"].max().date(),
)

print(
    "Testing:",
    test_df["date"].min().date(),
    "to",
    test_df["date"].max().date(),
)


print("\nTRAINING TARGETS")
print(
    y_train.value_counts()
)


print("\nTEST TARGETS")
print(
    y_test.value_counts()
)


# -------------------------------------------------
# Train Random Forest
#
# class_weight helps because storm days are rare.
# -------------------------------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
)


# -------------------------------------------------
# Predictions
# -------------------------------------------------

predictions = model.predict(
    X_test
)

probabilities = (
    model.predict_proba(
        X_test
    )[:, 1]
)


# -------------------------------------------------
# Evaluation
# -------------------------------------------------

accuracy = accuracy_score(
    y_test,
    predictions,
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0,
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0,
)


print("\nMODEL RESULTS")
print("---------------------")

print(
    f"Accuracy:  {accuracy:.3f}"
)

print(
    f"Precision: {precision:.3f}"
)

print(
    f"Recall:    {recall:.3f}"
)

print(
    f"F1 Score:  {f1:.3f}"
)


if y_test.nunique() == 2:
    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    print(
        f"ROC AUC:   {roc_auc:.3f}"
    )
else:
    print(
        "ROC AUC: not available "
        "(test data contains one class)"
    )


print("\nCONFUSION MATRIX")
print(
    confusion_matrix(
        y_test,
        predictions,
    )
)


print("\nCLASSIFICATION REPORT")

print(
    classification_report(
        y_test,
        predictions,
        digits=3,
        zero_division=0,
    )
)


# -------------------------------------------------
# Feature importance
# -------------------------------------------------

importance = pd.DataFrame(
    {
        "feature": feature_columns,
        "importance":
            model.feature_importances_,
    }
).sort_values(
    "importance",
    ascending=False,
)


print("\nTOP FEATURES")

print(
    importance.head(10)
    .to_string(index=False)
)


# -------------------------------------------------
# Save model
# -------------------------------------------------

joblib.dump(
    model,
    MODEL_PATH,
)

joblib.dump(
    feature_columns,
    FEATURES_PATH,
)


print("\nMODEL SAVED")
print(
    MODEL_PATH
)

print(
    FEATURES_PATH
)
