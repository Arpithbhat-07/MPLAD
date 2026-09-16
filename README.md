# 🛡️ MPLADS SENTINEL

## Risk & Anomaly Intelligence System for MPLADS

> An AI-powered system for detecting anomalies, financial irregularities,
> implementation risks, delays, and unusual project patterns in MPLADS
> implementation data.

---

# 📌 1. Project Overview

MPLADS SENTINEL is an AI-powered monitoring and risk-intelligence
platform designed to analyze project-level MPLADS implementation data.

The system combines:

- Data processing
- Feature engineering
- Rule-based risk detection
- Machine Learning anomaly detection
- Hybrid risk scoring
- Explainable risk indicators
- Investigation workflows
- Analytics
- Risk monitoring
- Dashboard visualization

The objective is to transform raw project records into actionable
risk intelligence.

Instead of manually examining thousands of project records, the system
processes the available records automatically and prioritizes projects
that require further review.

---

# 🎯 2. Problem Statement

Large-scale public development schemes can contain thousands of
individual project records.

Manually identifying:

- unusual expenditure
- abnormal project costs
- implementation inconsistencies
- delays
- unusual project characteristics
- potential duplicate works
- unusual utilization patterns

can be difficult when dealing with large datasets.

MPLADS SENTINEL provides an automated intelligence layer over project
data to identify records that deserve additional investigation.

---

# 🧠 3. Core Idea

The system follows this pipeline:

Raw Data
   ↓
Data Validation
   ↓
Data Standardization
   ↓
Feature Engineering
   ↓
Rule-Based Risk Detection
   ↓
Machine Learning Anomaly Detection
   ↓
Hybrid Risk Engine
   ↓
Risk Classification
   ↓
Inspection Priority
   ↓
Flask API
   ↓
Dashboard
   ↓
Investigation & Analytics

The system does not automatically declare that a project is fraudulent.

Instead, it identifies unusual patterns and generates risk indicators
that can support human investigation.

---

# 🏗️ 4. High-Level System Architecture

                    ┌────────────────────────────┐
                    │       DATA SOURCES         │
                    │                            │
                    │ Official MPLADS Dataset   │
                    │ Synthetic Demonstration   │
                    │ Dataset                   │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │      DATA PROCESSING       │
                    │                            │
                    │ CSV Loading                │
                    │ Validation                 │
                    │ Standardization            │
                    │ Missing-value handling     │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │    FEATURE ENGINEERING     │
                    │                            │
                    │ Fund utilization           │
                    │ Progress/Expenditure gap   │
                    │ Cost overrun               │
                    │ Timeline delay             │
                    │ Project metadata           │
                    └──────────────┬─────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
                 ▼                                   ▼
      ┌──────────────────────┐          ┌──────────────────────┐
      │ RULE-BASED ENGINE    │          │ MACHINE LEARNING     │
      │                      │          │                      │
      │ Financial rules      │          │ Isolation Forest     │
      │ Progress rules       │          │ Anomaly detection    │
      │ Timeline rules       │          │ ML anomaly score     │
      │ Cost rules           │          │                      │
      └──────────┬───────────┘          └──────────┬───────────┘
                 │                                   │
                 └─────────────────┬─────────────────┘
                                   ▼
                    ┌────────────────────────────┐
                    │     HYBRID RISK ENGINE     │
                    │                            │
                    │ Rule Risk       60%        │
                    │ ML Risk         40%        │
                    │                            │
                    │ Hybrid Risk Score          │
                    │ Risk Level                 │
                    │ Risk Reasons               │
                    │ Inspection Priority        │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │       FLASK BACKEND        │
                    │                            │
                    │ REST APIs                  │
                    │ Project Services            │
                    │ Analytics Services         │
                    │ Risk Services              │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │       WEB FRONTEND         │
                    │                            │
                    │ Command Center             │
                    │ Risk Monitor                │
                    │ Work Explorer               │
                    │ Analytics                   │
                    │ Alerts                      │
                    │ Investigation               │
                    │ Sentinel AI                 │
                    └────────────────────────────┘

---

# 📂 5. Project Structure

```text
MPLAD/
│
├── backend/
│   │
│   ├── data/
│   │   │
│   │   ├── officials/
│   │   │   └── mplads_official.csv
│   │   │
│   │   └── synthtic/
│   │       ├── flagged_works.csv
│   │       ├── unified_risk_results.csv
│   │       ├── explainable_risk_results.csv
│   │       └── hybrid_risk_results.csv
│   │
│   ├── ml/
│   │   ├── anomaly_detector.py
│   │   ├── duplicate_detector.py
│   │   ├── explainable_ai.py
│   │   ├── fund_detector.py
│   │   ├── risk_engine.py
│   │   ├── timeline_detector.py
│   │   ├── unified_risk_engine.py
│   │   │
│   │   └── Models/
│   │       └── anomaly_model_v1_7_1_final.joblib
│   │
│   ├── services/
│   │   ├── feature_engineering.py
│   │   ├── project_service.py
│   │   ├── analytics_service.py
│   │   └── risk_service.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_processor.py
│   │
│   └── app.py
│
├── frontend/
│   │
│   ├── static/
│   │   │
│   │   ├── css/
│   │   │   ├── risk_monitor.css
│   │   │   ├── style.css
│   │   │   └── work_explorer.css
│   │   │
│   │   └── js/
│   │       ├── charts.js
│   │       ├── dashboard.js
│   │       ├── global_search.js
│   │       ├── map.js
│   │       ├── risk_monitor.js
│   │       └── work_explorer.js
│   │
│   └── templates/
│       ├── agencies.html
│       ├── alerts.html
│       ├── analytics.html
│       ├── data_health.html
│       ├── districts.html
│       ├── index.html
│       ├── investigation.html
│       ├── map.html
│       ├── project.html
│       ├── reports.html
│       ├── risk_monitor.html
│       ├── sentinel_ai.html
│       ├── settings.html
│       └── work_explorer.html
│
├── tests/
│
├── venv/
│
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
