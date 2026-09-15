import pandas as pd

from backend.services.feature_engineering import standardize_dataset
from backend.ml.unified_risk_engine import calculate_hybrid_risk


def analyze_dataset(df: pd.DataFrame, source: str = "synthetic") -> pd.DataFrame:
    """
    Run the complete MPLADS risk-analysis pipeline.

    Pipeline:
        Raw data
        -> Standardization
        -> Feature engineering
        -> Rule engine
        -> ML anomaly detection
        -> Hybrid risk
    """

    if df is None or df.empty:
        return pd.DataFrame()

    # Standardize input
    standardized = standardize_dataset(
        df,
        source
    )

    # Run hybrid analysis
    result = calculate_hybrid_risk(
        standardized
    )

    return result


def get_risk_summary(result: pd.DataFrame) -> dict:
    """Create dashboard-friendly risk statistics."""

    if result is None or result.empty:
        return {
            "total_projects": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "ml_anomalies": 0,
        }

    return {
        "total_projects": len(result),

        "high_risk": int(
            (
                result["hybrid_risk_level"]
                == "HIGH"
            ).sum()
        ),

        "medium_risk": int(
            (
                result["hybrid_risk_level"]
                == "MEDIUM"
            ).sum()
        ),

        "low_risk": int(
            (
                result["hybrid_risk_level"]
                == "LOW"
            ).sum()
        ),

        "ml_anomalies": int(
            result["ml_anomaly"]
            .fillna(False)
            .sum()
        ),
    }