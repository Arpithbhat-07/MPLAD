import os
import sys
import traceback
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORT DATA PROCESSOR
# ============================================================

try:
    from utils.data_processor import load_projects
except Exception as e:
    print("ERROR: Could not import data_processor.")
    print("Reason:", e)
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "unified_risk_results.csv"
)

DUPLICATE_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "duplicate_detection_results.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_number(value, default=0.0):
    """
    Convert a value safely into a number.
    """
    try:
        if pd.isna(value):
            return default

        value = str(value).replace(",", "").strip()

        if value == "":
            return default

        return float(value)

    except Exception:
        return default


def normalize_score(value):
    """
    Keep score between 0 and 100.
    """
    value = safe_number(value)

    return max(0.0, min(100.0, value))


def get_column(df, possible_names):
    """
    Find a column using multiple possible names.
    """

    columns = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.lower()

        if key in columns:
            return columns[key]

    return None


def risk_level(score):
    """
    Convert final score into risk level.
    """

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    return "LOW"


def inspection_priority(level):
    """
    Convert risk level into inspection priority.
    """

    if level == "HIGH":
        return "IMMEDIATE"

    elif level == "MEDIUM":
        return "REVIEW"

    return "NORMAL"


# ============================================================
# COST / GENERAL RISK
# ============================================================

def calculate_general_risk(row):
    """
    Calculate general/cost risk.

    Uses existing risk_score when available.
    Otherwise checks basic cost/status anomalies.
    """

    risk = 0.0
    reasons = []

    # --------------------------------------------------------
    # Existing risk score
    # --------------------------------------------------------

    existing_score = safe_number(
        row.get("risk_score", 0)
    )

    if existing_score > 0:
        risk = existing_score

        if existing_score >= 70:
            reasons.append(
                "Existing project risk score is high."
            )

    # --------------------------------------------------------
    # Cost estimate
    # --------------------------------------------------------

    cost = safe_number(
        row.get("cost_estimate_lakhs", 0)
    )

    if cost > 100:
        risk += 10
        reasons.append(
            "Project cost estimate is unusually high."
        )

    elif cost > 50:
        risk += 5
        reasons.append(
            "Project has a relatively high cost estimate."
        )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    status = str(
        row.get("status", "")
    ).strip().lower()

    if status in [
        "cancelled",
        "canceled",
        "abandoned",
        "stopped"
    ]:
        risk += 20

        reasons.append(
            "Project status indicates cancellation or stoppage."
        )

    return normalize_score(risk), reasons


# ============================================================
# FUND RISK
# ============================================================

def calculate_fund_risk(row):
    """
    Calculate fund utilization risk.
    """

    reasons = []

    estimated_column = get_column(
        pd.DataFrame([row]),
        [
            "cost_estimate_lakhs",
            "estimated_cost",
            "estimated_amount",
            "sanctioned_amount",
            "approved_amount",
            "total_cost"
        ]
    )

    spent_column = get_column(
        pd.DataFrame([row]),
        [
            "expenditure",
            "spent_amount",
            "amount_spent",
            "fund_utilized",
            "funds_utilized",
            "utilized_amount"
        ]
    )

    estimated = 0
    spent = 0

    if estimated_column:
        estimated = safe_number(row.get(estimated_column, 0))

    if spent_column:
        spent = safe_number(row.get(spent_column, 0))

    # --------------------------------------------------------
    # No expenditure data
    # --------------------------------------------------------

    if estimated <= 0 or spent <= 0:
        return 0.0, reasons

    utilization = (spent / estimated) * 100

    # --------------------------------------------------------
    # Excess utilization
    # --------------------------------------------------------

    if utilization > 110:
        risk = 90

        reasons.append(
            f"Fund utilization is unusually high ({utilization:.1f}%)."
        )

    elif utilization > 100:
        risk = 75

        reasons.append(
            f"Expenditure exceeds estimated amount ({utilization:.1f}%)."
        )

    elif utilization > 95:
        risk = 50

        reasons.append(
            f"Fund utilization is very high ({utilization:.1f}%)."
        )

    # --------------------------------------------------------
    # Low utilization
    # --------------------------------------------------------

    elif utilization < 10:
        risk = 45

        reasons.append(
            f"Very low fund utilization ({utilization:.1f}%)."
        )

    elif utilization < 25:
        risk = 25

        reasons.append(
            f"Low fund utilization ({utilization:.1f}%)."
        )

    else:
        risk = 0

    return normalize_score(risk), reasons


# ============================================================
# TIMELINE RISK
# ============================================================

def calculate_timeline_risk(row):
    """
    Calculate timeline risk from project dates.
    """

    reasons = []

    start_column = get_column(
        pd.DataFrame([row]),
        [
            "start_date",
            "work_start_date",
            "project_start_date",
            "sanction_date"
        ]
    )

    completion_column = get_column(
        pd.DataFrame([row]),
        [
            "completion_date",
            "completed_date",
            "work_completion_date",
            "project_end_date"
        ]
    )

    if not start_column:
        return 0.0, reasons

    start_date = pd.to_datetime(
        row.get(start_column),
        errors="coerce"
    )

    if pd.isna(start_date):
        return 0.0, reasons

    # --------------------------------------------------------
    # Completion date
    # --------------------------------------------------------

    if completion_column:

        completion_date = pd.to_datetime(
            row.get(completion_column),
            errors="coerce"
        )

        if not pd.isna(completion_date):

            duration = (
                completion_date - start_date
            ).days

            if duration < 0:

                reasons.append(
                    "Completion date occurs before start date."
                )

                return 90.0, reasons

            elif duration > 730:

                reasons.append(
                    f"Project duration is unusually long ({duration} days)."
                )

                return 80.0, reasons

            elif duration > 540:

                reasons.append(
                    f"Project duration is high ({duration} days)."
                )

                return 60.0, reasons

            elif duration > 365:

                reasons.append(
                    f"Project duration exceeds one year ({duration} days)."
                )

                return 40.0, reasons

    # --------------------------------------------------------
    # Ongoing project
    # --------------------------------------------------------

    status = str(
        row.get("status", "")
    ).strip().lower()

    if status in [
        "ongoing",
        "in progress",
        "in-progress",
        "pending"
    ]:

        duration = (
            pd.Timestamp.now() - start_date
        ).days

        if duration > 730:

            reasons.append(
                f"Ongoing project has exceeded two years ({duration} days)."
            )

            return 85.0, reasons

        elif duration > 365:

            reasons.append(
                f"Ongoing project has exceeded one year ({duration} days)."
            )

            return 60.0, reasons

    return 0.0, reasons


# ============================================================
# DUPLICATE RISK
# ============================================================

def load_duplicate_results():
    """
    Load results generated by duplicate_detector.py.

    This prevents the unified engine from performing another
    expensive 3000 x 3000 comparison.
    """

    if not os.path.exists(DUPLICATE_FILE):

        print(
            "\nWARNING: duplicate_detection_results.csv "
            "was not found."
        )

        print(
            "Duplicate risk will be set to 0."
        )

        return None

    try:

        duplicate_df = pd.read_csv(
            DUPLICATE_FILE
        )

        print(
            f"\nLoaded duplicate detection results: "
            f"{len(duplicate_df)} rows"
        )

        return duplicate_df

    except Exception as e:

        print(
            "WARNING: Could not load duplicate results."
        )

        print("Reason:", e)

        return None


def calculate_duplicate_risk(row, duplicate_df):
    """
    Get duplicate risk for a project from the
    previously generated duplicate results.
    """

    reasons = []

    if duplicate_df is None:
        return 0.0, reasons

    # --------------------------------------------------------
    # Detect work ID column
    # --------------------------------------------------------

    main_work_id = row.get("work_id", "")

    duplicate_work_column = get_column(
        duplicate_df,
        [
            "work_id",
            "project_id",
            "id",
            "workid"
        ]
    )

    if duplicate_work_column is None:
        return 0.0, reasons

    matches = duplicate_df[
        duplicate_df[duplicate_work_column].astype(str)
        == str(main_work_id)
    ]

    if matches.empty:
        return 0.0, reasons

    # --------------------------------------------------------
    # Find score column
    # --------------------------------------------------------

    score_column = get_column(
        duplicate_df,
        [
            "duplicate_risk_score",
            "risk_score",
            "duplicate_score",
            "score"
        ]
    )

    if score_column:

        scores = matches[score_column].apply(
            safe_number
        )

        score = float(scores.max())

    else:

        score = 70.0

    # --------------------------------------------------------
    # Find duplicate flag
    # --------------------------------------------------------

    flag_column = get_column(
        duplicate_df,
        [
            "duplicate",
            "is_duplicate",
            "duplicate_detected",
            "possible_duplicate"
        ]
    )

    duplicate_found = True

    if flag_column:

        values = matches[flag_column].astype(str).str.lower()

        duplicate_found = values.isin(
            [
                "true",
                "yes",
                "1",
                "duplicate"
            ]
        ).any()

    if duplicate_found:

        reasons.append(
            "Possible duplicate or highly similar project detected."
        )

    return normalize_score(score), reasons


# ============================================================
# MAIN PROJECT ANALYSIS
# ============================================================

def analyze_project(row, duplicate_df=None):
    """
    Analyze one project using all risk layers.
    """

    # --------------------------------------------------------
    # General
    # --------------------------------------------------------

    general_risk, general_reasons = (
        calculate_general_risk(row)
    )

    # --------------------------------------------------------
    # Fund
    # --------------------------------------------------------

    fund_risk, fund_reasons = (
        calculate_fund_risk(row)
    )

    # --------------------------------------------------------
    # Timeline
    # --------------------------------------------------------

    timeline_risk, timeline_reasons = (
        calculate_timeline_risk(row)
    )

    # --------------------------------------------------------
    # Duplicate
    # --------------------------------------------------------

    duplicate_risk, duplicate_reasons = (
        calculate_duplicate_risk(
            row,
            duplicate_df
        )
    )

    # --------------------------------------------------------
    # Final weighted score
    #
    # General   = 20%
    # Fund      = 20%
    # Timeline  = 20%
    # Duplicate = 20%
    # Base risk = 20%
    #
    # Existing risk_score is already included inside
    # general risk, so we use the four layer scores
    # plus a normalized base component.
    # --------------------------------------------------------

    base_risk = safe_number(
        row.get("risk_score", 0)
    )

    base_risk = normalize_score(base_risk)

    final_score = (
        general_risk * 0.20
        + fund_risk * 0.20
        + timeline_risk * 0.20
        + duplicate_risk * 0.20
        + base_risk * 0.20
    )

    final_score = normalize_score(
        round(final_score, 2)
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    level = risk_level(
        final_score
    )

    priority = inspection_priority(
        level
    )

    # --------------------------------------------------------
    # Combine explanations
    # --------------------------------------------------------

    reasons = []

    reasons.extend(general_reasons)
    reasons.extend(fund_reasons)
    reasons.extend(timeline_reasons)
    reasons.extend(duplicate_reasons)

    # Remove duplicate reasons
    unique_reasons = []

    for reason in reasons:

        if reason not in unique_reasons:
            unique_reasons.append(reason)

    # --------------------------------------------------------
    # Default explanation
    # --------------------------------------------------------

    if not unique_reasons:

        if level == "LOW":

            unique_reasons.append(
                "No major anomaly detected by the current risk layers."
            )

        else:

            unique_reasons.append(
                "Project requires additional review based on combined risk indicators."
            )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "work_id": row.get("work_id", ""),
        "mp_name": row.get("mp_name", ""),
        "district": row.get("district", ""),
        "implementing_agency": row.get(
            "implementing_agency",
            ""
        ),
        "work_category": row.get(
            "work_category",
            ""
        ),
        "cost_estimate_lakhs": safe_number(
            row.get("cost_estimate_lakhs", 0)
        ),

        "general_risk": round(
            general_risk,
            2
        ),

        "fund_risk": round(
            fund_risk,
            2
        ),

        "timeline_risk": round(
            timeline_risk,
            2
        ),

        "duplicate_risk": round(
            duplicate_risk,
            2
        ),

        "base_risk": round(
            base_risk,
            2
        ),

        "final_risk_score": final_score,

        "risk_level": level,

        "inspection_priority": priority,

        "risk_reasons": " | ".join(
            unique_reasons
        )
    }


# ============================================================
# RUN UNIFIED ENGINE
# ============================================================

def run_unified_engine():

    print("\n")
    print("=" * 70)
    print("          MPLADS AI UNIFIED RISK ENGINE")
    print("=" * 70)

    print("\nStarting unified risk analysis...")

    # --------------------------------------------------------
    # Load main dataset
    # --------------------------------------------------------

    try:

        df = load_projects()

    except Exception as e:

        print("\nERROR: Could not load project dataset.")
        print("Reason:", e)

        traceback.print_exc()

        return None

    if df is None or df.empty:

        print(
            "\nERROR: Dataset is empty."
        )

        return None

    print(
        f"\nTotal projects loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # Load duplicate results
    # --------------------------------------------------------

    duplicate_df = load_duplicate_results()

    # --------------------------------------------------------
    # Analyze projects
    # --------------------------------------------------------

    results = []

    print(
        "\nRunning unified risk detection..."
    )

    for index, row in df.iterrows():

        try:

            result = analyze_project(
                row,
                duplicate_df
            )

            results.append(result)

        except Exception as e:

            print(
                f"\nWARNING: Could not analyze row {index}."
            )

            print("Reason:", e)

    # --------------------------------------------------------
    # Convert to dataframe
    # --------------------------------------------------------

    if not results:

        print(
            "\nERROR: No results generated."
        )

        return None

    result_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort by final risk score
    # --------------------------------------------------------

    result_df = result_df.sort_values(
        by="final_risk_score",
        ascending=False
    )

    result_df = result_df.reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    high_count = (
        result_df["risk_level"]
        .eq("HIGH")
        .sum()
    )

    medium_count = (
        result_df["risk_level"]
        .eq("MEDIUM")
        .sum()
    )

    low_count = (
        result_df["risk_level"]
        .eq("LOW")
        .sum()
    )

    # ========================================================
    # FINAL OUTPUT
    # ========================================================

    print("\n")
    print("=" * 70)
    print("              UNIFIED RISK ANALYSIS COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal Projects Analyzed : {len(result_df)}"
    )

    print(
        f"🚨 HIGH RISK             : {high_count}"
    )

    print(
        f"⚠️  MEDIUM RISK           : {medium_count}"
    )

    print(
        f"✅ LOW RISK              : {low_count}"
    )

    print("\n" + "-" * 70)

    print(
        "TOP 10 HIGH-RISK PROJECTS"
    )

    print("-" * 70)

    top_columns = [
        "work_id",
        "district",
        "final_risk_score",
        "risk_level",
        "inspection_priority"
    ]

    available_columns = [
        col
        for col in top_columns
        if col in result_df.columns
    ]

    print(
        result_df[
            available_columns
        ].head(10).to_string(index=False)
    )

    # --------------------------------------------------------
    # Detailed explanation for highest risk project
    # --------------------------------------------------------

    if not result_df.empty:

        top_project = result_df.iloc[0]

        print("\n")
        print("=" * 70)
        print("          HIGHEST-RISK PROJECT DETAILS")
        print("=" * 70)

        print(
            f"\nProject ID       : "
            f"{top_project['work_id']}"
        )

        print(
            f"District         : "
            f"{top_project['district']}"
        )

        print(
            f"Final Risk Score : "
            f"{top_project['final_risk_score']}/100"
        )

        print(
            f"Risk Level       : "
            f"{top_project['risk_level']}"
        )

        print(
            f"Inspection       : "
            f"{top_project['inspection_priority']}"
        )

        print("\nRisk Breakdown:")

        print(
            f"  General Risk   : "
            f"{top_project['general_risk']}"
        )

        print(
            f"  Fund Risk      : "
            f"{top_project['fund_risk']}"
        )

        print(
            f"  Timeline Risk  : "
            f"{top_project['timeline_risk']}"
        )

        print(
            f"  Duplicate Risk : "
            f"{top_project['duplicate_risk']}"
        )

        print(
            f"  Base Risk      : "
            f"{top_project['base_risk']}"
        )

        print("\nWhy flagged:")

        reasons = str(
            top_project["risk_reasons"]
        ).split(" | ")

        for number, reason in enumerate(
            reasons,
            start=1
        ):

            print(
                f"  {number}. {reason}"
            )

    print("\n")
    print("=" * 70)

    print(
        f"Results saved to:\n{OUTPUT_FILE}"
    )

    print("=" * 70)

    return result_df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        result = run_unified_engine()

        if result is not None:

            print(
                "\nUnified Risk Engine finished successfully."
            )

        else:

            print(
                "\nUnified Risk Engine finished with errors."
            )

    except KeyboardInterrupt:

        print(
            "\n\nProcess stopped by user."
        )

    except Exception as e:

        print(
            "\n\nUNEXPECTED ERROR:"
        )

        print(e)

        traceback.print_exc()

    input(
        "\nPress Enter to close..."
    )