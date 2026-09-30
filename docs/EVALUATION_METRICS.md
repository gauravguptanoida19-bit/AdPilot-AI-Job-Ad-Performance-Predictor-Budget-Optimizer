# Empirical Evaluation Metrics & Benchmark Comparison

This document details the exact empirical findings measured on the held-out test split (2,000 postings) and episodic multi-armed bandit simulation runs.

---

## 1. Candidate Application Rate Prediction (Regression)

| Model | RMSE (Error) ↓ | MAE ↓ | $R^2$ Variance Explained ↑ | Pearson $r$ ↑ |
| :--- | :--- | :--- | :--- | :--- |
| **Dummy Baseline (Median)** | 0.0584 | 0.0441 | -0.0130 | 0.0000 |
| **Ridge Regression (Linear)** | 0.0450 | 0.0335 | 0.3996 | 0.6324 |
| **LightGBM Regressor (Ours)** | **0.0440** | **0.0325** | **0.4260** | **0.6528** |

- **RMSE Reduction vs Dummy Baseline**: **24.66%**
- **$R^2$ Gain vs Dummy Baseline**: **+0.4390**

---

## 2. High-Converting Ad Classifier (Classification)

| Model | ROC-AUC ↑ | PR-AUC ↑ | F1 Score ↑ | Accuracy ↑ |
| :--- | :--- | :--- | :--- | :--- |
| **Dummy Baseline** | 0.5000 | 0.4000 | 0.0000 | 60.0% |
| **Logistic Regression** | 0.8235 | 0.7577 | 0.6649 | 75.1% |
| **LightGBM Classifier (Ours)** | **0.8258** | **0.7545** | **0.6707** | **75.4%** |

- **ROC-AUC Improvement vs Random**: **+65.16%**

---

## 3. Multi-Armed Bandit Budget Optimizer Simulation (\$10,000 Budget over 30 Days)

| Allocation Policy | Total Budget Spent | Total Applications | Total Clicks | Effective CPA ↓ | Application Lift vs Equal Split |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Naive Equal Split** | \$9,994.19 | 444 | 6,217 | \$22.51 | Baseline (0.0%) |
| **UCB1 Benchmark** | \$10,007.85 | 473 | 6,806 | \$21.16 | +6.53% |
| **Epsilon-Greedy Benchmark** | \$9,982.47 | 557 | 9,117 | \$17.92 | +25.45% |
| **Thompson Sampling (Ours)** | **\$10,000.30** | **601** | **9,247** | **\$16.64** | **+35.36%** (+157 candidates) |

### Business Lift Summary
- **Lift**: **+35.36% more applications** for the exact same budget.
- **Cost Reduction**: **-$5.87 per application** (**-26.08% cost savings**).

---

## 4. Subgroup Slice Error Analysis

| Slice Category | Sample Count | Slice MAE | Slice RMSE |
| :--- | :--- | :--- | :--- |
| **Salary Specified** | 1,300 | 0.0341 | 0.0464 |
| **Salary Omitted** | 700 | 0.0297 | 0.0392 |
| **Remote Roles** | 674 | 0.0374 | 0.0515 |
| **Onsite Roles** | 1,326 | 0.0300 | 0.0396 |
