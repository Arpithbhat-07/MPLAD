import os
import sys
import traceback
from datetime import datetime

import pandas as pd


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
    print("ERROR: Could not import data_processor.py")
    print("Reason:", e)
    raise


# ============================================================
# TIMELINE DETECTOR
# ============================================================

class TimelineDetector:

    def __init__(self, dataframe):
        self.df = dataframe.copy()

    # --------------------------------------------------------
    # FIND COLUMN
    # --------------------------------------------------------

    def find_column(self, possible_names):

        columns_lower = {
            str(col).strip().lower(): col
            for col in self.df.columns
        }

        for name in possible_names:
            if name.lower() in columns_lower:
                return columns_lower[name.lower()]

        # Partial matching
        for col_lower, original_col in columns_lower.items():
            for name in possible_names:
                if name.lower() in col_lower:
                    return original_col

        return None

    # --------------------------------------------------------
    # CONVERT DATE
    # --------------------------------------------------------

    def parse_date(self, value):

        if pd.isna(value):
            return None

        value = str(value).strip()

        if value == "":
            return None

        try:
            date = pd.to_datetime(
                value,
                errors="coerce",
                dayfirst=True
            )

            if pd.isna(date):
                return None

            return date

        except Exception:
            return None

    # --------------------------------------------------------
    # FIND TIMELINE COLUMNS
    # --------------------------------------------------------

    def get_timeline_columns(self):

        start_column = self.find_column([
            "start_date",
            "project_start_date",
            "work_start_date",
            "date_of_start",
            "work_commencement_date",
            "commencement_date",
            "sanction_date",
            "approved_date"
        ])

        end_column = self.find_column([
            "completion_date",
            "end_date",
            "project_end_date",
            "work_end_date",
            "date_of_completion",
            "completed_date"
        ])

        expected_column = self.find_column([
            "expected_completion_date",
            "expected_end_date",
            "target_completion_date",
            "scheduled_completion_date"
        ])

        status_column = self.find_column([
            "status",
            "work_status",
            "project_status"
        ])

        return (
            start_column,
            end_column,
            expected_column,
            status_column
        )

    # --------------------------------------------------------
    # DETECT TIMELINE ANOMALIES
    # --------------------------------------------------------

    def analyze_project(self, row):

        start_column, end_column, expected_column, status_column = (
            self.get_timeline_columns()
        )

        reasons = []
        score = 0

        timeline_flags = []

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = ""

        if status_column:
            status = str(row.get(status_column, "")).strip().lower()

        # ----------------------------------------------------
        # DATES
        # ----------------------------------------------------

        start_date = None
        end_date = None
        expected_date = None

        if start_column:
            start_date = self.parse_date(row.get(start_column))

        if end_column:
            end_date = self.parse_date(row.get(end_column))

        if expected_column:
            expected_date = self.parse_date(row.get(expected_column))

        today = pd.Timestamp.today().normalize()

        # ----------------------------------------------------
        # MISSING TIMELINE DATA
        # ----------------------------------------------------

        if not start_column and not end_column:
            reasons.append(
                "No start/completion date columns were found in the dataset."
            )
            score += 5
            timeline_flags.append("Missing timeline fields")

        else:

            if start_column and start_date is None:
                reasons.append(
                    "Project start date is missing or invalid."
                )
                score += 10
                timeline_flags.append("Invalid start date")

            if end_column and end_date is None:

                # Only flag missing completion date strongly when
                # the project appears completed.

                if any(word in status for word in [
                    "complete",
                    "completed",
                    "finish",
                    "finished",
                    "closed"
                ]):

                    reasons.append(
                        "Project is marked completed but completion date is missing or invalid."
                    )

                    score += 20
                    timeline_flags.append(
                        "Completed without valid completion date"
                    )

            # ------------------------------------------------
            # FUTURE START DATE
            # ------------------------------------------------

            if start_date and start_date > today:

                reasons.append(
                    "Project start date is in the future."
                )

                score += 15
                timeline_flags.append(
                    "Future start date"
                )

            # ------------------------------------------------
            # FUTURE COMPLETION DATE
            # ------------------------------------------------

            if end_date and end_date > today:

                # A future end date can be legitimate for
                # ongoing projects, so only flag it mildly.

                if any(word in status for word in [
                    "complete",
                    "completed",
                    "finish",
                    "finished",
                    "closed"
                ]):

                    reasons.append(
                        "Project is marked completed but completion date is in the future."
                    )

                    score += 20
                    timeline_flags.append(
                        "Future completion date"
                    )

            # ------------------------------------------------
            # END DATE BEFORE START DATE
            # ------------------------------------------------

            if start_date and end_date:

                if end_date < start_date:

                    reasons.append(
                        "Completion date occurs before the project start date."
                    )

                    score += 40
                    timeline_flags.append(
                        "Invalid date sequence"
                    )

                else:

                    duration_days = (
                        end_date - start_date
                    ).days

                    # ----------------------------------------
                    # VERY LONG PROJECT
                    # ----------------------------------------

                    if duration_days > 1095:

                        reasons.append(
                            f"Project duration is unusually long: "
                            f"{duration_days} days."
                        )

                        score += 25
                        timeline_flags.append(
                            "Excessive project duration"
                        )

                    elif duration_days > 730:

                        reasons.append(
                            f"Project duration exceeds two years: "
                            f"{duration_days} days."
                        )

                        score += 15
                        timeline_flags.append(
                            "Long project duration"
                        )

            # ------------------------------------------------
            # EXPECTED COMPLETION DATE
            # ------------------------------------------------

            if expected_date and end_date:

                if end_date > expected_date:

                    delay_days = (
                        end_date - expected_date
                    ).days

                    if delay_days > 180:

                        reasons.append(
                            f"Project was completed "
                            f"{delay_days} days after the expected completion date."
                        )

                        score += 30
                        timeline_flags.append(
                            "Major completion delay"
                        )

                    elif delay_days > 90:

                        reasons.append(
                            f"Project was completed "
                            f"{delay_days} days after the expected completion date."
                        )

                        score += 20
                        timeline_flags.append(
                            "Completion delay"
                        )

                    elif delay_days > 30:

                        reasons.append(
                            f"Project was completed "
                            f"{delay_days} days after the expected completion date."
                        )

                        score += 10
                        timeline_flags.append(
                            "Minor completion delay"
                        )

            # ------------------------------------------------
            # ONGOING PROJECT DELAY
            # ------------------------------------------------

            if start_date and end_date is None:

                if any(word in status for word in [
                    "ongoing",
                    "in progress",
                    "under progress",
                    "progress",
                    "started"
                ]):

                    duration_days = (
                        today - start_date
                    ).days

                    if duration_days > 1095:

                        reasons.append(
                            f"Ongoing project has exceeded "
                            f"three years: {duration_days} days."
                        )

                        score += 35
                        timeline_flags.append(
                            "Severe ongoing delay"
                        )

                    elif duration_days > 730:

                        reasons.append(
                            f"Ongoing project has exceeded "
                            f"two years: {duration_days} days."
                        )

                        score += 25
                        timeline_flags.append(
                            "Long ongoing project"
                        )

                    elif duration_days > 365:

                        reasons.append(
                            f"Ongoing project has been active "
                            f"for more than one year: {duration_days} days."
                        )

                        score += 15
                        timeline_flags.append(
                            "Ongoing project delay"
                        )

        # ----------------------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------------------

        reasons = list(dict.fromkeys(reasons))
        timeline_flags = list(dict.fromkeys(timeline_flags))

        # ----------------------------------------------------
        # LIMIT SCORE
        # ----------------------------------------------------

        score = min(score, 100)

        # ----------------------------------------------------
        # RISK LEVEL
        # ----------------------------------------------------

        if score >= 70:
            risk_level = "HIGH"

        elif score >= 30:
            risk_level = "MEDIUM"

        else:
            risk_level = "LOW"

        # ----------------------------------------------------
        # INSPECTION PRIORITY
        # ----------------------------------------------------

        if risk_level == "HIGH":
            inspection_priority = "IMMEDIATE"

        elif risk_level == "MEDIUM":
            inspection_priority = "REVIEW"

        else:
            inspection_priority = "NORMAL"

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "timeline_risk_score": score,
            "timeline_risk_level": risk_level,
            "timeline_flags": ", ".join(timeline_flags)
            if timeline_flags else "No major timeline anomaly",
            "timeline_reasons": reasons,
            "inspection_priority": inspection_priority
        }

    # --------------------------------------------------------
    # ANALYZE ALL PROJECTS
    # --------------------------------------------------------

    def analyze_all(self):

        results = []

        for index, row in self.df.iterrows():

            try:

                result = self.analyze_project(row)

                project_result = row.to_dict()

                project_result.update(result)

                results.append(project_result)

            except Exception as e:

                print(
                    f"Warning: Could not analyze row {index}: {e}"
                )

        return pd.DataFrame(results)


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_project_result(result):

    print("\n" + "=" * 65)
    print("TIMELINE ANALYSIS RESULT")
    print("=" * 65)

    print(
        f"Timeline Risk Score : "
        f"{result['timeline_risk_score']}/100"
    )

    print(
        f"Timeline Risk Level : "
        f"{result['timeline_risk_level']}"
    )

    print(
        f"Inspection Priority : "
        f"{result['inspection_priority']}"
    )

    print(
        f"Timeline Flags      : "
        f"{result['timeline_flags']}"
    )

    print("\nWhy flagged:")

    if result["timeline_reasons"]:

        for number, reason in enumerate(
            result["timeline_reasons"],
            start=1
        ):
            print(f"{number}. {reason}")

    else:

        print("No timeline anomaly detected.")

    print("=" * 65)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("          MPLADS TIMELINE DETECTION ENGINE")
    print("=" * 65)

    print("\nTimeline detector started successfully.")

    try:

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        print("\nLoading project dataset...")

        df = load_projects()

        if df is None:
            raise ValueError(
                "Data processor returned no dataset."
            )

        if df.empty:
            raise ValueError(
                "Dataset is empty."
            )

        print(
            f"Projects loaded successfully: {len(df)}"
        )

        print(
            f"Columns available: {list(df.columns)}"
        )

        # ----------------------------------------------------
        # CREATE DETECTOR
        # ----------------------------------------------------

        detector = TimelineDetector(df)

        # ----------------------------------------------------
        # SHOW DETECTED COLUMNS
        # ----------------------------------------------------

        columns = detector.get_timeline_columns()

        print("\nTimeline columns detected:")

        print(
            f"Start Date      : {columns[0]}"
        )

        print(
            f"Completion Date : {columns[1]}"
        )

        print(
            f"Expected Date   : {columns[2]}"
        )

        print(
            f"Status          : {columns[3]}"
        )

        # ----------------------------------------------------
        # ANALYZE FIRST PROJECT
        # ----------------------------------------------------

        print("\nAnalyzing first project...")

        first_result = detector.analyze_project(
            df.iloc[0]
        )

        display_project_result(first_result)

        # ----------------------------------------------------
        # ANALYZE ALL PROJECTS
        # ----------------------------------------------------

        print("\nAnalyzing all projects...")

        results_df = detector.analyze_all()

        print(
            f"\nSuccessfully analyzed "
            f"{len(results_df)} projects."
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        if not results_df.empty:

            print("\n" + "=" * 65)
            print("TIMELINE RISK SUMMARY")
            print("=" * 65)

            high_count = (
                results_df["timeline_risk_level"]
                .eq("HIGH")
                .sum()
            )

            medium_count = (
                results_df["timeline_risk_level"]
                .eq("MEDIUM")
                .sum()
            )

            low_count = (
                results_df["timeline_risk_level"]
                .eq("LOW")
                .sum()
            )

            print(f"HIGH RISK   : {high_count}")
            print(f"MEDIUM RISK : {medium_count}")
            print(f"LOW RISK    : {low_count}")

            print("\nTop timeline-risk projects:")

            display_columns = []

            for column in [
                "work_id",
                "mp_name",
                "district",
                "status",
                "timeline_risk_score",
                "timeline_risk_level",
                "timeline_flags"
            ]:

                if column in results_df.columns:
                    display_columns.append(column)

            if display_columns:

                top_projects = (
                    results_df
                    .sort_values(
                        "timeline_risk_score",
                        ascending=False
                    )
                    .head(10)
                )

                print(
                    top_projects[
                        display_columns
                    ].to_string(index=False)
                )

        print("\n")
        print("=" * 65)
        print("TIMELINE DETECTION COMPLETED")
        print("=" * 65)

    except Exception as e:

        print("\nERROR:")
        print(str(e))

        print("\nFull traceback:")
        traceback.print_exc()

    finally:

        input(
            "\nPress Enter to close..."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()