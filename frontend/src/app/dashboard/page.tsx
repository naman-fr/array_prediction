"use client";

import { useState, useEffect } from 'react';
import RadarVisualization from '@/components/RadarVisualization';
import ControlPanel from '@/components/ControlPanel';
import AgentChat from '@/components/AgentChat';
import { Globe, AlertCircle, Cpu, ShieldCheck } from 'lucide-react';
import api from '../../lib/api-client';

interface PredictionData {
  positions: number[];
  spacings: number[];
}

export default function Dashboard() {
  const [positions, setPositions] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [spacings, setSpacings] = useState<number[]>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.get('/health');
        setBackendStatus('online');
      } catch (_e) {
        setBackendStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResults = (data: PredictionData) => {
    setPositions(data.positions);
    setSpacings(data.spacings);
  };

  return (
    <div className="p-4 md:p-8 lg:p-10 space-y-8 animate-in fade-in duration-700">
      
      {/* Dynamic Header */}
      <header className="flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">System Control Dashboard</h2>
          <p className="text-slate-400 mt-1">Manage and optimize radar array geometry in real-time.</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900/50 border border-white/5">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-bold text-slate-300 uppercase tracking-tighter">HIL Node: Mock-01</span>
          </div>
          
          {backendStatus === 'online' ? (
            <div className="px-4 py-2 rounded-xl bg-green-500/10 border border-green-500/20 text-green-400 text-xs font-bold tracking-wider flex items-center gap-2">
              <Globe className="w-3 h-3" />
              ONLINE
            </div>
          ) : (
            <div className="px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-bold tracking-wider flex items-center gap-2 animate-pulse">
              <AlertCircle className="w-3 h-3" />
              OFFLINE
            </div>
          )}
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Controls */}
        <div className="lg:col-span-4 space-y-8">
          <ControlPanel 
            onResults={handleResults} 
            isLoading={isLoading} 
            setIsLoading={setIsLoading} 
          />

          {/* Results Summary Card */}
          {spacings.length > 0 && (
            <div className="glass-panel p-6 border-l-4 border-l-blue-500 shadow-2xl animate-in slide-in-from-left-4 duration-500">
              <div className="flex items-center gap-2 mb-6">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-bold text-slate-100">Verification Metrics</h3>
              </div>
              <ul className="space-y-4">
                {spacings.map((s, i) => (
                  <li key={i} className="flex justify-between items-center group">
                    <span className="text-slate-400 text-sm group-hover:text-slate-300 transition-colors">Element Spacing d{i+1}</span>
                    <span className="font-mono text-blue-300 font-bold bg-blue-500/5 px-2 py-1 rounded border border-blue-500/10">{s.toFixed(5)} m</span>
                  </li>
                ))}
                <div className="pt-4 border-t border-white/5 mt-4">
                  <li className="flex justify-between items-center bg-blue-600/10 p-4 rounded-xl border border-blue-500/20">
                    <span className="text-blue-200 font-semibold text-sm">Total Physical Aperture</span>
                    <span className="font-mono text-white font-black text-lg">
                      {positions[positions.length - 1]?.toFixed(4)} m
                    </span>
                  </li>
                </div>
              </ul>
            </div>
          )}
        </div>

        {/* Right Column: Visualization & Agent */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          <div className="relative group rounded-2xl overflow-hidden border border-white/5 bg-slate-950/40">
            <div className="absolute top-4 left-4 z-20 flex gap-2">
               <div className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-[10px] font-bold text-blue-400 uppercase">3D Digital Twin</div>
               <div className="px-3 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-[10px] font-bold text-slate-400 uppercase">Interactive AF Map</div>
            </div>
            <RadarVisualization positions={positions} />
          </div>

          <AgentChat onResultsUpdate={handleResults} />
        </div>
      </div>
    </div>
  );
}
