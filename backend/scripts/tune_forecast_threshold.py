import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


DATA_PATH = "data/missionguard_forecast_ml.csv"


FEATURES = [
    "c_flare_count",
    "m_flare_count",
    "x_flare_count",
    "high_speed_stream_count",

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


TARGET = "storm_next_3d"


def build_model():
    return RandomForestClassifier(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )


# --------------------------------------------
# Load chronologically
# --------------------------------------------

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

df = df.sort_values(
    "date"
).reset_index(drop=True)


# --------------------------------------------
# 70 / 15 / 15 time split
# --------------------------------------------

train_end = int(
    len(df) * 0.70
)

validation_end = int(
    len(df) * 0.85
)


train_df = df.iloc[
    :train_end
].copy()

validation_df = df.iloc[
    train_end:validation_end
].copy()

test_df = df.iloc[
    validation_end:
].copy()


print("\nTIME SPLITS")
print("----------------------------------")

print(
    "Train:",
    train_df["date"].min().date(),
    "to",
    train_df["date"].max().date(),
)

print(
    "Validation:",
    validation_df["date"].min().date(),
    "to",
    validation_df["date"].max().date(),
)

print(
    "Test:",
    test_df["date"].min().date(),
    "to",
    test_df["date"].max().date(),
)


print("\nTARGET COUNTS")

print(
    "Train:",
    train_df[TARGET].value_counts().to_dict(),
)

print(
    "Validation:",
    validation_df[TARGET].value_counts().to_dict(),
)

print(
    "Test:",
    test_df[TARGET].value_counts().to_dict(),
)


# --------------------------------------------
# Train initial model
# --------------------------------------------

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_validation = validation_df[FEATURES]
y_validation = validation_df[TARGET]


model = build_model()

model.fit(
    X_train,
    y_train,
)


validation_probabilities = (
    model.predict_proba(
        X_validation
    )[:, 1]
)


# --------------------------------------------
# Threshold tuning
#
# F2 weights recall more heavily than precision.
# That suits an early-warning prototype.
# --------------------------------------------

threshold_results = []


print("\nVALIDATION THRESHOLD TEST")
print("----------------------------------")

print(
    "Threshold  Precision  Recall  F1     F2"
)


for threshold in np.arange(
    0.10,
    0.61,
    0.05,
):
    predictions = (
        validation_probabilities
        >= threshold
    ).astype(int)

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0,
    )

    f2 = fbeta_score(
        y_validation,
        predictions,
        beta=2,
        zero_division=0,
    )

    threshold_results.append(
        {
            "threshold": float(
                round(
                    threshold,
                    2,
                )
            ),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "f2": f2,
        }
    )

    print(
        f"{threshold:0.2f}       "
        f"{precision:0.3f}      "
        f"{recall:0.3f}   "
        f"{f1:0.3f}  "
        f"{f2:0.3f}"
    )


# --------------------------------------------
# Choose threshold
#
# Require at least some precision so simply
# predicting everything as dangerous cannot win.
# --------------------------------------------

valid_candidates = [
    result
    for result in threshold_results
    if result["precision"] >= 0.20
]


if valid_candidates:
    best = max(
        valid_candidates,
        key=lambda result: (
            result["f2"],
            result["recall"],
            result["precision"],
        ),
    )

else:
    best = max(
        threshold_results,
        key=lambda result:
            result["f2"],
    )


best_threshold = best[
    "threshold"
]


print("\nSELECTED THRESHOLD")
print("----------------------------------")

print(
    "Threshold:",
    best_threshold,
)

print(
    "Validation precision:",
    round(
        best["precision"],
        3,
    ),
)

print(
    "Validation recall:",
    round(
        best["recall"],
        3,
    ),
)

print(
    "Validation F2:",
    round(
        best["f2"],
        3,
    ),
)


# --------------------------------------------
# Retrain using train + validation
# --------------------------------------------

training_final = pd.concat(
    [
        train_df,
        validation_df,
    ],
    ignore_index=True,
)


final_model = build_model()

final_model.fit(
    training_final[FEATURES],
    training_final[TARGET],
)


# --------------------------------------------
# FINAL untouched test
# --------------------------------------------

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


test_probabilities = (
    final_model.predict_proba(
        X_test
    )[:, 1]
)


test_predictions = (
    test_probabilities
    >= best_threshold
).astype(int)


accuracy = accuracy_score(
    y_test,
    test_predictions,
)

precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0,
)

recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0,
)

f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0,
)

f2 = fbeta_score(
    y_test,
    test_predictions,
    beta=2,
    zero_division=0,
)

roc_auc = roc_auc_score(
    y_test,
    test_probabilities,
)

pr_auc = average_precision_score(
    y_test,
    test_probabilities,
)


print("\nFINAL TEST RESULTS")
print("==================================")

print(
    f"Threshold: {best_threshold:.2f}"
)

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

print(
    f"F2 Score:  {f2:.3f}"
)

print(
    f"ROC AUC:   {roc_auc:.3f}"
)

print(
    f"PR AUC:    {pr_auc:.3f}"
)


print("\nCONFUSION MATRIX")

matrix = confusion_matrix(
    y_test,
    test_predictions,
)

print(matrix)


tn, fp, fn, tp = matrix.ravel()


print("\nEVENT DETECTION")

print(
    "Storm windows detected:",
    tp,
)

print(
    "Storm windows missed:",
    fn,
)

print(
    "False alarms:",
    fp,
)

print(
    "Correct normal windows:",
    tn,
)


# --------------------------------------------
# Deployment gate
#
# Do NOT deploy weak ML just because it exists.
# --------------------------------------------

passes_recall = (
    recall >= 0.50
)

passes_auc = (
    roc_auc >= 0.60
)

passes_precision = (
    precision >= 0.20
)


print("\nMISSIONGUARD ML GATE")
print("==================================")


if (
    passes_recall
    and passes_auc
    and passes_precision
):
    print(
        "PASS - model is eligible "
        "for prototype integration."
    )

else:
    print(
        "FAIL - model is NOT strong "
        "enough for MissionGuard "
        "decision scoring."
    )

    print(
        "It can remain an experimental "
        "ML component while we improve "
        "the data/features."
    )
