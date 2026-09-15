import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
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


# ---------------------------------------------
# Load and sort chronologically
# ---------------------------------------------

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["date"],
)

df = df.sort_values(
    "date"
).reset_index(drop=True)


# ---------------------------------------------
# Time-based 80/20 split
# ---------------------------------------------

split_index = int(
    len(df) * 0.80
)

train_df = df.iloc[
    :split_index
].copy()

test_df = df.iloc[
    split_index:
].copy()


X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


print("\nTIME SPLIT")
print("--------------------------")

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

print("\nTRAIN TARGETS")
print(y_train.value_counts())

print("\nTEST TARGETS")
print(y_test.value_counts())


# ---------------------------------------------
# Models
# ---------------------------------------------

models = {
    "Logistic Regression": Pipeline(
        [
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=500,
        max_depth=8,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    ),
}


# ---------------------------------------------
# Evaluation helper
# ---------------------------------------------

def evaluate_model(
    name,
    model,
):
    model.fit(
        X_train,
        y_train,
    )

    probabilities = (
        model.predict_proba(
            X_test
        )[:, 1]
    )

    predictions = (
        probabilities >= 0.50
    ).astype(int)


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

    roc_auc = roc_auc_score(
        y_test,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )


    print(
        "\n======================================"
    )

    print(name)

    print(
        "======================================"
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
        f"ROC AUC:   {roc_auc:.3f}"
    )

    print(
        f"PR AUC:    {pr_auc:.3f}"
    )


    print(
        "\nCONFUSION MATRIX"
    )

    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )


    print(
        "\nCLASSIFICATION REPORT"
    )

    print(
        classification_report(
            y_test,
            predictions,
            digits=3,
            zero_division=0,
        )
    )


    return {
        "name": name,
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
    }


# ---------------------------------------------
# Run both
# ---------------------------------------------

results = []

for name, model in models.items():
    result = evaluate_model(
        name,
        model,
    )

    results.append(result)


# ---------------------------------------------
# Comparison
# ---------------------------------------------

print(
    "\n\nMODEL COMPARISON"
)

print(
    "======================================"
)

comparison = pd.DataFrame(
    [
        {
            "model": r["name"],
            "accuracy": r["accuracy"],
            "precision": r["precision"],
            "recall": r["recall"],
            "f1": r["f1"],
            "roc_auc": r["roc_auc"],
            "pr_auc": r["pr_auc"],
        }
        for r in results
    ]
)

print(
    comparison.to_string(
        index=False
    )
)
