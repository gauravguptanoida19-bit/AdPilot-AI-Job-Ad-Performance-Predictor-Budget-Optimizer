"""Multi-Armed Bandit Recruitment Ad Budget Optimizer.

Simulates multiple recruitment advertising channels (job boards) with
differing Cost-Per-Click (CPC) and true conversion rates (apply rate).
Compares:
1. Thompson Sampling (Bayesian Beta-Bernoulli bandit)
2. Naive Equal Split
3. Epsilon-Greedy
4. Upper Confidence Bound (UCB1)
Demonstrates quantified business lift: "% more applications for the same budget".
"""

from __future__ import annotations
import os
import json
import random
from typing import Dict, List, Any, Tuple
import numpy as np

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")

DEFAULT_CHANNELS = [
    {
        "id": "linkedin_jobs",
        "name": "LinkedIn Jobs",
        "cpc": 2.80,
        "true_cvr": 0.095,
        "daily_capacity": 500,
        "description": "High intent professional network, higher CPC, high candidate qualification"
    },
    {
        "id": "indeed_sponsored",
        "name": "Indeed Sponsored",
        "cpc": 1.45,
        "true_cvr": 0.088,
        "daily_capacity": 1000,
        "description": "High volume job aggregator, balanced CPC and strong candidate throughput"
    },
    {
        "id": "ziprecruiter",
        "name": "ZipRecruiter",
        "cpc": 1.50,
        "true_cvr": 0.045,
        "daily_capacity": 700,
        "description": "Broad distribution network, moderate CPC but lower conversion rate"
    },
    {
        "id": "glassdoor",
        "name": "Glassdoor",
        "cpc": 2.35,
        "true_cvr": 0.068,
        "daily_capacity": 400,
        "description": "Company review seekers, high research intent, solid conversion"
    },
    {
        "id": "programmatic_aggregator",
        "name": "Programmatic Aggregator",
        "cpc": 0.80,
        "true_cvr": 0.055,
        "daily_capacity": 1400,
        "description": "High-volume programmatic ad exchange, lowest cost per applicant"
    },
    {
        "id": "niche_tech_board",
        "name": "Niche Tech Board",
        "cpc": 3.10,
        "true_cvr": 0.110,
        "daily_capacity": 250,
        "description": "Specialized developer community board, high CPC, high conversion"
    }
]


class ChannelEnvironment:
    """Simulates real-world recruitment advertising channel dynamics."""

    def __init__(self, channel_config: Dict[str, Any], seed: int | None = None):
        self.id = channel_config["id"]
        self.name = channel_config["name"]
        self.cpc = channel_config["cpc"]
        self.true_cvr = channel_config["true_cvr"]
        self.daily_capacity = channel_config["daily_capacity"]
        self.rng = np.random.default_rng(seed)

    def step(self, budget_allocated: float) -> Tuple[int, int, float]:
        """Simulate 1 day of ad spend on this channel.

        Returns (clicks, applications, actual_spend).
        """
        if budget_allocated <= 0.01:
            return 0, 0, 0.0

        # Clicks generated with slight CPC variance
        daily_cpc = max(0.20, self.cpc * self.rng.normal(1.0, 0.06))
        raw_clicks = budget_allocated / daily_cpc

        # Saturation curve: diminishing returns as budget approaches channel capacity
        saturation = 1.0 / (1.0 + (raw_clicks / max(self.daily_capacity, 100)) ** 1.8)
        effective_clicks = max(1, int(round(raw_clicks * min(1.0, saturation + 0.3))))
        actual_spend = round(effective_clicks * daily_cpc, 2)

        # Conversion: clicks to applications with day-to-day noise
        daily_cvr = max(0.005, min(0.35, self.true_cvr * self.rng.normal(1.0, 0.08)))
        applications = int(self.rng.binomial(n=effective_clicks, p=daily_cvr))

        return effective_clicks, applications, actual_spend


class BanditSimulator:
    """Runs comparative multi-round budget allocation simulations."""

    def __init__(
        self,
        channels: List[Dict[str, Any]] | None = None,
        total_budget: float = 10000.0,
        days: int = 30,
        seed: int = 42
    ):
        self.channel_configs = channels if channels is not None else DEFAULT_CHANNELS
        self.total_budget = total_budget
        self.days = days
        self.daily_budget = total_budget / max(1, days)
        self.seed = seed

    def run_simulation(self) -> Dict[str, Any]:
        """Run all strategies across the same timeline and return detailed comparisons."""
        np.random.seed(self.seed)
        random.seed(self.seed)

        strategies = ["thompson_sampling", "equal_split", "epsilon_greedy", "ucb1"]
        results = {}

        for strat in strategies:
            results[strat] = self._run_single_strategy(strat)

        # Quantify Business Lift (Thompson vs Equal Split)
        ts_apps = results["thompson_sampling"]["total_applications"]
        eq_apps = results["equal_split"]["total_applications"]
        ts_cpa = results["thompson_sampling"]["effective_cpa"]
        eq_cpa = results["equal_split"]["effective_cpa"]

        lift_pct = round(((ts_apps - eq_apps) / max(1, eq_apps)) * 100.0, 2)
        cpa_savings = round(eq_cpa - ts_cpa, 2)
        cpa_savings_pct = round((cpa_savings / max(0.01, eq_cpa)) * 100.0, 2)

        summary = {
            "simulation_parameters": {
                "total_budget": self.total_budget,
                "days": self.days,
                "daily_budget": round(self.daily_budget, 2),
                "channel_count": len(self.channel_configs)
            },
            "business_impact": {
                "application_lift_pct": lift_pct,
                "additional_applications": ts_apps - eq_apps,
                "cpa_savings_per_app": cpa_savings,
                "cpa_savings_pct": cpa_savings_pct,
                "headline": f"Thompson Sampling generated {lift_pct}% more applications for the identical ${self.total_budget:,.0f} budget (${ts_cpa:.2f} CPA vs ${eq_cpa:.2f} CPA)"
            },
            "strategy_comparisons": {
                strat: {
                    "total_budget_spent": results[strat]["total_spent"],
                    "total_applications": results[strat]["total_applications"],
                    "total_clicks": results[strat]["total_clicks"],
                    "effective_cpa": results[strat]["effective_cpa"],
                    "effective_cvr": results[strat]["effective_cvr"]
                }
                for strat in strategies
            },
            "detailed_trajectories": results
        }

        # Save to disk
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(os.path.join(REPORTS_DIR, "bandit_simulation_results.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary

    def _run_single_strategy(self, strategy: str) -> Dict[str, Any]:
        """Execute one simulation trajectory for a specific policy."""
        envs = [ChannelEnvironment(c, seed=self.seed + idx * 7) for idx, c in enumerate(self.channel_configs)]
        K = len(envs)

        # Bandit state: Beta prior parameters (alpha=successes/applies, beta=failures/non-applies)
        alphas = np.ones(K, dtype=float) * 2.0  # Weak uninformative prior
        betas = np.ones(K, dtype=float) * 25.0  # Anchored roughly at ~7% baseline CVR
        clicks_hist = np.zeros(K, dtype=int)
        applies_hist = np.zeros(K, dtype=int)
        spend_hist = np.zeros(K, dtype=float)

        daily_logs = []
        cumulative_apps = 0
        cumulative_spend = 0.0

        for day in range(1, self.days + 1):
            # 1. Decide Budget Allocation across K channels
            if strategy == "equal_split":
                allocations = np.ones(K) * (self.daily_budget / K)

            elif strategy == "thompson_sampling":
                # Sample posterior conversion rate for each channel
                sampled_cvrs = np.random.beta(alphas, betas)
                # Efficiency metric: expected applications per dollar = CVR / CPC
                expected_app_per_dollar = sampled_cvrs / np.array([e.cpc for e in envs])

                # Calibrate temperature to the scale of expected_app_per_dollar
                eff_std = np.std(expected_app_per_dollar)
                temp = max(0.005, eff_std * 0.75) if eff_std > 1e-4 else 0.008
                scaled_diff = (expected_app_per_dollar - np.max(expected_app_per_dollar)) / temp
                exp_weights = np.exp(np.clip(scaled_diff, -20, 0))
                weights = exp_weights / np.sum(exp_weights)

                # Ensure a realistic exploration floor (5% shared across all arms)
                weights = 0.95 * weights + 0.05 * (1.0 / K)
                allocations = weights * self.daily_budget

            elif strategy == "epsilon_greedy":
                if day <= 2:  # Warm-up exploration phase
                    allocations = np.ones(K) * (self.daily_budget / K)
                else:
                    epsilon = max(0.10, 0.40 - (day / self.days) * 0.30)  # Decaying epsilon
                    if np.random.random() < epsilon:
                        allocations = np.ones(K) * (self.daily_budget / K)
                    else:
                        empirical_cvr = applies_hist / np.maximum(clicks_hist, 1)
                        empirical_eff = empirical_cvr / np.array([e.cpc for e in envs])
                        best_k = int(np.argmax(empirical_eff))
                        allocations = np.zeros(K)
                        allocations[best_k] = self.daily_budget * 0.70
                        other_k = [k for k in range(K) if k != best_k]
                        for k in other_k:
                            allocations[k] = (self.daily_budget * 0.30) / max(1, len(other_k))

            elif strategy == "ucb1":
                if day <= 2:  # Warm-up exploration phase
                    allocations = np.ones(K) * (self.daily_budget / K)
                else:
                    total_rounds = max(K, np.sum(clicks_hist))
                    empirical_cvr = applies_hist / np.maximum(clicks_hist, 1)
                    bonus = np.sqrt(2.0 * np.log(total_rounds) / np.maximum(clicks_hist, 1))
                    ucb_scores = (empirical_cvr + bonus) / np.array([e.cpc for e in envs])
                    total_ucb = np.sum(ucb_scores)
                    if np.isnan(total_ucb) or total_ucb <= 0:
                        weights = np.ones(K) / K
                    else:
                        weights = ucb_scores / total_ucb
                    allocations = weights * self.daily_budget

            # 2. Step environment and record feedback
            day_clicks = 0
            day_applies = 0
            day_spend = 0.0
            day_channel_stats = []

            for k in range(K):
                budget_k = float(allocations[k])
                clicks_k, applies_k, spend_k = envs[k].step(budget_k)

                # Update state
                alphas[k] += applies_k
                betas[k] += max(0, clicks_k - applies_k)
                clicks_hist[k] += clicks_k
                applies_hist[k] += applies_k
                spend_hist[k] += spend_k

                day_clicks += clicks_k
                day_applies += applies_k
                day_spend += spend_k

                day_channel_stats.append({
                    "channel_id": envs[k].id,
                    "channel_name": envs[k].name,
                    "allocated_budget": round(budget_k, 2),
                    "spend": round(spend_k, 2),
                    "clicks": clicks_k,
                    "applications": applies_k,
                    "cpa": round(spend_k / max(1, applies_k), 2)
                })

            cumulative_apps += day_applies
            cumulative_spend += day_spend

            daily_logs.append({
                "day": day,
                "day_spend": round(day_spend, 2),
                "day_clicks": day_clicks,
                "day_applications": day_applies,
                "cumulative_spend": round(cumulative_spend, 2),
                "cumulative_applications": cumulative_apps,
                "day_cpa": round(day_spend / max(1, day_applies), 2),
                "channels": day_channel_stats
            })

        effective_cpa = round(cumulative_spend / max(1, cumulative_apps), 2)
        effective_cvr = round(cumulative_apps / max(1, int(np.sum(clicks_hist))), 4)

        return {
            "strategy": strategy,
            "total_spent": round(cumulative_spend, 2),
            "total_applications": cumulative_apps,
            "total_clicks": int(np.sum(clicks_hist)),
            "effective_cpa": effective_cpa,
            "effective_cvr": effective_cvr,
            "channel_totals": [
                {
                    "channel_id": envs[k].id,
                    "channel_name": envs[k].name,
                    "total_spend": round(float(spend_hist[k]), 2),
                    "total_clicks": int(clicks_hist[k]),
                    "total_applications": int(applies_hist[k]),
                    "observed_cpa": round(float(spend_hist[k]) / max(1, applies_hist[k]), 2),
                    "observed_cvr": round(applies_hist[k] / max(1, clicks_hist[k]), 4)
                }
                for k in range(K)
            ],
            "daily_logs": daily_logs
        }


if __name__ == "__main__":
    simulator = BanditSimulator(total_budget=10000.0, days=30)
    summary = simulator.run_simulation()
    print("=" * 60)
    print(summary["business_impact"]["headline"])
    print(f"Equal Split CPA: ${summary['strategy_comparisons']['equal_split']['effective_cpa']}")
    print(f"Thompson Sampling CPA: ${summary['strategy_comparisons']['thompson_sampling']['effective_cpa']}")
    print(f"Lift: +{summary['business_impact']['application_lift_pct']}% applications")
    print("=" * 60)
