# MPLAD AI Risk Monitoring System

A Flask-based web application for monitoring and assessing risk in MPLAD projects using AI-driven anomaly detection, project analytics, and inspection-ready reporting.

This branch focuses on the frontend dashboard and monitoring experience for the MPLAD risk intelligence platform.

## Overview

The system helps public-sector stakeholders review project execution quality by identifying:

- Financial and physical progress mismatches
- Delayed or critical projects
- High-risk districts and categories
- Potential anomalies in sanctioned-vs-spent trends
- Actionable recommendations for audit and site review

It combines curated project records, analytics dashboards, risk scoring, and a geographic overview to support decision-making for grant monitoring and oversight.

## Features

- Interactive dashboard with risk summary cards
- Project listing and filtering by state, district, category, status, and risk level
- Detailed project view with audit explanations and recommended actions
- Analytics page for category, district, and anomaly trend analysis
- Map-based project distribution view
- Reports page for high-risk and delayed project summaries
- CSV export functionality for risk reporting
- API endpoints for dashboard and project data

## Tech Stack

- Python
- Flask
- Pandas
- NumPy
- scikit-learn
- Jinja2 templates
- HTML, CSS, JavaScript

## Project Structure

```text
MPLADS-ai-risk-managment-system/
├── app.py                     # Flask application entry point
├── requirements.txt          # Python dependencies
├── data/                     # Risk and project dataset files
├── modules/                  # Risk analysis and detection logic
├── static/                   # CSS and JavaScript assets
├── templates/                # HTML dashboard templates
├── utils/                   # Data processing utilities
├── MPLAD/                   # Embedded project subfolder/reference
└── README.md                 # Project documentation
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Arpithbhat-07/MPLAD.git
cd MPLAD
git checkout frontend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

## Main Pages

- / - Dashboard overview
- /projects - Searchable project listing
- /project/<project_id> - Individual project details
- /analytics - AI risk analytics and trend dashboards
- /map - Geographic distribution view
- /reports - Monitoring and export reports

## API Endpoints

- /api/dashboard
- /api/projects
- /api/project/<project_id>
- /api/analyze
- /api/export
- /health

## Data & Risk Model

The application loads project-related data and integrates AI-assisted risk indicators to detect anomalies such as:

- unusual expenditure-to-progress ratios
- delayed milestones
- budget utilization spikes
- status-risk inconsistencies
- contract execution concerns

## Notes

This repository is structured for a monitoring dashboard and decision-support workflow. The app is intended to provide risk visibility for MPLAD implementation tracking, with a focus on transparency, audit readiness, and operational review.

## License

This project is for research, monitoring, and dashboard demonstration purposes.
