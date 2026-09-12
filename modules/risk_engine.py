import pandas as pd
from datetime import datetime


class RiskEngine:

    def __init__(self, dataframe=None):
        """
        Risk engine.

        If a dataframe is supplied, use it directly.
        This prevents the engine from accidentally loading
        an empty dataset.
        """

        if dataframe is not None:
            self.df = dataframe.copy()
        else:
            self.df = pd.DataFrame()

        self._prepare_data()

        print("\n==============================")
        print("RISK ENGINE INITIALIZED")
        print("Projects loaded:", len(self.df))
        print("==============================\n")

    # ---------------------------------------------------------
    # PREPARE DATA
    # ---------------------------------------------------------

    def _prepare_data(self):

        if self.df is None:
            self.df = pd.DataFrame()

        if self.df.empty:
            return

        # Column aliases
        rename_map = {
            "id": "work_id",
            "project_id": "work_id",
            "name": "project_name",
            "title": "project_name",
            "category": "work_category",
            "cost": "cost_estimate",
            "estimated_cost": "cost_estimate",
            "sanctioned": "sanctioned_amount",
            "spent": "spent_amount",
            "expenditure": "spent_amount",
            "progress": "physical_progress",
        }

        for old, new in rename_map.items():
            if old in self.df.columns and new not in self.df.columns:
                self.df.rename(columns={old: new}, inplace=True)

        # Required default columns
        defaults = {
            "work_id": "UNKNOWN",
            "project_name": "Unnamed Project",
            "mp_name": "Unknown MP",
            "district": "Unknown",
            "state": "Karnataka",
            "work_category": "General",
            "agency": "Unknown Agency",
            "sanctioned_amount": 0,
            "spent_amount": 0,
            "physical_progress": 0,
            "status": "Unknown",
            "start_date": "",
            "expected_date": "",
            "contractor": "Unknown Contractor",
        }

        for column, default in defaults.items():
            if column not in self.df.columns:
                self.df[column] = default

        # Numeric conversion
        numeric_columns = [
            "sanctioned_amount",
            "spent_amount",
            "physical_progress"
        ]

        for column in numeric_columns:
            self.df[column] = pd.to_numeric(
                self.df[column],
                errors="coerce"
            ).fillna(0)

        # Progress range
        self.df["physical_progress"] = (
            self.df["physical_progress"]
            .clip(0, 100)
        )

        # Text conversion
        text_columns = [
            "work_id",
            "project_name",
            "mp_name",
            "district",
            "state",
            "work_category",
            "agency",
            "status",
            "contractor",
        ]

        for column in text_columns:
            self.df[column] = (
                self.df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        # Calculate utilization
        self.df["utilization"] = self.df.apply(
            lambda row:
                round(
                    (row["spent_amount"] /
                     row["sanctioned_amount"]) * 100,
                    2
                )
                if row["sanctioned_amount"] > 0
                else 0,
            axis=1
        )

        # Calculate risk
        self.df["risk_score"] = self.df.apply(
            self.calculate_risk_score,
            axis=1
        )

        self.df["risk_level"] = self.df["risk_score"].apply(
            self.get_risk_level
        )

    # ---------------------------------------------------------
    # RISK SCORE
    # ---------------------------------------------------------

    def calculate_risk_score(self, row):

        score = 0

        sanctioned = float(row.get("sanctioned_amount", 0))
        spent = float(row.get("spent_amount", 0))
        progress = float(row.get("physical_progress", 0))
        status = str(row.get("status", "")).lower()

        # -----------------------------------------
        # 1. Fund utilization vs physical progress
        # -----------------------------------------

        if sanctioned > 0:

            utilization = (spent / sanctioned) * 100

            if utilization > progress + 30:
                score += 35

            elif utilization > progress + 20:
                score += 25

            elif utilization > progress + 10:
                score += 15

        # -----------------------------------------
        # 2. Delayed / critical status
        # -----------------------------------------

        if "critical" in status:
            score += 35

        elif "delay" in status:
            score += 30

        elif "pending" in status:
            score += 20

        elif "review" in status:
            score += 15

        elif "ongoing" in status:
            score += 5

        # -----------------------------------------
        # 3. Low physical progress
        # -----------------------------------------

        if progress < 30:
            score += 25

        elif progress < 50:
            score += 15

        elif progress < 70:
            score += 5

        # -----------------------------------------
        # 4. Very high spending
        # -----------------------------------------

        if sanctioned > 0:

            utilization = (spent / sanctioned) * 100

            if utilization >= 95 and progress < 80:
                score += 20

            elif utilization >= 85 and progress < 70:
                score += 15

        # -----------------------------------------
        # Final score
        # -----------------------------------------

        return min(int(score), 100)

    # ---------------------------------------------------------
    # RISK LEVEL
    # ---------------------------------------------------------

    def get_risk_level(self, score):

        score = float(score)

        if score >= 71:
            return "HIGH"

        elif score >= 31:
            return "MEDIUM"

        return "LOW"

    # ---------------------------------------------------------
    # FUND UTILIZATION ANOMALY
    # ---------------------------------------------------------

    def detect_fund_anomaly(self, row):

        sanctioned = float(row.get("sanctioned_amount", 0))
        spent = float(row.get("spent_amount", 0))
        progress = float(row.get("physical_progress", 0))

        if sanctioned <= 0:
            return None

        utilization = (spent / sanctioned) * 100

        if utilization > progress + 30:
            return {
                "type": "Fund Utilization Anomaly",
                "severity": "HIGH",
                "message": (
                    f"Financial utilization is {utilization:.1f}% "
                    f"while physical progress is only {progress:.1f}%."
                )
            }

        if utilization > progress + 15:
            return {
                "type": "Fund Utilization Anomaly",
                "severity": "MEDIUM",
                "message": (
                    f"Spending ({utilization:.1f}%) is significantly "
                    f"higher than physical progress ({progress:.1f}%)."
                )
            }

        return None

    # ---------------------------------------------------------
    # COST ANOMALY
    # ---------------------------------------------------------

    def detect_cost_anomaly(self, row):

        if self.df.empty:
            return None

        category = str(
            row.get("work_category", "")
        ).strip().lower()

        current_cost = float(
            row.get("sanctioned_amount", 0)
        )

        if not category or current_cost <= 0:
            return None

        category_rows = self.df[
            self.df["work_category"]
            .astype(str)
            .str.lower()
            == category
        ]

        if len(category_rows) < 2:
            return None

        average_cost = category_rows[
            "sanctioned_amount"
        ].mean()

        if average_cost <= 0:
            return None

        difference = (
            (current_cost - average_cost)
            / average_cost
        ) * 100

        if difference >= 50:
            return {
                "type": "Cost Anomaly",
                "severity": "HIGH",
                "message": (
                    f"Project cost is {difference:.1f}% "
                    f"above the category average."
                )
            }

        if difference >= 25:
            return {
                "type": "Cost Anomaly",
                "severity": "MEDIUM",
                "message": (
                    f"Project cost is {difference:.1f}% "
                    f"above the category average."
                )
            }

        return None

    # ---------------------------------------------------------
    # DUPLICATE PROJECT
    # ---------------------------------------------------------

    def detect_duplicate(self, row):

        if self.df.empty:
            return None

        current_id = str(row.get("work_id", ""))

        mp = str(row.get("mp_name", "")).strip().lower()
        district = str(
            row.get("district", "")
        ).strip().lower()
        category = str(
            row.get("work_category", "")
        ).strip().lower()

        if not mp or not district or not category:
            return None

        matches = self.df[
            (
                self.df["mp_name"]
                .astype(str)
                .str.lower()
                == mp
            )
            &
            (
                self.df["district"]
                .astype(str)
                .str.lower()
                == district
            )
            &
            (
                self.df["work_category"]
                .astype(str)
                .str.lower()
                == category
            )
            &
            (
                self.df["work_id"]
                .astype(str)
                != current_id
            )
        ]

        if len(matches) > 0:
            duplicate_ids = matches[
                "work_id"
            ].astype(str).tolist()

            return {
                "type": "Duplicate Project Pattern",
                "severity": "HIGH",
                "message": (
                    "Similar project found for the same "
                    "MP, district and work category."
                ),
                "related_projects": duplicate_ids
            }

        return None

    # ---------------------------------------------------------
    # TIMELINE ANOMALY
    # ---------------------------------------------------------

    def detect_timeline_anomaly(self, row):

        status = str(
            row.get("status", "")
        ).lower()

        progress = float(
            row.get("physical_progress", 0)
        )

        if (
            ("delay" in status or
             "pending" in status or
             "critical" in status)
            and progress < 50
        ):

            return {
                "type": "Timeline Anomaly",
                "severity": "HIGH",
                "message": (
                    "Project appears delayed with low "
                    "physical progress."
                )
            }

        if progress < 30:

            return {
                "type": "Timeline Anomaly",
                "severity": "MEDIUM",
                "message": (
                    "Physical progress is unusually low."
                )
            }

        return None

    # ---------------------------------------------------------
    # STATUS ANOMALY
    # ---------------------------------------------------------

    def detect_status_anomaly(self, row):

        status = str(
            row.get("status", "")
        ).lower()

        score = float(
            row.get("risk_score", 0)
        )

        if (
            score >= 71
            and
            (
                "ongoing" in status
                or "review" in status
                or "pending" in status
            )
        ):

            return {
                "type": "Status Risk",
                "severity": "HIGH",
                "message": (
                    "Project status and financial/physical "
                    "indicators require investigation."
                )
            }

        return None

    # ---------------------------------------------------------
    # ANALYZE ONE PROJECT
    # ---------------------------------------------------------

    def analyze_project(self, work_id):

        if self.df.empty:
            return {
                "success": False,
                "error": "No projects loaded."
            }

        matches = self.df[
            self.df["work_id"].astype(str)
            == str(work_id)
        ]

        if matches.empty:
            return {
                "success": False,
                "error": f"Project {work_id} not found."
            }

        row = matches.iloc[0]

        anomalies = []

        detectors = [
            self.detect_fund_anomaly,
            self.detect_cost_anomaly,
            self.detect_duplicate,
            self.detect_timeline_anomaly,
            self.detect_status_anomaly
        ]

        for detector in detectors:

            try:

                result = detector(row)

                if result:
                    anomalies.append(result)

            except Exception as error:

                print(
                    f"Detector error: {detector.__name__}: {error}"
                )

        risk_score = int(
            row.get("risk_score", 0)
        )

        risk_level = self.get_risk_level(
            risk_score
        )

        reasons = [
            anomaly["message"]
            for anomaly in anomalies
        ]

        return {
            "success": True,
            "project": {
                "work_id": str(row["work_id"]),
                "project_name": str(row["project_name"]),
                "mp_name": str(row["mp_name"]),
                "district": str(row["district"]),
                "state": str(row["state"]),
                "work_category": str(row["work_category"]),
                "agency": str(row["agency"]),
                "sanctioned_amount": float(
                    row["sanctioned_amount"]
                ),
                "spent_amount": float(
                    row["spent_amount"]
                ),
                "physical_progress": float(
                    row["physical_progress"]
                ),
                "utilization": float(
                    row["utilization"]
                ),
                "status": str(row["status"]),
                "contractor": str(row["contractor"]),
                "start_date": str(row["start_date"]),
                "expected_date": str(row["expected_date"]),
            },
            "risk_score": risk_score,
            "risk_level": risk_level,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "reasons": reasons,
            "inspection_priority": (
                "Immediate"
                if risk_score >= 71
                else
                "Review"
                if risk_score >= 31
                else
                "Normal"
            )
        }

    # ---------------------------------------------------------
    # ANALYZE ALL
    # ---------------------------------------------------------

    def analyze_all(self):

        results = []

        if self.df.empty:
            return results

        for work_id in self.df["work_id"].tolist():

            result = self.analyze_project(
                work_id
            )

            if result.get("success"):
                results.append(result)

        return results

    # ---------------------------------------------------------
    # STATISTICS
    # ---------------------------------------------------------

    def statistics(self):

        if self.df.empty:

            return {
                "total_projects": 0,
                "total_sanctioned": 0,
                "total_spent": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "delayed": 0,
                "average_progress": 0,
                "utilization": 0,
                "total_anomalies": 0
            }

        total_projects = len(self.df)

        total_sanctioned = float(
            self.df["sanctioned_amount"].sum()
        )

        total_spent = float(
            self.df["spent_amount"].sum()
        )

        high_risk = int(
            (self.df["risk_level"] == "HIGH").sum()
        )

        medium_risk = int(
            (self.df["risk_level"] == "MEDIUM").sum()
        )

        low_risk = int(
            (self.df["risk_level"] == "LOW").sum()
        )

        delayed = int(
            self.df["status"]
            .astype(str)
            .str.lower()
            .str.contains(
                "delay|critical|pending",
                regex=True
            )
            .sum()
        )

        average_progress = round(
            self.df["physical_progress"].mean(),
            2
        )

        utilization = round(
            (
                total_spent /
                total_sanctioned *
                100
            )
            if total_sanctioned > 0
            else 0,
            2
        )

        results = self.analyze_all()

        total_anomalies = sum(
            result.get("anomaly_count", 0)
            for result in results
        )

        return {
            "total_projects": total_projects,
            "total_sanctioned": round(
                total_sanctioned, 2
            ),
            "total_spent": round(
                total_spent, 2
            ),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "delayed": delayed,
            "average_progress": average_progress,
            "utilization": utilization,
            "total_anomalies": total_anomalies
        }