"use client";

import React from 'react';
import { Settings, Server, Database, Globe } from 'lucide-react';

export default function SettingsPage() {
  const apiURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  return (
    <div className="p-4 md:p-8 lg:p-10 space-y-8 animate-in fade-in duration-700">
      <header>
        <h2 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Settings className="w-8 h-8 text-slate-400" />
          System Settings
        </h2>
        <p className="text-slate-400 mt-1">Configure your environment and API connections.</p>
      </header>

      <div className="max-w-2xl space-y-6">
        <div className="glass-panel p-6">
          <div className="flex items-center gap-3 mb-6">
            <Server className="w-5 h-5 text-blue-400" />
            <h3 className="font-bold text-slate-100">API Configuration</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-slate-500 uppercase">Master API Gateway</label>
              <div className="flex gap-2">
                <input 
                  type="text" 
                  value={apiURL} 
                  readOnly
                  className="flex-1 glass-input px-4 py-2 rounded-lg text-sm font-mono opacity-60 cursor-not-allowed"
                />
                <div className="px-3 py-2 bg-green-500/10 border border-green-500/20 text-green-400 text-[10px] font-bold rounded-lg flex items-center">
                  ACTIVE
                </div>
              </div>
              <p className="text-[10px] text-slate-600 italic">This is managed via .env.local on the server side.</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 opacity-50 cursor-not-allowed">
          <div className="flex items-center gap-3 mb-6">
            <Database className="w-5 h-5 text-purple-400" />
            <h3 className="font-bold text-slate-100">Data Persistence</h3>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-slate-400">Database Engine</span>
            <span className="text-slate-300 font-mono">SQLite (SQLAlchemy ORM)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
