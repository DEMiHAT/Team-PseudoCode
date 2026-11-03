import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Terminal,
  TrendingUp,
  AlertOctagon,
  Clock,
  Layers,
  Code2,
} from 'lucide-react';
import Badge from '../ui/Badge';

export default function TestResultsPanel({
  result,
  running = false,
  submitting = false,
}) {
  const [activeTab, setActiveTab] = useState('test_cases'); // 'test_cases' | 'console'
  const [selectedCaseIndex, setSelectedCaseIndex] = useState(0);

  if (running || submitting) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-xs text-slate-400 space-y-4 shadow-xl">
        <div className="inline-flex p-3 rounded-full bg-indigo-500/10 text-indigo-400 animate-spin">
          <Terminal className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <p className="font-semibold text-slate-200 text-sm">
            {submitting ? 'Submitting to Assessment Engine...' : 'Compiling & Running Java Tests...'}
          </p>
          <p className="text-2xs text-slate-500">
            Dispatching code to sandboxed Judge0 runner with OpenJDK 17
          </p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-xs text-slate-500 space-y-2 shadow-xl">
        <Terminal className="w-8 h-8 mx-auto text-slate-600" />
        <p className="font-medium text-slate-400">Execution Sandbox Idle</p>
        <p className="text-2xs text-slate-500">
          Click "Run Tests" to test against visible cases or "Submit Solution" for full evaluation.
        </p>
      </div>
    );
  }

  const isAccepted = result.is_passed;
  const isCompilationError = result.status === 'Compilation Error' || Boolean(result.compile_error);
  const isRuntimeError = result.status === 'Runtime Error' || Boolean(result.runtime_error);
  const testCases = result.test_case_results || [];
  const selectedCase = testCases[selectedCaseIndex] || testCases[0];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl flex flex-col">
      {/* Header Bar */}
      <div className="px-5 py-4 bg-slate-950/60 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          {isAccepted ? (
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : isCompilationError ? (
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertOctagon className="w-5 h-5" />
            </div>
          ) : (
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <XCircle className="w-5 h-5" />
            </div>
          )}

          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-bold text-slate-100 text-sm tracking-tight">{result.status}</h3>
              <Badge variant={isAccepted ? 'success' : isCompilationError ? 'danger' : 'warning'}>
                {result.test_cases_passed} / {result.total_test_cases} Passed
              </Badge>
            </div>
            {result.execution_time_ms !== undefined && (
              <p className="text-2xs text-slate-400 font-mono flex items-center space-x-1 mt-0.5">
                <Clock className="w-3 h-3 text-slate-500" />
                <span>Execution Time: {result.execution_time_ms} ms</span>
              </p>
            )}
          </div>
        </div>

        {/* BKT Mastery Indicator */}
        {result.bkt_updated_mastery !== null && result.bkt_updated_mastery !== undefined && (
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-xs">
            <TrendingUp className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-400">BKT Mastery p(L):</span>
            <span className="font-mono font-bold text-indigo-300">
              {(result.bkt_updated_mastery * 100).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 bg-slate-950/30 px-4 text-xs font-medium text-slate-400">
        <button
          onClick={() => setActiveTab('test_cases')}
          className={`py-2.5 px-3 border-b-2 transition flex items-center space-x-1.5 ${
            activeTab === 'test_cases'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent hover:text-slate-200'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Test Cases ({testCases.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('console')}
          className={`py-2.5 px-3 border-b-2 transition flex items-center space-x-1.5 ${
            activeTab === 'console'
              ? 'border-indigo-500 text-indigo-400'
              : 'border-transparent hover:text-slate-200'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Console & Diagnostics</span>
          {(isCompilationError || isRuntimeError) && (
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
          )}
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="p-5 space-y-4">
        {/* Adaptive Intervention Recommendation */}
        {result.triggered_intervention && (
          <div className="p-3.5 rounded-lg bg-amber-950/20 border border-amber-500/30 text-xs text-amber-200 space-y-1">
            <div className="flex items-center space-x-2 font-semibold text-amber-300">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                Recommended Scaffold: Tier {result.triggered_intervention.tier} ({result.triggered_intervention.strategy})
              </span>
            </div>
            <p className="text-2xs text-amber-300/80 leading-relaxed pl-6">
              {result.triggered_intervention.rationale}
            </p>
          </div>
        )}

        {/* Tab 1: Test Cases Tab */}
        {activeTab === 'test_cases' && (
          <div className="space-y-4">
            {testCases.length > 0 ? (
              <div>
                {/* Horizontal Case Selectors */}
                <div className="flex flex-wrap gap-2 mb-3">
                  {testCases.map((tc, idx) => (
                    <button
                      key={tc.test_case_id || idx}
                      onClick={() => setSelectedCaseIndex(idx)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center space-x-1.5 transition ${
                        selectedCaseIndex === idx
                          ? 'bg-slate-800 text-slate-100 border border-slate-700'
                          : 'bg-slate-950/40 text-slate-400 border border-slate-800/60 hover:bg-slate-850'
                      }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full ${
                          tc.passed ? 'bg-emerald-400' : 'bg-rose-400'
                        }`}
                      ></span>
                      <span>Case {idx + 1}</span>
                    </button>
                  ))}
                </div>

                {/* Selected Case Inspection */}
                {selectedCase && (
                  <div className="bg-slate-950/80 rounded-lg p-4 border border-slate-800/80 space-y-3 font-mono text-xs">
                    <div>
                      <span className="text-2xs uppercase tracking-wider text-slate-500 font-sans block mb-1">
                        Input
                      </span>
                      <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-slate-200">
                        {selectedCase.input || '<empty>'}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <span className="text-2xs uppercase tracking-wider text-slate-500 font-sans block mb-1">
                          Expected Output
                        </span>
                        <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-emerald-400 font-semibold">
                          {selectedCase.expected_output}
                        </div>
                      </div>

                      <div>
                        <span className="text-2xs uppercase tracking-wider text-slate-500 font-sans block mb-1">
                          Actual Output
                        </span>
                        <div
                          className={`p-2.5 rounded bg-slate-900 border ${
                            selectedCase.passed
                              ? 'border-emerald-500/30 text-emerald-300'
                              : 'border-rose-500/30 text-rose-300'
                          }`}
                        >
                          {selectedCase.actual_output !== null && selectedCase.actual_output !== undefined
                            ? selectedCase.actual_output.trim() || '<empty stdout>'
                            : '<no output produced>'}
                        </div>
                      </div>
                    </div>

                    {selectedCase.error && (
                      <div>
                        <span className="text-2xs uppercase tracking-wider text-rose-400 font-sans block mb-1">
                          Error Details
                        </span>
                        <pre className="p-2.5 rounded bg-rose-950/20 border border-rose-500/30 text-rose-300 text-2xs overflow-x-auto whitespace-pre-wrap">
                          {selectedCase.error}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 text-xs">
                No test case outputs generated. Check the Console tab for compilation diagnostics.
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Console & Diagnostics Tab */}
        {activeTab === 'console' && (
          <div className="space-y-3">
            {/* Compilation Error Display */}
            {result.compile_error && (
              <div className="space-y-1">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-rose-400">
                  <AlertOctagon className="w-3.5 h-3.5" />
                  <span>Compilation Error (javac)</span>
                </div>
                <pre className="p-3.5 rounded-lg bg-slate-950 border border-rose-500/30 text-rose-300 font-mono text-2xs overflow-x-auto whitespace-pre-wrap leading-relaxed">
                  {result.compile_error}
                </pre>
              </div>
            )}

            {/* Runtime Error Display */}
            {result.runtime_error && (
              <div className="space-y-1">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-amber-400">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Runtime Exception (java)</span>
                </div>
                <pre className="p-3.5 rounded-lg bg-slate-950 border border-amber-500/30 text-amber-300 font-mono text-2xs overflow-x-auto whitespace-pre-wrap leading-relaxed">
                  {result.runtime_error}
                </pre>
              </div>
            )}

            {!result.compile_error && !result.runtime_error && (
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-400 space-y-1">
                <p className="text-emerald-400 font-semibold">Build and execution exited with status code 0.</p>
                <p className="text-2xs text-slate-500">All tests executed within bounded cpu and memory limits.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
