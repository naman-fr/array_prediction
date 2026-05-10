"use client";

import React, { useState } from 'react';
import { Target, Activity, Settings2, CheckCircle2, AlertCircle, Download } from 'lucide-react';
import axios from 'axios';

interface ControlPanelProps {
  onResults: (data: any) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
}

export default function ControlPanel({ onResults, isLoading, setIsLoading }: ControlPanelProps) {
  const [targetError, setTargetError] = useState<string>("0.1");
  const [verifyResult, setVerifyResult] = useState<any>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setVerifyResult(null);
    try {
      const response = await axios.post('http://localhost:8000/predict', {
        target_error: parseFloat(targetError)
      });
      onResults(response.data);
      
      // Auto verify
      const vResponse = await axios.post('http://localhost:8000/verify', {
        spacings: response.data.spacings,
        target_error: parseFloat(targetError)
      });
      setVerifyResult(vResponse.data);
      
      } catch (error) {
        console.error("Error predicting spacings:", error);
      } finally {
        setIsLoading(false);
      }
    };
  
    const handleExport = () => {
      if (!verifyResult) return;
      const dataStr = JSON.stringify({
          targetError: parseFloat(targetError),
          achievedError: verifyResult.achieved_error,
          spacings: verifyResult.spacings || [] // Note: might need to be passed down if not in verifyResult
      }, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
      
      const exportFileDefaultName = 'radar_configuration.json';
      
      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    };
  
    return (
    <div className="glass-panel p-6 flex flex-col gap-6">
      <div className="flex items-center gap-3 border-b border-white/10 pb-4">
        <div className="bg-blue-500/20 p-2 rounded-lg">
          <Settings2 className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <h2 className="text-xl font-bold">Array Configuration</h2>
          <p className="text-sm text-slate-400">Set target parameters to optimize spacing</p>
        </div>
      </div>

      <form onSubmit={handlePredict} className="flex flex-col gap-5">
        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
            <Target className="w-4 h-4 text-blue-400" />
            Target RMS Angular Error (degrees)
          </label>
          <div className="relative">
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={targetError}
              onChange={(e) => setTargetError(e.target.value)}
              className="w-full glass-input rounded-lg px-4 py-3 text-lg"
              required
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">deg°</span>
          </div>
        </div>

        <button 
          type="submit" 
          disabled={isLoading}
          className="glass-button w-full py-3 rounded-lg font-bold text-lg flex items-center justify-center gap-2 mt-2"
        >
          {isLoading ? (
            <Activity className="w-5 h-5 animate-spin" />
          ) : (
            <Activity className="w-5 h-5" />
          )}
          {isLoading ? 'Optimizing AI Model...' : 'Generate Optimal Array'}
        </button>
      </form>

      {verifyResult && (
        <div className="flex flex-col gap-3 mt-4">
          <div className={`p-4 rounded-lg border ${verifyResult.acceptable ? 'bg-green-500/10 border-green-500/30' : 'bg-orange-500/10 border-orange-500/30'} flex items-start gap-3`}>
            {verifyResult.acceptable ? (
              <CheckCircle2 className="w-5 h-5 text-green-400 shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-orange-400 shrink-0 mt-0.5" />
            )}
            <div>
              <h4 className={`text-sm font-bold ${verifyResult.acceptable ? 'text-green-400' : 'text-orange-400'}`}>
                Verification {verifyResult.acceptable ? 'Passed' : 'Warning'}
              </h4>
              <p className="text-xs text-slate-300 mt-1">
                Achieved RMS Error: <strong>{verifyResult.achieved_error.toFixed(4)}°</strong> 
                <br/>(Target: {verifyResult.target_error.toFixed(3)}°)
              </p>
            </div>
          </div>
          
          <button 
            onClick={handleExport}
            className="flex items-center justify-center gap-2 w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-slate-300 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Configuration
          </button>
        </div>
      )}
    </div>
  );
}
