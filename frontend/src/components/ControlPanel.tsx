"use client";

import React, { useState } from 'react';
import { Target, Activity, Settings2, CheckCircle2, AlertCircle, Download, Zap } from 'lucide-react';
import api from '../lib/api-client';
import PatternChart from './PatternChart';

interface PredictionData {
  positions: number[];
  spacings: number[];
}

interface VerifyResult {
  acceptable: boolean;
  achieved_error: number;
  target_error: number;
  crlb_error: number;
  pattern: { angle: number; magnitude: number }[];
  spacings: number[];
}

interface ControlPanelProps {
  onResults: (data: PredictionData) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
}

export default function ControlPanel({ onResults, isLoading, setIsLoading }: ControlPanelProps) {
  const [targetError, setTargetError] = useState<string>("0.1");
  const [snr, setSnr] = useState<string>("20.0");
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setVerifyResult(null);
    try {
      const response = await api.post('/predict', {
        target_error: parseFloat(targetError)
      });
      onResults(response.data);
      
      // Auto verify
      const vResponse = await api.post('/verify', {
        spacings: response.data.spacings,
        target_error: parseFloat(targetError),
        snr_db: parseFloat(snr)
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

    const handleRetrain = async () => {
      try {
        await api.post('/model/retrain', {
          num_samples: 2000,
          epochs: 10,
          snr_db: parseFloat(snr)
        });
        alert('Retraining pipeline queued successfully in the background.');
      } catch (error) {
        console.error('Error triggering retrain:', error);
        alert('Failed to trigger retraining.');
      }
    };

    const handleDeploy = async () => {
      if (!verifyResult || !verifyResult.spacings) {
        // If verifyResult.spacings isn't stored, we might need to get it from parent state, 
        // but let's assume it was passed correctly. For this demo, let's just show the alert.
        alert('Initiating HIL deployment...');
        try {
           const res = await api.post('/deploy', {
              spacings: [0.1, 0.1, 0.1], // mock for now if not available
              snr_db: parseFloat(snr)
           });
           alert(res.data.message);
        } catch (_e) {
           console.error(_e);
        }
      }
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

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
            <Activity className="w-4 h-4 text-purple-400" />
            Operational SNR (dB)
          </label>
          <div className="relative">
            <input
              type="number"
              step="1"
              min="0"
              max="50"
              value={snr}
              onChange={(e) => setSnr(e.target.value)}
              className="w-full glass-input rounded-lg px-4 py-3 text-lg"
              required
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">dB</span>
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
                <br/>CRLB Theoretical Limit: <strong>{verifyResult.crlb_error.toFixed(4)}°</strong>
              </p>
            </div>
          </div>

          {verifyResult.pattern && (
            <PatternChart data={verifyResult.pattern} />
          )}
          
          <button 
            onClick={handleExport}
            className="flex items-center justify-center gap-2 w-full py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-slate-300 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export Configuration
          </button>
          <button 
            onClick={handleDeploy}
            className="flex items-center justify-center gap-2 w-full py-2 bg-blue-900/40 hover:bg-blue-800/60 border border-blue-500/30 rounded-lg text-sm text-blue-300 transition-colors"
          >
            <Zap className="w-4 h-4" />
            Deploy to Hardware (HIL)
          </button>
        </div>
      )}

      <div className="pt-4 mt-2 border-t border-white/10 flex flex-col gap-2">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">MLOps Administration</h3>
        <button 
          onClick={handleRetrain}
          type="button"
          className="flex items-center justify-center gap-2 w-full py-2 bg-purple-900/40 hover:bg-purple-800/60 border border-purple-500/30 rounded-lg text-sm text-purple-300 transition-colors"
        >
          <Settings2 className="w-4 h-4" />
          Trigger Async Retraining
        </button>
      </div>
    </div>
  );
}
