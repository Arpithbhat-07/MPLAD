"""Flask application for the MPLADS AI Monitoring System."""

from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from backend.services.analytics_service import (
    category_breakdown,
    district_breakdown,
    map_breakdown,
    status_breakdown,
    top_anomalies,
)

from backend.services.project_service import (
    ProjectRepository,
    calculate_statistics,
    filter_projects,
    get_filter_options,
)

from backend.services.risk_service import (
    analyze_dataset,
    get_risk_summary,
)

from backend.utils.data_processor import (
    load_official_data,
    load_synthetic_data,
)


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FRONTEND_ROOT = PROJECT_ROOT / "frontend"


# ==========================================================
# CREATE FLASK APP
# ==========================================================

def create_app() -> Flask:

    app = Flask(
        __name__,
        template_folder=str(
            FRONTEND_ROOT / "templates"
        ),
        static_folder=str(
            FRONTEND_ROOT / "static"
        ),
        static_url_path="/static",
    )

    # ======================================================
    # JINJA GLOBALS
    # ======================================================

    app.jinja_env.globals.update(
        min=min,
        max=max,
    )

    # ======================================================
    # PROJECT REPOSITORY
    # ======================================================

    repository = ProjectRepository.load()

    app.config["PROJECTS"] = repository.projects
    app.config["REPOSITORY"] = repository

    def projects_data():
        return app.config["PROJECTS"]

    def refresh_projects():
        repository.refresh()
        app.config["PROJECTS"] = repository.projects

    # ======================================================
    # GLOBAL TEMPLATE DATA
    # ======================================================

    @app.context_processor
    def inject_globals():

        return {
            "statistics": calculate_statistics(
                projects_data()
            )
        }

    # ======================================================
    # HOME PAGE
    # ======================================================

    @app.get("/")
    def home():

        projects = projects_data()

        return render_template(
            "index.html",

            projects=projects[:10],

            alert_projects=[
                project
                for project in projects
                if project.get("risk") == "High"
            ][:8],

            statistics=calculate_statistics(
                projects
            ),

            filter_options=get_filter_options(
                projects
            ),
        )

    # ======================================================
    # PROJECTS / WORK EXPLORER PAGE
    # ======================================================

    @app.get("/projects")
    def projects():

        all_projects = projects_data()

        filtered = filter_projects(
            all_projects,
            request.args,
        )

        try:
            page = max(
                1,
                int(
                    request.args.get(
                        "page",
                        1,
                    )
                ),
            )

        except ValueError:
            page = 1

        per_page = 20

        total_items = len(filtered)

        total_pages = max(
            1,
            (
                total_items
                + per_page
                - 1
            )
            // per_page,
        )

        page = min(
            page,
            total_pages,
        )

        start_idx = (
            page - 1
        ) * per_page

        end_idx = min(
            start_idx + per_page,
            total_items,
        )

        active_filters = {
            key: request.args.get(
                key,
                "All",
            )
            for key in (
                "risk",
                "status",
                "state",
                "district",
                "category",
            )
        }

        active_filters["search"] = (
            request.args.get(
                "search",
                "",
            )
        )

        # /projects = Work Explorer
        # project.html is only for /project/<project_id>

        return render_template(
            "work_explorer.html",

            projects=filtered[
                start_idx:end_idx
            ],

            total_items=total_items,

            page=page,

            total_pages=total_pages,

            start_item=(
                start_idx + 1
                if total_items
                else 0
            ),

            end_item=end_idx,

            active_filters=active_filters,

            filter_options=get_filter_options(
                all_projects
            ),
        )

    # ======================================================
    # SINGLE PROJECT / WORK INVESTIGATION
    # ======================================================

    @app.get("/project/<project_id>")
    def project_details(
        project_id: str,
    ):

        project = repository.get(
            project_id
        )

        if not project:

            return render_template(
                "project.html",

                project=None,

                projects=projects_data()[:15],

                error_message=(
                    f"Project with ID "
                    f"'{project_id}' "
                    "was not found "
                    "in the monitoring records."
                ),

                filter_options=get_filter_options(
                    projects_data()
                ),

                total_items=len(
                    projects_data()
                ),

                page=1,

                total_pages=1,

                start_item=1,

                end_item=min(
                    15,
                    len(
                        projects_data()
                    ),
                ),

                active_filters={
                    "risk": "All",
                    "status": "All",
                    "state": "All",
                    "district": "All",
                    "category": "All",
                    "search": "",
                },
            ), 404

        return render_template(
            "project.html",

            project=project,

            projects=projects_data()[:10],
        )

    # ======================================================
    # ANALYTICS PAGE
    # ======================================================

    @app.get("/analytics")
    def analytics():

        projects = projects_data()

        return render_template(
            "analytics.html",

            statistics=calculate_statistics(
                projects
            ),

            category_list=category_breakdown(
                projects
            ),

            district_list=district_breakdown(
                projects
            )[:12],

            statuses=status_breakdown(
                projects
            ),

            top_anomalies=top_anomalies(
                projects
            ),

            flagged_projects=[
                project
                for project in projects
                if project.get("risk") == "High"
            ][:10],
        )

    # ======================================================
    # ALERTS PAGE
    # ======================================================

    @app.get("/alerts")
    def alerts():

        projects = projects_data()

        high_risk_projects = []

        for project in projects:

            risk = str(
                project.get(
                    "risk",
                    "",
                )
                or ""
            ).strip().lower()

            try:

                risk_score = float(
                    project.get(
                        "risk_score",
                        0,
                    )
                    or 0
                )

            except (
                ValueError,
                TypeError,
            ):

                risk_score = 0

            if (
                risk == "high"
                or risk_score >= 70
            ):

                high_risk_projects.append(
                    project
                )

        return render_template(
            "alerts.html",

            projects=high_risk_projects,
        )

    # ======================================================
    # RISK MONITOR PAGE
    # ======================================================

    @app.get("/risk-analysis")
    def risk_analysis():

        return render_template(
            "risk_monitor.html"
        )

    # ======================================================
    # MAP PAGE
    # ======================================================

    @app.get("/map")
    def map_view():

        projects = projects_data()

        districts, states = map_breakdown(
            projects
        )

        return render_template(
            "map.html",

            statistics=calculate_statistics(
                projects
            ),

            districts=districts,

            states=states,
        )

    # ======================================================
    # REPORTS PAGE
    # ======================================================

    @app.get("/reports")
    def reports():

        projects = projects_data()

        categories = {}

        for project in projects:

            category = project.get(
                "category",
                "General",
            )

            item = categories.setdefault(
                category,
                {
                    "count": 0,
                    "sanctioned": 0,
                    "spent": 0,
                    "high_risk": 0,
                },
            )

            item["count"] += 1

            item["sanctioned"] += (
                project.get(
                    "sanctioned",
                    0,
                )
            )

            item["spent"] += (
                project.get(
                    "spent",
                    0,
                )
            )

            item["high_risk"] += (
                project.get("risk")
                == "High"
            )

        return render_template(
            "reports.html",

            statistics=calculate_statistics(
                projects
            ),

            high_risk_count=sum(
                project.get("risk")
                == "High"
                for project in projects
            ),

            delayed_count=sum(
                project.get("status")
                in {
                    "Delayed",
                    "Critical",
                }
                for project in projects
            ),

            categories=categories,
        )

    # ======================================================
    # DASHBOARD API
    # ======================================================

    @app.get("/api/dashboard")
    def dashboard_api():

        projects = projects_data()

        return jsonify(
            success=True,

            statistics=calculate_statistics(
                projects
            ),

            projects=projects[:25],
        )

    # ======================================================
    # PROJECTS API
    # ======================================================

    @app.get("/api/projects")
    def projects_api():

        filtered = filter_projects(
            projects_data(),
            request.args,
        )

        return jsonify(
            success=True,

            count=len(filtered),

            projects=filtered,
        )

    # ======================================================
    # SINGLE PROJECT API
    # ======================================================

    @app.get("/api/project/<project_id>")
    def single_project_api(
        project_id: str,
    ):

        project = repository.get(
            project_id
        )

        if not project:

            return jsonify(
                success=False,

                error="Project not found",
            ), 404

        return jsonify(
            success=True,

            project=project,
        )

    # ======================================================
    # AI RISK ANALYSIS API
    # ======================================================

    @app.get("/api/risk-analysis")
    def api_risk_analysis():

        source = request.args.get(
            "source",
            "synthetic",
        ).lower()

        # --------------------------------------------------
        # SELECT DATASET
        # --------------------------------------------------

        if source == "official":

            df = load_official_data()

        elif source == "synthetic":

            df = load_synthetic_data()

        else:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "source must be "
                        "official or synthetic"
                    ),
                }
            ), 400

        # --------------------------------------------------
        # CHECK DATA
        # --------------------------------------------------

        if df is None:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        f"{source} dataset "
                        "could not be loaded."
                    ),
                }
            ), 500

        if df.empty:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        f"{source} dataset "
                        "is empty."
                    ),
                }
            ), 404

        # --------------------------------------------------
        # RUN COMPLETE AI PIPELINE
        # --------------------------------------------------

        try:

            result = analyze_dataset(
                df,
                source,
            )

        except Exception as exc:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "AI risk analysis failed: "
                        f"{exc}"
                    ),
                }
            ), 500

        # --------------------------------------------------
        # GET SUMMARY
        # --------------------------------------------------

        summary = get_risk_summary(
            result
        )

        # --------------------------------------------------
        # CONVERT DATA TO JSON-SAFE FORMAT
        # --------------------------------------------------

        records = result.copy()

        # Convert datetime columns.
        # NaT becomes None.

        for column in records.columns:

            if pd.api.types.is_datetime64_any_dtype(
                records[column]
            ):

                records[column] = (
                    records[column].apply(
                        lambda x:
                        x.isoformat()
                        if pd.notna(x)
                        else None
                    )
                )

        # --------------------------------------------------
        # CONVERT DATAFRAME TO OBJECT
        # --------------------------------------------------

        records = records.astype(
            object
        )

        # --------------------------------------------------
        # REPLACE INVALID VALUES
        # --------------------------------------------------

        records = records.replace(
            [
                float("inf"),
                float("-inf"),
            ],
            None,
        )

        records = records.where(
            pd.notna(records),
            None,
        )

        # --------------------------------------------------
        # CONVERT TO PYTHON DICTIONARIES
        # --------------------------------------------------

        projects_json = records.to_dict(
            orient="records"
        )

        # --------------------------------------------------
        # CONVERT NUMPY VALUES
        # --------------------------------------------------

        for project in projects_json:

            for key, value in project.items():

                if hasattr(
                    value,
                    "item",
                ):

                    try:

                        project[key] = (
                            value.item()
                        )

                    except (
                        ValueError,
                        TypeError,
                    ):

                        pass

        # --------------------------------------------------
        # DATA LABEL
        # --------------------------------------------------

        if source == "synthetic":

            data_label = (
                "Synthetic Demonstration Dataset"
            )

            data_description = (
                "AI risk intelligence generated "
                "from synthetic demonstration "
                "records. Not official government "
                "findings."
            )

        else:

            data_label = (
                "Official MPLADS Dataset"
            )

            data_description = (
                "Analysis based on data available "
                "from the official MPLADS dataset. "
                "Unavailable source fields are not "
                "fabricated."
            )

        # --------------------------------------------------
        # RETURN JSON
        # --------------------------------------------------

        return jsonify(
            {
                "success": True,

                "source": source,

                "data_label": data_label,

                "data_description": (
                    data_description
                ),

                "summary": summary,

                "projects": projects_json,
            }
        )

    # ======================================================
    # OLD ANALYZE API
    # ======================================================

    @app.post("/api/analyze")
    def analyze_api():

        try:

            source = request.args.get(
                "source",
                "synthetic",
            ).lower()

            # --------------------------------------------------
            # SELECT DATASET
            # --------------------------------------------------

            if source == "official":

                df = load_official_data()

            elif source == "synthetic":

                df = load_synthetic_data()

            else:

                return jsonify(
                    success=False,

                    message=(
                        "source must be "
                        "official or synthetic"
                    ),
                ), 400

            # --------------------------------------------------
            # RUN AI PIPELINE
            # --------------------------------------------------

            result = analyze_dataset(
                df,
                source,
            )

            # --------------------------------------------------
            # SUMMARY
            # --------------------------------------------------

            summary = get_risk_summary(
                result
            )

            return jsonify(
                success=True,

                message=(
                    "AI Risk Analysis "
                    "completed successfully."
                ),

                source=source,

                analyzed_count=len(
                    result
                ),

                high_risk_count=summary.get(
                    "high_risk",
                    0,
                ),

                ml_anomalies=summary.get(
                    "ml_anomalies",
                    0,
                ),

                statistics=summary,
            )

        except Exception as exc:

            return jsonify(
                success=False,

                message=(
                    "Risk analysis failed: "
                    f"{exc}"
                ),
            ), 500

    # ======================================================
    # EXPORT API
    # ======================================================

    @app.get("/api/export")
    def export_api():

        filtered = filter_projects(
            projects_data(),
            request.args,
        )

        output = io.StringIO()

        writer = csv.writer(
            output
        )

        writer.writerow(
            [
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
                "Recommended Action",
            ]
        )

        for project in filtered:

            writer.writerow(
                [
                    project.get(
                        "id",
                        "",
                    ),

                    project.get(
                        "name",
                        "",
                    ),

                    project.get(
                        "district",
                        "",
                    ),

                    project.get(
                        "state",
                        "",
                    ),

                    project.get(
                        "category",
                        "",
                    ),

                    project.get(
                        "agency",
                        "",
                    ),

                    project.get(
                        "contractor",
                        "",
                    ),

                    project.get(
                        "sanctioned",
                        0,
                    ),

                    project.get(
                        "spent",
                        0,
                    ),

                    project.get(
                        "progress",
                        0,
                    ),

                    project.get(
                        "status",
                        "",
                    ),

                    project.get(
                        "risk",
                        "",
                    ),

                    project.get(
                        "risk_score",
                        0,
                    ),

                    "; ".join(
                        project.get(
                            "anomalies",
                            [],
                        )
                    ),

                    project.get(
                        "recommended_action",
                        "",
                    ),
                ]
            )

        risk = request.args.get(
            "risk"
        )

        filename = (
            f"MPLAD_{risk}_Risk_Report.csv"
            if risk
            else "MPLAD_Risk_Report.csv"
        )

        return Response(
            output.getvalue(),

            mimetype="text/csv",

            headers={
                "Content-Disposition":
                    f"attachment; filename={filename}"
            },
        )

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    @app.get("/health")
    def health():

        return jsonify(
            status="healthy",

            service=(
                "MPLAD AI Risk "
                "Monitoring System"
            ),

            total_projects=len(
                projects_data()
            ),
        )

    # ======================================================
    # 404 HANDLER
    # ======================================================

    @app.errorhandler(404)
    def not_found(_error):

        return redirect(
            url_for(
                "projects"
            )
        )

    # ======================================================
    # RETURN APP
    # ======================================================

    return app