import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Terminal, TrendingUp, Info } from 'lucide-react';
import Badge from '../ui/Badge';

export default function TestResultsPanel({ result, running = false }) {
  if (running) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-xs text-slate-500 space-y-3">
        <div className="inline-flex p-3 rounded-full bg-slate-100 text-indigo-600 animate-pulse">
          <Terminal className="w-5 h-5" />
        </div>
        <p className="font-medium text-slate-700">Submitting Java code to Judge0 execution sandbox...</p>
        <p className="text-2xs text-slate-400">Compiling with OpenJDK 14 and evaluating against benchmark test suites</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-xs text-slate-400 space-y-2">
        <Terminal className="w-6 h-6 mx-auto text-slate-300" />
        <p>No execution results yet. Click "Run Code & Evaluate" to test your solution.</p>
      </div>
    );
  }

  const isAccepted = result.is_passed;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-5">
      {/* Header Status Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          {isAccepted ? (
            <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          ) : (
            <div className="p-2 rounded-lg bg-rose-100 text-rose-700">
              <XCircle className="w-5 h-5" />
            </div>
          )}
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-bold text-slate-900 text-base">{result.status}</h3>
              <Badge variant={isAccepted ? 'success' : 'danger'}>
                {result.test_cases_passed} / {result.total_test_cases} Test Cases Passed
              </Badge>
            </div>
            {result.execution_time_ms !== undefined && (
              <p className="text-2xs text-slate-500 font-mono mt-0.5">
                Execution Time: {result.execution_time_ms.toFixed(1)} ms
              </p>
            )}
          </div>
        </div>

        {/* BKT Mastery Update Badge */}
        {result.bkt_updated_mastery !== undefined && (
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-xs">
            <TrendingUp className="w-3.5 h-3.5 text-indigo-600" />
            <span className="text-slate-600">Updated Mastery p(L):</span>
            <span className="font-mono font-bold text-indigo-700">
              {(result.bkt_updated_mastery * 100).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Adaptive Intervention Recommendation */}
      {result.triggered_intervention && (
        <div className="p-3.5 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
          <div className="flex items-center space-x-2 font-semibold">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Recommended Cognitive Intervention: {result.triggered_intervention.strategy}</span>
          </div>
          <p className="text-2xs text-amber-800 leading-relaxed pl-6">
            {result.triggered_intervention.message}
          </p>
        </div>
      )}

      {/* Compiler / Runtime Errors */}
      {(result.compile_error || result.runtime_error) && (
        <div className="space-y-1.5">
          <span className="text-xs font-semibold text-rose-700 flex items-center space-x-1">
            <Info className="w-3.5 h-3.5" />
            <span>Diagnostic Execution Output</span>
          </span>
          <pre className="p-3 rounded-lg bg-slate-900 text-rose-300 font-mono text-2xs overflow-x-auto whitespace-pre-wrap">
            {result.compile_error || result.runtime_error}
          </pre>
        </div>
      )}

      {/* Test Cases Output Grid */}
      {result.test_case_results && result.test_case_results.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-700">Evaluated Test Cases</p>
          <div className="space-y-2">
            {result.test_case_results.map((tc) => (
              <div
                key={tc.test_case_id}
                className={`p-3 rounded-lg border text-xs font-mono space-y-1 ${
                  tc.passed ? 'border-emerald-200 bg-emerald-50/30' : 'border-rose-200 bg-rose-50/30'
                }`}
              >
                <div className="flex items-center justify-between text-2xs">
                  <span className="font-bold text-slate-700">Test Case #{tc.test_case_id}</span>
                  <span className={tc.passed ? 'text-emerald-700 font-bold' : 'text-rose-700 font-bold'}>
                    {tc.passed ? 'PASSED' : 'FAILED'}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-2xs pt-1">
                  <div>
                    <span className="text-slate-500">Input: </span>
                    <span className="text-slate-900">{tc.input}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Expected: </span>
                    <span className="text-slate-900">{tc.expected_output}</span>
                  </div>
                </div>
                {tc.actual_output && !tc.passed && (
                  <div className="text-2xs text-rose-600 pt-0.5">
                    <span>Actual Output: </span>
                    <span>{tc.actual_output}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
