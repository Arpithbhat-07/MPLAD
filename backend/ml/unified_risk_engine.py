import numpy as np
import pandas as pd

from backend.ml.anomaly_detector import detect_anomalies
from backend.ml.risk_engine import calculate_rule_risk


def calculate_hybrid_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine rule-based risk with trained ML anomaly detection.

    Rule risk = 60%
    ML risk   = 40%

    This identifies projects that deserve further inspection.
    It does NOT prove fraud.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    # -----------------------------
    # 1. Rule-based analysis
    # -----------------------------
    result = calculate_rule_risk(df)

    # -----------------------------
    # 2. ML anomaly detection
    # -----------------------------
    result = detect_anomalies(result)

    # -----------------------------
    # 3. Convert ML score to 0-100
    # -----------------------------
    ml_score = pd.to_numeric(
        result["ml_anomaly_score"],
        errors="coerce"
    ).fillna(0)

    result["ml_risk_score"] = (
        ml_score.rank(pct=True) * 100
    ).round(2)

    # -----------------------------
    # 4. Get rule score
    # -----------------------------
    rule_score = pd.to_numeric(
        result["rule_risk_score"],
        errors="coerce"
    ).fillna(0)

    # -----------------------------
    # 5. Hybrid risk score
    # -----------------------------
    result["hybrid_risk_score"] = (
        rule_score * 0.60
        + result["ml_risk_score"] * 0.40
    ).round(2)

    # -----------------------------
    # 6. Risk level
    # -----------------------------
    result["hybrid_risk_level"] = np.select(
        [
            result["hybrid_risk_score"] >= 70,
            result["hybrid_risk_score"] >= 40,
        ],
        [
            "HIGH",
            "MEDIUM",
        ],
        default="LOW",
    )

    # -----------------------------
    # 7. Build risk reasons
    # -----------------------------
    def build_reason(row):
        reasons = []

        rule_reason = str(
            row.get("rule_reasons", "")
        )

        if (
            rule_reason
            and
            "No rule-based risk condition"
            not in rule_reason
        ):
            reasons.append(
                f"Rule: {rule_reason}"
            )

        if bool(row.get("ml_anomaly", False)):
            reasons.append(
                "ML: Isolation Forest identified "
                "unusual project characteristics"
            )

        if not reasons:
            reasons.append(
                "No significant risk indicator detected"
            )

        return " | ".join(reasons)

    result["hybrid_risk_reasons"] = (
        result.apply(
            build_reason,
            axis=1
        )
    )

    # -----------------------------
    # 8. Inspection priority
    # -----------------------------
    result["inspection_priority"] = np.select(
        [
            result["hybrid_risk_score"] >= 80,
            result["hybrid_risk_score"] >= 60,
            result["hybrid_risk_score"] >= 40,
        ],
        [
            "URGENT",
            "HIGH",
            "MEDIUM",
        ],
        default="LOW",
    )

    return result


def get_hybrid_summary(
    df: pd.DataFrame
) -> dict:
    """Return hybrid risk statistics."""

    if df is None or df.empty:
        return {
            "total_projects": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "ml_anomalies": 0,
        }

    return {
        "total_projects": len(df),

        "high_risk": int(
            (
                df["hybrid_risk_level"]
                == "HIGH"
            ).sum()
        ),

        "medium_risk": int(
            (
                df["hybrid_risk_level"]
                == "MEDIUM"
            ).sum()
        ),

        "low_risk": int(
            (
                df["hybrid_risk_level"]
                == "LOW"
            ).sum()
        ),

        "ml_anomalies": int(
            df["ml_anomaly"]
            .fillna(False)
            .sum()
        ),
    }