"use client";

import React from 'react';
import { BarChart3, TrendingUp, Info, Activity } from 'lucide-react';

export default function Analytics() {
  return (
    <div className="p-4 md:p-8 lg:p-10 space-y-8 animate-in fade-in duration-700">
      <header>
        <h2 className="text-3xl font-bold text-white tracking-tight">Performance Analytics</h2>
        <p className="text-slate-400 mt-1">Deep-dive into the mathematical performance of your current array configuration.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Avg. Sidelobe Level', value: '-13.4 dB', icon: Activity, color: 'text-blue-400' },
          { label: 'Mainbeam Width', value: '8.2°', icon: TrendingUp, color: 'text-purple-400' },
          { label: 'CRLB Margin', value: '12%', icon: Info, color: 'text-green-400' },
        ].map((stat, i) => (
          <div key={i} className="glass-panel p-6 flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{stat.label}</p>
              <p className="text-2xl font-mono font-bold mt-1">{stat.value}</p>
            </div>
            <stat.icon className={`w-8 h-8 ${stat.color} opacity-20`} />
          </div>
        ))}
      </div>

      <div className="glass-panel p-8 min-h-[400px] flex flex-col items-center justify-center text-center">
        <BarChart3 className="w-16 h-16 text-slate-700 mb-4" />
        <h3 className="text-xl font-bold text-slate-300">Detailed Pattern Analysis</h3>
        <p className="text-slate-500 max-w-md mt-2">
          This module is designed to integrate with high-resolution radiation pattern data. 
          Configure an array in the Dashboard to see real-time CRLB vs. Simulation benchmarks here.
        </p>
        <div className="mt-8 px-6 py-3 rounded-full bg-blue-600/10 border border-blue-500/20 text-blue-400 text-sm font-semibold">
          AI-Inference Engine Ready
        </div>
      </div>
    </div>
  );
}
