import React, { useState } from 'react';
import { Lightbulb, ChevronRight, HelpCircle, Loader2 } from 'lucide-react';
import Button from '../ui/Button';
import Badge from '../ui/Badge';

export default function ScaffoldingPanel({ onRequestHint, loading = false, activeHint = null }) {
  const [selectedTier, setSelectedTier] = useState(1);

  const tiers = [
    { level: 1, name: 'Tier 1: Conceptual Orientation', desc: 'Reflective hints and boundary constraints' },
    { level: 2, name: 'Tier 2: Algorithmic Blueprint', desc: 'Pseudocode and logical step flow' },
    { level: 3, name: 'Tier 3: Concrete State Trace', desc: 'Sample input pointer & array transitions' },
    { level: 4, name: 'Tier 4: Code Skeleton', desc: 'Scaffolded Java block with targeted blanks' },
  ];

  const handleRequest = (level) => {
    setSelectedTier(level);
    onRequestHint(level);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <Lightbulb className="w-4 h-4 text-amber-600" />
          <h3 className="text-sm font-bold text-slate-800">Adaptive Scaffolding & 1-to-1 Tutor</h3>
        </div>
        <Badge variant="primary" size="sm">
          Cognitive Scaffolding
        </Badge>
      </div>

      <p className="text-xs text-slate-600 leading-relaxed">
        Select a cognitive assistance level. The tutoring engine serves non-prescriptive scaffolding according to your current knowledge state.
      </p>

      {/* Tier Selector Buttons */}
      <div className="grid grid-cols-2 gap-2">
        {tiers.map((t) => (
          <button
            key={t.level}
            onClick={() => handleRequest(t.level)}
            disabled={loading}
            className={`text-left p-3 rounded-lg border text-xs transition-all cursor-pointer ${
              selectedTier === t.level
                ? 'border-indigo-600 bg-indigo-50/60 text-indigo-950 font-medium'
                : 'border-slate-200 hover:border-slate-300 bg-slate-50/50 text-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-semibold">{t.name.split(':')[0]}</span>
              <ChevronRight className="w-3 h-3 text-slate-400" />
            </div>
            <p className="text-2xs text-slate-500 mt-0.5 line-clamp-1">{t.desc}</p>
          </button>
        ))}
      </div>

      {/* Loading state */}
      {loading && (
        <div className="p-6 text-center text-xs text-slate-500 flex flex-col items-center justify-center space-y-2">
          <Loader2 className="w-5 h-5 animate-spin text-indigo-600" />
          <span>Generating scaffolding explanation...</span>
        </div>
      )}

      {/* Active Hint Card */}
      {!loading && activeHint && (
        <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-900">{activeHint.title}</span>
            <span className="text-2xs px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-mono">
              Strategy: {activeHint.pedagogical_strategy}
            </span>
          </div>
          <p className="text-xs text-slate-700 whitespace-pre-line leading-relaxed">{activeHint.hint_text}</p>
          {activeHint.code_snippet && (
            <pre className="p-3 rounded bg-slate-900 text-emerald-400 font-mono text-2xs overflow-x-auto mt-2">
              <code>{activeHint.code_snippet}</code>
            </pre>
          )}
          <div className="pt-2 text-2xs text-slate-400 flex items-center justify-between border-t border-slate-200/60">
            <span>{activeHint.is_llm_generated ? 'Generated via Gemini Socratic Interface' : 'Deterministic Pedagogical Template'}</span>
            <span className="font-mono">Tier {activeHint.level}/4</span>
          </div>
        </div>
      )}
    </div>
  );
}

