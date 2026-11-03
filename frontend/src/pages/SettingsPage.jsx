import React, { useState, useEffect } from 'react';
import { Server, Database, Cpu, Sparkles, RefreshCw, CheckCircle2, XCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { healthService } from '../services/healthService';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';

export default function SettingsPage() {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const res = await healthService.getSystemHealth();
      if (res.success) {
        setHealthData(res.data);
      }
    } catch (err) {
      console.error('Health probe failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Server className="w-5 h-5 text-indigo-700" />
            <h1 className="text-xl font-bold text-slate-900">Architecture & Service Status</h1>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            Live diagnostic overview of the backend API, persistence layer, and external microservice integrations.
          </p>
        </div>

        <Button onClick={fetchHealth} disabled={loading} size="sm" variant="outline" icon={RefreshCw}>
          {loading ? 'Probing Services...' : 'Re-probe Services'}
        </Button>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Backend API Service */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-slate-100 text-slate-800">
                <Server className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">FastAPI Application Server</h3>
                <p className="text-2xs text-slate-500 font-mono">Python 3.12 • Port 8000</p>
              </div>
            </div>
            <Badge variant={healthData ? 'success' : 'danger'}>
              {healthData ? 'Operational' : 'Offline'}
            </Badge>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Asynchronous REST backend serving domain endpoints, BKT cognitive modeling, and scaffolding orchestration.
          </p>
          <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-2xs font-mono text-slate-600">
            <div>
              <span className="text-slate-400">Environment: </span>
              <span className="font-semibold text-slate-800">{healthData?.environment || 'development'}</span>
            </div>
            <div>
              <span className="text-slate-400">CORS: </span>
              <span className="font-semibold text-slate-800">Enabled (Vite 5173)</span>
            </div>
          </div>
        </div>

        {/* Database Layer */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-emerald-50 text-emerald-800">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Persistence Layer</h3>
                <p className="text-2xs text-slate-500 font-mono">SQLite (PostgreSQL Ready)</p>
              </div>
            </div>
            <Badge variant={healthData?.database_connected ? 'success' : 'danger'}>
              {healthData?.database_connected ? 'Connected' : 'Disconnected'}
            </Badge>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            SQLAlchemy ORM configured with pooled connections and database-agnostic schema types for instant migration to PostgreSQL.
          </p>
          <div className="pt-2 border-t border-slate-100 text-2xs font-mono text-slate-600">
            <span className="text-slate-400">Target URL: </span>
            <span className="text-slate-800">sqlite:///./dsa_tutor.db</span>
          </div>
        </div>

        {/* External: Judge0 CE */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-indigo-50 text-indigo-800">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Judge0 CE Execution Server</h3>
                <p className="text-2xs text-slate-500 font-mono">Java Sandboxed Runner</p>
              </div>
            </div>
            {healthData?.services?.judge0?.is_healthy ? (
              <Badge variant="success">Online</Badge>
            ) : (
              <Badge variant="warning">Offline / Fallback</Badge>
            )}
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            {healthData?.services?.judge0?.message ||
              'Compiles and runs Java student code inside sandboxed containers against test vectors.'}
          </p>
          <div className="pt-2 border-t border-slate-100 text-2xs font-mono text-slate-600">
            <span className="text-slate-400">Endpoint: </span>
            <span className="text-slate-800">{healthData?.services?.judge0?.endpoint || 'http://localhost:2358'}</span>
          </div>
        </div>

        {/* External: Google Gemini */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-lg bg-purple-50 text-purple-800">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Google Gemini LLM Interface</h3>
                <p className="text-2xs text-slate-500 font-mono">Socratic Tutoring</p>
              </div>
            </div>
            {healthData?.services?.gemini?.is_healthy ? (
              <Badge variant="success">Connected</Badge>
            ) : (
              <Badge variant="neutral">Deterministic Fallback</Badge>
            )}
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            {healthData?.services?.gemini?.message ||
              'Generates contextual Socratic guidance. When unconfigured, the system automatically uses structured pedagogical templates.'}
          </p>
          <div className="pt-2 border-t border-slate-100 text-2xs font-mono text-slate-600">
            <span className="text-slate-400">Security: </span>
            <span className="text-slate-800">Key kept exclusively on backend server</span>
          </div>
        </div>
      </div>

      {/* Architectural Security Notice */}
      <div className="p-5 rounded-xl bg-slate-900 text-slate-300 text-xs space-y-2 border border-slate-800">
        <div className="flex items-center space-x-2 text-white font-semibold">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Architectural Integrity & Decoupling Guarantees</span>
        </div>
        <p className="text-2xs text-slate-400 leading-relaxed">
          1. <strong>Separation of Concerns:</strong> Learner intelligence (Bayesian Knowledge Tracing, progressive scaffolding rules) is decoupled from external LLM providers and DSA domain content.
          <br />
          2. <strong>Zero Credential Leakage:</strong> No API keys are exposed to the browser or frontend source code. All external communication is mediated through backend service abstractions.
          <br />
          3. <strong>Graceful Degradation:</strong> If Judge0 or Gemini endpoints are unreachable, the platform degrades gracefully using pre-seeded deterministic templates rather than failing or simulating fake connections.
        </p>
      </div>
    </div>
  );
}

