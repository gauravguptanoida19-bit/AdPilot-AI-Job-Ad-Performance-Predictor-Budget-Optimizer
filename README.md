<div align="center">

# AdPilot • Recruitment Ad Performance Predictor & Budget Optimizer

**Classical Machine Learning (LightGBM) & Bayesian Multi-Armed Bandit (Thompson Sampling) for Programmatic Job Advertising**

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.7.0-brightgreen?style=for-the-badge&logo=lightgbm&logoColor=white)](https://lightgbm.readthedocs.io/)
[![TreeSHAP](https://img.shields.io/badge/TreeSHAP-Explainability-indigo?style=for-the-badge)](https://shap.readthedocs.io/)
[![Thompson Sampling](https://img.shields.io/badge/Bandit-Thompson%20Sampling-emerald?style=for-the-badge)](https://en.wikipedia.org/wiki/Thompson_sampling)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-11%2F11%20Passed-success?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)

<p align="center">
  <a href="#-screenshots-gallery">Screenshots</a> •
  <a href="#-key-measured-results-for-resume">Resume Numbers</a> •
  <a href="#-system-architecture">Architecture</a> •
  <a href="#-repository-structure">Structure</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-docs">Documentation</a>
</p>

</div>

---

## 📸 Screenshots Gallery

<div align="center">

### Executive Overview & Model Benchmarks
![Executive Overview Dashboard](screenshots/overview_dashboard.svg)

### Multi-Armed Bandit Budget Optimizer (+35.4% Lift)
![Bandit Budget Simulator](screenshots/budget_simulator.svg)

### Ad Performance Predictor & TreeSHAP Factor Waterfall
![Ad Predictor and TreeSHAP](screenshots/ad_predictor_shap.svg)

### Enterprise Authentication Portal
![Enterprise Login Portal](screenshots/enterprise_login.svg)

</div>

---

## 🎯 Key Measured Results (For Resume)

Empirically measured from held-out test split evaluation (2,000 postings) and 30-day multi-armed bandit simulation runs:

| Performance Dimension | Baseline / Benchmark | AdPilot (Our Model / Optimizer) | Measured Improvement |
| :--- | :--- | :--- | :--- |
| **Total Applications** *(for identical \$10,000 budget)* | 444 applications *(Naive Equal Split)* | **601 applications** *(Thompson Sampling)* | **+35.36% lift** *(+157 candidates)* |
| **Effective Cost-Per-Application (eCPA)** | \$22.51 / application | **\$16.64 / application** | **-$5.87 / app** (**-26.08% cost reduction**) |
| **Candidate Classification ROC-AUC** | 0.5000 *(Random Dummy)* | **0.8258** *(LightGBM Classifier)* | **+65.16% lift** *(vs 0.8235 Logistic)* |
| **Precision-Recall AUC (PR-AUC)** | 0.4000 | **0.7545** | **+88.6% lift** |
| **Apply Rate RMSE Error** | 0.0584 *(Dummy Mean)* | **0.0440** *(LightGBM Regressor)* | **24.66% error reduction** |
| **Apply Rate $R^2$ Variance Explained** | -0.0130 | **0.4260** | **+0.4390 jump** *(vs 0.3996 Ridge)* |
| **Salary Transparency Impact** *(EDA)* | 7.52% CVR *(withheld)* | **11.85% CVR** *(salary stated)* | **+57.5% candidate conversion lift** |
| **Remote Flexibility Impact** *(EDA)* | 9.41% CVR *(on-site only)* | **11.92% CVR** *(remote eligible)* | **+26.7% candidate conversion lift** |

### 💼 Recommended Resume Bullet
> *"Developed a programmatic recruitment ad predictor (LightGBM, TreeSHAP) and multi-armed bandit budget optimizer (Thompson Sampling) trained on 10k LinkedIn postings; achieved **0.8258 ROC-AUC** in applicant conversion prediction and **+35.4% more applications for the identical budget** with a **26.1% reduction in CPA (\$16.64 vs \$22.51)** compared to naive equal-split baselines."*

---

## 🏛️ System Architecture

```mermaid
graph TD
    A[Raw Job Postings Data<br/>Kaggle LinkedIn Schema] --> B[Data Cleaning & Feature Engineering<br/>26 Predictive Signals]
    B --> C[80/20 Train / Test Split]
    C --> D[Baseline Regressors & Classifiers<br/>Dummy Median, Ridge, Logistic]
    C --> E[LightGBM Gradient Boosted Trees]
    E --> F[Evaluation: RMSE 0.0440, ROC-AUC 0.8258]
    E --> G[TreeSHAP Attribution Engine<br/>Local Waterfall & Prescriptive Tips]
    
    H[Advertising Budget Pool] --> I[Multi-Armed Bandit Simulator]
    I --> J[Thompson Sampling Policy<br/>Beta-Bernoulli Posterior Sampling]
    I --> K[Equal Split Baseline]
    I --> L[Epsilon-Greedy & UCB1 Benchmarks]
    J --> M[Performance Delta: +35.4% Lift, -26.1% CPA]
    K --> M
    
    E --> N[FastAPI Backend Server<br/>Port 8000]
    G --> N
    I --> N
    
    N --> O[Next.js Client Dashboard<br/>Port 3001]
```

---

## 📁 Repository Structure

```text
├── client/                        # Next.js 16 + React + Tailwind CSS Dashboard
│   ├── src/
│   │   ├── app/page.tsx           # Single-page dashboard application
│   │   ├── components/            # Navbar, OverviewTab, PredictorTab, SimulatorTab, LoginPage
│   │   └── lib/api.ts             # Typed API client with offline benchmark fallback
│   ├── package.json
│   └── Dockerfile
├── docs/                          # Comprehensive Technical Documentation
│   ├── ARCHITECTURE.md            # LightGBM, TreeSHAP & Thompson Sampling math
│   ├── EVALUATION_METRICS.md      # Detailed benchmark tables & slice error analysis
│   └── API_DOCUMENTATION.md       # REST endpoints, schemas, and cURL examples
├── screenshots/                   # Visual UI and Architecture Showcase Previews
│   ├── overview_dashboard.svg     # Executive metrics and model comparisons
│   ├── budget_simulator.svg       # Multi-Armed Bandit trajectory curve
│   ├── ad_predictor_shap.svg      # Ad scorer and TreeSHAP waterfall
│   ├── enterprise_login.svg       # Enterprise authentication portal
│   └── README.md
├── server/                        # FastAPI Backend & Machine Learning Engine
│   ├── backend/                   # FastAPI app, schemas, and routes (auth, predict, simulate)
│   ├── src/                       # Data loader, model trainers, TreeSHAP explainer, bandit
│   ├── models/                    # Trained LightGBM artifacts (.joblib) & metadata
│   ├── reports/                   # Verified evaluation JSON logs and error analysis
│   ├── tests/                     # 11/11 automated unit and integration tests
│   ├── main.py                    # Server entrypoint
│   ├── requirements.txt           # Pinned Python dependencies
│   └── Dockerfile
├── .env.example                   # Environment configuration template
├── docker-compose.yml             # Multi-container orchestration
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.13 or 3.11+
- Node.js 18+ and npm

### 2. Start Backend Server
```bash
# Navigate to server directory
cd server

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests (11/11 passing)
pytest -v tests/

# Launch FastAPI backend
python main.py
# Server runs on: http://127.0.0.1:8000
# Interactive Swagger docs: http://127.0.0.1:8000/docs
```

### 3. Start Frontend Client
```bash
# In a new terminal, navigate to client directory
cd client

# Install packages
npm install

# Start Next.js development server
npm run dev
# Dashboard opens at: http://localhost:3000 (or http://localhost:3001)
```

### 4. 🐳 Run via Docker Compose
```bash
docker-compose up --build
```
- **Dashboard**: `http://localhost:3000`
- **FastAPI Documentation**: `http://localhost:8000/docs`

---

## 🔐 Demo Credentials for Login Page

| Profile Name | Role | Email | Password |
| :--- | :--- | :--- | :--- |
| **Sarah Chen** | Lead Talent Acquisition & Media Buyer (Joveo) | `recruiter@joveo.com` | `password123` |
| **Alex Mercer** | Programmatic Advertising Director | `admin@adopt.ai` | `password123` |
| **Guest Mode** | Reviewer Access | *1-Click Guest Access* | *None* |

---

## ⚖️ Data Origin & Methodology Disclaimer

- The job posting feature schema and behavioral engagement distributions are derived from the publicly available **LinkedIn Job Postings dataset on Kaggle**.
- Advertising channel cost-per-click (CPC) figures and channel-specific conversion dynamics are simulated for research, modeling, and technical demonstration purposes.
- This project **does not use, store, or claim access to proprietary client data from Joveo** or any commercial advertising partner.
