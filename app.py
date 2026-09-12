from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ==========================================================
# DEMO PROJECT DATA
# Replace this later with your CSV / database data
# ==========================================================

PROJECTS = [
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
        "anomalies": []
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
            "Project completion delayed",
            "Unusual cost pattern"
        ]
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
            "Expenditure is high for current completion level"
        ]
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
        "anomalies": []
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
            "Completion deadline exceeded",
            "Potential cost overrun"
        ]
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
        "anomalies": []
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
            "Low physical progress",
            "High fund utilization",
            "Timeline inconsistency"
        ]
    }
]


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def calculate_statistics(projects):
    total_projects = len(projects)

    total_sanctioned = sum(p["sanctioned"] for p in projects)
    total_spent = sum(p["spent"] for p in projects)

    high_risk = len([
        p for p in projects
        if p["risk"] == "High"
    ])

    medium_risk = len([
        p for p in projects
        if p["risk"] == "Medium"
    ])

    low_risk = len([
        p for p in projects
        if p["risk"] == "Low"
    ])

    delayed = len([
        p for p in projects
        if p["status"] in ["Delayed", "Critical"]
    ])

    average_progress = (
        sum(p["progress"] for p in projects) / total_projects
        if total_projects else 0
    )

    utilization = (
        (total_spent / total_sanctioned) * 100
        if total_sanctioned else 0
    )

    return {
        "total_projects": total_projects,
        "total_sanctioned": total_sanctioned,
        "total_spent": total_spent,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "delayed": delayed,
        "average_progress": round(average_progress, 1),
        "utilization": round(utilization, 1)
    }


# ==========================================================
# ROUTES
# ==========================================================

@app.route("/")
def home():
    statistics = calculate_statistics(PROJECTS)
    return render_template(
        "index.html",
        projects=PROJECTS,
        statistics=statistics
    )


@app.route("/projects")
def projects():
    return render_template(
        "project.html",
        projects=PROJECTS
    )


@app.route("/api/dashboard")
def dashboard_api():
    statistics = calculate_statistics(PROJECTS)

    return jsonify({
        "success": True,
        "statistics": statistics,
        "projects": PROJECTS
    })


@app.route("/api/projects")
def projects_api():

    risk_filter = request.args.get("risk", "All")
    status_filter = request.args.get("status", "All")
    search = request.args.get("search", "").lower()

    filtered = PROJECTS

    if risk_filter != "All":
        filtered = [
            p for p in filtered
            if p["risk"] == risk_filter
        ]

    if status_filter != "All":
        filtered = [
            p for p in filtered
            if p["status"] == status_filter
        ]

    if search:
        filtered = [
            p for p in filtered
            if search in p["name"].lower()
            or search in p["district"].lower()
            or search in p["category"].lower()
            or search in p["contractor"].lower()
        ]

    return jsonify({
        "success": True,
        "count": len(filtered),
        "projects": filtered
    })


@app.route("/project/<project_id>")
def project_details(project_id):

    project = next(
        (p for p in PROJECTS if p["id"] == project_id),
        None
    )

    if project is None:
        return "Project not found", 404

    return render_template(
        "project.html",
        project=project,
        projects=PROJECTS
    )


@app.route("/risk-analysis")
def risk_analysis():
    return render_template(
        "project.html",
        projects=PROJECTS
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "MPLAD AI Risk Monitoring System"
    })


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )