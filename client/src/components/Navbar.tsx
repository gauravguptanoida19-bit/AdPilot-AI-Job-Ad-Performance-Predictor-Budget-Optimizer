"use client";

import React from "react";
import { BarChart3, Calculator, Cpu, Layers, Sparkles, LogOut, User, LogIn } from "lucide-react";
import { UserProfile } from "../lib/api";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  apiConnected: boolean;
  user: UserProfile | null;
  onSignOut: () => void;
  onSignInClick: () => void;
}

export function Navbar({
  activeTab,
  setActiveTab,
  apiConnected,
  user,
  onSignOut,
  onSignInClick
}: NavbarProps) {
  const tabs = [
    { id: "overview", label: "Executive Overview & Metrics", icon: BarChart3 },
    { id: "predictor", label: "Ad Predictor & SHAP Explainer", icon: Calculator },
    { id: "simulator", label: "Bandit Budget Simulator", icon: Cpu },
    { id: "channels", label: "Channel Economics & Theory", icon: Layers },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-blue-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-white tracking-tight">AdOpt</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                  LightGBM + Thompson Sampling
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Recruitment Ad Performance Predictor & Programmatic Budget Optimizer
              </p>
            </div>
          </div>

          {/* Right Action Bar: Status & User Profile */}
          <div className="flex items-center gap-3">
            {/* Status Indicator */}
            <span className={`inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
              apiConnected 
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" 
                : "bg-amber-500/10 text-amber-400 border-amber-500/20"
            }`}>
              <span className={`w-2 h-2 rounded-full ${apiConnected ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
              <span className="hidden sm:inline">{apiConnected ? "FastAPI Connected" : "Local Benchmark"}</span>
            </span>

            {/* User Profile / Auth State */}
            {user ? (
              <div className="flex items-center gap-3 pl-3 border-l border-slate-800">
                <div className="flex items-center gap-2">
                  <img
                    src={user.avatar_url}
                    alt={user.name}
                    className="w-8 h-8 rounded-full border border-indigo-500/40 object-cover"
                  />
                  <div className="hidden md:block text-left">
                    <div className="text-xs font-semibold text-white leading-tight">{user.name}</div>
                    <div className="text-[10px] text-indigo-400 leading-tight truncate max-w-[130px]">{user.role}</div>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={onSignOut}
                  title="Sign out of enterprise portal"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={onSignInClick}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium shadow-md shadow-indigo-600/20 transition"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Enterprise Sign In</span>
              </button>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 sm:space-x-4 overflow-x-auto py-2 border-t border-slate-800/60 no-scrollbar">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
