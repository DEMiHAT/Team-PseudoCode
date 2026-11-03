import React from 'react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white py-6 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
        <p>
          <strong className="text-slate-700 font-semibold">IT22301 – Data Structures and Algorithms</strong> • Intelligent 1-to-1 Learning Support System
        </p>
        <p className="font-mono text-2xs text-slate-400">
          FastAPI • SQLAlchemy • SQLite/PostgreSQL • BKT Engine • React 19 • Monaco • Judge0 CE
        </p>
      </div>
    </footer>
  );
}
