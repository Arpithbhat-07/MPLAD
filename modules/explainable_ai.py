import os
import sys
import pandas as pd
import numpy as np
import traceback


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# FILE PATHS
# ============================================================

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "unified_risk_results.csv"
)

OUTPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "explainable_risk_results.csv"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_number(value, default=0.0):
    """Safely convert a value to float."""

    try:
        if pd.isna(value):
            return default

        value = str(value).replace(",", "").strip()

        if value == "":
            return default

        return float(value)

    except Exception:
        return default


def clean_text(value):
    """Safely convert value to text."""

    if pd.isna(value):
        return ""

    return str(value).strip()


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score):
    """Determine risk level from score."""

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    return "LOW"


# ============================================================
# INSPECTION PRIORITY
# ============================================================

def get_priority(level):
    """Determine inspection priority."""

    if level == "HIGH":
        return "IMMEDIATE"

    elif level == "MEDIUM":
        return "REVIEW"

    return "NORMAL"


# ============================================================
# EXPLAIN GENERAL RISK
# ============================================================

def explain_general_risk(row, reasons):
    """Explain general/cost risk."""

    score = safe_number(
        row.get("general_risk", 0)
    )

    if score >= 70:

        reasons.append(
            "General project risk indicators are high."
        )

    elif score >= 40:

        reasons.append(
            "General project risk indicators require review."
        )

    cost = safe_number(
        row.get("cost_estimate_lakhs", 0)
    )

    if cost > 100:

        reasons.append(
            f"Project cost estimate is relatively high "
            f"({cost:.2f} lakhs)."
        )


# ============================================================
# EXPLAIN FUND RISK
# ============================================================

def explain_fund_risk(row, reasons):
    """Explain fund-related risk."""

    score = safe_number(
        row.get("fund_risk", 0)
    )

    if score >= 70:

        reasons.append(
            "Significant fund utilization anomaly detected."
        )

    elif score >= 40:

        reasons.append(
            "Fund utilization pattern requires review."
        )

    # --------------------------------------------------------
    # Calculate utilization when possible
    # --------------------------------------------------------

    estimated_columns = [
        "cost_estimate_lakhs",
        "estimated_cost",
        "estimated_amount",
        "sanctioned_amount",
        "approved_amount",
        "total_cost"
    ]

    spent_columns = [
        "expenditure",
        "spent_amount",
        "amount_spent",
        "fund_utilized",
        "funds_utilized",
        "utilized_amount"
    ]

    estimated = 0
    spent = 0

    for column in estimated_columns:

        if column in row.index:

            estimated = safe_number(
                row[column]
            )

            if estimated > 0:
                break

    for column in spent_columns:

        if column in row.index:

            spent = safe_number(
                row[column]
            )

            if spent > 0:
                break

    if estimated > 0 and spent > 0:

        utilization = (
            spent / estimated
        ) * 100

        if utilization > 100:

            reasons.append(
                f"Reported expenditure exceeds the "
                f"estimated amount ({utilization:.1f}% utilization)."
            )

        elif utilization > 95:

            reasons.append(
                f"Fund utilization is very high "
                f"({utilization:.1f}%)."
            )

        elif utilization < 25:

            reasons.append(
                f"Fund utilization is relatively low "
                f"({utilization:.1f}%)."
            )


# ============================================================
# EXPLAIN TIMELINE RISK
# ============================================================

def explain_timeline_risk(row, reasons):
    """Explain timeline-related risk."""

    score = safe_number(
        row.get("timeline_risk", 0)
    )

    if score >= 70:

        reasons.append(
            "Significant timeline inconsistency or project delay detected."
        )

    elif score >= 40:

        reasons.append(
            "Project timeline requires additional review."
        )

    # --------------------------------------------------------
    # Date validation
    # --------------------------------------------------------

    start_columns = [
        "start_date",
        "work_start_date",
        "project_start_date",
        "sanction_date"
    ]

    completion_columns = [
        "completion_date",
        "completed_date",
        "work_completion_date",
        "project_end_date"
    ]

    start_date = None
    completion_date = None

    for column in start_columns:

        if column in row.index:

            date = pd.to_datetime(
                row[column],
                errors="coerce"
            )

            if not pd.isna(date):

                start_date = date
                break

    for column in completion_columns:

        if column in row.index:

            date = pd.to_datetime(
                row[column],
                errors="coerce"
            )

            if not pd.isna(date):

                completion_date = date
                break

    if (
        start_date is not None
        and completion_date is not None
    ):

        duration = (
            completion_date - start_date
        ).days

        if duration < 0:

            reasons.append(
                "Completion date occurs before the project start date."
            )

        elif duration > 730:

            reasons.append(
                f"Project duration is unusually long "
                f"({duration} days)."
            )

        elif duration > 365:

            reasons.append(
                f"Project duration exceeds one year "
                f"({duration} days)."
            )


# ============================================================
# EXPLAIN DUPLICATE RISK
# ============================================================

def explain_duplicate_risk(row, reasons):
    """Explain duplicate-project risk."""

    score = safe_number(
        row.get("duplicate_risk", 0)
    )

    if score >= 70:

        reasons.append(
            "Possible duplicate or highly similar project detected."
        )

    elif score >= 40:

        reasons.append(
            "Project has similarity indicators that require review."
        )


# ============================================================
# EXPLAIN BASE RISK
# ============================================================

def explain_base_risk(row, reasons):
    """Explain existing/base risk."""

    score = safe_number(
        row.get("base_risk", 0)
    )

    if score >= 70:

        reasons.append(
            "The underlying project risk score is high."
        )

    elif score >= 40:

        reasons.append(
            "The underlying project risk score indicates moderate risk."
        )


# ============================================================
# REMOVE DUPLICATE REASONS
# ============================================================

def remove_duplicate_reasons(reasons):
    """Remove repeated explanation messages."""

    final_reasons = []

    for reason in reasons:

        reason = str(reason).strip()

        if reason and reason not in final_reasons:

            final_reasons.append(reason)

    return final_reasons


# ============================================================
# GENERATE RECOMMENDATION
# ============================================================

def generate_recommendation(
    risk_level,
    reasons
):
    """Generate an explainable recommended action."""

    if risk_level == "HIGH":

        return (
            "Immediate inspection recommended. "
            "Verify financial records, project progress, "
            "supporting documents, and related works."
        )

    elif risk_level == "MEDIUM":

        return (
            "Detailed review recommended. "
            "Verify the detected risk indicators "
            "before taking further action."
        )

    return (
        "No immediate action required. "
        "Continue routine monitoring."
    )


# ============================================================
# ANALYZE ONE PROJECT
# ============================================================

def explain_project(row):
    """Generate complete explanation for one project."""

    reasons = []

    # --------------------------------------------------------
    # Individual explanations
    # --------------------------------------------------------

    explain_general_risk(
        row,
        reasons
    )

    explain_fund_risk(
        row,
        reasons
    )

    explain_timeline_risk(
        row,
        reasons
    )

    explain_duplicate_risk(
        row,
        reasons
    )

    explain_base_risk(
        row,
        reasons
    )

    # --------------------------------------------------------
    # Remove duplicate reasons
    # --------------------------------------------------------

    reasons = remove_duplicate_reasons(
        reasons
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    final_score = safe_number(
        row.get(
            "final_risk_score",
            0
        )
    )

    final_score = max(
        0,
        min(100, final_score)
    )

    level = clean_text(
        row.get(
            "risk_level",
            ""
        )
    ).upper()

    if level not in [
        "HIGH",
        "MEDIUM",
        "LOW"
    ]:

        level = get_risk_level(
            final_score
        )

    priority = get_priority(
        level
    )

    # --------------------------------------------------------
    # If no reason found
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "No major anomaly was identified by the current detection layers."
        )

    # --------------------------------------------------------
    # Main explanation
    # --------------------------------------------------------

    if level == "HIGH":

        explanation = (
            "This project has been classified as HIGH RISK "
            "because one or more risk indicators have reached "
            "a level that requires immediate inspection."
        )

    elif level == "MEDIUM":

        explanation = (
            "This project has been classified as MEDIUM RISK "
            "because some risk indicators require additional review."
        )

    else:

        explanation = (
            "This project has been classified as LOW RISK "
            "because the current risk indicators are within "
            "the acceptable monitoring range."
        )

    recommendation = generate_recommendation(
        level,
        reasons
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "work_id": clean_text(
            row.get("work_id", "")
        ),

        "mp_name": clean_text(
            row.get("mp_name", "")
        ),

        "district": clean_text(
            row.get("district", "")
        ),

        "implementing_agency": clean_text(
            row.get("implementing_agency", "")
        ),

        "work_category": clean_text(
            row.get("work_category", "")
        ),

        "final_risk_score": round(
            final_score,
            2
        ),

        "risk_level": level,

        "inspection_priority": priority,

        "general_risk": round(
            safe_number(
                row.get("general_risk", 0)
            ),
            2
        ),

        "fund_risk": round(
            safe_number(
                row.get("fund_risk", 0)
            ),
            2
        ),

        "timeline_risk": round(
            safe_number(
                row.get("timeline_risk", 0)
            ),
            2
        ),

        "duplicate_risk": round(
            safe_number(
                row.get("duplicate_risk", 0)
            ),
            2
        ),

        "base_risk": round(
            safe_number(
                row.get("base_risk", 0)
            ),
            2
        ),

        "explanation": explanation,

        "why_flagged": " | ".join(
            reasons
        ),

        "recommended_action": recommendation
    }


# ============================================================
# RUN EXPLAINABLE AI
# ============================================================

def run_explainable_ai():

    print("\n")
    print("=" * 70)
    print("              MPLADS EXPLAINABLE AI")
    print("=" * 70)

    print(
        "\nStarting Explainable AI analysis..."
    )

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not os.path.exists(INPUT_FILE):

        print("\nERROR:")
        print(
            "unified_risk_results.csv was not found."
        )

        print(
            "\nExpected file:"
        )

        print(
            INPUT_FILE
        )

        print(
            "\nPlease run unified_risk_engine.py first."
        )

        return None

    # --------------------------------------------------------
    # Load unified results
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            INPUT_FILE
        )

    except Exception as e:

        print(
            "\nERROR: Could not read unified risk results."
        )

        print(
            "Reason:",
            e
        )

        return None

    if df.empty:

        print(
            "\nERROR: Unified risk dataset is empty."
        )

        return None

    print(
        f"\nProjects loaded: {len(df)}"
    )

    # --------------------------------------------------------
    # Generate explanations
    # --------------------------------------------------------

    results = []

    print(
        "\nGenerating explanations..."
    )

    for index, row in df.iterrows():

        try:

            result = explain_project(
                row
            )

            results.append(
                result
            )

        except Exception as e:

            print(
                f"\nWARNING: Could not explain project at row {index}."
            )

            print(
                "Reason:",
                e
            )

    # --------------------------------------------------------
    # Create dataframe
    # --------------------------------------------------------

    if not results:

        print(
            "\nERROR: No explanations generated."
        )

        return None

    result_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort by risk score
    # --------------------------------------------------------

    result_df = result_df.sort_values(
        by="final_risk_score",
        ascending=False
    )

    result_df = result_df.reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

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

    print("\n")
    print("=" * 70)
    print("             EXPLAINABLE AI COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal Projects : {len(result_df)}"
    )

    print(
        f"🚨 HIGH        : {high_count}"
    )

    print(
        f"⚠️  MEDIUM      : {medium_count}"
    )

    print(
        f"✅ LOW         : {low_count}"
    )

    # ========================================================
    # SHOW TOP PROJECT
    # ========================================================

    if not result_df.empty:

        top = result_df.iloc[0]

        print("\n")
        print("=" * 70)
        print("             TOP RISK PROJECT")
        print("=" * 70)

        print(
            f"\nProject ID      : {top['work_id']}"
        )

        print(
            f"MP Name         : {top['mp_name']}"
        )

        print(
            f"District        : {top['district']}"
        )

        print(
            f"Risk Score      : {top['final_risk_score']}/100"
        )

        print(
            f"Risk Level      : {top['risk_level']}"
        )

        print(
            f"Inspection      : {top['inspection_priority']}"
        )

        print(
            "\nRisk Breakdown:"
        )

        print(
            f"  General Risk   : {top['general_risk']}"
        )

        print(
            f"  Fund Risk      : {top['fund_risk']}"
        )

        print(
            f"  Timeline Risk  : {top['timeline_risk']}"
        )

        print(
            f"  Duplicate Risk : {top['duplicate_risk']}"
        )

        print(
            f"  Base Risk      : {top['base_risk']}"
        )

        print(
            "\nWhy was this project flagged?"
        )

        reasons = str(
            top["why_flagged"]
        ).split(" | ")

        for number, reason in enumerate(
            reasons,
            start=1
        ):

            print(
                f"  {number}. {reason}"
            )

        print(
            "\nRecommended Action:"
        )

        print(
            f"  {top['recommended_action']}"
        )

    # ========================================================
    # FINISH
    # ========================================================

    print("\n")
    print("=" * 70)

    print(
        "Explainable results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)

    return result_df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        result = run_explainable_ai()

        if result is not None:

            print(
                "\nExplainable AI finished successfully."
            )

        else:

            print(
                "\nExplainable AI finished with errors."
            )

    except KeyboardInterrupt:

        print(
            "\n\nProcess stopped by user."
        )

    except Exception as e:

        print(
            "\n\nUNEXPECTED ERROR:"
        )

        print(
            e
        )

        traceback.print_exc()

    input(
        "\nPress Enter to close..."
    )