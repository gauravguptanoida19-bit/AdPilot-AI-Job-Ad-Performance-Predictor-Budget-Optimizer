"use client";

import React, { useState, useEffect } from "react";
import { Cpu, DollarSign, TrendingUp, BarChart3, RefreshCw, CheckCircle2, Sliders, ShieldCheck } from "lucide-react";
import { SimulationResponse, runSimulation, DEFAULT_CHANNELS_LIST, ChannelConfig } from "../lib/api";

export function SimulatorTab() {
  const [totalBudget, setTotalBudget] = useState(10000);
  const [days, setDays] = useState(30);
  const [channels, setChannels] = useState<ChannelConfig[]>(DEFAULT_CHANNELS_LIST);
  const [loading, setLoading] = useState(false);
  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);

  // Auto-run baseline simulation on mount
  useEffect(() => {
    executeSimulation();
  }, []);

  const executeSimulation = async () => {
    setLoading(true);
    try {
      const res = await runSimulation({
        total_budget: totalBudget,
        days: days,
        channels: channels,
        seed: 42
      });
      setSimResult(res);
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const tsTraj = simResult?.detailed_trajectories?.thompson_sampling?.daily_logs || [];
  const eqTraj = simResult?.detailed_trajectories?.equal_split?.daily_logs || [];
  const egTraj = simResult?.detailed_trajectories?.epsilon_greedy?.daily_logs || [];
  const ucbTraj = simResult?.detailed_trajectories?.ucb1?.daily_logs || [];

  const maxApps = Math.max(
    ...tsTraj.map((d) => d.cumulative_applications),
    ...eqTraj.map((d) => d.cumulative_applications),
    1
  );

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Banner */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-indigo-400" />
              Multi-Armed Bandit Budget Optimizer Simulator
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Simulates real-time programmatic ad distribution across 6 recruitment channels. A Bayesian Multi-Armed Bandit
              (Thompson Sampling) continuously estimates conversion rates and reallocates a fixed budget toward high-efficiency channels,
              beating static equal splits.
            </p>
          </div>

          <button
            onClick={executeSimulation}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold text-sm shadow-lg shadow-emerald-600/20 transition disabled:opacity-50 shrink-0"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Simulating Episodes...
              </>
            ) : (
              <>
                <TrendingUp className="w-4 h-4" />
                Run Bandit Simulation
              </>
            )}
          </button>
        </div>

        {/* Sliders & Configuration */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-6 pt-6 border-t border-slate-800">
          <div>
            <div className="flex justify-between items-center text-xs text-slate-300 mb-2">
              <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Total Campaign Budget
              </span>
              <span className="font-mono text-emerald-400 font-bold text-sm">
                ${totalBudget.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min={1000}
              max={50000}
              step={500}
              value={totalBudget}
              onChange={(e) => setTotalBudget(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-slate-500 mt-1 font-mono">
              <span>$1,000</span>
              <span>$25,000</span>
              <span>$50,000</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center text-xs text-slate-300 mb-2">
              <span className="font-semibold uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-3.5 h-3.5 text-indigo-400" /> Simulation Duration
              </span>
              <span className="font-mono text-indigo-400 font-bold text-sm">
                {days} Days (${(totalBudget / days).toFixed(0)}/day)
              </span>
            </div>
            <input
              type="range"
              min={7}
              max={60}
              step={1}
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full accent-indigo-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[11px] text-slate-500 mt-1 font-mono">
              <span>7 Days</span>
              <span>30 Days</span>
              <span>60 Days</span>
            </div>
          </div>
        </div>
      </div>

      {/* Simulated Channels Badges */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Simulated Ad Channels & Market Dynamics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {channels.map((c) => (
            <div key={c.id} className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-xs space-y-1">
              <div className="font-semibold text-white truncate">{c.name}</div>
              <div className="flex justify-between text-slate-400 font-mono text-[11px]">
                <span>CPC:</span>
                <span className="text-slate-200">${c.cpc.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-400 font-mono text-[11px]">
                <span>Base CVR:</span>
                <span className="text-indigo-400 font-medium">{(c.true_cvr * 100).toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hero Lift Banner */}
      {simResult && (
        <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-indigo-950/40 border border-emerald-500/30 rounded-2xl p-6 sm:p-8 animate-fadeIn">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <ShieldCheck className="w-4 h-4" /> Quantified Business Value
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white leading-tight">
            {simResult.business_impact.headline}
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block">Total Lift</span>
              <span className="text-2xl sm:text-3xl font-bold text-emerald-400">
                +{simResult.business_impact.application_lift_pct}%
              </span>
              <span className="text-xs text-slate-400 block mt-1">
                +{simResult.business_impact.additional_applications} candidates
              </span>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block">Thompson Sampling CPA</span>
              <span className="text-2xl sm:text-3xl font-bold text-white">
                ${simResult.strategy_comparisons.thompson_sampling.effective_cpa.toFixed(2)}
              </span>
              <span className="text-xs text-emerald-400 block mt-1">
                -${simResult.business_impact.cpa_savings_per_app.toFixed(2)} (-{simResult.business_impact.cpa_savings_pct}%)
              </span>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block">Equal Split Baseline CPA</span>
              <span className="text-2xl sm:text-3xl font-bold text-slate-400">
                ${simResult.strategy_comparisons.equal_split.effective_cpa.toFixed(2)}
              </span>
              <span className="text-xs text-slate-500 block mt-1">Naive static 1/K allocation</span>
            </div>

            <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
              <span className="text-xs text-slate-400 block">Identical Spend</span>
              <span className="text-2xl sm:text-3xl font-bold text-white font-mono">
                ${simResult.strategy_comparisons.thompson_sampling.total_budget_spent.toLocaleString()}
              </span>
              <span className="text-xs text-slate-400 block mt-1">Over {days} days</span>
            </div>
          </div>
        </div>
      )}

      {/* SVG Interactive Chart: Cumulative Applications Over Time */}
      {simResult && tsTraj.length > 0 && (
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-400" />
                Cumulative Applications Trajectory (Day 1 to {days})
              </h3>
              <p className="text-xs text-slate-400">
                Notice how Thompson Sampling accelerates as the posterior distribution concentrates on high-efficiency channels.
              </p>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap items-center gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-3 h-1 rounded bg-emerald-400" /> Thompson Sampling (Bayesian)
              </span>
              <span className="flex items-center gap-1.5 text-blue-400">
                <span className="w-3 h-1 rounded bg-blue-400" /> Epsilon-Greedy
              </span>
              <span className="flex items-center gap-1.5 text-purple-400">
                <span className="w-3 h-1 rounded bg-purple-400" /> UCB1
              </span>
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-3 h-1 rounded bg-slate-500 stroke-dashed" /> Naive Equal Split
              </span>
            </div>
          </div>

          {/* SVG Line Chart */}
          <div className="w-full h-72 sm:h-80 relative">
            <svg className="w-full h-full" viewBox="0 0 800 300" preserveAspectRatio="none">
              {/* Background Grid Lines */}
              {[0, 75, 150, 225, 300].map((y, i) => (
                <line key={i} x1="40" y1={y} x2="790" y2={y} stroke="#1e293b" strokeDasharray="3 3" />
              ))}

              {/* Line: Equal Split */}
              <polyline
                fill="none"
                stroke="#64748b"
                strokeWidth="2.5"
                strokeDasharray="4 4"
                points={eqTraj.map((d, i) => {
                  const x = 40 + (i / (days - 1)) * 740;
                  const y = 290 - (d.cumulative_applications / maxApps) * 260;
                  return `${x},${y}`;
                }).join(" ")}
              />

              {/* Line: UCB1 */}
              <polyline
                fill="none"
                stroke="#a855f7"
                strokeWidth="2"
                points={ucbTraj.map((d, i) => {
                  const x = 40 + (i / (days - 1)) * 740;
                  const y = 290 - (d.cumulative_applications / maxApps) * 260;
                  return `${x},${y}`;
                }).join(" ")}
              />

              {/* Line: Epsilon Greedy */}
              <polyline
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2"
                points={egTraj.map((d, i) => {
                  const x = 40 + (i / (days - 1)) * 740;
                  const y = 290 - (d.cumulative_applications / maxApps) * 260;
                  return `${x},${y}`;
                }).join(" ")}
              />

              {/* Line: Thompson Sampling (Highlight) */}
              <polyline
                fill="none"
                stroke="#10b981"
                strokeWidth="3.5"
                points={tsTraj.map((d, i) => {
                  const x = 40 + (i / (days - 1)) * 740;
                  const y = 290 - (d.cumulative_applications / maxApps) * 260;
                  return `${x},${y}`;
                }).join(" ")}
              />
            </svg>

            {/* End Point Badges */}
            <div className="absolute right-2 top-2 text-xs space-y-1 bg-slate-950/80 p-2.5 rounded-lg border border-slate-800">
              <div className="text-emerald-400 font-bold font-mono">
                Thompson: {simResult.strategy_comparisons.thompson_sampling.total_applications} apps
              </div>
              <div className="text-blue-400 font-mono text-[11px]">
                Eps-Greedy: {simResult.strategy_comparisons.epsilon_greedy.total_applications} apps
              </div>
              <div className="text-purple-400 font-mono text-[11px]">
                UCB1: {simResult.strategy_comparisons.ucb1.total_applications} apps
              </div>
              <div className="text-slate-400 font-mono text-[11px]">
                Equal Split: {simResult.strategy_comparisons.equal_split.total_applications} apps
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Channel Totals Breakdown Table */}
      {simResult && (
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
          <h3 className="text-base font-semibold text-white mb-4">
            Thompson Sampling Channel Allocation & Empirical Returns
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/60 text-slate-300">
                <tr>
                  <th className="py-2.5 px-3 rounded-l">Channel Name</th>
                  <th className="py-2.5 px-3">Total Spend ($)</th>
                  <th className="py-2.5 px-3">Clicks Generated</th>
                  <th className="py-2.5 px-3">Total Applications</th>
                  <th className="py-2.5 px-3">Observed CVR</th>
                  <th className="py-2.5 px-3 rounded-r">Effective CPA ($)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {simResult.detailed_trajectories.thompson_sampling.channel_totals.map((ch) => (
                  <tr key={ch.channel_id} className="hover:bg-slate-800/30">
                    <td className="py-3 px-3 font-semibold text-white">{ch.channel_name}</td>
                    <td className="py-3 px-3 font-mono">${ch.total_spend.toLocaleString()}</td>
                    <td className="py-3 px-3 font-mono">{ch.total_clicks.toLocaleString()}</td>
                    <td className="py-3 px-3 font-mono text-emerald-400 font-bold">{ch.total_applications}</td>
                    <td className="py-3 px-3 font-mono">{(ch.observed_cvr * 100).toFixed(2)}%</td>
                    <td className="py-3 px-3 font-mono font-semibold">${ch.observed_cpa.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
