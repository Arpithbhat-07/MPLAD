import numpy as np
import pandas as pd


def calculate_rule_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate transparent rule-based risk.

    This is a screening mechanism.
    A high score does NOT prove fraud.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    rule_score = pd.Series(
        0.0,
        index=result.index,
        dtype=float,
    )

    reasons = {
        index: []
        for index in result.index
    }

    # ---------------------------------
    # Rule 1: High fund utilization
    # ---------------------------------

    if "fund_utilization_pct" in result.columns:

        utilization = pd.to_numeric(
            result["fund_utilization_pct"],
            errors="coerce",
        ).fillna(0)

        mask = utilization >= 90

        rule_score.loc[mask] += 20

        for index in result.index[mask]:
            reasons[index].append(
                "High fund utilization"
            )

    # ---------------------------------
    # Rule 2: Progress / expenditure gap
    # ---------------------------------

    if "progress_expenditure_gap" in result.columns:

        gap = pd.to_numeric(
            result["progress_expenditure_gap"],
            errors="coerce",
        ).fillna(0)

        mask = gap > 25

        rule_score.loc[mask] += 25

        for index in result.index[mask]:
            reasons[index].append(
                "Expenditure is significantly "
                "higher than physical progress"
            )

    # ---------------------------------
    # Rule 3: Cost overrun
    # ---------------------------------

    if "cost_overrun_amount" in result.columns:

        overrun = pd.to_numeric(
            result["cost_overrun_amount"],
            errors="coerce",
        ).fillna(0)

        mask = overrun > 0

        rule_score.loc[mask] += 25

        for index in result.index[mask]:
            reasons[index].append(
                "Expenditure exceeds sanctioned amount"
            )

    # ---------------------------------
    # Rule 4: Timeline delay
    # ---------------------------------

    if "delay_days" in result.columns:

        delay = pd.to_numeric(
            result["delay_days"],
            errors="coerce",
        ).fillna(0)

        mask = delay > 30

        rule_score.loc[mask] += 20

        for index in result.index[mask]:
            reasons[index].append(
                "Project delayed by more than 30 days"
            )

    # ---------------------------------
    # Preserve existing synthetic score
    # ---------------------------------

    if "existing_rule_score" in result.columns:

        existing_score = pd.to_numeric(
            result["existing_rule_score"],
            errors="coerce",
        ).fillna(0)

        # If no new rule triggered,
        # preserve the original synthetic score.
        mask = rule_score == 0

        rule_score.loc[mask] = (
            existing_score.loc[mask]
        )

    # ---------------------------------
    # Final rule score
    # ---------------------------------

    result["rule_risk_score"] = (
        rule_score
        .clip(0, 100)
        .round(2)
    )

    # ---------------------------------
    # Risk level
    # ---------------------------------

    result["rule_risk_level"] = np.select(
        [
            result["rule_risk_score"] >= 70,
            result["rule_risk_score"] >= 40,
        ],
        [
            "HIGH",
            "MEDIUM",
        ],
        default="LOW",
    )

    # ---------------------------------
    # Risk reasons
    # ---------------------------------

    result["rule_reasons"] = [
        "; ".join(reasons[index])
        if reasons[index]
        else "No rule-based risk condition triggered"
        for index in result.index
    ]

    return result