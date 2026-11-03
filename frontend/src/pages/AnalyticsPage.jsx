import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { BarChart2, Activity, Award, CheckCircle2, TrendingUp } from 'lucide-react';
import { learnerService } from '../services/learnerService';
import StatCard from '../components/ui/StatCard';
import ProgressBar from '../components/ui/ProgressBar';
import Badge from '../components/ui/Badge';

export default function AnalyticsPage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      setLoading(true);
      try {
        const res = await learnerService.getProfile(1);
        if (res.success) {
          setProfile(res.data);
        }
      } catch (err) {
        console.error('Failed to load learner analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  const chartData = (profile?.mastery_overview || []).map((item) => ({
    name: item.concept_code.replace('IT22301-', ''),
    fullName: item.concept_name,
    mastery: item.mastery_percentage,
    attempts: item.total_attempts,
    successes: item.successful_attempts,
  }));

  const masteredCount = (profile?.mastery_overview || []).filter(
    (item) => item.mastery_percentage >= 85
  ).length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <BarChart2 className="w-5 h-5 text-indigo-700" />
              <h1 className="text-xl font-bold text-slate-900">Knowledge State & Cognitive Analytics</h1>
            </div>
            <p className="text-xs text-slate-600 mt-1">
              Bayesian Knowledge Tracing estimates of latent skill mastery across IT22301 syllabus topics.
            </p>
          </div>

          {profile && (
            <div className="flex items-center space-x-3 text-xs bg-slate-50 px-3 py-2 rounded-xl border border-slate-200">
              <span className="font-semibold text-slate-800">{profile.learner.full_name}</span>
              <span className="font-mono text-2xs text-slate-500">ID: {profile.learner.student_id}</span>
            </div>
          )}
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Overall Mastery Index"
          value={`${profile?.overall_mastery_index || 20.0}%`}
          subtitle="Aggregated BKT latent state"
          icon={TrendingUp}
        />
        <StatCard
          title="Mastered Units"
          value={`${masteredCount} / ${profile?.mastery_overview?.length || 10}`}
          subtitle="p(L) >= 0.85 threshold"
          icon={Award}
        />
        <StatCard
          title="Total Practice Runs"
          value={profile?.mastery_overview?.reduce((acc, curr) => acc + curr.total_attempts, 0) || 0}
          subtitle="Logged executions"
          icon={Activity}
        />
        <StatCard
          title="Model Specification"
          value="Standard BKT"
          subtitle="Corbin & Anderson Model"
          icon={CheckCircle2}
        />
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Bar Chart: Mastery Percentage by Concept */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Mastery Distribution by Syllabus Concept</h2>
            <p className="text-2xs text-slate-500">BKT probability percentage P(L_t) * 100</p>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} angle={-25} textAnchor="end" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip
                  formatter={(val) => [`${val}%`, 'Mastery']}
                  labelFormatter={(name, payload) => payload?.[0]?.payload?.fullName || name}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: '#f8fafc',
                  }}
                />
                <Bar dataKey="mastery" fill="#4338ca" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar Chart: Multi-dimensional Profile */}
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Cognitive Profile Radar</h2>
            <p className="text-2xs text-slate-500">Multi-axis proficiency mapping</p>
          </div>

          <div className="h-72 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={chartData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="name" tick={{ fontSize: 9, fill: '#475569' }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 8, fill: '#94a3b8' }} />
                <Radar name="Mastery %" dataKey="mastery" stroke="#4338ca" fill="#4338ca" fillOpacity={0.25} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Concept Breakdown Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
          <h2 className="text-sm font-bold text-slate-900">Cognitive Parameters & Attempt Metrics</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-2xs border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 font-semibold">Concept Code</th>
                <th className="px-6 py-3 font-semibold">Concept Name</th>
                <th className="px-6 py-3 font-semibold">Category</th>
                <th className="px-6 py-3 font-semibold">p(L) Probability</th>
                <th className="px-6 py-3 font-semibold">Mastery Status</th>
                <th className="px-6 py-3 font-semibold text-right">Attempts (Success/Total)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-slate-700">
              {(profile?.mastery_overview || []).map((item) => (
                <tr key={item.concept_id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-6 py-3.5 font-bold text-slate-900">{item.concept_code}</td>
                  <td className="px-6 py-3.5 font-sans font-medium text-slate-800">{item.concept_name}</td>
                  <td className="px-6 py-3.5 font-sans text-slate-500">{item.category}</td>
                  <td className="px-6 py-3.5">
                    <span className="font-bold text-indigo-700">{item.p_known.toFixed(3)}</span>
                    <span className="text-slate-400 text-2xs ml-1.5">({item.mastery_percentage}%)</span>
                  </td>
                  <td className="px-6 py-3.5 font-sans">
                    {item.mastery_percentage >= 85 ? (
                      <Badge variant="success" size="sm">
                        Mastered
                      </Badge>
                    ) : (
                      <Badge variant="neutral" size="sm">
                        In Progress
                      </Badge>
                    )}
                  </td>
                  <td className="px-6 py-3.5 text-right font-medium">
                    {item.successful_attempts} / {item.total_attempts}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

