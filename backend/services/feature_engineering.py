from typing import Any

import numpy as np
import pandas as pd


# Common column names used by official and synthetic datasets.
COLUMN_ALIASES = {
    "state": [
        "state",
        "State",
        "state_name",
        "State Name",
    ],
    "district": [
        "district",
        "District",
        "district_name",
        "District Name",
    ],
    "constituency": [
        "constituency",
        "Constituency",
        "parliamentary_constituency",
    ],
    "mp_name": [
        "mp_name",
        "MP Name",
        "mp",
        "MP",
        "member_name",
    ],
    "work_id": [
        "work_id",
        "Work ID",
        "workid",
        "id",
    ],
    "work_name": [
        "work_name",
        "Work Name",
        "name",
        "project_name",
    ],
    "work_category": [
        "work_category",
        "Work Category",
        "category",
        "Category",
    ],
    "implementing_agency": [
        "implementing_agency",
        "Implementing Agency",
        "agency",
        "Agency",
    ],
    "sanction_amount": [
        "sanction_amount",
        "Sanction Amount",
        "sanctioned_amount",
        "cost_estimate_lakhs",
        "Cost Estimate",
    ],
    "expenditure": [
        "expenditure",
        "Expenditure",
        "amount_spent",
        "spent_amount",
        "expenditure_amount",
    ],
    "physical_progress": [
        "physical_progress",
        "Physical Progress",
        "progress",
        "completion_percentage",
    ],
    "start_date": [
        "start_date",
        "Start Date",
        "work_start_date",
    ],
    "expected_completion_date": [
        "expected_completion_date",
        "Expected Completion Date",
        "planned_completion_date",
    ],
    "actual_completion_date": [
        "actual_completion_date",
        "Actual Completion Date",
        "completion_date",
    ],
    "contractor": [
        "contractor",
        "Contractor",
        "contractor_name",
    ],
    "latitude": [
        "latitude",
        "Latitude",
        "lat",
    ],
    "longitude": [
        "longitude",
        "Longitude",
        "lon",
        "lng",
    ],
    "status": [
        "status",
        "Status",
        "work_status",
    ],
}


def _find_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    """Find the first matching column from a list of aliases."""

    normalized = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for alias in aliases:
        key = alias.strip().lower()

        if key in normalized:
            return normalized[key]

    return None


def _get_series(
    df: pd.DataFrame,
    canonical_name: str,
) -> pd.Series:
    """Return a dataset column using the canonical name."""

    aliases = COLUMN_ALIASES.get(canonical_name, [])

    column = _find_column(df, aliases)

    if column is None:
        return pd.Series(np.nan, index=df.index)

    return df[column]


def _numeric(series: pd.Series) -> pd.Series:
    """Convert a series to numeric safely."""

    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    cleaned = (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(cleaned, errors="coerce")


def standardize_dataset(
    df: pd.DataFrame,
    source: str,
) -> pd.DataFrame:
    """
    Convert official/synthetic MPLADS data into a common schema.

    source must be either:
        official
        synthetic
    """

    if source not in {"official", "synthetic"}:
        raise ValueError(
            "source must be 'official' or 'synthetic'"
        )

    if df is None or df.empty:
        return pd.DataFrame()

    result = pd.DataFrame(index=df.index)

    # -----------------------------
    # Basic/common fields
    # -----------------------------

    for canonical_name in COLUMN_ALIASES:
        result[canonical_name] = _get_series(
            df,
            canonical_name,
        )
    # Preserve the original synthetic risk score.
    # This is NOT used as an ML feature.
    if source == "synthetic" and "risk_score" in df.columns:
        result["existing_rule_score"] = pd.to_numeric(
            df["risk_score"],
            errors="coerce",
        )

    # -----------------------------
    # Numeric fields
    # -----------------------------

    result["sanction_amount"] = _numeric(
        result["sanction_amount"]
    )

    result["expenditure"] = _numeric(
        result["expenditure"]
    )

    result["physical_progress"] = _numeric(
        result["physical_progress"]
    )

    # -----------------------------
    # Dates
    # -----------------------------

    result["start_date"] = pd.to_datetime(
        result["start_date"],
        errors="coerce",
    )

    result["expected_completion_date"] = pd.to_datetime(
        result["expected_completion_date"],
        errors="coerce",
    )

    result["actual_completion_date"] = pd.to_datetime(
        result["actual_completion_date"],
        errors="coerce",
    )

    # -----------------------------
    # Data source
    # -----------------------------

    result["data_source"] = source

    if source == "official":
        result["data_label"] = "Official MPLADS Data"
    else:
        result["data_label"] = "Synthetic Test Data"

    # -----------------------------
    # Fund utilization
    # -----------------------------

    result["fund_utilization_pct"] = np.where(
        result["sanction_amount"] > 0,
        (
            result["expenditure"]
            / result["sanction_amount"]
        ) * 100,
        np.nan,
    )

    result["fund_utilization_pct"] = (
        result["fund_utilization_pct"]
        .replace([np.inf, -np.inf], np.nan)
        .clip(lower=0)
    )

    # -----------------------------
    # Progress vs expenditure
    # -----------------------------

    result["progress_expenditure_gap"] = (
        result["fund_utilization_pct"]
        - result["physical_progress"]
    )

    # Large positive value means:
    # money spent is much higher than
    # physical progress.

    result["progress_expenditure_mismatch"] = (
        result["progress_expenditure_gap"] > 25
    )

    # -----------------------------
    # Cost overrun
    # -----------------------------

    result["cost_overrun_amount"] = (
        result["expenditure"]
        - result["sanction_amount"]
    )

    result["cost_overrun_pct"] = np.where(
        result["sanction_amount"] > 0,
        (
            result["cost_overrun_amount"]
            / result["sanction_amount"]
        ) * 100,
        np.nan,
    )

    result["cost_overrun_flag"] = (
        result["cost_overrun_amount"] > 0
    )

    # -----------------------------
    # Timeline
    # -----------------------------

    result["planned_duration_days"] = (
        result["expected_completion_date"]
        - result["start_date"]
    ).dt.days

    result["actual_duration_days"] = (
        result["actual_completion_date"]
        - result["start_date"]
    ).dt.days

    result["delay_days"] = (
        result["actual_completion_date"]
        - result["expected_completion_date"]
    ).dt.days

    result["timeline_delay_flag"] = (
        result["delay_days"] > 0
    )

    # -----------------------------
    # High fund utilization
    # -----------------------------

    result["high_fund_utilization"] = (
        result["fund_utilization_pct"] >= 90
    )

    # -----------------------------
    # Record ID
    # -----------------------------

    result["record_id"] = (
        result["work_id"]
        .astype(str)
        .replace("nan", "")
    )

    missing_id = result["record_id"].eq("")

    result.loc[missing_id, "record_id"] = (
        "ROW-"
        + result.index.astype(str)
    )

    return result.reset_index(drop=True)


def get_feature_summary(
    df: pd.DataFrame,
) -> dict[str, Any]:
    """Return a compact summary of the engineered dataset."""

    if df is None or df.empty:
        return {
            "rows": 0,
            "columns": 0,
        }

    summary = {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
    }

    if "data_source" in df.columns:
        summary["data_source"] = (
            df["data_source"]
            .dropna()
            .unique()
            .tolist()
        )

    flag_columns = [
        "high_fund_utilization",
        "progress_expenditure_mismatch",
        "cost_overrun_flag",
        "timeline_delay_flag",
    ]

    for column in flag_columns:
        if column in df.columns:
            summary[column] = int(
                df[column]
                .fillna(False)
                .sum()
            )

    return summary