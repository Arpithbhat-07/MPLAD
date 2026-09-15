import numpy as np
import pandas as pd


def calculate_rule_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate transparent rule-based risk indicators.

    IMPORTANT:
    These rules are deterministic indicators.
    They do NOT prove fraud.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    rule_score = pd.Series(
        0.0,
        index=result.index,
    )

    rule_reasons = [
        []
        for _ in range(len(result))
    ]

    # ---------------------------------
    # Rule 1: High fund utilization
    # ---------------------------------

    if "fund_utilization_pct" in result.columns:

        mask = (
            result["fund_utilization_pct"]
            .fillna(0)
            >= 90
        )

        rule_score.loc[mask] += 20

        for index in result.index[mask]:
            rule_reasons[
                result.index.get_loc(index)
            ].append(
                "High fund utilization"
            )

    # ---------------------------------
    # Rule 2: Expenditure/progress mismatch
    # ---------------------------------

    if "progress_expenditure_gap" in result.columns:

        mask = (
            result["progress_expenditure_gap"]
            .fillna(0)
            > 25
        )

        rule_score.loc[mask] += 25

        for index in result.index[mask]:
            rule_reasons[
                result.index.get_loc(index)
            ].append(
                "Expenditure is significantly higher "
                "than physical progress"
            )

    # ---------------------------------
    # Rule 3: Cost overrun
    # ---------------------------------

    if "cost_overrun_amount" in result.columns:

        mask = (
            result["cost_overrun_amount"]
            .fillna(0)
            > 0
        )

        rule_score.loc[mask] += 25

        for index in result.index[mask]:
            rule_reasons[
                result.index.get_loc(index)
            ].append(
                "Expenditure exceeds sanctioned amount"
            )

    # ---------------------------------
    # Rule 4: Timeline delay
    # ---------------------------------

    if "delay_days" in result.columns:

        mask = (
            result["delay_days"]
            .fillna(0)
            > 30
        )

        rule_score.loc[mask] += 20

        for index in result.index[mask]:
            rule_reasons[
                result.index.get_loc(index)
            ].append(
                "Project delayed by more than 30 days"
            )

    # ---------------------------------
    # Rule 5: Existing synthetic
    # rule score
    # ---------------------------------

    # We can preserve an existing rule score
    # from the synthetic dataset, but it is NOT
    # used by the ML model.

    if "risk_score" in result.columns:

        existing_score = pd.to_numeric(
            result["risk_score"],
            errors="coerce",
        ).fillna(0)

        # If there are no newly calculated rules,
        # preserve the existing synthetic rule score.
        no_new_rules = rule_score.eq(0)

        rule_score.loc[no_new_rules] = (
            existing_score.loc[no_new_rules]
        )

    # ---------------------------------
    # Limit score
    # ---------------------------------

    result["rule_risk_score"] = (
        rule_score
        .clip(0, 100)
        .round(2)
    )

    # ---------------------------------
    # Rule risk level
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
    # Rule reasons
    # ---------------------------------

    result["rule_reasons"] = [
        "; ".join(reasons)
        if reasons
        else "No rule-based risk condition triggered"
        for reasons in rule_reasons
    ]

    return result