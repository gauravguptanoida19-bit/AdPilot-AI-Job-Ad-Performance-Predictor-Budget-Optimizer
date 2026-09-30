# Live Production & Deployment Guide

## 🌐 Live Production Website
The AdPilot platform is deployed live and publicly accessible at:
👉 **[https://gauravguptanoida19-bit.github.io/AdPilot-AI-Job-Ad-Performance-Predictor-Budget-Optimizer/](https://gauravguptanoida19-bit.github.io/AdPilot-AI-Job-Ad-Performance-Predictor-Budget-Optimizer/)**

### Key Platform Features Live in Browser:
- **Executive Overview Dashboard**: High-level KPIs, model benchmark scores (RMSE, R², ROC-AUC, PR-AUC).
- **Interactive Ad Scorer & TreeSHAP Waterfall**: Real-time feature attribution explaining why ads perform well or poorly.
- **Bayesian Multi-Armed Bandit Simulator**: 30-day Thompson Sampling vs Equal Split budget allocation simulation (+35.4% lift, -26.1% eCPA).
- **Channel Economics Matrix**: In-depth breakdown across LinkedIn, Indeed, ZipRecruiter, Glassdoor, Programmatic DSP, and Niche Tech Boards.
- **Enterprise Authentication Portal**: 1-click credential switching for recruiters and ad managers.

---

## 🚀 Local Development Setup

### Backend (FastAPI)
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start FastAPI server
$env:PYTHONPATH="server"; uvicorn server.main:app --reload --host 127.0.0.1 --port 8000
```
- **API URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`

### Frontend (Next.js)
```bash
cd client
npm install
npm run dev
```
- **Local Dashboard**: `http://localhost:3000` (or `http://localhost:3001`)

---

## ⚙️ Automated CI/CD (GitHub Pages)
The client frontend is built via GitHub Actions (`.github/workflows/deploy.yml`) on every push to `main`:
1. Triggers Next.js static HTML/CSS/JS export (`output: 'export'`).
2. Generates optimized bundle into `client/out`.
3. Injects `.nojekyll` to preserve `_next` asset delivery.
4. Deploys directly to GitHub Pages hosting environment.
