"use client";

import React, { useState } from "react";
import { Sparkles, Lock, Mail, Eye, EyeOff, ShieldCheck, ArrowRight, UserCheck, Zap, AlertCircle } from "lucide-react";
import { loginUser, UserProfile } from "../lib/api";

interface LoginPageProps {
  onLoginSuccess: (user: UserProfile) => void;
  onExploreAsGuest: () => void;
}

export function LoginPage({ onLoginSuccess, onExploreAsGuest }: LoginPageProps) {
  const [email, setEmail] = useState("recruiter@joveo.com");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await loginUser(email, password);
      onLoginSuccess(res.user);
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Try demo password: password123");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemo = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword("password123");
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background glowing gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-indigo-600/10 via-purple-600/10 to-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md z-10">
        {/* App Logo */}
        <div className="flex items-center justify-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 via-blue-500 to-emerald-400 flex items-center justify-center shadow-xl shadow-indigo-500/25">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">AdOpt Portal</h1>
            <span className="text-[11px] font-medium text-indigo-400 tracking-wider uppercase block">
              Programmatic Recruitment Intelligence
            </span>
          </div>
        </div>

        <h2 className="mt-6 text-center text-lg font-semibold text-slate-200">
          Sign in to your enterprise advertising suite
        </h2>
        <p className="mt-1 text-center text-xs text-slate-400">
          Predict job ad performance and optimize multi-channel recruitment bidding
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md z-10 px-4 sm:px-0">
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-md space-y-6">
          {/* Quick Demo Credentials */}
          <div className="p-3.5 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-300">
              <span className="font-semibold text-indigo-400 flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5" /> 1-Click Demo Profiles
              </span>
              <span className="text-[11px] text-slate-500">Click to autofill</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <button
                type="button"
                onClick={() => handleSelectDemo("recruiter@joveo.com")}
                className={`px-2.5 py-2 rounded-lg border text-left transition ${
                  email === "recruiter@joveo.com"
                    ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 font-medium"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="font-semibold text-white truncate">Sarah Chen</div>
                <div className="text-[10px] text-slate-400 truncate">Joveo Recruiter</div>
              </button>

              <button
                type="button"
                onClick={() => handleSelectDemo("admin@adopt.ai")}
                className={`px-2.5 py-2 rounded-lg border text-left transition ${
                  email === "admin@adopt.ai"
                    ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 font-medium"
                    : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                <div className="font-semibold text-white truncate">Alex Mercer</div>
                <div className="text-[10px] text-slate-400 truncate">Campaign Director</div>
              </button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Enterprise Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-3.5 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-3 text-slate-500 hover:text-slate-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center text-slate-400 hover:text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-3.5 h-3.5 rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500 mr-2"
                />
                Remember this device
              </label>
              <span className="text-indigo-400 text-[11px] font-mono">Demo: password123</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>Verifying Session...</>
              ) : (
                <>
                  <span>Sign In to Dashboard</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Guest Explore Option */}
          <div className="pt-4 border-t border-slate-800 text-center">
            <button
              type="button"
              onClick={onExploreAsGuest}
              className="text-xs text-slate-400 hover:text-slate-200 font-medium inline-flex items-center gap-1.5 transition"
            >
              <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Continue as Guest Reviewer &rarr;</span>
            </button>
          </div>
        </div>

        {/* Security badges */}
        <div className="mt-6 flex items-center justify-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> SOC-2 Encrypted Session
          </span>
          <span>•</span>
          <span>LightGBM Engine</span>
          <span>•</span>
          <span>Thompson Sampling</span>
        </div>
      </div>
    </div>
  );
}
