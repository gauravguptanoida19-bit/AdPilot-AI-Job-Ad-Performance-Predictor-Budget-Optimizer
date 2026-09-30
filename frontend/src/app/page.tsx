"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { OverviewTab } from "../components/OverviewTab";
import { PredictorTab } from "../components/PredictorTab";
import { SimulatorTab } from "../components/SimulatorTab";
import { ChannelTab } from "../components/ChannelTab";
import { LoginPage } from "../components/LoginPage";
import {
  fetchModelMetrics,
  fetchGlobalShap,
  ModelMetricsResponse,
  ShapGlobalResponse,
  UserProfile
} from "../lib/api";

const STORAGE_KEY = "adopt_enterprise_user";

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview");
  const [metrics, setMetrics] = useState<ModelMetricsResponse | null>(null);
  const [shap, setShap] = useState<ShapGlobalResponse | null>(null);
  const [apiConnected, setApiConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  // Authentication State
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isGuest, setIsGuest] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    // Check saved session
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        setUser(JSON.parse(saved));
      }
    } catch (e) {
      console.warn("Storage check failed:", e);
    }

    async function loadData() {
      try {
        const [metricsData, shapData] = await Promise.all([
          fetchModelMetrics(),
          fetchGlobalShap()
        ]);
        setMetrics(metricsData);
        setShap(shapData);
        setApiConnected(true);
      } catch (err) {
        console.warn("Backend offline or loading fallback:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleLoginSuccess = (authenticatedUser: UserProfile) => {
    setUser(authenticatedUser);
    setIsGuest(false);
    setShowLoginModal(false);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(authenticatedUser));
    } catch (e) {
      // ignore
    }
  };

  const handleSignOut = () => {
    setUser(null);
    setIsGuest(false);
    setShowLoginModal(true);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      // ignore
    }
  };

  const handleExploreAsGuest = () => {
    setIsGuest(true);
    setShowLoginModal(false);
  };

  // If user is neither logged in nor guest, show LoginPage
  if (!user && !isGuest) {
    return (
      <LoginPage
        onLoginSuccess={handleLoginSuccess}
        onExploreAsGuest={handleExploreAsGuest}
      />
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiConnected={apiConnected}
        user={user}
        onSignOut={handleSignOut}
        onSignInClick={() => setShowLoginModal(true)}
      />

      {/* Modal overlay if guest clicks "Enterprise Sign In" */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="relative max-w-md w-full">
            <button
              onClick={() => setShowLoginModal(false)}
              className="absolute right-4 top-4 text-slate-400 hover:text-white z-20 text-xs px-2 py-1 rounded bg-slate-800"
            >
              ✕ Close
            </button>
            <LoginPage
              onLoginSuccess={handleLoginSuccess}
              onExploreAsGuest={() => setShowLoginModal(false)}
            />
          </div>
        </div>
      )}

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-400">Loading model evaluation metrics and TreeSHAP weights...</p>
          </div>
        ) : (
          <>
            {activeTab === "overview" && metrics && shap && (
              <OverviewTab metrics={metrics} shap={shap} />
            )}
            {activeTab === "predictor" && <PredictorTab />}
            {activeTab === "simulator" && <SimulatorTab />}
            {activeTab === "channels" && <ChannelTab />}
          </>
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>
          AdOpt Enterprise Portal • Programmatic Recruitment Ad Performance Predictor & Budget Optimizer
        </p>
        <p className="mt-1">
          Classical Machine Learning (LightGBM) & Bayesian Multi-Armed Bandit (Thompson Sampling)
        </p>
      </footer>
    </div>
  );
}
