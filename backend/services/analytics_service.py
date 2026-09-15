"""Analytics aggregations used by dashboard pages."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any


def category_breakdown(
    projects: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    data = defaultdict(
        lambda: {
            "count": 0,
            "sanctioned": 0,
            "spent": 0,
            "high_risk": 0,
        }
    )

    for project in projects:

        category = project.get(
            "category",
            "General",
        )

        item = data[category]

        item["count"] += 1
        item["sanctioned"] += project.get(
            "sanctioned",
            0,
        )

        item["spent"] += project.get(
            "spent",
            0,
        )

        item["high_risk"] += (
            project.get("risk") == "High"
        )

    result = []

    for category, item in data.items():

        utilization = (
            item["spent"]
            / item["sanctioned"]
            * 100
            if item["sanctioned"]
            else 0
        )

        result.append(
            {
                "category": category,
                "count": item["count"],
                "sanctioned_cr": round(
                    item["sanctioned"] / 10_000_000,
                    2,
                ),
                "spent_cr": round(
                    item["spent"] / 10_000_000,
                    2,
                ),
                "utilization": round(
                    utilization,
                    1,
                ),
                "high_risk": item["high_risk"],
            }
        )

    return sorted(
        result,
        key=lambda item: item["count"],
        reverse=True,
    )


def district_breakdown(
    projects: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    data = defaultdict(
        lambda: {
            "count": 0,
            "high_risk": 0,
            "sanctioned": 0,
            "state": "Unknown",
        }
    )

    for project in projects:

        district = project.get(
            "district",
            "General",
        )

        item = data[district]

        item["count"] += 1
        item["sanctioned"] += project.get(
            "sanctioned",
            0,
        )

        item["high_risk"] += (
            project.get("risk") == "High"
        )

        item["state"] = project.get(
            "state",
            "Unknown",
        )

    result = []

    for district, item in data.items():

        result.append(
            {
                "district": district,
                "state": item["state"],
                "count": item["count"],
                "high_risk": item["high_risk"],
                "sanctioned_cr": round(
                    item["sanctioned"] / 10_000_000,
                    2,
                ),
            }
        )

    return sorted(
        result,
        key=lambda item: (
            item["high_risk"],
            item["count"],
        ),
        reverse=True,
    )


def status_breakdown(
    projects: list[dict[str, Any]],
) -> dict[str, int]:

    counts = Counter(
        project.get(
            "status",
            "Ongoing",
        )
        for project in projects
    )

    statuses = [
        "Ongoing",
        "Completed",
        "Delayed",
        "Critical",
        "Under Review",
    ]

    return {
        status: counts.get(
            status,
            0,
        )
        for status in statuses
    }


def top_anomalies(
    projects: list[dict[str, Any]],
    limit: int = 6,
) -> list[dict[str, Any]]:

    counts = Counter(
        anomaly.strip()
        for project in projects
        for anomaly in project.get(
            "anomalies",
            [],
        )
        if anomaly.strip()
    )

    rows = counts.most_common(limit)

    max_count = (
        rows[0][1]
        if rows
        else 1
    )

    return [
        {
            "reason": reason,
            "count": count,
            "pct": max(
                10,
                min(
                    100,
                    int(
                        count
                        / max_count
                        * 100
                    ),
                ),
            ),
        }
        for reason, count in rows
    ]


def map_breakdown(
    projects: list[dict[str, Any]],
):

    district_map = {}

    for project in projects:

        district = project.get(
            "district",
            "Unknown",
        )

        item = district_map.setdefault(
            district,
            {
                "district": district,
                "state": project.get(
                    "state",
                    "Karnataka",
                ),
                "total": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "sanctioned": 0,
                "spent": 0,
            },
        )

        item["total"] += 1

        item["sanctioned"] += project.get(
            "sanctioned",
            0,
        )

        item["spent"] += project.get(
            "spent",
            0,
        )

        risk = str(
            project.get(
                "risk",
                "Low",
            )
        ).lower()

        if risk == "high":
            item["high_risk"] += 1

        elif risk == "medium":
            item["medium_risk"] += 1

        else:
            item["low_risk"] += 1

    districts = sorted(
        district_map.values(),
        key=lambda item: item["total"],
        reverse=True,
    )

    state_map = {}

    for district in districts:

        state = district["state"]

        item = state_map.setdefault(
            state,
            {
                "state": state,
                "total": 0,
                "high_risk": 0,
                "sanctioned": 0,
                "districts": [],
            },
        )

        item["total"] += district["total"]
        item["high_risk"] += district["high_risk"]
        item["sanctioned"] += district["sanctioned"]

        item["districts"].append(
            district["district"]
        )

    states = sorted(
        state_map.values(),
        key=lambda item: item["total"],
        reverse=True,
    )

    return districts, states