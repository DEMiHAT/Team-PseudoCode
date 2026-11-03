import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, trend, className = '' }) {
  return (
    <div className={`p-5 rounded-xl border border-slate-200 bg-white shadow-2xs ${className}`}>
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
        {Icon && (
          <div className="p-2 rounded-lg bg-slate-50 text-slate-600 border border-slate-100">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-baseline space-x-2">
        <p className="text-2xl font-bold tracking-tight text-slate-900">{value}</p>
        {trend && <span className="text-xs font-medium text-emerald-600">{trend}</span>}
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}

