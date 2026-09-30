"use client";

import React, { useState } from "react";
import { Sparkles, ArrowUpRight, ArrowDownRight, Lightbulb, CheckCircle2, AlertTriangle, Info, Play, RefreshCw } from "lucide-react";
import { JobPostingInput, PredictionResponse, predictAdPerformance } from "../lib/api";

const PRESETS: Array<{ label: string; data: JobPostingInput }> = [
  {
    label: "Lead Systems Engineer (High Performer)",
    data: {
      title: "Lead Systems Engineer",
      company_name: "Apex Tech Systems",
      description: `About the Role:\nWe are looking for an experienced Lead Systems Engineer to architect reliable distributed cloud platforms at Apex Tech Systems.\n\nKey Responsibilities:\n- Architect high-throughput microservices infrastructure across multi-region AWS.\n- Drive Kubernetes and Docker container deployment automation with CI/CD.\n- Mentor senior and mid-level software engineers.\n- Partner with product managers on reliability SLAs and performance bottlenecks.\n\nQualifications & Requirements:\n- 6+ years experience in systems engineering and cloud platforms.\n- Strong proficiency in Python, Go, Docker, Kubernetes, AWS.\n- Demonstrated experience optimizing distributed databases and SQL queries.\n- Excellent communication skills and bias for action.\n\nWhat We Offer:\n- Competitive salary $160,000 - $200,000 with annual equity grant.\n- Comprehensive medical, dental, and vision insurance.\n- 401(k) matching up to 5% with immediate vesting.\n- Generous flexible PTO and $2,000 yearly learning stipend.`,
      min_salary: 160000,
      max_salary: 200000,
      pay_period: "YEARLY",
      location: "Remote",
      formatted_work_type: "Full-time",
      formatted_experience_level: "Mid-Senior level",
      skills: "Python, Kubernetes, AWS, Docker, Microservices, SQL",
      sponsored: true
    }
  },
  {
    label: "Account Executive (Vague / Low CVR)",
    data: {
      title: "Account Executive",
      company_name: "Nexus Digital Partners",
      description: `We are looking for a hungry Account Executive to hunt new logos in B2B tech.\nMust be energetic, competitive, and willing to dial 80 calls per day.\nFast-paced environment with unlimited earning potential.`,
      min_salary: null,
      max_salary: null,
      pay_period: "YEARLY",
      location: "New York, NY",
      formatted_work_type: "Full-time",
      formatted_experience_level: "Associate",
      skills: "Cold Calling, Sales",
      sponsored: false
    }
  },
  {
    label: "Data Scientist (On-site)",
    data: {
      title: "Data Scientist",
      company_name: "Vanguard Financial Analytics",
      description: `Position: Data Scientist\nLocation: Boston, MA\n\nResponsibilities:\n- Build predictive machine learning models for risk evaluation.\n- Analyze large datasets with Pandas and SQL.\n- Partner with stakeholders to deploy models into production.\n\nRequirements:\n- 3+ years experience with Scikit-Learn and LightGBM.\n- Master's in Statistics or Computer Science.\n\nCompensation:\n- Base salary $115,000 - $140,000.`,
      min_salary: 115000,
      max_salary: 140000,
      pay_period: "YEARLY",
      location: "Boston, MA",
      formatted_work_type: "Full-time",
      formatted_experience_level: "Mid-Senior level",
      skills: "Python, SQL, Machine Learning, Scikit-Learn",
      sponsored: false
    }
  },
  {
    label: "Customer Support Rep (Hourly)",
    data: {
      title: "Customer Support Representative",
      company_name: "BlueSky Retail Group",
      description: `Join our support team helping thousands of customers daily.\n\nWhat you'll do:\n- Answer customer inquiries via Zendesk and chat.\n- Troubleshoot order issues.\n- Maintain high satisfaction ratings.\n\nRequirements:\n- Excellent communication skills.\n- Shift flexibility.`,
      min_salary: 22,
      max_salary: 26,
      pay_period: "HOURLY",
      location: "Remote",
      formatted_work_type: "Full-time",
      formatted_experience_level: "Entry level",
      skills: "Zendesk, Customer Service",
      sponsored: true
    }
  }
];

export function PredictorTab() {
  const [formData, setFormData] = useState<JobPostingInput>(PRESETS[0].data);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);

  const descLength = formData.description?.length || 0;
  const wordCount = formData.description ? formData.description.split(/\s+/).filter(Boolean).length : 0;
  const bulletCount = (formData.description?.match(/(?:^|\n)\s*[-*•–]\s+/g) || []).length;

  const handlePredict = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const res = await predictAdPerformance(formData);
      setResult(res);
    } catch (err) {
      console.error("Prediction error:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset: typeof PRESETS[0]) => {
    setFormData(preset.data);
    setResult(null);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header & Preset Switchers */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              Recruitment Ad Performance Scorer & Explainer
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Enter job posting details to predict candidate apply rate, explain factors using TreeSHAP, and receive prescriptive hiring tips.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400 font-medium mr-1">Quick Presets:</span>
            {PRESETS.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => loadPreset(p)}
                className="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
              >
                {p.label.split(" ")[0]} {p.label.split(" ")[1]}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Form Column (7 cols) */}
        <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-2xl p-6">
          <form onSubmit={handlePredict} className="space-y-5">
            {/* Title & Company */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Job Title *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g. Senior Software Engineer"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  value={formData.company_name || ""}
                  onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                  placeholder="e.g. Apex Tech Systems"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            {/* Location & Remote Toggle */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Location *
                </label>
                <input
                  type="text"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="e.g. San Francisco, CA or Remote"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Workplace Type
                </label>
                <select
                  value={formData.location.toLowerCase().includes("remote") ? "Remote" : "Onsite/Hybrid"}
                  onChange={(e) => {
                    const isRem = e.target.value === "Remote";
                    setFormData({
                      ...formData,
                      location: isRem ? "Remote" : (formData.location === "Remote" ? "San Francisco, CA" : formData.location)
                    });
                  }}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Remote">Remote Eligible</option>
                  <option value="Onsite/Hybrid">Onsite / Hybrid</option>
                </select>
              </div>
            </div>

            {/* Experience Level & Employment Type */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Experience Level
                </label>
                <select
                  value={formData.formatted_experience_level}
                  onChange={(e) => setFormData({ ...formData, formatted_experience_level: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Internship">Internship</option>
                  <option value="Entry level">Entry level</option>
                  <option value="Associate">Associate</option>
                  <option value="Mid-Senior level">Mid-Senior level</option>
                  <option value="Director">Director</option>
                  <option value="Executive">Executive</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Employment Type
                </label>
                <select
                  value={formData.formatted_work_type}
                  onChange={(e) => setFormData({ ...formData, formatted_work_type: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>
            </div>

            {/* Salary Range & Pay Period */}
            <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Compensation Transparency (Top SHAP Feature)
                </span>
                <button
                  type="button"
                  onClick={() => {
                    if (formData.min_salary || formData.max_salary) {
                      setFormData({ ...formData, min_salary: null, max_salary: null });
                    } else {
                      setFormData({ ...formData, min_salary: 120000, max_salary: 150000 });
                    }
                  }}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  {formData.min_salary || formData.max_salary ? "Clear Salary (Test Missing)" : "Add Salary"}
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Min Salary</label>
                  <input
                    type="number"
                    value={formData.min_salary ?? ""}
                    onChange={(e) => setFormData({ ...formData, min_salary: e.target.value ? Number(e.target.value) : null })}
                    placeholder="Optional (e.g. 130000)"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Max Salary</label>
                  <input
                    type="number"
                    value={formData.max_salary ?? ""}
                    onChange={(e) => setFormData({ ...formData, max_salary: e.target.value ? Number(e.target.value) : null })}
                    placeholder="Optional (e.g. 170000)"
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Pay Period</label>
                  <select
                    value={formData.pay_period || "YEARLY"}
                    onChange={(e) => setFormData({ ...formData, pay_period: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="YEARLY">Yearly (USD)</option>
                    <option value="HOURLY">Hourly (USD)</option>
                    <option value="MONTHLY">Monthly (USD)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Skills */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Required Skills (Comma-separated)
              </label>
              <input
                type="text"
                value={formData.skills || ""}
                onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                placeholder="e.g. Python, SQL, Docker, React, AWS"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Job Description Textarea */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Job Description Text *
                </label>
                <div className="text-xs text-slate-400 space-x-2 font-mono">
                  <span>{descLength} chars</span>
                  <span>•</span>
                  <span>{wordCount} words</span>
                  <span>•</span>
                  <span className={bulletCount >= 3 ? "text-emerald-400" : "text-amber-400"}>
                    {bulletCount} bullets
                  </span>
                </div>
              </div>
              <textarea
                rows={7}
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Paste complete job description here..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Computing LightGBM Predictions & TreeSHAP...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  Score Job Posting & Generate TreeSHAP Breakdown
                </>
              )}
            </button>
          </form>
        </div>

        {/* Results & SHAP Explanations Column (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {result ? (
            <div className="space-y-6 animate-fadeIn">
              {/* Prediction Score Card */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">
                    Predicted Ad Performance
                  </span>
                  <span className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                    result.is_high_converting
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                      : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                  }`}>
                    {result.is_high_converting ? "Top Tier High Converter" : "Moderate / Average CVR"}
                  </span>
                </div>

                <div className="flex items-baseline gap-3">
                  <span className="text-4xl sm:text-5xl font-extrabold text-white">
                    {result.predicted_apply_rate_pct}%
                  </span>
                  <span className="text-sm text-slate-400">apply-to-view rate</span>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 block">Expected Yield</span>
                    <span className="font-semibold text-white text-sm">
                      ~{result.expected_applications_per_100_views} applies / 100 views
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">High Performer Likelihood</span>
                    <span className="font-semibold text-indigo-400 text-sm">
                      {(result.high_conversion_probability * 100).toFixed(1)}% probability
                    </span>
                  </div>
                </div>
              </div>

              {/* TreeSHAP Local Drivers Card */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white">TreeSHAP Factor Breakdown</h3>
                    <p className="text-xs text-slate-400">
                      Baseline: {(result.baseline_apply_rate * 100).toFixed(1)}% | Net Impact: {result.total_shap_impact > 0 ? "+" : ""}{(result.total_shap_impact * 100).toFixed(1)}%
                    </p>
                  </div>
                  <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
                    TreeSHAP
                  </span>
                </div>

                {/* Positive Drivers */}
                <div className="space-y-2 mt-4">
                  <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                    <ArrowUpRight className="w-3.5 h-3.5" /> Positive Conversion Boosters
                  </span>
                  {result.top_positive_drivers.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No significant positive drivers detected.</p>
                  ) : (
                    result.top_positive_drivers.map((d, i) => (
                      <div key={i} className="flex items-center justify-between text-xs bg-slate-950/60 p-2 rounded border border-slate-800/80">
                        <span className="font-mono text-slate-300 truncate max-w-[200px]">
                          {d.feature.replace(/_/g, " ")}
                        </span>
                        <span className="font-mono text-emerald-400 font-semibold">
                          +{(d.shap_impact * 100).toFixed(2)}%
                        </span>
                      </div>
                    ))
                  )}
                </div>

                {/* Negative Drags */}
                <div className="space-y-2 mt-5">
                  <span className="text-xs font-semibold text-rose-400 flex items-center gap-1">
                    <ArrowDownRight className="w-3.5 h-3.5" /> Conversion Drags
                  </span>
                  {result.top_negative_drivers.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No drag factors found.</p>
                  ) : (
                    result.top_negative_drivers.map((d, i) => (
                      <div key={i} className="flex items-center justify-between text-xs bg-slate-950/60 p-2 rounded border border-slate-800/80">
                        <span className="font-mono text-slate-300 truncate max-w-[200px]">
                          {d.feature.replace(/_/g, " ")}
                        </span>
                        <span className="font-mono text-rose-400 font-semibold">
                          {(d.shap_impact * 100).toFixed(2)}%
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Actionable Recommendations */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-amber-400" />
                  Prescriptive Optimization Advice
                </h3>
                <div className="space-y-3">
                  {result.actionable_recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white flex items-center gap-1.5">
                          {rec.severity === "HIGH" && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
                          {rec.severity === "MEDIUM" && <Info className="w-3.5 h-3.5 text-amber-400" />}
                          {rec.severity === "LOW" && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />}
                          {rec.category}
                        </span>
                        <span className="text-emerald-400 font-mono text-[11px] font-medium">
                          {rec.impact}
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed">{rec.recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/40 border border-slate-800/80 border-dashed rounded-2xl p-10 text-center flex flex-col items-center justify-center min-h-[400px]">
              <Sparkles className="w-10 h-10 text-indigo-400/40 mb-3" />
              <h4 className="text-base font-semibold text-slate-300">Ready to Evaluate Ad</h4>
              <p className="text-xs text-slate-400 max-w-xs mt-1">
                Select a preset or enter your custom posting parameters, then click "Score Job Posting" to compute live LightGBM and TreeSHAP metrics.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
