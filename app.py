import os
import io
import csv
from flask import Flask, render_template, jsonify, request, Response

app = Flask(__name__)
app.jinja_env.globals.update(min=min, max=max)

# ==========================================================
# CURATED FEATURED PROJECTS (DEMO PROJECTS)
# ==========================================================

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
        "why_flagged": "Project implementation parameters are within normal variance thresholds.",
        "recommended_action": "Routine quarterly inspection. Maintain milestone monitoring.",
        "explanation": "This project is proceeding on schedule with expenditure matching physical verification.",
        "inspection_priority": "Normal"
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
            "Unusual cost disbursement velocity"
        ],
        "why_flagged": "Fund utilization reached 89.6% while physical completion is only 57%. Project milestone exceeded by 100+ days.",
        "recommended_action": "Immediate field engineering audit and hold on further fund disbursements.",
        "explanation": "High Risk: Significant divergence between recorded physical completion and cumulative fund releases.",
        "inspection_priority": "Immediate"
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
        "why_flagged": "Fund utilization is 95.2% against 72% physical completion.",
        "recommended_action": "Conduct site inspection before releasing final retention tranche.",
        "explanation": "Medium Risk: Moderate gap between financial releases and work completion.",
        "inspection_priority": "Review"
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
        "why_flagged": "Indicators within standard deviation bounds.",
        "recommended_action": "Proceed with regular equipment verification protocol.",
        "explanation": "Low Risk: Procurement timelines and expenditure curves align with standard benchmarks.",
        "inspection_priority": "Normal"
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
            "Severe progress-expenditure mismatch (44% progress vs 92% spent)",
            "Completion deadline exceeded by over 180 days",
            "Potential cost overrun and stalled pipeline work"
        ],
        "why_flagged": "Over 92% funds disbursed with less than half of physical milestones completed. Scheduled target passed.",
        "recommended_action": "Summon executing agency for administrative hearing and physical inventory assessment.",
        "explanation": "High Risk: Critical timeline overshoot and severe budget utilization disproportion.",
        "inspection_priority": "Immediate"
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
        "why_flagged": "Project metrics align with baseline specifications.",
        "recommended_action": "Continue regular monthly inspection.",
        "explanation": "Low Risk: Physical and financial pacing correspond to project charter.",
        "inspection_priority": "Normal"
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
            "Low physical progress (39%) vs high fund utilization (84.7%)",
            "Timeline inconsistency in contractor reports",
            "Delayed execution across culvert sections"
        ],
        "why_flagged": "Severe variance between disbursed funds and measured on-site progress.",
        "recommended_action": "Depute technical inspection team for on-site cross-measurement.",
        "explanation": "High Risk: High financial exhaustion with sub-40% physical completion requires technical review.",
        "inspection_priority": "Immediate"
    }
]

# District to State Mapping
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
    "Kolkata": "West Bengal"
}

# ==========================================================
# DATASET LOADER (CSV + DEMO DATA INTEGRATION)
# ==========================================================

def load_all_projects():
    """
    Loads project records from flagged_works.csv and explainable_risk_results.csv,
    normalizes fields safely with robust defaults, and combines them with DEMO_PROJECTS.
    """
    projects = list(DEMO_PROJECTS)
    seen_ids = {p["id"] for p in projects}

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    flagged_path = os.path.join(data_dir, "flagged_works.csv")
    explainable_path = os.path.join(data_dir, "explainable_risk_results.csv")

    explainable_lookup = {}
    if os.path.exists(explainable_path):
        try:
            with open(explainable_path, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    wid = row.get("work_id", "").strip()
                    if wid:
                        explainable_lookup[wid] = row
        except Exception as e:
            print("Notice: Could not load explainable_risk_results.csv:", e)

    if os.path.exists(flagged_path):
        try:
            with open(flagged_path, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    wid = row.get("work_id", "").strip() or f"MPLAD-W-{idx+1000}"
                    if wid in seen_ids:
                        continue
                    seen_ids.add(wid)

                    exp_row = explainable_lookup.get(wid, {})

                    district = row.get("district", "").strip() or "General District"
                    state = DISTRICT_STATE_MAP.get(district, "Karnataka")
                    category = row.get("work_category", "").strip() or "Infrastructure"
                    agency = row.get("implementing_agency", "").strip() or "District Development Authority"
                    mp_name = row.get("mp_name", "").strip()

                    try:
                        cost_lakhs = float(row.get("cost_estimate_lakhs", 0))
                    except (ValueError, TypeError):
                        cost_lakhs = 25.0
                    sanctioned = int(cost_lakhs * 100000)
                    if sanctioned <= 0:
                        sanctioned = 2500000

                    status = row.get("status", "").strip() or "Ongoing"
                    reasons_text = row.get("reasons_text", "").strip()

                    try:
                        raw_score = float(row.get("risk_score", 0))
                    except (ValueError, TypeError):
                        raw_score = 15.0

                    # Calibrate risk score and level
                    if ";" in reasons_text or raw_score >= 38 or cost_lakhs >= 110 or "disproportionate" in reasons_text:
                        risk_level = "High"
                        risk_score = min(96, max(72, int(raw_score * 1.5) + 12))
                        if status == "Ongoing" and "2+ years" in reasons_text:
                            status = "Delayed"
                    elif "2+ years" in reasons_text or raw_score >= 18 or cost_lakhs >= 65:
                        risk_level = "Medium"
                        risk_score = min(69, max(42, int(raw_score * 1.2) + 8))
                    else:
                        risk_level = "Low"
                        risk_score = min(38, max(12, int(raw_score)))

                    # Physical progress & expenditure
                    if status == "Completed":
                        progress = 100
                        spent = int(sanctioned * 0.96)
                    elif status in ["Critical", "Delayed"]:
                        progress = max(25, min(58, int(100 - risk_score * 0.65)))
                        spent = int(sanctioned * min(0.95, (progress + 25) / 100.0))
                    elif status == "Under Review":
                        progress = 65
                        spent = int(sanctioned * 0.82)
                    else:
                        progress = max(35, min(88, int(85 - risk_score * 0.4)))
                        spent = int(sanctioned * (progress / 100.0 * 1.05))

                    if spent > sanctioned:
                        spent = sanctioned

                    # Parse anomalies
                    anomalies = []
                    if reasons_text:
                        for part in reasons_text.split(";"):
                            clean_part = part.strip()
                            if clean_part:
                                anomalies.append(clean_part)

                    why_flagged = exp_row.get("why_flagged", "").strip() or (
                        f"Project flagged due to: {', '.join(anomalies)}" if anomalies else "Standard algorithmic monitoring baseline."
                    )
                    recommended_action = exp_row.get("recommended_action", "").strip() or (
                        "Immediate inspection and technical audit recommended." if risk_level == "High"
                        else "Review milestone report prior to next disbursement." if risk_level == "Medium"
                        else "Continue scheduled oversight monitoring."
                    )
                    explanation = exp_row.get("explanation", "").strip() or (
                        f"Potential anomaly assessment indicates {risk_level.lower()} risk indicators."
                    )

                    project_item = {
                        "id": wid,
                        "name": f"{category} - {district}",
                        "district": district,
                        "state": state,
                        "category": category,
                        "agency": agency,
                        "sanctioned": sanctioned,
                        "spent": spent,
                        "progress": progress,
                        "status": status,
                        "risk": risk_level,
                        "risk_score": risk_score,
                        "start_date": "2025-04-10",
                        "expected_date": "2026-10-30",
                        "contractor": f"{agency} Assigned Agency",
                        "anomalies": anomalies,
                        "why_flagged": why_flagged,
                        "recommended_action": recommended_action,
                        "explanation": explanation,
                        "inspection_priority": "Immediate" if risk_level == "High" else ("Review" if risk_level == "Medium" else "Normal"),
                        "mp_name": mp_name
                    }
                    projects.append(project_item)

        except Exception as e:
            print("Notice: Error reading flagged_works.csv:", e)

    return projects


# Initialize Global Dataset
PROJECTS = load_all_projects()


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def calculate_statistics(projects):
    """
    Computes summary metrics for cards and analytics.
    """
    total_projects = len(projects)
    if total_projects == 0:
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

    total_sanctioned = sum(p.get("sanctioned", 0) for p in projects)
    total_spent = sum(p.get("spent", 0) for p in projects)

    high_risk = sum(1 for p in projects if p.get("risk") == "High")
    medium_risk = sum(1 for p in projects if p.get("risk") == "Medium")
    low_risk = sum(1 for p in projects if p.get("risk") == "Low")

    delayed = sum(1 for p in projects if p.get("status") in ["Delayed", "Critical", "Under Review"])

    average_progress = (
        sum(p.get("progress", 0) for p in projects) / total_projects
    )

    utilization = (
        (total_spent / total_sanctioned * 100) if total_sanctioned > 0 else 0
    )

    total_anomalies = sum(len(p.get("anomalies", [])) for p in projects)

    return {
        "total_projects": total_projects,
        "total_sanctioned": total_sanctioned,
        "total_spent": total_spent,
        "high_risk": high_risk,
        "medium_risk": medium_risk,
        "low_risk": low_risk,
        "delayed": delayed,
        "average_progress": round(average_progress, 1),
        "utilization": round(utilization, 1),
        "total_anomalies": total_anomalies
    }


def get_filter_options():
    """Returns sorted unique values for select dropdowns across the dataset."""
    states = sorted(list({p.get("state") for p in PROJECTS if p.get("state")}))
    districts = sorted(list({p.get("district") for p in PROJECTS if p.get("district")}))
    categories = sorted(list({p.get("category") for p in PROJECTS if p.get("category")}))
    statuses = ["Ongoing", "Completed", "Delayed", "Critical", "Under Review"]
    risks = ["High", "Medium", "Low"]

    return {
        "states": states,
        "districts": districts,
        "categories": categories,
        "statuses": statuses,
        "risks": risks
    }


def filter_projects_list(projects, args):
    """Filters projects by query parameters."""
    risk_filter = args.get("risk", "All").strip()
    status_filter = args.get("status", "All").strip()
    state_filter = args.get("state", "All").strip()
    district_filter = args.get("district", "All").strip()
    category_filter = args.get("category", "All").strip()
    search = args.get("search", "").strip().lower()

    filtered = projects

    if risk_filter and risk_filter != "All":
        filtered = [p for p in filtered if p.get("risk", "").lower() == risk_filter.lower()]

    if status_filter and status_filter != "All":
        filtered = [p for p in filtered if p.get("status", "").lower() == status_filter.lower()]

    if state_filter and state_filter != "All":
        filtered = [p for p in filtered if p.get("state", "").lower() == state_filter.lower()]

    if district_filter and district_filter != "All":
        filtered = [p for p in filtered if p.get("district", "").lower() == district_filter.lower()]

    if category_filter and category_filter != "All":
        filtered = [p for p in filtered if p.get("category", "").lower() == category_filter.lower()]

    if search:
        filtered = [
            p for p in filtered
            if search in p.get("name", "").lower()
            or search in p.get("id", "").lower()
            or search in p.get("district", "").lower()
            or search in p.get("state", "").lower()
            or search in p.get("category", "").lower()
            or search in p.get("agency", "").lower()
            or search in p.get("contractor", "").lower()
            or search in p.get("mp_name", "").lower()
            or any(search in a.lower() for a in p.get("anomalies", []))
        ]

    return filtered


# ==========================================================
# CORE ROUTES
# ==========================================================

@app.route("/")
def home():
    """Dashboard homepage."""
    statistics = calculate_statistics(PROJECTS)
    filter_opts = get_filter_options()

    # Get recent projects for the dashboard preview table (prioritize featured demo items)
    preview_projects = PROJECTS[:10]

    # Get prominent high-risk projects for the alerts section
    alert_projects = [p for p in PROJECTS if p.get("risk") == "High"][:8]

    return render_template(
        "index.html",
        projects=preview_projects,
        alert_projects=alert_projects,
        statistics=statistics,
        filter_options=filter_opts
    )


@app.route("/projects")
def projects():
    """Projects explorer page with filtering, search, and pagination."""
    filter_opts = get_filter_options()
    filtered_list = filter_projects_list(PROJECTS, request.args)

    # Active filters dictionary for retaining UI state
    active_filters = {
        "risk": request.args.get("risk", "All"),
        "status": request.args.get("status", "All"),
        "state": request.args.get("state", "All"),
        "district": request.args.get("district", "All"),
        "category": request.args.get("category", "All"),
        "search": request.args.get("search", "")
    }

    # Pagination
    try:
        page = int(request.args.get("page", 1))
    except (ValueError, TypeError):
        page = 1
    if page < 1:
        page = 1

    per_page = 20
    total_items = len(filtered_list)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_projects = filtered_list[start_idx:end_idx]

    return render_template(
        "project.html",
        project=None,
        projects=paginated_projects,
        total_items=total_items,
        page=page,
        total_pages=total_pages,
        start_item=start_idx + 1 if total_items > 0 else 0,
        end_item=end_idx,
        active_filters=active_filters,
        filter_options=filter_opts
    )


@app.route("/project/<project_id>")
def project_details(project_id):
    """Detailed view for a single project."""
    target_id = project_id.strip().lower()

    project = next(
        (p for p in PROJECTS if p["id"].lower() == target_id),
        None
    )

    if project is None:
        # Fallback search by prefix or suffix
        project = next(
            (p for p in PROJECTS if target_id in p["id"].lower()),
            None
        )

    if project is None:
        # Return friendly not found inside the template structure
        return render_template(
            "project.html",
            project=None,
            projects=PROJECTS[:15],
            error_message=f"Project with ID '{project_id}' was not found in the monitoring records.",
            filter_options=get_filter_options(),
            total_items=len(PROJECTS),
            page=1,
            total_pages=1,
            start_item=1,
            end_item=15,
            active_filters={"risk": "All", "status": "All", "state": "All", "district": "All", "category": "All", "search": ""}
        ), 404

    return render_template(
        "project.html",
        project=project,
        projects=PROJECTS[:10]
    )


@app.route("/analytics")
def analytics():
    """Analytics & AI Risk Analysis Dashboard."""
    statistics = calculate_statistics(PROJECTS)

    # Category Breakdown
    categories = {}
    for p in PROJECTS:
        cat = p.get("category", "General")
        if cat not in categories:
            categories[cat] = {"count": 0, "sanctioned": 0, "spent": 0, "high_risk": 0}
        categories[cat]["count"] += 1
        categories[cat]["sanctioned"] += p.get("sanctioned", 0)
        categories[cat]["spent"] += p.get("spent", 0)
        if p.get("risk") == "High":
            categories[cat]["high_risk"] += 1

    category_list = []
    for cat, data in categories.items():
        util = (data["spent"] / data["sanctioned"] * 100) if data["sanctioned"] > 0 else 0
        category_list.append({
            "category": cat,
            "count": data["count"],
            "sanctioned_cr": round(data["sanctioned"] / 10000000, 2),
            "spent_cr": round(data["spent"] / 10000000, 2),
            "utilization": round(util, 1),
            "high_risk": data["high_risk"]
        })
    category_list.sort(key=lambda x: x["count"], reverse=True)

    # District Risk Distribution
    districts = {}
    for p in PROJECTS:
        d = p.get("district", "General")
        if d not in districts:
            districts[d] = {"count": 0, "high_risk": 0, "sanctioned": 0, "state": p.get("state", "Karnataka")}
        districts[d]["count"] += 1
        districts[d]["sanctioned"] += p.get("sanctioned", 0)
        if p.get("risk") == "High":
            districts[d]["high_risk"] += 1

    district_list = []
    for d, data in districts.items():
        district_list.append({
            "district": d,
            "state": data["state"],
            "count": data["count"],
            "high_risk": data["high_risk"],
            "sanctioned_cr": round(data["sanctioned"] / 10000000, 2)
        })
    district_list.sort(key=lambda x: x["high_risk"], reverse=True)

    # Status Distribution
    statuses = {"Ongoing": 0, "Completed": 0, "Delayed": 0, "Critical": 0, "Under Review": 0}
    for p in PROJECTS:
        st = p.get("status", "Ongoing")
        statuses[st] = statuses.get(st, 0) + 1

    # Top Anomaly Reasons
    anomaly_counts = {}
    for p in PROJECTS:
        for a in p.get("anomalies", []):
            clean_a = a.strip()
            if clean_a:
                anomaly_counts[clean_a] = anomaly_counts.get(clean_a, 0) + 1
    raw_anomalies = sorted(anomaly_counts.items(), key=lambda x: x[1], reverse=True)[:6]
    max_count = raw_anomalies[0][1] if raw_anomalies else 1
    top_anomalies = [
        {"reason": r, "count": c, "pct": max(10, min(100, int((c / max_count) * 100)))}
        for r, c in raw_anomalies
    ]

    # Flagged projects needing review
    flagged_projects = [p for p in PROJECTS if p.get("risk") == "High"][:10]

    return render_template(
        "analytics.html",
        statistics=statistics,
        category_list=category_list,
        district_list=district_list[:12],
        statuses=statuses,
        top_anomalies=top_anomalies,
        flagged_projects=flagged_projects
    )


@app.route("/risk-analysis")
def risk_analysis():
    """Direct alias to Analytics & Risk Dashboard."""
    return analytics()


@app.route("/map")
def map_view():
    """Geographic project distribution view."""
    statistics = calculate_statistics(PROJECTS)

    # Group by district
    district_data = {}
    for p in PROJECTS:
        dist = p.get("district", "Unknown")
        st = p.get("state", "Karnataka")
        if dist not in district_data:
            district_data[dist] = {
                "district": dist,
                "state": st,
                "total": 0,
                "high_risk": 0,
                "medium_risk": 0,
                "low_risk": 0,
                "sanctioned": 0,
                "spent": 0
            }
        district_data[dist]["total"] += 1
        district_data[dist]["sanctioned"] += p.get("sanctioned", 0)
        district_data[dist]["spent"] += p.get("spent", 0)
        if p.get("risk") == "High":
            district_data[dist]["high_risk"] += 1
        elif p.get("risk") == "Medium":
            district_data[dist]["medium_risk"] += 1
        else:
            district_data[dist]["low_risk"] += 1

    districts = sorted(district_data.values(), key=lambda x: x["total"], reverse=True)

    # Group by state
    state_data = {}
    for d in districts:
        st = d["state"]
        if st not in state_data:
            state_data[st] = {"state": st, "total": 0, "high_risk": 0, "sanctioned": 0, "districts": []}
        state_data[st]["total"] += d["total"]
        state_data[st]["high_risk"] += d["high_risk"]
        state_data[st]["sanctioned"] += d["sanctioned"]
        state_data[st]["districts"].append(d["district"])

    states = sorted(state_data.values(), key=lambda x: x["total"], reverse=True)

    return render_template(
        "map.html",
        statistics=statistics,
        districts=districts,
        states=states
    )


@app.route("/reports")
def reports():
    """System Reports & Audit Export View."""
    statistics = calculate_statistics(PROJECTS)
    high_risk_projects = [p for p in PROJECTS if p.get("risk") == "High"]
    delayed_projects = [p for p in PROJECTS if p.get("status") in ["Delayed", "Critical"]]

    # Summary table by category
    categories = {}
    for p in PROJECTS:
        cat = p.get("category", "General")
        if cat not in categories:
            categories[cat] = {"count": 0, "sanctioned": 0, "spent": 0, "high_risk": 0}
        categories[cat]["count"] += 1
        categories[cat]["sanctioned"] += p.get("sanctioned", 0)
        categories[cat]["spent"] += p.get("spent", 0)
        if p.get("risk") == "High":
            categories[cat]["high_risk"] += 1

    return render_template(
        "reports.html",
        statistics=statistics,
        high_risk_count=len(high_risk_projects),
        delayed_count=len(delayed_projects),
        categories=categories
    )


# ==========================================================
# REST API ENDPOINTS
# ==========================================================

@app.route("/api/dashboard")
def dashboard_api():
    """Returns dashboard statistics and preview items."""
    statistics = calculate_statistics(PROJECTS)
    return jsonify({
        "success": True,
        "statistics": statistics,
        "projects": PROJECTS[:25]
    })


@app.route("/api/projects")
def projects_api():
    """API endpoint for querying and filtering projects."""
    filtered = filter_projects_list(PROJECTS, request.args)
    return jsonify({
        "success": True,
        "count": len(filtered),
        "projects": filtered
    })


@app.route("/api/project/<project_id>")
def single_project_api(project_id):
    """API endpoint for a single project details."""
    target_id = project_id.strip().lower()
    project = next((p for p in PROJECTS if p["id"].lower() == target_id), None)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404
    return jsonify({"success": True, "project": project})


@app.route("/api/analyze", methods=["POST"])
def analyze_api():
    """Triggers the AI risk engine anomaly detection run."""
    global PROJECTS
    # Reload and refresh calculations
    PROJECTS = load_all_projects()
    stats = calculate_statistics(PROJECTS)

    return jsonify({
        "success": True,
        "message": "AI Risk Analysis completed successfully.",
        "analyzed_count": len(PROJECTS),
        "high_risk_count": stats["high_risk"],
        "total_anomalies": stats["total_anomalies"],
        "statistics": stats
    })


@app.route("/api/export")
def export_api():
    """Exports projects dataset or filtered subset as a CSV download."""
    filtered = filter_projects_list(PROJECTS, request.args)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow([
        "Project ID",
        "Project Name",
        "District",
        "State",
        "Category",
        "Implementing Agency",
        "Contractor",
        "Sanctioned Amount (INR)",
        "Expenditure (INR)",
        "Physical Progress (%)",
        "Project Status",
        "AI Risk Level",
        "Risk Score (0-100)",
        "Detected Anomalies",
        "Recommended Action"
    ])

    for p in filtered:
        anomalies_str = "; ".join(p.get("anomalies", []))
        writer.writerow([
            p.get("id", ""),
            p.get("name", ""),
            p.get("district", ""),
            p.get("state", ""),
            p.get("category", ""),
            p.get("agency", ""),
            p.get("contractor", ""),
            p.get("sanctioned", 0),
            p.get("spent", 0),
            p.get("progress", 0),
            p.get("status", ""),
            p.get("risk", ""),
            p.get("risk_score", 0),
            anomalies_str,
            p.get("recommended_action", "")
        ])

    csv_data = output.getvalue()
    output.close()

    filename = "MPLAD_Risk_Report.csv"
    if request.args.get("risk"):
        filename = f"MPLAD_{request.args.get('risk')}_Risk_Report.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "MPLAD AI Risk Monitoring System",
        "total_projects": len(PROJECTS)
    })


@app.errorhandler(404)
def page_not_found(e):
    """Graceful 404 handler."""
    return render_template(
        "project.html",
        project=None,
        projects=PROJECTS[:10],
        error_message="The requested page or project was not found.",
        filter_options=get_filter_options(),
        total_items=len(PROJECTS),
        page=1,
        total_pages=1,
        start_item=1,
        end_item=10,
        active_filters={"risk": "All", "status": "All", "state": "All", "district": "All", "category": "All", "search": ""}
    ), 404


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )