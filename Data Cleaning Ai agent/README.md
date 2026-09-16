# 🤖 Data Cleaning AI Agent

> **An autonomous, multi-agent AI system built in Python & Flask for intelligent dataset analysis, defect detection, rule-based data cleaning, and human-readable audit reporting.**

---

## 📌 1. Project Objective

The **Data Cleaning AI Agent** is a full-stack, student-friendly AI application engineered to automate the tedious process of cleaning messy tabular datasets (CSV/Excel).

Rather than blindly applying hardcoded transformations or relying strictly on external cloud APIs, this system utilizes a **deterministic multi-agent workflow** paired with a smart explanation layer. It inspects data structure, identifies defects, applies conservative domain cleaning strategies, presents before-and-after metrics, and generates downloadable audit logs and reports.

---

## ✨ 2. Key Features

- **📊 Comprehensive Dataset Analysis**: Automatically scans uploaded CSV/Excel files for missing values, exact row duplicates, numerical outliers (IQR), date format inconsistencies, invalid domain bounds (e.g. negative ages), and constant columns.
- **🤖 Autonomous Multi-Agent Workflow**:
  - `AnalyzerAgent`: Performs deep structural quality analysis and computes a Data Quality Score (0–100).
  - `CleaningAgent`: Executes configurable cleaning strategies (imputation, deduplication, casing/whitespace normalization, ISO date standardization).
  - `ValidationAgent`: Calculates before-vs-after comparative metrics and verifies dataset integrity.
  - `ExplanationAgent`: Synthesizes natural language quality summaries and recommendations using an external LLM API (if configured in `.env`) or a built-in rule-based template engine (zero external dependencies required!).
- **🛡️ Conservative Data Safety Rules**:
  - Never deletes potential outliers by default (detects and reports only unless explicitly configured).
  - Preserves original raw uploads in `uploads/` and exports clean versions to `outputs/`.
  - Maintains an explicit, chronological audit log for every single cell modification.
- **🎨 Glassmorphic Modern Dashboard**: Built with HTML5, Bootstrap 5, custom CSS glassmorphism styling, and Chart.js interactive charts.
- **📥 One-Click Exports**: Download cleaned CSV/XLSX datasets and structured text audit reports (`cleaning_report.txt`).
- **⚡ Pre-loaded Messy Dataset**: Instant one-click demo dataset (`sample_data/messy_dataset.csv`) included for presentation demonstrations.

---

## 🏗️ 3. Agent Architecture Pipeline

```text
               User Uploads CSV / XLSX (or Click "Load Sample Dataset")
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Analyzer Agent  │  <-- Structural Inspection & Quality Scoring
                              └────────┬────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ Decision Engine / Config  │  <-- Strategy Selection (Imputation/Outliers)
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Cleaning Agent  │  <-- Sequential Rule Execution & Audit Logging
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Validation Agent│  <-- Before vs After Verification
                              └────────┬────────┘
                                       │
                                       ▼
                             ┌───────────────────┐
                             │ Explanation Agent │  <-- LLM / Template Natural Language Rationale
                             └─────────┬─────────┘
                                       │
                                       ▼
                  Cleaned Dataset (.csv) + Cleaning Audit Report (.txt)
```

---

## 🛠️ 4. Technology Stack

- **Language**: Python 3.13+
- **Backend Web Server**: Flask 3.1
- **Data Processing & ML**: Pandas, NumPy, Scikit-learn
- **File Handling**: OpenPyXL (Excel support), Werkzeug
- **Frontend & UI**: HTML5, Vanilla CSS3 (Glassmorphism theme), JavaScript, Bootstrap 5, Bootstrap Icons
- **Visualizations**: Chart.js (Dynamic client-side missing value & quality breakdown charts)
- **Testing**: Python `unittest` framework

---

## 📁 5. Project Directory Structure

```text
Data Cleaning Ai agent/
├── app.py                      # Flask application server & route handlers
├── config.py                   # Global configuration & directory setup
├── requirements.txt            # Python dependencies
├── README.md                   # Project presentation documentation
├── .env.example                # Optional LLM API key configuration
│
├── agents/
│   ├── analyzer_agent.py       # Structural inspector & quality scorer
│   ├── cleaning_agent.py       # Sequential cleaning pipeline manager
│   ├── validation_agent.py     # Comparative metrics calculator
│   └── explanation_agent.py    # LLM & rule-based template explanation synthesizer
│
├── cleaning/
│   ├── missing_values.py       # Missing value detection & imputation (Median/Mean/Mode)
│   ├── duplicates.py           # Deduplication logic
│   ├── outliers.py             # IQR & Z-score numerical outlier detection & handling
│   ├── text_cleaning.py        # Whitespace stripping & casing normalization
│   ├── date_cleaning.py        # ISO (YYYY-MM-DD) date standardization
│   └── type_conversion.py      # Safe numeric conversion & domain bound checks
│
├── utils/
│   ├── file_handler.py         # Secure file loading/saving with encoding fallbacks
│   ├── report_generator.py     # Text report generator (.txt)
│   └── validators.py           # Structure & schema validators
│
├── templates/
│   ├── base.html               # Shared layout & navigation header
│   ├── index.html              # Step 1: Upload & Sample dataset loader
│   ├── analysis.html           # Step 2: Quality Inspection Dashboard & Column breakdown
│   ├── configure.html          # Step 3: Interactive cleaning strategy selector
│   └── results.html            # Step 4: Before vs After comparison, audit log & downloads
│
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism dark theme styling
│   └── js/
│       └── main.js             # Drag-and-drop file upload & UI interactions
│
├── uploads/                    # Uploaded raw datasets storage
├── outputs/                    # Exported cleaned datasets storage
├── reports/                    # Exported cleaning audit reports storage
├── sample_data/
│   └── messy_dataset.csv       # Pre-configured messy demonstration dataset
│
└── tests/
    └── test_cleaning.py        # Automated test suite
```

---

## 🚀 6. Installation & How to Run

### Step 1: Clone or Navigate to Project Directory
```bash
cd "Data Cleaning Ai agent"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Open in Web Browser
Navigate to `http://127.0.0.1:5000` in your web browser.

---

## 🧪 7. Running Automated Tests

To run the unit test suite and verify data cleaning modules:
```bash
python -m unittest discover tests
```

---

## 💡 8. Demonstration Instructions for Presentation

1. **Start the Flask server** (`python app.py`).
2. **Open browser** at `http://127.0.0.1:5000`.
3. Click **"Load Messy Sample Dataset"** on the home page.
4. **Step 2 (Analysis)**: Observe the initial **Quality Score** (e.g. 52/100), total missing values, duplicate count, outlier flags, and Chart.js bar graph.
5. Click **"Proceed to Cleaning Configuration"**.
6. **Step 3 (Configuration)**: Select desired cleaning rules (e.g. Median numeric imputation, Mode categorical imputation, Deduplication, Date standardization, Outliers detect only).
7. Click **"Execute Data Cleaning Agent"**.
8. **Step 4 (Results)**: View the improved **Quality Score** (e.g. 96/100), Before vs After comparison card, chronological agent log, AI natural language summary, and download your cleaned CSV and report!
