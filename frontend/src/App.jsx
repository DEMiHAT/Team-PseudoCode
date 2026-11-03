import { useState, useEffect } from 'react';
import { checkHealth, API_BASE_URL } from './services/api';
import { 
  BookOpen, 
  Brain, 
  CheckCircle2, 
  AlertCircle, 
  RefreshCw, 
  ArrowRight, 
  Sparkles, 
  Target, 
  Lightbulb, 
  Activity, 
  Server, 
  Database 
} from 'lucide-react';

export default function App() {
  const [healthStatus, setHealthStatus] = useState({
    loading: true,
    connected: false,
    data: null,
    error: null,
  });

  const [started, setStarted] = useState(false);

  // Fetch health check status on mount
  const runHealthCheck = async () => {
    setHealthStatus(prev => ({ ...prev, loading: true, error: null }));
    const result = await checkHealth();
    if (result.success) {
      setHealthStatus({
        loading: false,
        connected: true,
        data: result.data,
        error: null,
      });
    } else {
      setHealthStatus({
        loading: false,
        connected: false,
        data: null,
        error: result.error,
      });
    }
  };

  useEffect(() => {
    runHealthCheck();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <Brain className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-900 to-indigo-700 bg-clip-text text-transparent">
                Adaptive Learning
              </span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                Class 8 Math
              </span>
            </div>
          </div>

          {/* Backend Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg border bg-slate-50">
              <span className="relative flex h-2.5 w-2.5">
                {healthStatus.connected && (
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                )}
                <span
                  className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                    healthStatus.loading
                      ? 'bg-amber-400'
                      : healthStatus.connected
                      ? 'bg-emerald-500'
                      : 'bg-rose-500'
                  }`}
                ></span>
              </span>
              <span className="text-slate-600">
                {healthStatus.loading
                  ? 'Connecting...'
                  : healthStatus.connected
                  ? 'Backend Online'
                  : 'Backend Offline'}
              </span>
            </div>

            <button
              onClick={runHealthCheck}
              title="Refresh connection status"
              disabled={healthStatus.loading}
              className="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-slate-100 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${healthStatus.loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full space-y-12">
        
        {/* Hero Section */}
        <div className="text-center space-y-6 pt-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100">
            <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
            <span>Hackathon Project Boilerplate • Ready to Build</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
            Empowering the Individual
            <span className="block text-indigo-600 mt-1">
              One-to-One Learning Support System
            </span>
          </h1>

          <p className="text-lg text-slate-600 leading-relaxed">
            An intelligent, student-centered platform for <strong>Class 8 Mathematics</strong>. 
            It diagnoses underlying student misconceptions, serves adaptive scaffolds, assesses independent mastery, and remembers which explanations work best.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <button
              onClick={() => setStarted(true)}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200 transition-all transform hover:-translate-y-0.5 flex items-center justify-center space-x-2 group cursor-pointer"
            >
              <span>Start Learning</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <a
              href={`${API_BASE_URL}/docs`}
              target="_blank"
              rel="noreferrer"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-semibold text-slate-700 bg-white hover:bg-slate-50 border border-slate-300 shadow-sm transition-all flex items-center justify-center space-x-2"
            >
              <Server className="w-4 h-4 text-slate-500" />
              <span>Explore FastAPI Docs</span>
            </a>
          </div>

          {/* Modal / Toast when Start Learning clicked */}
          {started && (
            <div className="mt-6 p-4 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-900 text-sm animate-fadeIn flex items-center justify-between">
              <div className="flex items-center space-x-3 text-left">
                <CheckCircle2 className="w-5 h-5 text-indigo-600 shrink-0" />
                <div>
                  <p className="font-semibold">Boilerplate initialized & running!</p>
                  <p className="text-indigo-700 text-xs">
                    Next step: connect your question bank and Bayesian Knowledge Tracing (BKT) engine.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setStarted(false)}
                className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-100 hover:bg-indigo-200 text-indigo-800 transition-colors"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>

        {/* Live System Status Banner */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-800 flex items-center space-x-2">
                <Activity className="w-5 h-5 text-indigo-600" />
                <span>System Verification & Health Check</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Verifies communication between React Vite frontend, FastAPI backend, and SQLite database.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-500">Target:</span>
              <code className="text-xs font-mono bg-slate-100 px-2 py-1 rounded border border-slate-200 text-slate-700">
                {API_BASE_URL}/api/health
              </code>
            </div>
          </div>

          <div className="mt-5 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Frontend Status */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start space-x-3">
              <div className="p-2 rounded-lg bg-emerald-100 text-emerald-700 mt-0.5">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Frontend</p>
                <p className="font-bold text-slate-800">React + Vite + Tailwind</p>
                <p className="text-xs text-emerald-600 font-medium mt-0.5">Active on Port 5173</p>
              </div>
            </div>

            {/* Backend Status */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start space-x-3">
              <div
                className={`p-2 rounded-lg mt-0.5 ${
                  healthStatus.connected ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                }`}
              >
                {healthStatus.connected ? <Server className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Backend API</p>
                <p className="font-bold text-slate-800">Python + FastAPI</p>
                <p className={`text-xs font-medium mt-0.5 ${healthStatus.connected ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {healthStatus.loading
                    ? 'Probing backend...'
                    : healthStatus.connected
                    ? 'Connected (HTTP 200)'
                    : 'Unreachable'}
                </p>
              </div>
            </div>

            {/* Database Status */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-start space-x-3">
              <div
                className={`p-2 rounded-lg mt-0.5 ${
                  healthStatus.data?.database_connected ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
                }`}
              >
                <Database className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Database</p>
                <p className="font-bold text-slate-800">SQLite + SQLAlchemy</p>
                <p className={`text-xs font-medium mt-0.5 ${healthStatus.data?.database_connected ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {healthStatus.data?.database_connected ? 'Schema & Connection Ready' : 'Pending Server Response'}
                </p>
              </div>
            </div>
          </div>

          {/* Diagnostic payload preview */}
          {healthStatus.data && (
            <div className="mt-4 p-3 rounded-lg bg-slate-900 text-emerald-400 font-mono text-xs overflow-x-auto">
              <span className="text-slate-400">// Live backend response payload:</span>
              <pre>{JSON.stringify(healthStatus.data, null, 2)}</pre>
            </div>
          )}

          {healthStatus.error && (
            <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              <p className="font-semibold">Backend Connection Note:</p>
              <p className="mt-0.5">
                {healthStatus.error}. Make sure the FastAPI backend is running via{' '}
                <code className="bg-rose-100 px-1.5 py-0.5 rounded font-mono">
                  uvicorn app.main:app --reload
                </code>
              </p>
            </div>
          )}
        </div>

        {/* Core Pedagogical Pillars Grid */}
        <div className="space-y-4">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-900">Architecture & Pedagogical Flow</h2>
            <p className="text-sm text-slate-600">The 4-stage intelligent loop designed for individualized Math support</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
            {/* Card 1 */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:border-indigo-300 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
                <Target className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 text-base">1. Misconception Engine</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Rules-based diagnosis that detects predictable cognitive slips in Class 8 equations (e.g., sign transposition errors).
              </p>
            </div>

            {/* Card 2 */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:border-indigo-300 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-3">
                <Lightbulb className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 text-base">2. Targeted Explanations</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Scaffolded hints with predefined pedagogical fallbacks or an optional single LLM call for conversational guidance.
              </p>
            </div>

            {/* Card 3 */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:border-indigo-300 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
                <BookOpen className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 text-base">3. Independent Check</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Presents a similar transfer question to verify whether the student truly comprehended the concept independently.
              </p>
            </div>

            {/* Card 4 */}
            <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm hover:border-indigo-300 transition-colors">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-3">
                <Brain className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 text-base">4. Bayesian Knowledge Tracing</h3>
              <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                Tracks mastery probability p(L) over time, recording which intervention strategies yielded genuine learning gains.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-6">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-3">
          <p>
            <strong>Empowering the Individual</strong> • Class 8 Mathematics Intelligent Tutoring System
          </p>
          <p className="flex items-center space-x-2">
            <span>FastAPI • SQLAlchemy • SQLite • React • Vite • Tailwind</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
