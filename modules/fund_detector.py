import os
import sys
import traceback
import pandas as pd


# ============================================================
# MPLADS FUND UTILIZATION ANOMALY DETECTOR
# ============================================================

print("\n" + "=" * 70)
print("             MPLADS FUND UTILIZATION DETECTOR")
print("=" * 70)
print("Fund detector started successfully.")


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
# FUND DETECTOR
# ============================================================

class FundDetector:

    def __init__(self):

        print("\nLoading dataset...")

        self.df = load_projects()

        if self.df is None:
            raise ValueError("Dataset returned None.")

        if not isinstance(self.df, pd.DataFrame):
            raise TypeError(
                "Dataset must be a pandas DataFrame."
            )

        self.df = self.df.copy()

        # Clean column names
        self.df.columns = [
            str(column).strip().lower()
            for column in self.df.columns
        ]

        print(
            f"Dataset loaded successfully."
        )

        print(
            f"Total projects: {len(self.df)}"
        )

        print("\nAvailable columns:")
        print(list(self.df.columns))


    # ========================================================
    # SAFE NUMBER
    # ========================================================

    def safe_number(self, value):

        try:

            if pd.isna(value):
                return 0.0

            value = str(value)

            # Remove commas and currency symbols
            value = (
                value
                .replace(",", "")
                .replace("₹", "")
                .replace("$", "")
                .strip()
            )

            return float(value)

        except Exception:
            return 0.0


    # ========================================================
    # FIND COLUMN
    # ========================================================

    def find_column(self, possible_columns):

        for column in possible_columns:

            if column in self.df.columns:
                return column

        return None


    # ========================================================
    # GET PROJECT INFORMATION
    # ========================================================

    def get_project_info(self, row):

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

            "category": str(
                row.get("work_category", "")
            ),

            "status": str(
                row.get("status", "")
            )
        }


    # ========================================================
    # 1. FUND UTILIZATION PERCENTAGE
    # ========================================================

    def calculate_utilization(self, row):

        estimate_column = self.find_column([
            "cost_estimate_lakhs",
            "estimated_cost",
            "sanctioned_amount",
            "sanction_amount",
            "approved_amount",
            "project_cost"
        ])

        expenditure_column = self.find_column([
            "expenditure",
            "amount_spent",
            "spent_amount",
            "actual_expenditure",
            "fund_utilized",
            "fund_utilization",
            "utilized_amount"
        ])

        if not estimate_column:
            return None

        if not expenditure_column:
            return None

        estimated = self.safe_number(
            row.get(estimate_column)
        )

        spent = self.safe_number(
            row.get(expenditure_column)
        )

        if estimated <= 0:
            return None

        utilization = (
            spent / estimated
        ) * 100

        return {
            "estimated": estimated,
            "spent": spent,
            "percentage": utilization,
            "estimate_column": estimate_column,
            "expenditure_column": expenditure_column
        }


    # ========================================================
    # 2. EXCESS FUND UTILIZATION
    # ========================================================

    def detect_excess_utilization(self, row):

        result = {
            "detected": False,
            "type": "EXCESS_FUND_UTILIZATION",
            "severity": "LOW",
            "message": "",
            "utilization_percentage": None
        }

        data = self.calculate_utilization(row)

        if data is None:
            return result

        percentage = data["percentage"]

        result["utilization_percentage"] = round(
            percentage,
            2
        )

        # More than 120% of estimated amount
        if percentage > 120:

            result["detected"] = True
            result["severity"] = "HIGH"

            result["message"] = (
                f"Expenditure is {percentage:.1f}% "
                f"of the estimated/sanctioned amount. "
                f"This indicates possible excess expenditure."
            )

        elif percentage > 100:

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                f"Expenditure is {percentage:.1f}% "
                f"of the estimated/sanctioned amount."
            )

        return result


    # ========================================================
    # 3. LOW UTILIZATION
    # ========================================================

    def detect_low_utilization(self, row):

        result = {
            "detected": False,
            "type": "LOW_FUND_UTILIZATION",
            "severity": "LOW",
            "message": "",
            "utilization_percentage": None
        }

        data = self.calculate_utilization(row)

        if data is None:
            return result

        percentage = data["percentage"]

        result["utilization_percentage"] = round(
            percentage,
            2
        )

        status = str(
            row.get("status", "")
        ).strip().lower()

        completed_statuses = [
            "completed",
            "complete",
            "finished",
            "closed"
        ]

        # Completed but less than 20% utilized
        if (
            percentage < 20
            and status in completed_statuses
        ):

            result["detected"] = True
            result["severity"] = "HIGH"

            result["message"] = (
                f"Only {percentage:.1f}% of the "
                f"estimated/sanctioned amount has been "
                f"utilized although the project is marked "
                f"as '{status}'."
            )

        # Ongoing project with extremely low utilization
        elif (
            percentage < 10
            and status in [
                "ongoing",
                "in progress",
                "pending"
            ]
        ):

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                f"Fund utilization is unusually low "
                f"at {percentage:.1f}% for a project "
                f"currently marked '{status}'."
            )

        return result


    # ========================================================
    # 4. STATUS VS FUND INCONSISTENCY
    # ========================================================

    def detect_status_fund_inconsistency(self, row):

        result = {
            "detected": False,
            "type": "STATUS_FUND_INCONSISTENCY",
            "severity": "LOW",
            "message": "",
            "utilization_percentage": None
        }

        data = self.calculate_utilization(row)

        if data is None:
            return result

        percentage = data["percentage"]

        result["utilization_percentage"] = round(
            percentage,
            2
        )

        status = str(
            row.get("status", "")
        ).strip().lower()

        # Completed but very high utilization
        if (
            status in [
                "completed",
                "complete",
                "finished"
            ]
            and percentage > 120
        ):

            result["detected"] = True
            result["severity"] = "HIGH"

            result["message"] = (
                f"Project is marked completed but "
                f"reported expenditure is {percentage:.1f}% "
                f"of the estimated/sanctioned amount."
            )

        # Ongoing but almost completely spent
        elif (
            status in [
                "ongoing",
                "in progress"
            ]
            and percentage >= 100
        ):

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                f"Project is still marked '{status}' "
                f"but {percentage:.1f}% of the "
                f"estimated/sanctioned amount has already "
                f"been spent."
            )

        return result


    # ========================================================
    # 5. VERY LOW FUND UTILIZATION
    # ========================================================

    def detect_idle_funds(self, row):

        result = {
            "detected": False,
            "type": "IDLE_FUNDS",
            "severity": "LOW",
            "message": "",
            "utilization_percentage": None
        }

        data = self.calculate_utilization(row)

        if data is None:
            return result

        percentage = data["percentage"]

        result["utilization_percentage"] = round(
            percentage,
            2
        )

        status = str(
            row.get("status", "")
        ).strip().lower()

        # Pending project with very little spending
        if (
            status in [
                "pending",
                "approved",
                "not started"
            ]
            and percentage > 0
            and percentage < 5
        ):

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                f"Only {percentage:.1f}% of allocated/"
                f"estimated funds have been utilized while "
                f"the project status is '{status}'."
            )

        return result


    # ========================================================
    # 6. FUND DATA QUALITY
    # ========================================================

    def detect_fund_data_quality(self, row):

        result = {
            "detected": False,
            "type": "FUND_DATA_QUALITY",
            "severity": "LOW",
            "message": ""
        }

        estimate_column = self.find_column([
            "cost_estimate_lakhs",
            "estimated_cost",
            "sanctioned_amount",
            "sanction_amount",
            "approved_amount",
            "project_cost"
        ])

        if not estimate_column:
            return result

        value = row.get(
            estimate_column
        )

        if pd.isna(value) or str(value).strip() == "":

            result["detected"] = True
            result["severity"] = "MEDIUM"

            result["message"] = (
                "Estimated/sanctioned project amount "
                "is missing."
            )

        return result


    # ========================================================
    # ANALYZE ONE PROJECT
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
            ==
            str(work_id).strip()
        ]

        if matches.empty:

            return {
                "error": f"Project {work_id} not found."
            }

        row = matches.iloc[0]

        info = self.get_project_info(row)

        # Run all fund detectors
        detectors = [

            self.detect_excess_utilization,

            self.detect_low_utilization,

            self.detect_status_fund_inconsistency,

            self.detect_idle_funds,

            self.detect_fund_data_quality
        ]

        anomalies = []

        for detector in detectors:

            try:

                result = detector(row)

                if result["detected"]:

                    anomalies.append(result)

            except Exception as e:

                print(
                    f"Detector error in "
                    f"{detector.__name__}: {e}"
                )

        # ----------------------------------------------------
        # FUND SCORE
        # ----------------------------------------------------

        score = 0

        points = {
            "HIGH": 40,
            "MEDIUM": 20,
            "LOW": 5
        }

        for anomaly in anomalies:

            score += points.get(
                anomaly["severity"],
                0
            )

        score = min(score, 100)

        # ----------------------------------------------------
        # FUND RISK LEVEL
        # ----------------------------------------------------

        if score >= 70:

            risk_level = "HIGH"

        elif score >= 30:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # ----------------------------------------------------
        # UTILIZATION
        # ----------------------------------------------------

        utilization_data = (
            self.calculate_utilization(row)
        )

        if utilization_data:

            utilization = round(
                utilization_data["percentage"],
                2
            )

            estimated = round(
                utilization_data["estimated"],
                2
            )

            spent = round(
                utilization_data["spent"],
                2
            )

        else:

            utilization = None
            estimated = None
            spent = None

        # ----------------------------------------------------
        # EXPLAINABLE REASONS
        # ----------------------------------------------------

        reasons = []

        for anomaly in anomalies:

            reasons.append(
                anomaly["message"]
            )

        if not reasons:

            reasons.append(
                "No major fund utilization anomaly "
                "detected."
            )

        # ----------------------------------------------------
        # INSPECTION PRIORITY
        # ----------------------------------------------------

        if risk_level == "HIGH":

            priority = "IMMEDIATE"

        elif risk_level == "MEDIUM":

            priority = "REVIEW"

        else:

            priority = "NORMAL"

        return {

            **info,

            "estimated_amount": estimated,

            "spent_amount": spent,

            "utilization_percentage": utilization,

            "fund_anomaly_score": score,

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
# MAIN TEST
# ============================================================

def main():

    try:

        detector = FundDetector()

        if len(detector.df) == 0:

            print(
                "\nNo projects found in dataset."
            )

            return

        # ----------------------------------------------------
        # FIRST PROJECT
        # ----------------------------------------------------

        first_work_id = detector.df.iloc[0]["work_id"]

        print("\n" + "=" * 70)
        print("                 FIRST PROJECT FUND ANALYSIS")
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
            f"{result['category']}"
        )

        print(
            f"Status              : "
            f"{result['status']}"
        )

        print(
            f"\nEstimated Amount    : "
            f"{result['estimated_amount']}"
        )

        print(
            f"Spent Amount       : "
            f"{result['spent_amount']}"
        )

        print(
            f"Fund Utilization   : "
            f"{result['utilization_percentage']}%"
        )

        print(
            f"Fund Anomaly Score : "
            f"{result['fund_anomaly_score']}/100"
        )

        print(
            f"Risk Level         : "
            f"{result['risk_level']}"
        )

        print(
            f"Inspection Priority: "
            f"{result['inspection_priority']}"
        )

        # ----------------------------------------------------
        # ANOMALIES
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("DETECTED FUND ANOMALIES")
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
                "\nNo fund anomalies detected."
            )

        # ----------------------------------------------------
        # EXPLAINABLE REASONS
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print("EXPLAINABLE FUND RISK REASONS")
        print("-" * 70)

        for index, reason in enumerate(
            result["reasons"],
            start=1
        ):

            print(
                f"{index}. {reason}"
            )

        # ----------------------------------------------------
        # ANALYZE ALL
        # ----------------------------------------------------

        print("\n" + "=" * 70)
        print("             ANALYZING ALL PROJECT FUNDS")
        print("=" * 70)

        results = detector.analyze_all()

        print(
            f"\nProjects analyzed : "
            f"{len(results)}"
        )

        high = sum(
            1
            for r in results
            if r["risk_level"] == "HIGH"
        )

        medium = sum(
            1
            for r in results
            if r["risk_level"] == "MEDIUM"
        )

        low = sum(
            1
            for r in results
            if r["risk_level"] == "LOW"
        )

        total_anomalies = sum(
            r["anomaly_count"]
            for r in results
        )

        print(
            f"High Risk Funds   : {high}"
        )

        print(
            f"Medium Risk Funds : {medium}"
        )

        print(
            f"Low Risk Funds    : {low}"
        )

        print(
            f"Total Fund Alerts : {total_anomalies}"
        )

        print("\n" + "=" * 70)
        print("        FUND DETECTION COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:

        print("\n" + "=" * 70)
        print("             FUND DETECTOR FAILED")
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