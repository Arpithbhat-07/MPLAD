"""CSV data loading and normalization for the MPLADS project dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = BACKEND_ROOT / "data"

REQUIRED_COLUMNS = [
    "work_id",
    "mp_name",
    "district",
    "implementing_agency",
    "work_category",
    "cost_estimate_lakhs",
    "status",
    "risk_score",
]

TEXT_COLUMNS = [
    "work_id",
    "mp_name",
    "district",
    "implementing_agency",
    "work_category",
    "status",
]


def find_dataset(
    preferred_names: Iterable[str] = ("flagged_works.csv",),
) -> Path:
    """Return the preferred CSV dataset."""

    if not DATA_FOLDER.exists():
        raise FileNotFoundError(
            f"Data folder not found: {DATA_FOLDER}"
        )

    csv_files = sorted(DATA_FOLDER.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found inside: {DATA_FOLDER}"
        )

    lookup = {
        path.name.lower(): path
        for path in csv_files
    }

    for name in preferred_names:
        path = lookup.get(name.lower())

        if path:
            return path

    return csv_files[0]


def load_projects(
    dataset_path: Path | None = None,
) -> pd.DataFrame:
    """Load, validate, and normalize the main dataset."""

    data_file = dataset_path or find_dataset()

    df = pd.read_csv(data_file)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    for column in TEXT_COLUMNS:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["cost_estimate_lakhs"] = pd.to_numeric(
        df["cost_estimate_lakhs"],
        errors="coerce",
    ).fillna(0.0)

    df["risk_score"] = pd.to_numeric(
        df["risk_score"],
        errors="coerce",
    ).fillna(0.0)

    if "reasons_text" not in df.columns:
        df["reasons_text"] = ""

    df["reasons_text"] = (
        df["reasons_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df