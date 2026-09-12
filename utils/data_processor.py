import os
import pandas as pd


# =========================================================
# PROJECT PATH
# =========================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

DATA_FOLDER = os.path.join(
    PROJECT_ROOT,
    "data"
)


# =========================================================
# FIND CSV FILE AUTOMATICALLY
# =========================================================

def find_dataset():

    if not os.path.exists(DATA_FOLDER):

        raise FileNotFoundError(
            f"\nDATA FOLDER NOT FOUND:\n{DATA_FOLDER}"
        )

    csv_files = [
        file
        for file in os.listdir(DATA_FOLDER)
        if file.lower().endswith(".csv")
    ]

    if not csv_files:

        raise FileNotFoundError(
            f"\nNO CSV FILE FOUND INSIDE:\n{DATA_FOLDER}"
        )

    # Prefer "flagged works.csv"
    preferred = [
        file for file in csv_files
        if file.lower() == "flagged works.csv"
    ]

    if preferred:
        filename = preferred[0]
    else:
        # If filename is different, use the first CSV
        filename = csv_files[0]

    return os.path.join(
        DATA_FOLDER,
        filename
    )


# =========================================================
# LOAD PROJECTS
# =========================================================

def load_projects():

    print("\n" + "=" * 60)
    print("MPLADS DATA PROCESSOR")
    print("=" * 60)

    print("\nProject folder:")
    print(PROJECT_ROOT)

    print("\nData folder:")
    print(DATA_FOLDER)


    # Find CSV
    DATA_FILE = find_dataset()

    print("\nDataset found:")
    print(DATA_FILE)


    # Read CSV
    df = pd.read_csv(DATA_FILE)


    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    print("\nColumns detected:")

    for column in df.columns:
        print(" -", column)


    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    REQUIRED_COLUMNS = [
        "work_id",
        "mp_name",
        "district",
        "implementing_agency",
        "work_category",
        "cost_estimate_lakhs",
        "status",
        "risk_score"
    ]


    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]


    if missing_columns:

        raise ValueError(
            "\n\nMISSING COLUMNS:\n"
            + "\n".join(
                "- " + column
                for column in missing_columns
            )
            + "\n\nYour CSV contains:\n"
            + "\n".join(
                "- " + column
                for column in df.columns
            )
        )


    # =====================================================
    # CLEAN TEXT COLUMNS
    # =====================================================

    text_columns = [
        "work_id",
        "mp_name",
        "district",
        "implementing_agency",
        "work_category",
        "status"
    ]


    for column in text_columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    # =====================================================
    # CLEAN NUMERIC COLUMNS
    # =====================================================

    df["cost_estimate_lakhs"] = pd.to_numeric(
        df["cost_estimate_lakhs"],
        errors="coerce"
    ).fillna(0)


    df["risk_score"] = pd.to_numeric(
        df["risk_score"],
        errors="coerce"
    ).fillna(0)


    # =====================================================
    # OPTIONAL REASON COLUMN
    # =====================================================

    if "reasons_text" not in df.columns:

        df["reasons_text"] = ""


    df["reasons_text"] = (
        df["reasons_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    print("\nRows loaded:", len(df))

    print("\nDATASET LOADED SUCCESSFULLY!")

    print("=" * 60)


    return df


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    try:

        data = load_projects()

        print("\nFirst 5 records:")
        print(data.head())

        print(
            "\nDATA PROCESSOR WORKING SUCCESSFULLY!"
        )

    except Exception as error:

        print("\n" + "=" * 60)
        print("DATASET ERROR")
        print("=" * 60)

        print(error)

        print("=" * 60)