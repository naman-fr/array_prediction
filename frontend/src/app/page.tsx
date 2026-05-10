"use client";

import { useState, useEffect } from 'react';
import RadarVisualization from '@/components/RadarVisualization';
import ControlPanel from '@/components/ControlPanel';
import AgentChat from '@/components/AgentChat';
import { Network, Globe, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

export default function Home() {
  const [positions, setPositions] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [spacings, setSpacings] = useState<number[]>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await api.get('/health');
        setBackendStatus('online');
      } catch (e) {
        setBackendStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResults = (data: any) => {
    setPositions(data.positions);
    setSpacings(data.spacings);
  };

  return (
    <main className="min-h-screen p-4 md:p-8 lg:p-12 relative z-10">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="glass-panel p-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-3 rounded-xl shadow-lg">
              <Network className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                Sentinel AI
              </h1>
              <p className="text-slate-400 font-medium tracking-wide">Radar Array Optimization Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {backendStatus === 'online' ? (
              <div className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-semibold tracking-wider flex items-center gap-2">
                <Globe className="w-4 h-4" />
                BACKEND ONLINE
              </div>
            ) : backendStatus === 'offline' ? (
              <div className="px-4 py-2 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-semibold tracking-wider flex items-center gap-2 animate-pulse">
                <AlertCircle className="w-4 h-4" />
                BACKEND OFFLINE
              </div>
            ) : (
              <div className="px-4 py-2 rounded-full bg-slate-500/10 border border-slate-500/20 text-slate-400 text-sm font-semibold tracking-wider">
                CHECKING SYSTEM...
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

            {/* Results Details */}
            {spacings.length > 0 && (
              <div className="glass-panel p-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <h3 className="text-lg font-bold text-slate-200 mb-4 border-b border-white/10 pb-2">Optimized Elements</h3>
                <ul className="space-y-3">
                  {spacings.map((s, i) => (
                    <li key={i} className="flex justify-between items-center bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                      <span className="text-slate-400 text-sm">Spacing d{i+1}</span>
                      <span className="font-mono text-blue-300 font-semibold">{s.toFixed(5)} m</span>
                    </li>
                  ))}
                  <li className="flex justify-between items-center bg-blue-900/20 p-3 rounded-lg border border-blue-500/30 mt-4">
                    <span className="text-blue-200 font-medium">Total Aperture</span>
                    <span className="font-mono text-white font-bold">
                      {positions[positions.length - 1]?.toFixed(5)} m
                    </span>
                  </li>
                </ul>
              </div>
            )}
          </div>

          {/* Right Column: Visualization */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
              <RadarVisualization positions={positions} />
            </div>

            {/* Agentic Chat Area */}
            <AgentChat onResultsUpdate={handleResults} />
          </div>
        </div>
        
      </div>
    </main>
  );
}
