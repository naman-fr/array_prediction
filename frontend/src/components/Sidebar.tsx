"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  BarChart3, 
  BookOpen, 
  Settings, 
  Network,
  ChevronRight
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
  { name: 'Analytics', icon: BarChart3, href: '/analytics' },
  { name: 'Documentation', icon: BookOpen, href: '/docs' },
  { name: 'Settings', icon: Settings, href: '/settings' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen sticky top-0 border-r border-white/10 bg-slate-950/50 backdrop-blur-xl flex flex-col p-6 hidden md:flex">
      <div className="flex items-center gap-3 mb-12 px-2">
        <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg shadow-lg">
          <Network className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
          Sentinel AI
        </h1>
      </div>

      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link 
              key={item.href} 
              href={item.href}
              className={`flex items-center justify-between group px-4 py-3 rounded-xl transition-all duration-300 ${
                isActive 
                  ? 'bg-blue-600/20 border border-blue-500/30 text-blue-400' 
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              <div className="flex items-center gap-3">
                <item.icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className="font-semibold text-sm tracking-wide">{item.name}</span>
              </div>
              {isActive && <ChevronRight className="w-4 h-4 text-blue-500" />}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 border-t border-white/5 px-2">
        <div className="bg-slate-900/50 rounded-2xl p-4 border border-white/5">
          <p className="text-[10px] uppercase font-bold text-slate-500 tracking-widest mb-1">Current Version</p>
          <p className="text-xs font-mono text-blue-400">v1.2.4-PRO</p>
        </div>
      </div>
    </aside>
  );
}
