from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BACKEND_DIR / "data"

OFFICIAL_DIR = DATA_DIR / "officials"
SYNTHETIC_DIR = DATA_DIR / "synthtic"


OFFICIAL_FILE = (
    OFFICIAL_DIR / "mplads_official.csv"
)

SYNTHETIC_FILE = (
    SYNTHETIC_DIR / "flagged_works.csv"
)


# ============================================================
# GENERIC CSV LOADER
# ============================================================

def load_csv(path: Path) -> pd.DataFrame:
    """
    Load a CSV file safely.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{path}"
        )

    df = pd.read_csv(path)

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df


# ============================================================
# OFFICIAL MPLADS DATA
# ============================================================

def load_official_data() -> pd.DataFrame:
    """
    Load the official MPLADS dataset.

    This dataset must remain unchanged.
    """

    df = load_csv(
        OFFICIAL_FILE
    )

    # Mark the source explicitly
    df["data_source"] = "official"

    return df


# ============================================================
# SYNTHETIC DATA
# ============================================================

def load_synthetic_data() -> pd.DataFrame:
    """
    Load the synthetic MPLADS dataset.

    Synthetic data is used to demonstrate
    additional AI capabilities where the
    official dataset does not provide
    sufficient attributes.
    """

    df = load_csv(
        SYNTHETIC_FILE
    )

    df["data_source"] = "synthetic"

    return df


# ============================================================
# DATASET INFORMATION
# ============================================================

def get_official_info() -> dict:
    """
    Return basic information about
    the official dataset.
    """

    df = load_official_data()

    return {
        "source": "official",
        "file": OFFICIAL_FILE.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
    }


def get_synthetic_info() -> dict:
    """
    Return basic information about
    the synthetic dataset.
    """

    df = load_synthetic_data()

    return {
        "source": "synthetic",
        "file": SYNTHETIC_FILE.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
    }


# ============================================================
# COMMON DATA LOADER
# ============================================================

def load_projects(
    source: str = "synthetic",
) -> pd.DataFrame:
    """
    Load project data according to the
    selected source.

    source:
        official
        synthetic
    """

    source = source.lower().strip()

    if source == "official":

        return load_official_data()

    if source == "synthetic":

        return load_synthetic_data()

    raise ValueError(
        "Invalid data source. "
        "Use 'official' or 'synthetic'."
    )


# ============================================================
# COMBINED VIEW
# ============================================================

def load_all_data() -> pd.DataFrame:
    """
    Load both datasets into one DataFrame
    while preserving the data_source column.

    This does NOT claim that the two datasets
    have identical schemas.
    """

    official = load_official_data()

    synthetic = load_synthetic_data()

    # Union of columns
    all_columns = sorted(
        set(official.columns)
        | set(synthetic.columns)
    )

    official = official.reindex(
        columns=all_columns
    )

    synthetic = synthetic.reindex(
        columns=all_columns
    )

    return pd.concat(
        [
            official,
            synthetic,
        ],
        ignore_index=True,
    )


# ============================================================
# DATASET SUMMARY
# ============================================================

def dataset_summary(
    source: str = "synthetic",
) -> dict:
    """
    Generate a summary for the selected
    dataset.
    """

    df = load_projects(source)

    return {
        "source": source,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(
            df.isna()
            .sum()
            .sum()
        ),
        "column_names": df.columns.tolist(),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("MPLADS DATA PROCESSOR")
    print("===================================\n")

    print("OFFICIAL DATA")
    print("-----------------------------------")

    official_info = (
        get_official_info()
    )

    print(
        "Rows:",
        official_info["rows"],
    )

    print(
        "Columns:",
        official_info["columns"],
    )

    print(
        "Fields:"
    )

    for column in official_info[
        "column_names"
    ]:
        print(
            " -",
            column,
        )

    print("\nSYNTHETIC DATA")
    print("-----------------------------------")

    synthetic_info = (
        get_synthetic_info()
    )

    print(
        "Rows:",
        synthetic_info["rows"],
    )

    print(
        "Columns:",
        synthetic_info["columns"],
    )

    print(
        "Fields:"
    )

    for column in synthetic_info[
        "column_names"
    ]:
        print(
            " -",
            column,
        )

    print("\n===================================")
    print("DATA PROCESSOR CHECK COMPLETE")
    print("===================================")