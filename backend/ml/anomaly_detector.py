from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# Location of the trained model
MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "anomaly_model_v1_7_1_final.joblib"
)


def load_anomaly_model():
    """Load the trained Isolation Forest pipeline."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained anomaly model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run the trained Isolation Forest model on project data.

    The trained model expects:
        cost_estimate_lakhs
        work_category
        implementing_agency
        status

    Our standardized dataset uses:
        sanction_amount
        work_category
        implementing_agency
        status
    """

    if df is None or df.empty:
        return pd.DataFrame()

    # Load trained model
    model = load_anomaly_model()

    # ---------------------------------
    # Prepare features
    # ---------------------------------

    X = pd.DataFrame(index=df.index)

    if "sanction_amount" not in df.columns:
        raise ValueError(
            "Standardized dataset does not contain "
            "'sanction_amount'."
        )

    # Our standardized field
    # becomes the feature name used during training.
    X["cost_estimate_lakhs"] = pd.to_numeric(
        df["sanction_amount"],
        errors="coerce",
    )

    X["work_category"] = df["work_category"]

    X["implementing_agency"] = (
        df["implementing_agency"]
    )

    X["status"] = df["status"]

    # ---------------------------------
    # Handle missing cost values
    # ---------------------------------

    X["cost_estimate_lakhs"] = (
        X["cost_estimate_lakhs"]
        .replace([np.inf, -np.inf], np.nan)
    )

    median_cost = X["cost_estimate_lakhs"].median()

    if pd.isna(median_cost):
        median_cost = 0

    X["cost_estimate_lakhs"] = (
        X["cost_estimate_lakhs"]
        .fillna(median_cost)
    )

    # ---------------------------------
    # Handle missing categorical values
    # ---------------------------------

    for column in [
        "work_category",
        "implementing_agency",
        "status",
    ]:
        X[column] = (
            X[column]
            .fillna("Unknown")
            .astype(str)
        )

    # ---------------------------------
    # Run trained ML model
    # ---------------------------------

    predictions = model.predict(X)

    # Higher value = more unusual
    anomaly_scores = (
        -model.decision_function(X)
    )

    # ---------------------------------
    # Add ML results
    # ---------------------------------

    result = df.copy()

    result["ml_anomaly"] = (
        predictions == -1
    )

    result["ml_anomaly_score"] = (
        pd.Series(
            anomaly_scores,
            index=result.index,
        ).round(4)
    )

    result["ml_anomaly_status"] = np.where(
        result["ml_anomaly"],
        "Anomaly",
        "Normal",
    )

    result["ml_model"] = (
        "Isolation Forest"
    )

    return result


def get_anomaly_summary(
    df: pd.DataFrame,
) -> dict:
    """Return a summary of ML anomaly results."""

    if df is None or df.empty:
        return {
            "total_records": 0,
            "anomalies": 0,
            "normal": 0,
            "anomaly_percentage": 0,
            "model": "Isolation Forest",
        }

    anomalies = int(
        df["ml_anomaly"]
        .fillna(False)
        .sum()
    )

    total = len(df)

    return {
        "total_records": total,
        "anomalies": anomalies,
        "normal": total - anomalies,
        "anomaly_percentage": round(
            anomalies / total * 100,
            2,
        ),
        "model": "Isolation Forest",
    }