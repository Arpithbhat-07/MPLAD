import os
import sys
import traceback
import pandas as pd
import numpy as np


# ============================================================
# MPLADS MULTI-LAYER ANOMALY DETECTOR
# ============================================================

print("\n" + "=" * 70)
print("          MPLADS MULTI-LAYER ANOMALY DETECTOR")
print("=" * 70)
print("Anomaly detector started successfully.")


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print(f"Project root: {PROJECT_ROOT}")


# ============================================================
# IMPORT DATA PROCESSOR
# ============================================================

try:
    from utils.data_processor import load_projects
    print("Data processor imported successfully.")
except Exception as e:
    print("\nERROR: Could not import data_processor.py")
    print(e)
    traceback.print_exc()
    sys.exit(1)


# ============================================================
# ANOMALY DETECTOR CLASS
# ============================================================

class AnomalyDetector:

    def __init__(self):

        print("\nLoading dataset...")

        self.df = load_projects()

        if self.df is None:
            raise ValueError("Dataset returned None.")

        if not isinstance(self.df, pd.DataFrame):
            raise TypeError("Dataset must be a pandas DataFrame.")

        print(f"Dataset loaded successfully.")
        print(f"Total projects: {len(self.df)}")

        # Make a copy so original dataframe is never modified
        self.df = self.df.copy()

        # Clean column names
        self.df.columns = [
            str(col).strip().lower()
            for col in self.df.columns
        ]

        print("\nColumns detected:")
        print(list(self.df.columns))


    # ========================================================
    # HELPER: SAFE NUMBER
    # ========================================================

    def safe_number(self, value):

        try:

            if pd.isna(value):
                return 0.0

            value = str(value).replace(",", "").strip()

            return float(value)

        except Exception:
            return 0.0


    # ========================================================
    # 1. COST ANOMALY
    # ========================================================

    def detect_cost_anomaly(self, row):

        result = {
            "detected": False,
            "type": "COST_ANOMALY",
            "severity": "LOW",
            "message": ""
        }

        if "cost_estimate_lakhs" not in self.df.columns:
            return result

        cost = self.safe_number(
            row.get("cost_estimate_lakhs", 0)
        )

        if cost <= 0:
            return result

        category = str(
            row.get("work_category", "")
        ).strip().lower()

        if "work_category" not in self.df.columns:
            return result

        category_df = self.df[
            self.df["work_category"]
            .astype(str)
            .str.strip()
            .str.lower()
            == category
        ]

        if len(category_df) < 2:
            return result

        category_costs = pd.to_numeric(
            category_df["cost_estimate_lakhs"],
            errors="coerce"
        ).dropna()

        if len(category_costs) < 2:
            return result

        average_cost = category_costs.mean()

        if average_cost <= 0:
            return result

        difference = (
            (cost - average_cost)
            / average_cost
        ) * 100

        # Very high cost
        if difference >= 75:

            result["detected"] = True
            result["severity"] = "HIGH"
            result["message"] = (
                f"Project cost is {difference:.1f}% "
                f"higher than the average cost of "
                f"similar projects."
            )

        # Moderately high cost
        elif difference >= 50:

            result["detected"] = True
            result["severity"] = "MEDIUM"
            result["message"] = (
                f"Project cost is {difference:.1f}% "
                f"higher than the category average."
            )

        return result


    # ========================================================
    # 2. DUPLICATE PROJECT DETECTION
    # ========================================================

    def detect_duplicate(self, row):

        result = {
            "detected": False,
            "type": "DUPLICATE_PROJECT",
            "severity": "LOW",
            "message": "",
            "similar_projects": []
        }

        required = [
            "work_id",
            "mp_name",
            "district",
            "work_category"
        ]

        for column in required:

            if column not in self.df.columns:
                return result

        work_id = str(
            row.get("work_id", "")
        ).strip().lower()

        mp_name = str(
            row.get("mp_name", "")
        ).strip().lower()

        district = str(
            row.get("district", "")
        ).strip().lower()

        category = str(
            row.get("work_category", "")
        ).strip().lower()

        matches = self.df[
            (
                self.df["mp_name"]
                .astype(str)
                .str.strip()
                .str.lower()
                == mp_name
            )
            &
            (
                self.df["district"]
                .astype(str)
                .str.strip()
                .str.lower()
                == district
            )
            &
            (
                self.df["work_category"]
                .astype(str)
                .str.strip()
                .str.lower()
                == category
            )
            &
            (
                self.df["work_id"]
                .astype(str)
                .str.strip()
                .str.lower()
                != work_id
            )
        ]

        if len(matches) > 0:

            result["detected"] = True
            result["severity"] = "HIGH"

            result["similar_projects"] = (
                matches["work_id"]
                .astype(str)
                .tolist()
            )

            result["message"] = (
                f"{len(matches)} similar project(s) "
                f"found for the same MP, district "
                f"and work category."
            )

        return result


    # ========================================================
    # 3. STATUS ANOMALY
    # ========================================================

    def detect_status_anomaly(self, row):

        result = {
            "detected": False,
            "type": "STATUS_ANOMALY",
            "severity": "LOW",
            "message": ""
        }

        status = str(
            row.get("status", "")
        ).strip().lower()

        risk_score = self.safe_number(
            row.get("risk_score", 0)
        )

        # High risk + ongoing/pending
        if (
            status in [
                "ongoing",
                "pending",
                "delayed",
                "in progress"
            ]
            and risk_score >= 70
        ):

            result["detected"] = True
            result["severity"] = "HIGH"

            result["message"] = (
                f"Project status is '{status}' "
                f"while its risk score is {risk_score:.0f}/100."
            )

        return result


    # ========================================================
    # 4. TIMELINE INCONSISTENCY
    # ========================================================

    def detect_timeline_anomaly(self, row):

        result = {
            "detected": False,
            "type": "TIMELINE_INCONSISTENCY",
            "severity": "LOW",
            "message": ""
        }

        status = str(
            row.get("status", "")
        ).strip().lower()

        # If dataset contains dates
        start_columns = [
            "start_date",
            "work_start_date",
            "project_start_date"
        ]

        end_columns = [
            "completion_date",
            "end_date",
            "expected_completion_date"
        ]

        start_column = next(
            (
                col for col in start_columns
                if col in self.df.columns
            ),
            None
        )

        end_column = next(
            (
                col for col in end_columns
                if col in self.df.columns
            ),
            None
        )

        # If dates are available
        if start_column and end_column:

            try:

                start_date = pd.to_datetime(
                    row.get(start_column),
                    errors="coerce"
                )

                end_date = pd.to_datetime(
                    row.get(end_column),
                    errors="coerce"
                )

                if (
                    not pd.isna(start_date)
                    and not pd.isna(end_date)
                    and end_date < start_date
                ):

                    result["detected"] = True
                    result["severity"] = "HIGH"

                    result["message"] = (
                        "Completion date occurs before "
                        "the project start date."
                    )

                    return result

            except Exception:
                pass

        # Completed project with high risk
        risk_score = self.safe_number(
            row.get("risk_score", 0)
        )

        if (
            status in [
                "completed",
                "complete",
                "finished"
            ]
            and risk_score >= 70
        ):

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                "Project is marked completed but "
                "has a high risk score."
            )

        return result


    # ========================================================
    # 5. FUND UTILIZATION ANOMALY
    # ========================================================

    def detect_fund_anomaly(self, row):

        result = {
            "detected": False,
            "type": "FUND_UTILIZATION_ANOMALY",
            "severity": "LOW",
            "message": ""
        }

        # Possible column names
        estimate_columns = [
            "cost_estimate_lakhs",
            "estimated_cost",
            "sanctioned_amount",
            "sanction_amount"
        ]

        expenditure_columns = [
            "expenditure",
            "amount_spent",
            "spent_amount",
            "actual_expenditure",
            "fund_utilized"
        ]

        estimate_column = next(
            (
                col for col in estimate_columns
                if col in self.df.columns
            ),
            None
        )

        expenditure_column = next(
            (
                col for col in expenditure_columns
                if col in self.df.columns
            ),
            None
        )

        if not estimate_column or not expenditure_column:
            return result

        estimated = self.safe_number(
            row.get(estimate_column, 0)
        )

        spent = self.safe_number(
            row.get(expenditure_column, 0)
        )

        if estimated <= 0:
            return result

        utilization = (
            spent / estimated
        ) * 100

        # Spending greater than sanctioned/estimated amount
        if utilization > 120:

            result["detected"] = True
            result["severity"] = "HIGH"

            result["message"] = (
                f"Fund utilization is {utilization:.1f}% "
                f"of the estimated/sanctioned amount, "
                f"which exceeds the expected limit."
            )

        # Very low utilization
        elif utilization < 20:

            status = str(
                row.get("status", "")
            ).lower()

            if status in [
                "completed",
                "complete",
                "finished"
            ]:

                result["detected"] = True
                result["severity"] = "MEDIUM"

                result["message"] = (
                    f"Only {utilization:.1f}% of the "
                    f"estimated/sanctioned amount appears "
                    f"to have been utilized despite the "
                    f"project being marked completed."
                )

        return result


    # ========================================================
    # 6. MISSING/INCOMPLETE DATA CHECK
    # ========================================================

    def detect_data_quality(self, row):

        result = {
            "detected": False,
            "type": "DATA_QUALITY_ANOMALY",
            "severity": "LOW",
            "message": ""
        }

        important_columns = [
            "work_id",
            "mp_name",
            "district",
            "work_category",
            "cost_estimate_lakhs",
            "status"
        ]

        missing = []

        for column in important_columns:

            if column in self.df.columns:

                value = row.get(column)

                if (
                    pd.isna(value)
                    or str(value).strip() == ""
                ):

                    missing.append(column)

        if missing:

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                "Important project information is missing: "
                + ", ".join(missing)
            )

        return result


    # ========================================================
    # RUN ALL DETECTORS FOR ONE PROJECT
    # ========================================================

    def analyze_project(self, work_id):

        if "work_id" not in self.df.columns:

            return {
                "error": "work_id column not found."
            }

        matches = self.df[
            self.df["work_id"]
            .astype(str)
            .str.strip()
            == str(work_id).strip()
        ]

        if matches.empty:

            return {
                "error": f"Project {work_id} not found."
            }

        row = matches.iloc[0]

        detectors = [
            self.detect_cost_anomaly,
            self.detect_duplicate,
            self.detect_status_anomaly,
            self.detect_timeline_anomaly,
            self.detect_fund_anomaly,
            self.detect_data_quality
        ]

        anomalies = []

        for detector in detectors:

            try:

                result = detector(row)

                if result["detected"]:
                    anomalies.append(result)

            except Exception as e:

                print(
                    f"Detector error: {detector.__name__}: {e}"
                )

        # ----------------------------------------------------
        # Calculate anomaly score
        # ----------------------------------------------------

        anomaly_score = 0

        severity_points = {
            "HIGH": 30,
            "MEDIUM": 15,
            "LOW": 5
        }

        for anomaly in anomalies:

            anomaly_score += severity_points.get(
                anomaly["severity"],
                0
            )

        # Maximum 100
        anomaly_score = min(
            anomaly_score,
            100
        )

        if anomaly_score >= 70:

            risk_level = "HIGH"

        elif anomaly_score >= 30:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # ----------------------------------------------------
        # Explainable reasons
        # ----------------------------------------------------

        reasons = []

        for anomaly in anomalies:

            reasons.append(
                anomaly["message"]
            )

        if not reasons:

            reasons.append(
                "No major anomaly detected by the "
                "current anomaly detection rules."
            )

        # ----------------------------------------------------
        # Inspection priority
        # ----------------------------------------------------

        if risk_level == "HIGH":

            priority = "IMMEDIATE"

        elif risk_level == "MEDIUM":

            priority = "REVIEW"

        else:

            priority = "NORMAL"

        return {

            "work_id": str(
                row.get("work_id", "")
            ),

            "mp_name": str(
                row.get("mp_name", "")
            ),

            "district": str(
                row.get("district", "")
            ),

            "work_category": str(
                row.get("work_category", "")
            ),

            "status": str(
                row.get("status", "")
            ),

            "cost_estimate_lakhs": self.safe_number(
                row.get("cost_estimate_lakhs", 0)
            ),

            "anomaly_score": anomaly_score,

            "risk_level": risk_level,

            "inspection_priority": priority,

            "anomaly_count": len(anomalies),

            "anomalies": anomalies,

            "reasons": reasons
        }


    # ========================================================
    # ANALYZE ALL PROJECTS
    # ========================================================

    def analyze_all(self):

        results = []

        if "work_id" not in self.df.columns:

            print(
                "\nERROR: work_id column not found."
            )

            return results

        for work_id in self.df["work_id"]:

            result = self.analyze_project(
                work_id
            )

            if "error" not in result:

                results.append(result)

        return results


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        detector = AnomalyDetector()

        if len(detector.df) == 0:

            print(
                "\nNo projects found in dataset."
            )

            return

        # ----------------------------------------------------
        # TEST FIRST PROJECT
        # ----------------------------------------------------

        first_work_id = detector.df.iloc[0]["work_id"]

        print("\n" + "=" * 70)
        print("             FIRST PROJECT ANALYSIS")
        print("=" * 70)

        result = detector.analyze_project(
            first_work_id
        )

        print(
            f"\nWork ID             : "
            f"{result['work_id']}"
        )

        print(
            f"MP Name             : "
            f"{result['mp_name']}"
        )

        print(
            f"District            : "
            f"{result['district']}"
        )

        print(
            f"Work Category       : "
            f"{result['work_category']}"
        )

        print(
            f"Status              : "
            f"{result['status']}"
        )

        print(
            f"Cost                : "
            f"{result['cost_estimate_lakhs']} Lakhs"
        )

        print(
            f"\nAnomaly Score       : "
            f"{result['anomaly_score']}/100"
        )

        print(
            f"Risk Level          : "
            f"{result['risk_level']}"
        )

        print(
            f"Inspection Priority : "
            f"{result['inspection_priority']}"
        )

        print(
            f"Anomalies Found     : "
            f"{result['anomaly_count']}"
        )

        # ----------------------------------------------------
        # ANOMALIES
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("DETECTED ANOMALIES")
        print("-" * 70)

        if result["anomalies"]:

            for index, anomaly in enumerate(
                result["anomalies"],
                start=1
            ):

                print(
                    f"\n{index}. "
                    f"{anomaly['type']}"
                )

                print(
                    f"   Severity : "
                    f"{anomaly['severity']}"
                )

                print(
                    f"   Reason   : "
                    f"{anomaly['message']}"
                )

        else:

            print(
                "\nNo anomalies detected."
            )

        # ----------------------------------------------------
        # EXPLAINABLE AI
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("EXPLAINABLE RISK REASONS")
        print("-" * 70)

        for index, reason in enumerate(
            result["reasons"],
            start=1
        ):

            print(
                f"{index}. {reason}"
            )

        # ----------------------------------------------------
        # ALL PROJECTS
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("             ANALYZING ALL PROJECTS")
        print("=" * 70)

        results = detector.analyze_all()

        print(
            f"\nProjects analyzed: "
            f"{len(results)}"
        )

        high = sum(
            1 for r in results
            if r["risk_level"] == "HIGH"
        )

        medium = sum(
            1 for r in results
            if r["risk_level"] == "MEDIUM"
        )

        low = sum(
            1 for r in results
            if r["risk_level"] == "LOW"
        )

        total_anomalies = sum(
            r["anomaly_count"]
            for r in results
        )

        print(
            f"High Risk Projects   : {high}"
        )

        print(
            f"Medium Risk Projects : {medium}"
        )

        print(
            f"Low Risk Projects    : {low}"
        )

        print(
            f"Total Anomalies      : {total_anomalies}"
        )

        print("\n" + "=" * 70)
        print("      MULTI-LAYER ANOMALY DETECTION COMPLETE")
        print("=" * 70)

    except Exception as e:

        print("\n" + "=" * 70)
        print("              ANOMALY DETECTOR FAILED")
        print("=" * 70)

        print(
            f"\nError: {e}"
        )

        traceback.print_exc()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()

    input("\nPress Enter to close...")