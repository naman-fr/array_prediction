"use client";

import React from 'react';
import Link from 'next/link';
import { Network, ArrowRight, Shield, Zap, Target } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center space-y-12">
      
      {/* Hero Section */}
      <div className="space-y-6 max-w-4xl animate-in fade-in slide-in-from-bottom-8 duration-1000">
        <div className="flex justify-center">
          <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-5 rounded-3xl shadow-2xl shadow-blue-500/20 mb-4">
            <Network className="w-12 h-12 text-white" />
          </div>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-white">
          The Future of <br/>
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
            Radar Intelligence
          </span>
        </h1>
        
        <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Sentinel AI leverages Agentic ReAct reasoning and Deep Learning to optimize 
          multi-frequency radar arrays for elite aerospace performance.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Link href="/dashboard" className="glass-button px-8 py-4 rounded-2xl font-bold text-lg flex items-center gap-2 group">
            Launch Control Dashboard
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
          <Link href="/docs" className="px-8 py-4 rounded-2xl font-bold text-lg border border-white/10 hover:bg-white/5 transition-colors">
            Read Whitepaper
          </Link>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full pt-12 animate-in fade-in duration-1000 delay-300">
        {[
          { title: 'Digital Twin', desc: 'Real-time 3D simulation with radome interference modeling.', icon: Shield },
          { title: 'MLOps Pipeline', desc: 'Automatic retraining loops for adaptive SNR environments.', icon: Zap },
          { title: 'ReAct Agent', desc: 'Natural language control for complex physical parameters.', icon: Target },
        ].map((feature, i) => (
          <div key={i} className="glass-panel p-8 text-left border-white/5 hover:border-blue-500/20 transition-all">
            <feature.icon className="w-8 h-8 text-blue-400 mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
            <p className="text-slate-400 text-sm leading-relaxed">{feature.desc}</p>
          </div>
        ))}
      </div>

      {/* Footer Decoration */}
      <div className="text-slate-600 text-xs font-mono uppercase tracking-[0.5em] pt-12">
        Powered by Hierarchical CRT Unwrapping
      </div>
    </div>
  );
}
