import React from 'react';

export default function Card({ children, className = '', header, footer, ...props }) {
  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden ${className}`}
      {...props}
    >
      {header && <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">{header}</div>}
      <div className="p-5">{children}</div>
      {footer && <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/80">{footer}</div>}
    </div>
  );
}
