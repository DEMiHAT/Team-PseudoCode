import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Play, RotateCcw, ArrowLeft, Lightbulb, Terminal, AlertCircle } from 'lucide-react';
import { curriculumService } from '../services/curriculumService';
import { executionService } from '../services/executionService';
import { tutoringService } from '../services/tutoringService';
import CodeEditor from '../components/workspace/CodeEditor';
import ScaffoldingPanel from '../components/workspace/ScaffoldingPanel';
import TestResultsPanel from '../components/workspace/TestResultsPanel';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';

export default function WorkspacePage() {
  const { problemId = '1' } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
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
        <Terminal className="w-8 h-8 mx-auto text-slate-300 animate-pulse" />
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
      {/* Top Workspace Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center space-x-3">
          <Link to="/" className="text-slate-400 hover:text-slate-700 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-900">{problem.title}</h1>
              <Badge variant={problem.difficulty === 'Easy' ? 'success' : 'warning'}>
                {problem.difficulty}
              </Badge>
            </div>
            <p className="text-2xs text-slate-500 font-mono mt-0.5">Problem ID: #{problem.id} • OpenJDK 14</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleResetCode} icon={RotateCcw}>
            Reset Code
          </Button>
          <Button variant="primary" size="sm" onClick={handleRunCode} disabled={executing} icon={Play}>
            {executing ? 'Evaluating...' : 'Run Code & Evaluate'}
          </Button>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Problem Description & Scaffolding */}
        <div className="lg:col-span-5 space-y-6">
          {/* Problem Statement Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider">Problem Specification</h2>
            <div className="prose prose-sm text-xs text-slate-700 leading-relaxed space-y-3">
              <p className="whitespace-pre-line">{problem.description_md}</p>
            </div>

            {/* Public Test Cases Preview */}
            {problem.sample_test_cases && problem.sample_test_cases.length > 0 && (
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <span className="text-2xs font-bold text-slate-500 uppercase tracking-wider">Sample Test Cases</span>
                <div className="space-y-2">
                  {problem.sample_test_cases.map((tc) => (
                    <div key={tc.id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-2xs font-mono">
                      <div>
                        <span className="text-slate-500 font-semibold">Input: </span>
                        <span className="text-slate-900">{tc.input}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 font-semibold">Expected: </span>
                        <span className="text-slate-900">{tc.expected_output}</span>
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

        {/* Right Column: Monaco Code Editor & Test Results */}
        <div className="lg:col-span-7 space-y-6">
          {/* Code Editor */}
          <CodeEditor
            value={code}
            onChange={setCode}
            language="java"
            height="460px"
          />

          {/* Execution & Misconception Results */}
          <TestResultsPanel result={executionResult} running={executing} />
        </div>
      </div>
    </div>
  );
}

