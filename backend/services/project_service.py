"""Project loading, normalization, filtering, and summaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from backend.utils.data_processor import (
    DATA_FOLDER,
    load_projects,
)


DISTRICT_STATE_MAP = {
    "Belagavi": "Karnataka",
    "Bengaluru Urban": "Karnataka",
    "Dharwad": "Karnataka",
    "Mysuru": "Karnataka",
    "Dakshina Kannada": "Karnataka",
    "Udupi": "Karnataka",
    "Kodagu": "Karnataka",
    "Hassan": "Karnataka",
    "Mangaluru": "Karnataka",
    "Nagpur": "Maharashtra",
    "Nashik": "Maharashtra",
    "Pune": "Maharashtra",
    "Thane": "Maharashtra",
    "Chennai": "Tamil Nadu",
    "Coimbatore": "Tamil Nadu",
    "Madurai": "Tamil Nadu",
    "Salem": "Tamil Nadu",
    "Agra": "Uttar Pradesh",
    "Kanpur": "Uttar Pradesh",
    "Lucknow": "Uttar Pradesh",
    "Varanasi": "Uttar Pradesh",
    "Asansol": "West Bengal",
    "Darjeeling": "West Bengal",
    "Howrah": "West Bengal",
    "Kolkata": "West Bengal",
}


DEMO_PROJECTS = [
    {
        "id": "MPLAD-2026-001",
        "name": "Construction of Community Hall",
        "district": "Dakshina Kannada",
        "state": "Karnataka",
        "category": "Community Infrastructure",
        "agency": "Rural Development Department",
        "sanctioned": 2500000,
        "spent": 2100000,
        "progress": 84,
        "status": "Ongoing",
        "risk": "Low",
        "risk_score": 21,
        "start_date": "2026-02-10",
        "expected_date": "2026-11-20",
        "contractor": "ABC Infrastructure",
        "anomalies": [],
        "why_flagged": (
            "Project implementation parameters are "
            "within normal variance thresholds."
        ),
        "recommended_action": (
            "Routine quarterly inspection. "
            "Maintain milestone monitoring."
        ),
        "explanation": (
            "This project is proceeding on schedule "
            "with expenditure matching physical verification."
        ),
        "inspection_priority": "Normal",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-002",
        "name": "Government School Building Renovation",
        "district": "Udupi",
        "state": "Karnataka",
        "category": "Education",
        "agency": "Public Works Department",
        "sanctioned": 4800000,
        "spent": 4300000,
        "progress": 57,
        "status": "Delayed",
        "risk": "High",
        "risk_score": 86,
        "start_date": "2025-08-15",
        "expected_date": "2026-05-30",
        "contractor": "Coastal Builders",
        "anomalies": [
            "High expenditure compared with physical progress",
            "Project completion delayed beyond target milestone",
            "Unusual cost disbursement velocity",
        ],
        "why_flagged": (
            "Fund utilization reached 89.6% while "
            "physical completion is only 57%."
        ),
        "recommended_action": (
            "Immediate field engineering audit and hold "
            "on further fund disbursements."
        ),
        "explanation": (
            "High Risk: Significant divergence between "
            "recorded physical completion and cumulative fund releases."
        ),
        "inspection_priority": "Immediate",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-003",
        "name": "Village Road Development",
        "district": "Mysuru",
        "state": "Karnataka",
        "category": "Roads",
        "agency": "Rural Works Division",
        "sanctioned": 6200000,
        "spent": 5900000,
        "progress": 72,
        "status": "Under Review",
        "risk": "Medium",
        "risk_score": 61,
        "start_date": "2025-11-01",
        "expected_date": "2026-09-15",
        "contractor": "Mysore Road Works",
        "anomalies": [
            "Expenditure velocity is high for current physical completion level"
        ],
        "why_flagged": (
            "Fund utilization is 95.2% against "
            "72% physical completion."
        ),
        "recommended_action": (
            "Conduct site inspection before releasing "
            "final retention tranche."
        ),
        "explanation": (
            "Medium Risk: Moderate gap between "
            "financial releases and work completion."
        ),
        "inspection_priority": "Review",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-004",
        "name": "Primary Health Centre Equipment",
        "district": "Kodagu",
        "state": "Karnataka",
        "category": "Healthcare",
        "agency": "Health Department",
        "sanctioned": 1800000,
        "spent": 1050000,
        "progress": 76,
        "status": "Ongoing",
        "risk": "Low",
        "risk_score": 18,
        "start_date": "2026-03-05",
        "expected_date": "2026-10-10",
        "contractor": "Meditech Solutions",
        "anomalies": [],
        "why_flagged": (
            "Indicators within standard deviation bounds."
        ),
        "recommended_action": (
            "Proceed with regular equipment verification protocol."
        ),
        "explanation": (
            "Low Risk: Procurement timelines and expenditure "
            "curves align with standard benchmarks."
        ),
        "inspection_priority": "Normal",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-005",
        "name": "Drinking Water Supply Project",
        "district": "Belagavi",
        "state": "Karnataka",
        "category": "Water Supply",
        "agency": "Water Resources Department",
        "sanctioned": 7500000,
        "spent": 6900000,
        "progress": 44,
        "status": "Critical",
        "risk": "High",
        "risk_score": 91,
        "start_date": "2025-06-20",
        "expected_date": "2026-03-15",
        "contractor": "National Water Works",
        "anomalies": [
            "Severe progress-expenditure mismatch",
            "Completion deadline exceeded by over 180 days",
            "Potential cost overrun and stalled pipeline work",
        ],
        "why_flagged": (
            "Over 92% funds disbursed with less than "
            "half of physical milestones completed."
        ),
        "recommended_action": (
            "Summon executing agency for administrative hearing "
            "and physical inventory assessment."
        ),
        "explanation": (
            "High Risk: Critical timeline overshoot and severe "
            "budget utilization disproportion."
        ),
        "inspection_priority": "Immediate",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-006",
        "name": "Digital Learning Centre",
        "district": "Hassan",
        "state": "Karnataka",
        "category": "Education",
        "agency": "Education Department",
        "sanctioned": 3200000,
        "spent": 1900000,
        "progress": 68,
        "status": "Ongoing",
        "risk": "Low",
        "risk_score": 27,
        "start_date": "2026-01-20",
        "expected_date": "2026-12-10",
        "contractor": "EduTech Projects",
        "anomalies": [],
        "why_flagged": (
            "Project metrics align with baseline specifications."
        ),
        "recommended_action": (
            "Continue regular monthly inspection."
        ),
        "explanation": (
            "Low Risk: Physical and financial pacing "
            "correspond to project charter."
        ),
        "inspection_priority": "Normal",
        "mp_name": "Demo MP",
    },

    {
        "id": "MPLAD-2026-007",
        "name": "Urban Drainage Improvement",
        "district": "Mangaluru",
        "state": "Karnataka",
        "category": "Drainage",
        "agency": "Municipal Corporation",
        "sanctioned": 8500000,
        "spent": 7200000,
        "progress": 39,
        "status": "Under Review",
        "risk": "High",
        "risk_score": 78,
        "start_date": "2025-09-10",
        "expected_date": "2026-06-15",
        "contractor": "City Infra Projects",
        "anomalies": [
            "Low physical progress vs high fund utilization",
            "Timeline inconsistency in contractor reports",
            "Delayed execution across culvert sections",
        ],
        "why_flagged": (
            "Severe variance between disbursed funds "
            "and measured on-site progress."
        ),
        "recommended_action": (
            "Depute technical inspection team for "
            "on-site cross-measurement."
        ),
        "explanation": (
            "High Risk: High financial exhaustion with "
            "sub-40% physical completion requires technical review."
        ),
        "inspection_priority": "Immediate",
        "mp_name": "Demo MP",
    },
]


@dataclass
class ProjectRepository:
    projects: list[dict[str, Any]]

    @classmethod
    def load(cls) -> "ProjectRepository":
        projects = [
            dict(project)
            for project in DEMO_PROJECTS
        ]

        seen_ids = {
            project["id"]
            for project in projects
        }

        flagged_df = load_projects()

        explainable = cls._read_lookup(
            DATA_FOLDER / "explainable_risk_results.csv"
        )

        unified = cls._read_lookup(
            DATA_FOLDER / "unified_risk_results.csv"
        )

        for idx, row in flagged_df.iterrows():
            work_id = (
                str(row.get("work_id", "")).strip()
                or f"MPLAD-W-{idx + 1000}"
            )

            if work_id in seen_ids:
                continue

            project = cls._normalize_row(
                row,
                explainable.get(work_id, {}),
                unified.get(work_id, {}),
            )

            projects.append(project)
            seen_ids.add(work_id)

        return cls(projects)

    @staticmethod
    def _read_lookup(
        path: Path,
    ) -> dict[str, dict[str, Any]]:

        if not path.exists():
            return {}

        frame = pd.read_csv(path).fillna("")

        if "work_id" not in frame.columns:
            return {}

        return {
            str(row["work_id"]).strip(): row.to_dict()
            for _, row in frame.iterrows()
            if str(row["work_id"]).strip()
        }

    @classmethod
    def _normalize_row(
        cls,
        row: pd.Series,
        explainable: dict[str, Any],
        unified: dict[str, Any],
    ) -> dict[str, Any]:

        work_id = str(
            row.get("work_id", "")
        ).strip()

        district = (
            str(row.get("district", "General District"))
            .strip()
            or "General District"
        )

        category = (
            str(row.get("work_category", "Infrastructure"))
            .strip()
            or "Infrastructure"
        )

        agency = (
            str(
                row.get(
                    "implementing_agency",
                    "District Development Authority",
                )
            ).strip()
            or "District Development Authority"
        )

        status = (
            str(row.get("status", "Ongoing"))
            .strip()
            or "Ongoing"
        )

        cost_lakhs = cls._number(
            row.get("cost_estimate_lakhs", 25.0),
            25.0,
        )

        sanctioned = max(
            2500000,
            int(cost_lakhs * 100000),
        )

        final_score = cls._number(
            unified.get(
                "final_risk_score",
                row.get("risk_score", 0),
            ),
            0.0,
        )

        raw_level = (
            str(
                unified.get(
                    "risk_level",
                    "",
                )
            )
            .strip()
            .upper()
        )

        risk = {
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low",
        }.get(raw_level)

        if risk is None:
            risk = (
                "High"
                if final_score >= 70
                else "Medium"
                if final_score >= 40
                else "Low"
            )

        status_lower = status.lower()

        if status_lower in {"critical", "delayed"}:
            progress = int(
                max(
                    25,
                    min(
                        58,
                        100 - final_score * 0.65,
                    ),
                )
            )

        elif status_lower == "completed":
            progress = 100

        elif status_lower == "under review":
            progress = 65

        else:
            progress = int(
                max(
                    35,
                    min(
                        88,
                        85 - final_score * 0.4,
                    ),
                )
            )

        spent = min(
            sanctioned,
            int(
                sanctioned
                * min(
                    0.96,
                    max(
                        0.12,
                        progress / 100 * 1.05,
                    ),
                )
            ),
        )

        reasons_text = str(
            row.get("reasons_text", "")
        ).strip()

        reasons = [
            part.strip()
            for part in reasons_text.split(";")
            if part.strip()
        ]

        why_flagged = str(
            explainable.get(
                "why_flagged",
                "",
            )
        ).strip()

        recommended_action = str(
            explainable.get(
                "recommended_action",
                "",
            )
        ).strip()

        explanation = str(
            explainable.get(
                "explanation",
                "",
            )
        ).strip()

        if not why_flagged:
            why_flagged = (
                " | ".join(reasons)
                or "Standard algorithmic monitoring baseline."
            )

        if not recommended_action:
            recommended_action = {
                "High": (
                    "Immediate inspection and technical audit recommended."
                ),
                "Medium": (
                    "Review milestone report prior to next disbursement."
                ),
                "Low": (
                    "Continue scheduled oversight monitoring."
                ),
            }[risk]

        if not explanation:
            explanation = (
                "Potential anomaly assessment indicates "
                f"{risk.lower()} risk indicators."
            )

        return {
            "id": work_id,
            "name": f"{category} - {district}",
            "district": district,
            "state": DISTRICT_STATE_MAP.get(
                district,
                "Karnataka",
            ),
            "category": category,
            "agency": agency,
            "sanctioned": sanctioned,
            "spent": spent,
            "progress": progress,
            "status": status,
            "risk": risk,
            "risk_score": round(
                final_score,
                2,
            ),
            "start_date": "2025-04-10",
            "expected_date": "2026-10-30",
            "contractor": (
                f"{agency} Assigned Agency"
            ),
            "anomalies": reasons,
            "why_flagged": why_flagged,
            "recommended_action": recommended_action,
            "explanation": explanation,
            "inspection_priority": (
                str(
                    unified.get(
                        "inspection_priority",
                        "NORMAL",
                    )
                ).title()
                or "Normal"
            ),
            "mp_name": str(
                row.get("mp_name", "")
            ).strip(),
        }

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            number = float(
                str(value)
                .replace(",", "")
                .strip()
            )

            return (
                number
                if pd.notna(number)
                else default
            )

        except (TypeError, ValueError):
            return default

    def refresh(self) -> None:
        refreshed = self.load()
        self.projects = refreshed.projects

    def get(
        self,
        project_id: str,
    ) -> dict[str, Any] | None:

        needle = project_id.strip().lower()

        return next(
            (
                project
                for project in self.projects
                if project["id"].lower() == needle
            ),
            None,
        )


def calculate_statistics(
    projects: list[dict[str, Any]],
) -> dict[str, Any]:

    total = len(projects)

    if total == 0:
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
            "total_anomalies": 0,
        }

    sanctioned = sum(
        project.get("sanctioned", 0)
        for project in projects
    )

    spent = sum(
        project.get("spent", 0)
        for project in projects
    )

    return {
        "total_projects": total,
        "total_sanctioned": sanctioned,
        "total_spent": spent,
        "high_risk": sum(
            project.get("risk") == "High"
            for project in projects
        ),
        "medium_risk": sum(
            project.get("risk") == "Medium"
            for project in projects
        ),
        "low_risk": sum(
            project.get("risk") == "Low"
            for project in projects
        ),
        "delayed": sum(
            project.get("status")
            in {
                "Delayed",
                "Critical",
                "Under Review",
            }
            for project in projects
        ),
        "average_progress": round(
            sum(
                project.get("progress", 0)
                for project in projects
            )
            / total,
            1,
        ),
        "utilization": (
            round(
                spent / sanctioned * 100,
                1,
            )
            if sanctioned
            else 0
        ),
        "total_anomalies": sum(
            len(
                project.get(
                    "anomalies",
                    [],
                )
            )
            for project in projects
        ),
    }


def get_filter_options(
    projects: list[dict[str, Any]],
) -> dict[str, list[str]]:

    return {
        "states": sorted(
            {
                project["state"]
                for project in projects
                if project.get("state")
            }
        ),
        "districts": sorted(
            {
                project["district"]
                for project in projects
                if project.get("district")
            }
        ),
        "categories": sorted(
            {
                project["category"]
                for project in projects
                if project.get("category")
            }
        ),
        "statuses": [
            "Ongoing",
            "Completed",
            "Delayed",
            "Critical",
            "Under Review",
        ],
        "risks": [
            "High",
            "Medium",
            "Low",
        ],
    }


def filter_projects(
    projects: list[dict[str, Any]],
    params: Any,
) -> list[dict[str, Any]]:

    values = {
        key: str(
            params.get(
                key,
                "All",
            )
        ).strip()
        for key in (
            "risk",
            "status",
            "state",
            "district",
            "category",
        )
    }

    search = str(
        params.get(
            "search",
            "",
        )
    ).strip().lower()

    result = projects

    for field, value in values.items():

        if value and value.lower() != "all":
            result = [
                project
                for project in result
                if str(
                    project.get(
                        field,
                        "",
                    )
                ).lower()
                == value.lower()
            ]

    if search:

        result = [
            project
            for project in result
            if any(
                search in str(
                    project.get(
                        key,
                        "",
                    )
                ).lower()
                for key in (
                    "id",
                    "name",
                    "district",
                    "state",
                    "category",
                    "agency",
                    "contractor",
                    "mp_name",
                )
            )
            or any(
                search in anomaly.lower()
                for anomaly in project.get(
                    "anomalies",
                    [],
                )
            )
        ]

    return result