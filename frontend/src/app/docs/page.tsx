"use client";

import React from 'react';
import { BookOpen, Zap, Layers, Calculator } from 'lucide-react';

export default function Documentation() {
  const sections = [
    {
      title: "Chinese Remainder Theorem (CRT)",
      desc: "Used for resolving phase ambiguities across multi-frequency observations. By using the difference between prime-related frequencies, we synthesize a 'coarse' wavelength that is much larger than the physical spacing.",
      icon: Zap,
      color: "text-yellow-400"
    },
    {
      title: "Cramer-Rao Lower Bound (CRLB)",
      desc: "The theoretical minimum variance for any unbiased estimator. In our system, we use CRLB to benchmark the performance of the MLP predictor against the absolute mathematical limit of the physical array geometry.",
      icon: Calculator,
      color: "text-blue-400"
    },
    {
      title: "Array Factor (AF)",
      desc: "The radiation pattern of the array. It determines the gain and the location of grating lobes. Our 3D Digital Twin renders this in real-time to ensure no secondary lobes interfere with the target accuracy.",
      icon: Layers,
      color: "text-purple-400"
    }
  ];

  return (
    <div className="p-4 md:p-8 lg:p-10 space-y-8 animate-in fade-in duration-700">
      <header className="max-w-3xl">
        <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-blue-500" />
          Technical Documentation
        </h2>
        <p className="text-slate-400 mt-2 text-lg">
          Understanding the physics and mathematics behind Sentinel AI's optimization engine.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 max-w-4xl">
        {sections.map((section, i) => (
          <div key={i} className="glass-panel p-8 group hover:border-blue-500/30 transition-all duration-300">
            <div className="flex items-start gap-6">
              <div className={`p-4 rounded-2xl bg-slate-900/50 border border-white/5 ${section.color}`}>
                <section.icon className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-100 mb-3">{section.title}</h3>
                <p className="text-slate-400 leading-relaxed">
                  {section.desc}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-600/5 border border-blue-500/20 rounded-2xl p-8 max-w-4xl">
        <h4 className="text-sm font-bold text-blue-400 uppercase tracking-widest mb-4">Implementation Note</h4>
        <p className="text-slate-300 italic">
          "The integration of ReAct agents allows the system to bridge the gap between high-level human requirements ('I need better accuracy') and the low-level physical parameters (d1, d2, d3) dictated by the CRT boundary conditions."
        </p>
      </div>
    </div>
  );
}
