import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { Terminal, BarChart2, BookOpen, Settings as SettingsIcon, RefreshCw, Cpu } from 'lucide-react';
import { healthService } from '../../services/healthService';

export default function Navbar() {
  const [health, setHealth] = useState({ online: false, loading: true });

  const checkStatus = async () => {
    setHealth((prev) => ({ ...prev, loading: true }));
    try {
      const res = await healthService.getSystemHealth();
      setHealth({ online: res.success && res.data.database_connected, loading: false });
    } catch {
      setHealth({ online: false, loading: false });
    }
  };

  useEffect(() => {
    checkStatus();
  }, []);

  const navLinks = [
    { to: '/', label: 'Curriculum & Units', icon: BookOpen },
    { to: '/workspace/1', label: 'Coding Workspace', icon: Terminal },
    { to: '/analytics', label: 'BKT Analytics', icon: BarChart2 },
    { to: '/settings', label: 'Architecture & Health', icon: SettingsIcon },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left Branding */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center text-white">
            <Cpu className="w-5 h-5 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-slate-900 tracking-tight text-base">IT22301</span>
              <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 uppercase">
                DSA 1-to-1 Tutor
              </span>
            </div>
            <p className="text-2xs text-slate-500 font-medium">Undergraduate Engineering Learning Support System</p>
          </div>
        </div>

        {/* Center Navigation Links */}
        <nav className="hidden md:flex items-center space-x-1">
          {navLinks.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-slate-100 text-slate-900 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Right Status Indicator */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2 px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 text-xs">
            <span
              className={`h-2 w-2 rounded-full ${
                health.loading ? 'bg-amber-400' : health.online ? 'bg-emerald-500' : 'bg-rose-500'
              }`}
            />
            <span className="text-slate-600 text-2xs font-medium">
              {health.loading ? 'Connecting' : health.online ? 'Backend Online' : 'Backend Offline'}
            </span>
            <button
              onClick={checkStatus}
              title="Refresh connection status"
              disabled={health.loading}
              className="text-slate-400 hover:text-slate-700 cursor-pointer p-0.5"
            >
              <RefreshCw className={`w-3 h-3 ${health.loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

