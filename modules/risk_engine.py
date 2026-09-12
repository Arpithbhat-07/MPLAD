import os
import sys
import traceback
import pandas as pd


# ============================================================
# RISK ENGINE START
# ============================================================

print("\n" + "=" * 60)
print("        MPLADS AI RISK DETECTION ENGINE")
print("=" * 60)
print("Risk engine file started successfully.")


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

print(f"Project root: {PROJECT_ROOT}")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


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
    input("\nPress Enter to exit...")
    sys.exit(1)


# ============================================================
# RISK ENGINE CLASS
# ============================================================

class RiskEngine:

    def __init__(self):
        print("\nLoading MPLADS dataset...")

        try:
            self.df = load_projects()

            if self.df is None:
                raise ValueError("load_projects() returned None")

            if not isinstance(self.df, pd.DataFrame):
                raise TypeError("Dataset is not a pandas DataFrame")

            print(f"Dataset loaded successfully.")
            print(f"Number of projects: {len(self.df)}")

            if len(self.df) == 0:
                print("WARNING: Dataset contains 0 projects.")

            print("\nAvailable columns:")
            print(list(self.df.columns))

        except Exception as e:
            print("\nERROR while loading dataset:")
            print(e)
            traceback.print_exc()
            raise

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    def get_risk_level(self, score):

        if score >= 71:
            return "HIGH"

        elif score >= 31:
            return "MEDIUM"

        return "LOW"

    # --------------------------------------------------------
    # COST ANOMALY
    # --------------------------------------------------------

    def detect_cost_anomaly(self, row):

        try:

            if "cost_estimate_lakhs" not in self.df.columns:
                return None

            cost = float(row.get("cost_estimate_lakhs", 0))

            if cost <= 0:
                return None

            category = row.get("work_category", "")

            category_data = self.df[
                self.df["work_category"].astype(str).str.lower()
                == str(category).lower()
            ]

            if len(category_data) < 2:
                return None

            average_cost = pd.to_numeric(
                category_data["cost_estimate_lakhs"],
                errors="coerce"
            ).mean()

            if pd.isna(average_cost) or average_cost <= 0:
                return None

            percentage = ((cost - average_cost) / average_cost) * 100

            if percentage >= 50:

                return {
                    "type": "COST_ANOMALY",
                    "severity": "HIGH",
                    "message": (
                        f"Project cost is {percentage:.1f}% "
                        f"higher than the category average."
                    ),
                    "project_cost": round(cost, 2),
                    "category_average": round(average_cost, 2)
                }

        except Exception as e:
            print(f"Cost anomaly error: {e}")

        return None

    # --------------------------------------------------------
    # DUPLICATE PROJECT DETECTION
    # --------------------------------------------------------

    def detect_duplicate(self, row):

        try:

            required = [
                "mp_name",
                "district",
                "work_category",
                "work_id"
            ]

            for column in required:
                if column not in self.df.columns:
                    return None

            mp = str(row.get("mp_name", "")).strip().lower()
            district = str(row.get("district", "")).strip().lower()
            category = str(row.get("work_category", "")).strip().lower()
            work_id = str(row.get("work_id", "")).strip()

            matches = self.df[
                (self.df["mp_name"].astype(str).str.strip().str.lower() == mp)
                &
                (self.df["district"].astype(str).str.strip().str.lower() == district)
                &
                (
                    self.df["work_category"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    == category
                )
                &
                (self.df["work_id"].astype(str).str.strip() != work_id)
            ]

            if len(matches) > 0:

                return {
                    "type": "DUPLICATE_PROJECT",
                    "severity": "HIGH",
                    "message": (
                        f"Possible duplicate work detected. "
                        f"{len(matches)} similar project(s) found."
                    ),
                    "similar_projects": matches[
                        "work_id"
                    ].astype(str).tolist()
                }

        except Exception as e:
            print(f"Duplicate detection error: {e}")

        return None

    # --------------------------------------------------------
    # STATUS ANOMALY
    # --------------------------------------------------------

    def detect_status_anomaly(self, row):

        try:

            status = str(row.get("status", "")).strip().lower()

            risk_score = float(row.get("risk_score", 0))

            if status in [
                "ongoing",
                "delayed",
                "pending",
                "in progress"
            ] and risk_score >= 70:

                return {
                    "type": "STATUS_ANOMALY",
                    "severity": "HIGH",
                    "message": (
                        "Project has a high risk score while "
                        f"status is '{status}'."
                    )
                }

        except Exception as e:
            print(f"Status anomaly error: {e}")

        return None

    # --------------------------------------------------------
    # TIMELINE INCONSISTENCY
    # --------------------------------------------------------

    def detect_timeline_anomaly(self, row):

        try:

            status = str(row.get("status", "")).lower()

            if status in ["completed", "complete", "finished"]:

                risk_score = float(row.get("risk_score", 0))

                if risk_score >= 70:

                    return {
                        "type": "TIMELINE_INCONSISTENCY",
                        "severity": "MEDIUM",
                        "message": (
                            "Project is marked completed but "
                            "has a very high risk score."
                        )
                    }

        except Exception as e:
            print(f"Timeline detection error: {e}")

        return None

    # --------------------------------------------------------
    # EXPLAINABLE AI
    # --------------------------------------------------------

    def explain_risk(self, row):

        reasons = []

        try:

            score = float(row.get("risk_score", 0))

            if score >= 71:
                reasons.append(
                    "Existing risk score indicates a high-risk project."
                )

            elif score >= 31:
                reasons.append(
                    "Existing risk score indicates a medium-risk project."
                )

            # Cost
            cost_result = self.detect_cost_anomaly(row)

            if cost_result:
                reasons.append(
                    cost_result["message"]
                )

            # Duplicate
            duplicate_result = self.detect_duplicate(row)

            if duplicate_result:
                reasons.append(
                    duplicate_result["message"]
                )

            # Status
            status_result = self.detect_status_anomaly(row)

            if status_result:
                reasons.append(
                    status_result["message"]
                )

            # Timeline
            timeline_result = self.detect_timeline_anomaly(row)

            if timeline_result:
                reasons.append(
                    timeline_result["message"]
                )

            if not reasons:
                reasons.append(
                    "No major anomaly detected by the current rules."
                )

        except Exception as e:

            reasons.append(
                f"Risk explanation error: {e}"
            )

        return reasons

    # --------------------------------------------------------
    # ANALYZE ONE PROJECT
    # --------------------------------------------------------

    def analyze_project(self, work_id):

        if "work_id" not in self.df.columns:
            return {
                "error": "work_id column not found in dataset."
            }

        matches = self.df[
            self.df["work_id"].astype(str) == str(work_id)
        ]

        if matches.empty:

            return {
                "error": f"Project '{work_id}' not found."
            }

        row = matches.iloc[0]

        try:
            score = float(row.get("risk_score", 0))
        except:
            score = 0

        risk_level = self.get_risk_level(score)

        anomalies = []

        cost = self.detect_cost_anomaly(row)
        duplicate = self.detect_duplicate(row)
        status = self.detect_status_anomaly(row)
        timeline = self.detect_timeline_anomaly(row)

        for anomaly in [
            cost,
            duplicate,
            status,
            timeline
        ]:

            if anomaly:
                anomalies.append(anomaly)

        reasons = self.explain_risk(row)

        result = {
            "work_id": str(row.get("work_id", "")),
            "mp_name": str(row.get("mp_name", "")),
            "district": str(row.get("district", "")),
            "work_category": str(
                row.get("work_category", "")
            ),
            "cost_estimate_lakhs": row.get(
                "cost_estimate_lakhs", 0
            ),
            "status": str(row.get("status", "")),
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons,
            "anomalies": anomalies,
            "inspection_priority": (
                "IMMEDIATE"
                if risk_level == "HIGH"
                else "NORMAL"
            )
        }

        return result

    # --------------------------------------------------------
    # ANALYZE ALL PROJECTS
    # --------------------------------------------------------

    def analyze_all(self):

        results = []

        if "work_id" not in self.df.columns:
            print("ERROR: work_id column not found.")
            return results

        for work_id in self.df["work_id"]:

            result = self.analyze_project(work_id)

            if "error" not in result:
                results.append(result)

        return results


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\nStarting Risk Engine...\n")

    try:

        engine = RiskEngine()

        if len(engine.df) == 0:
            print("\nNo projects available for analysis.")
            return

        # ----------------------------------------------------
        # TEST FIRST PROJECT
        # ----------------------------------------------------

        first_work_id = engine.df.iloc[0]["work_id"]

        print("\n" + "=" * 60)
        print("TESTING FIRST PROJECT")
        print("=" * 60)

        result = engine.analyze_project(first_work_id)

        print("\nPROJECT DETAILS")
        print("-" * 40)

        print(f"Work ID       : {result.get('work_id')}")
        print(f"MP Name       : {result.get('mp_name')}")
        print(f"District      : {result.get('district')}")
        print(f"Category      : {result.get('work_category')}")
        print(f"Cost          : {result.get('cost_estimate_lakhs')} Lakhs")
        print(f"Status        : {result.get('status')}")

        print("\nRISK ANALYSIS")
        print("-" * 40)

        print(f"Risk Score    : {result.get('risk_score')}")
        print(f"Risk Level    : {result.get('risk_level')}")
        print(
            f"Inspection    : {result.get('inspection_priority')}"
        )

        print("\nEXPLAINABLE AI REASONS")
        print("-" * 40)

        for i, reason in enumerate(
            result.get("reasons", []),
            start=1
        ):
            print(f"{i}. {reason}")

        print("\nDETECTED ANOMALIES")
        print("-" * 40)

        anomalies = result.get("anomalies", [])

        if anomalies:

            for anomaly in anomalies:

                print(
                    f"• {anomaly.get('type')} "
                    f"[{anomaly.get('severity')}]"
                )

                print(
                    f"  {anomaly.get('message')}"
                )

        else:
            print("No additional anomalies detected.")

        # ----------------------------------------------------
        # ANALYZE ALL
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("ANALYZING ALL PROJECTS")
        print("=" * 60)

        results = engine.analyze_all()

        print(
            f"\nTotal projects analyzed: {len(results)}"
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

        print(f"High Risk   : {high}")
        print(f"Medium Risk : {medium}")
        print(f"Low Risk    : {low}")

        print("\n" + "=" * 60)
        print("RISK ENGINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        print("\n" + "=" * 60)
        print("RISK ENGINE FAILED")
        print("=" * 60)

        print(f"\nError: {e}")

        traceback.print_exc()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()

    input("\nPress Enter to close...")