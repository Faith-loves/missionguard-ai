import json
from pathlib import Path

import joblib
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


DATA_PATH = "data/missionguard_forecast_ml_cme.csv"

MODEL_PATH = Path(
    "models/storm_forecast_model.pkl"
)

FEATURES_PATH = Path(
    "models/storm_forecast_features.pkl"
)

METADATA_PATH = Path(
    "models/storm_forecast_metadata.json"
)


TARGET = "storm_next_3d"


FEATURES = [
    # Solar activity
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

    # CME activity
    "cme_count",
    "earth_directed_cme_count",
    "max_cme_speed",
    "fast_cme_count",

    "cme_count_lag_1",
    "earth_directed_cme_count_lag_1",
    "max_cme_speed_lag_1",
    "fast_cme_count_lag_1",

    "cme_count_lag_2",
    "earth_directed_cme_count_lag_2",
    "max_cme_speed_lag_2",
    "fast_cme_count_lag_2",

    "cme_count_lag_3",
    "earth_directed_cme_count_lag_3",
    "max_cme_speed_lag_3",
    "fast_cme_count_lag_3",

    "cme_count_3d",
    "earth_directed_cme_3d",
    "fast_cme_3d",
    "max_cme_speed_3d",
]


def create_model():
    return RandomForestClassifier(
        n_estimators=700,
        max_depth=10,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )


# ============================================
# LOAD DATA
# ============================================

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

df = df.sort_values(
    "date"
).reset_index(drop=True)


# ============================================
# 70 / 15 / 15 CHRONOLOGICAL SPLIT
# ============================================

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
print("====================================")

print(
    "Training:",
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
    "Testing:",
    test_df["date"].min().date(),
    "to",
    test_df["date"].max().date(),
)


print("\nTARGET DISTRIBUTION")

print(
    "Training:",
    train_df[TARGET]
    .value_counts()
    .to_dict(),
)

print(
    "Validation:",
    validation_df[TARGET]
    .value_counts()
    .to_dict(),
)

print(
    "Testing:",
    test_df[TARGET]
    .value_counts()
    .to_dict(),
)


# ============================================
# TRAIN ON TRAIN SET ONLY
# ============================================

model = create_model()

model.fit(
    train_df[FEATURES],
    train_df[TARGET],
)


validation_probabilities = (
    model.predict_proba(
        validation_df[FEATURES]
    )[:, 1]
)


# ============================================
# THRESHOLD SEARCH
#
# MissionGuard is an early-warning prototype.
# Missing a storm matters more than issuing
# some extra caution alerts.
#
# Require recall >= 50%, then choose the
# strongest F2 score.
# ============================================

threshold_results = []


print("\nVALIDATION THRESHOLDS")
print(
    "===================================="
)

print(
    "Threshold  Precision  Recall   F1      F2"
)


for threshold in np.arange(
    0.05,
    0.61,
    0.025,
):
    predictions = (
        validation_probabilities
        >= threshold
    ).astype(int)

    precision = precision_score(
        validation_df[TARGET],
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        validation_df[TARGET],
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        validation_df[TARGET],
        predictions,
        zero_division=0,
    )

    f2 = fbeta_score(
        validation_df[TARGET],
        predictions,
        beta=2,
        zero_division=0,
    )

    threshold_results.append(
        {
            "threshold": float(
                round(threshold, 3)
            ),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "f2": f2,
        }
    )

    print(
        f"{threshold:0.3f}      "
        f"{precision:0.3f}      "
        f"{recall:0.3f}   "
        f"{f1:0.3f}   "
        f"{f2:0.3f}"
    )


# ============================================
# SELECT THRESHOLD
# ============================================

recall_candidates = [
    result
    for result in threshold_results
    if result["recall"] >= 0.50
]


if recall_candidates:
    best = max(
        recall_candidates,
        key=lambda result: (
            result["f2"],
            result["precision"],
        ),
    )

else:
    best = max(
        threshold_results,
        key=lambda result: (
            result["f2"],
            result["recall"],
        ),
    )


best_threshold = best["threshold"]


print("\nSELECTED THRESHOLD")
print("====================================")

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
    "Validation F1:",
    round(
        best["f1"],
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


# ============================================
# RETRAIN ON TRAIN + VALIDATION
# ============================================

final_training_df = pd.concat(
    [
        train_df,
        validation_df,
    ],
    ignore_index=True,
)


final_model = create_model()

final_model.fit(
    final_training_df[FEATURES],
    final_training_df[TARGET],
)


# ============================================
# FINAL UNTOUCHED TEST
# ============================================

test_probabilities = (
    final_model.predict_proba(
        test_df[FEATURES]
    )[:, 1]
)


test_predictions = (
    test_probabilities
    >= best_threshold
).astype(int)


y_test = test_df[TARGET]


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


matrix = confusion_matrix(
    y_test,
    test_predictions,
)

tn, fp, fn, tp = matrix.ravel()


print("\nFINAL TEST RESULTS")
print("====================================")

print(
    f"Threshold: {best_threshold:.3f}"
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
print(matrix)


print("\nMISSIONGUARD DETECTION")

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


# ============================================
# DEPLOYMENT GATE
# ============================================

passes_recall = recall >= 0.50
passes_precision = precision >= 0.20
passes_auc = roc_auc >= 0.60


print("\nMISSIONGUARD ML GATE")
print("====================================")


if (
    passes_recall
    and passes_precision
    and passes_auc
):
    print(
        "PASS - model can be used as an "
        "experimental MissionGuard ML signal."
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        final_model,
        MODEL_PATH,
    )

    joblib.dump(
        FEATURES,
        FEATURES_PATH,
    )

    metadata = {
        "model_type":
            "RandomForestClassifier",

        "forecast_horizon_days": 3,

        "threshold":
            best_threshold,

        "accuracy":
            round(accuracy, 4),

        "precision":
            round(precision, 4),

        "recall":
            round(recall, 4),

        "f1":
            round(f1, 4),

        "f2":
            round(f2, 4),

        "roc_auc":
            round(roc_auc, 4),

        "pr_auc":
            round(pr_auc, 4),

        "status":
            "experimental",
    }

    with METADATA_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )

    print("\nMODEL SAVED")

    print(MODEL_PATH)
    print(FEATURES_PATH)
    print(METADATA_PATH)

else:
    print(
        "FAIL - model will NOT be used "
        "for MissionGuard decision scoring."
    )

    print(
        "The rule-based risk engine remains "
        "the primary decision engine."
    )
