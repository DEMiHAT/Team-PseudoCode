import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Play, CheckCircle, RotateCcw, ArrowLeft, Terminal, AlertCircle, RefreshCw } from 'lucide-react';
import { curriculumService } from '../services/curriculumService';
import { executionService } from '../services/executionService';
import { tutoringService } from '../services/tutoringService';
import CodeEditor from '../components/workspace/CodeEditor';
import ScaffoldingPanel from '../components/workspace/ScaffoldingPanel';
import TestResultsPanel from '../components/workspace/TestResultsPanel';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';

export default function WorkspacePage() {
  const { problemId = '2' } = useParams(); // Defaults to Valid Parentheses (ID 2)
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [scaffoldLoading, setScaffoldLoading] = useState(false);
  const [activeHint, setActiveHint] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadProblem() {
      setLoading(true);
      setError(null);
      try {
        const res = await curriculumService.getProblemDetail(problemId);
        if (res.success && res.data) {
          setProblem(res.data);
          setCode(res.data.starter_code_java);
        } else {
          setError('Problem not found or inactive.');
        }
      } catch (err) {
        console.error('Error loading problem:', err);
        setError(err.message || 'Failed to fetch problem workspace.');
      } finally {
        setLoading(false);
      }
    }
    loadProblem();
  }, [problemId]);

  const handleRunCode = async () => {
    setExecuting(true);
    try {
      const res = await executionService.runCode({
        learnerId: 1,
        problemId: parseInt(problemId, 10),
        code,
        language: 'java',
      });
      if (res.success) {
        setExecutionResult(res.data);
      }
    } catch (err) {
      console.error('Execution error:', err);
      setExecutionResult({
        status: 'Client Execution Error',
        is_passed: false,
        test_cases_passed: 0,
        total_test_cases: problem?.sample_test_cases?.length || 0,
        compile_error: err.message || 'Unable to communicate with execution server.',
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleSubmitCode = async () => {
    setSubmitting(true);
    try {
      const res = await executionService.submitCode({
        learnerId: 1,
        problemId: parseInt(problemId, 10),
        code,
        language: 'java',
      });
      if (res.success) {
        setExecutionResult(res.data);
      }
    } catch (err) {
      console.error('Submission error:', err);
      setExecutionResult({
        status: 'Submission Error',
        is_passed: false,
        test_cases_passed: 0,
        total_test_cases: problem?.sample_test_cases?.length || 0,
        compile_error: err.message || 'Submission failed.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleRequestHint = async (level) => {
    setScaffoldLoading(true);
    try {
      const res = await tutoringService.requestScaffold({
        learnerId: 1,
        problemId: parseInt(problemId, 10),
        currentCode: code,
        requestedLevel: level,
        compilerError: executionResult?.compile_error || null,
        failingTestInput: executionResult?.test_case_results?.find((t) => !t.passed)?.input || null,
      });
      if (res.success) {
        setActiveHint(res.data);
      }
    } catch (err) {
      console.error('Scaffolding request failed:', err);
    } finally {
      setScaffoldLoading(false);
    }
  };

  const handleResetCode = () => {
    if (problem) {
      setCode(problem.starter_code_java);
      setExecutionResult(null);
      setActiveHint(null);
    }
  };

  if (loading) {
    return (
      <div className="py-20 text-center text-xs text-slate-500 space-y-2">
        <Terminal className="w-8 h-8 mx-auto text-slate-400 animate-pulse" />
        <p>Loading IT22301 coding workspace...</p>
      </div>
    );
  }

  if (error || !problem) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <AlertCircle className="w-10 h-10 mx-auto text-rose-500" />
        <h2 className="text-base font-bold text-slate-800">Workspace Unavailable</h2>
        <p className="text-xs text-slate-600">{error || 'Requested problem not found.'}</p>
        <Link to="/">
          <Button variant="outline" size="sm" icon={ArrowLeft}>
            Return to Curriculum
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Workspace Header Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center space-x-3">
          <Link to="/" className="text-slate-400 hover:text-slate-700 transition-colors p-1.5 rounded-lg hover:bg-slate-100">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900">{problem.title}</h1>
              <Badge variant={problem.difficulty === 'Easy' ? 'success' : 'warning'}>
                {problem.difficulty}
              </Badge>
              <span className="text-2xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                IT22301 Unit 2
              </span>
            </div>
            <p className="text-2xs text-slate-500 font-mono mt-0.5">
              Activity #{problem.id} • Language: Java (OpenJDK 17)
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={handleResetCode}
            disabled={executing || submitting}
            icon={RotateCcw}
          >
            Reset
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={handleRunCode}
            disabled={executing || submitting}
            icon={executing ? RefreshCw : Play}
          >
            {executing ? 'Running...' : 'Run Tests'}
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleSubmitCode}
            disabled={executing || submitting}
            icon={submitting ? RefreshCw : CheckCircle}
          >
            {submitting ? 'Submitting...' : 'Submit Solution'}
          </Button>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Problem Description & Scaffolding */}
        <div className="lg:col-span-5 space-y-6">
          {/* Problem Statement Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Problem Specification
            </h2>
            <div className="text-xs text-slate-700 leading-relaxed space-y-3">
              <p className="whitespace-pre-line font-normal">{problem.description_md}</p>
            </div>

            {/* Test Cases Preview */}
            {problem.sample_test_cases && problem.sample_test_cases.length > 0 && (
              <div className="pt-4 border-t border-slate-100 space-y-2.5">
                <span className="text-2xs font-bold text-slate-500 uppercase tracking-wider block">
                  Benchmark Test Cases ({problem.sample_test_cases.length})
                </span>
                <div className="space-y-1.5 font-mono text-2xs">
                  {problem.sample_test_cases.map((tc) => (
                    <div
                      key={tc.id}
                      className="p-2 rounded bg-slate-50 border border-slate-200 flex items-center justify-between"
                    >
                      <div>
                        <span className="text-slate-500 font-semibold">Input: </span>
                        <span className="text-slate-900 font-bold">{tc.input || '<empty>'}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 font-semibold">Expected: </span>
                        <span className="text-emerald-700 font-bold">{tc.expected_output}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Progressive Scaffolding Panel */}
          <ScaffoldingPanel
            onRequestHint={handleRequestHint}
            loading={scaffoldLoading}
            activeHint={activeHint}
          />
        </div>

        {/* Right Column: Monaco Code Editor & Test Results Panel */}
        <div className="lg:col-span-7 space-y-6">
          <CodeEditor
            value={code}
            onChange={setCode}
            language="java"
            height="460px"
          />

          <TestResultsPanel
            result={executionResult}
            running={executing}
            submitting={submitting}
          />
        </div>
      </div>
    </div>
  );
}
