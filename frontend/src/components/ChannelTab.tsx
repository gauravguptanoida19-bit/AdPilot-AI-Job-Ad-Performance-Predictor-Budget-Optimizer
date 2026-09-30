"use client";

import React from "react";
import { BookOpen, Layers, ShieldCheck, Target, Zap, DollarSign } from "lucide-react";
import { DEFAULT_CHANNELS_LIST } from "../lib/api";

export function ChannelTab() {
  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* Introduction */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8">
        <div className="flex items-center gap-2 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <BookOpen className="w-4 h-4" /> Domain Background & Mathematical Formulation
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white">
          Programmatic Job Advertising & Real-Time Bidding (RTB)
        </h2>
        <p className="text-slate-300 text-sm mt-3 leading-relaxed">
          Modern recruitment advertising relies on algorithmic media buying across fragmented channels.
          Rather than buying static 30-day job slots on a single board, programmatic platforms like Joveo dynamically distribute
          employer budgets across hundreds of job sites in real-time, bidding aggressively on high-converting candidate segments
          and throttling spend when targets are met or channels saturate.
        </p>
      </div>

      {/* 2-Column Core Architecture */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Component 1: Performance Predictor */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Target className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">1. Classical ML & TreeSHAP</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            A gradient boosted decision tree (LightGBM) trained on 10,000 real-world job posting records predicting applicant engagement
            (<span className="text-slate-200 font-mono">apply_rate = applies / views</span>).
          </p>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 font-mono text-xs text-slate-300">
            f(x) = &phi;<sub>0</sub> + &sum; &phi;<sub>i</sub>(x)
          </div>
          <p className="text-xs text-slate-400">
            Native TreeSHAP decomposes predictions into exact feature attributions, explaining whether missing salary, excessive length,
            or seniority dragged down performance.
          </p>
        </div>

        {/* Component 2: Multi-Armed Bandit */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="text-base font-semibold text-white">2. Thompson Sampling Bandit</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            A Bayesian Multi-Armed Bandit allocates daily budget <span className="text-slate-200 font-mono">B<sub>t</sub></span> across K advertising channels.
            Each arm maintains a Beta posterior distribution over its conversion rate:
          </p>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 font-mono text-xs text-slate-300">
            p<sub>k</sub> ~ Beta(&alpha;<sub>k</sub> + applies, &beta;<sub>k</sub> + clicks - applies)
          </div>
          <p className="text-xs text-slate-400">
            By sampling from the posterior and weighting by cost-efficiency (sampled CVR / CPC), Thompson Sampling achieves the theoretical
            optimal balance between exploration and exploitation.
          </p>
        </div>
      </div>

      {/* Channel Economics Profiles */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
        <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          Advertising Channels Modeled in Simulation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DEFAULT_CHANNELS_LIST.map((c) => (
            <div key={c.id} className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl text-xs space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-white text-sm">{c.name}</span>
                <span className="text-slate-400 font-mono">${c.cpc.toFixed(2)} CPC</span>
              </div>
              <p className="text-slate-400">{c.description}</p>
              <div className="flex items-center gap-4 text-[11px] text-slate-500 pt-2 border-t border-slate-800/80">
                <span>Baseline CVR: <strong className="text-indigo-400">{(c.true_cvr * 100).toFixed(1)}%</strong></span>
                <span>Daily Capacity: <strong className="text-slate-300">{c.daily_capacity} clicks</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Academic & Professional Disclaimer */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 text-xs text-slate-400 space-y-2">
        <div className="flex items-center gap-2 text-slate-200 font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Data Origin & Methodology Disclaimer
        </div>
        <p className="leading-relaxed">
          The job posting feature schema and behavioral engagement distributions are derived from the publicly available{" "}
          <strong>LinkedIn Job Postings dataset on Kaggle</strong>. Advertising channel cost-per-click (CPC) figures and
          channel-specific conversion dynamics are simulated for research, modeling, and demonstration purposes.
          This project does not use, store, or claim access to proprietary client data from Joveo or any commercial advertising partner.
        </p>
      </div>
    </div>
  );
}
