"use client";

import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface PatternChartProps {
  data: { angle: number, magnitude: number }[];
}

export default function PatternChart({ data }: PatternChartProps) {
  return (
    <div className="w-full h-48 mt-4 rounded-lg overflow-hidden glass-panel border border-white/5 p-4">
      <h3 className="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Radiation Pattern (Array Factor)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorMag" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.5}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
          <XAxis 
            dataKey="angle" 
            stroke="#ffffff40" 
            tick={{fill: '#ffffff60', fontSize: 10}}
            tickFormatter={(val) => `${val}°`}
            ticks={[-90, -45, 0, 45, 90]}
          />
          <YAxis 
            stroke="#ffffff40" 
            tick={{fill: '#ffffff60', fontSize: 10}}
            tickFormatter={(val) => `${val}dB`}
            domain={[-40, 0]}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', fontSize: '12px' }}
            formatter={(value: number) => [`${value.toFixed(2)} dB`, 'Magnitude']}
            labelFormatter={(label) => `Angle: ${label}°`}
          />
          <Area type="monotone" dataKey="magnitude" stroke="#3b82f6" fillOpacity={1} fill="url(#colorMag)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
