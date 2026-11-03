import React from 'react';

export default function ProgressBar({
  value = 0, // 0 to 100
  label,
  showPercentage = true,
  height = 'h-2',
  className = '',
}) {
  const clampedValue = Math.min(100, Math.max(0, value));

  // Determine indicator color based on mastery bracket
  let barColor = 'bg-slate-400';
  if (clampedValue >= 80) barColor = 'bg-emerald-600';
  else if (clampedValue >= 50) barColor = 'bg-indigo-600';
  else if (clampedValue >= 25) barColor = 'bg-amber-500';

  return (
    <div className={`space-y-1.5 ${className}`}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between text-xs text-slate-600">
          {label && <span className="font-medium text-slate-700">{label}</span>}
          {showPercentage && <span className="font-mono text-slate-500">{clampedValue.toFixed(1)}%</span>}
        </div>
      )}
      <div className={`w-full bg-slate-200/80 rounded-full overflow-hidden ${height}`}>
        <div
          className={`${height} ${barColor} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  );
}
