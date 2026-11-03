import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Terminal, CheckCircle2, ChevronRight, Award, Target, Activity, AlertCircle } from 'lucide-react';
import { curriculumService } from '../services/curriculumService';
import { learnerService } from '../services/learnerService';
import StatCard from '../components/ui/StatCard';
import ProgressBar from '../components/ui/ProgressBar';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';

export default function DashboardPage() {
  const [concepts, setConcepts] = useState([]);
  const [problems, setProblems] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const [cRes, pRes, profRes] = await Promise.all([
          curriculumService.getConcepts(1),
          curriculumService.getProblems(),
          learnerService.getProfile(1),
        ]);

        if (cRes.success) setConcepts(cRes.data);
        if (pRes.success) setProblems(pRes.data);
        if (profRes.success) setProfile(profRes.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
        setError(err.message || 'Unable to connect to backend service.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Course Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 md:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-100">
              <span>IT22301 • Semester III</span>
              <span>•</span>
              <span>B.Tech Information Technology</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight">
              Data Structures and Algorithms
            </h1>
            <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
              Intelligent 1-to-1 Learning Support System. Diagnoses cognitive misconceptions in Java implementations, provides progressive scaffolding, and models skill acquisition using Bayesian Knowledge Tracing.
            </p>
          </div>

          {profile && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 md:w-72 shrink-0 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-800">{profile.learner.full_name}</span>
                <span className="font-mono text-2xs text-slate-500">{profile.learner.student_id}</span>
              </div>
              <ProgressBar
                value={profile.overall_mastery_index}
                label="Overall BKT Mastery Index"
                showPercentage={true}
              />
              <p className="text-2xs text-slate-500">
                Cognitive mastery computed across {concepts.length} syllabus learning units.
              </p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-600" />
          <div>
            <p className="font-semibold">Backend Connection Notice</p>
            <p className="text-rose-700 mt-0.5">{error}. Verify the FastAPI backend is running on port 8000.</p>
          </div>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Syllabus Units"
          value={concepts.length || 10}
          subtitle="4 Comprehensive Units"
          icon={BookOpen}
        />
        <StatCard
          title="Practice Problems"
          value={problems.length || 3}
          subtitle="Java DSA Exercises"
          icon={Terminal}
        />
        <StatCard
          title="Cognitive Model"
          value="BKT Engine"
          subtitle="p(L0), p(T), p(G), p(S)"
          icon={Activity}
        />
        <StatCard
          title="Scaffolding Tiers"
          value="4 Levels"
          subtitle="Concept to Code Skeleton"
          icon={Target}
        />
      </div>

      {/* Main Content: Concepts & Problems */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Syllabus Units & Concepts */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">Curriculum Units & Knowledge State</h2>
            <Link to="/analytics" className="text-xs font-semibold text-indigo-700 hover:text-indigo-800">
              View Detailed Analytics
            </Link>
          </div>

          <div className="space-y-3">
            {concepts.map((concept) => (
              <div
                key={concept.id}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs hover:border-slate-300 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-2xs text-slate-500 font-semibold">{concept.code}</span>
                      <span className="text-2xs text-slate-300">•</span>
                      <span className="text-2xs font-medium text-slate-500">{concept.category}</span>
                    </div>
                    <h3 className="font-bold text-slate-900 text-sm">{concept.name}</h3>
                    <p className="text-xs text-slate-600 line-clamp-2">{concept.description}</p>
                  </div>

                  <div className="sm:w-44 shrink-0 space-y-1.5 pt-2 sm:pt-0">
                    <ProgressBar
                      value={(concept.current_mastery_p || 0.2) * 100}
                      label="BKT Mastery"
                      showPercentage={true}
                    />
                    <div className="flex items-center justify-between text-2xs text-slate-500">
                      <span>{concept.problem_count} Problem(s)</span>
                      <span>
                        {(concept.current_mastery_p || 0.2) >= 0.85 ? (
                          <span className="text-emerald-700 font-semibold">Mastered</span>
                        ) : (
                          <span className="text-indigo-700 font-semibold">In Progress</span>
                        )}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Benchmark Coding Problems */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900">Benchmark Problems</h2>
            <Badge variant="primary">{problems.length} Available</Badge>
          </div>

          <div className="space-y-3">
            {problems.map((problem) => (
              <div
                key={problem.id}
                className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs space-y-3 hover:border-slate-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="font-mono text-2xs text-slate-500">{problem.concept_code}</span>
                    <h4 className="font-bold text-slate-900 text-sm">{problem.title}</h4>
                  </div>
                  <Badge variant={problem.difficulty === 'Easy' ? 'success' : 'warning'} size="sm">
                    {problem.difficulty}
                  </Badge>
                </div>

                <div className="pt-1 flex items-center justify-between">
                  <span className="text-2xs text-slate-500">Java • Judge0 CE Ready</span>
                  <Link to={`/workspace/${problem.id}`}>
                    <Button size="sm" variant="outline" icon={ChevronRight}>
                      Open Workspace
                    </Button>
                  </Link>
                </div>
              </div>
            ))}

            {problems.length === 0 && !loading && (
              <div className="p-8 text-center text-xs text-slate-400 bg-white rounded-xl border border-slate-200">
                No problems found. Start the backend to initialize seed content.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

