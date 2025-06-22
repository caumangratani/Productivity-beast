import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdvancedAnalytics = ({ currentUser }) => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [selectedMetric, setSelectedMetric] = useState('productivity');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedPeriod, selectedMetric]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      // Generate comprehensive analytics data
      const data = generateAdvancedAnalytics();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
    setLoading(false);
  };

  const generateAdvancedAnalytics = () => {
    // Advanced analytics simulation with comprehensive metrics
    return {
      productivity_overview: {
        current_score: 8.2,
        previous_score: 7.8,
        trend: 'increasing',
        change_percentage: 5.1,
        benchmark: 7.5,
        industry_percentile: 85
      },
      time_analytics: {
        total_focus_time: 32.5,
        average_session_length: 28,
        peak_hours: ['9:00-11:00', '14:00-16:00'],
        distraction_incidents: 12,
        break_compliance: 85,
        deep_work_ratio: 72
      },
      task_analytics: {
        completion_rate: 87,
        average_completion_time: 2.3,
        overdue_rate: 8,
        priority_distribution: {
          urgent_important: 15,
          important_not_urgent: 55,
          urgent_not_important: 20,
          not_urgent_not_important: 10
        },
        complexity_breakdown: {
          simple: 40,
          moderate: 45,
          complex: 15
        }
      },
      team_analytics: {
        collaboration_score: 9.1,
        communication_frequency: 45,
        project_delivery_rate: 92,
        team_satisfaction: 8.7,
        knowledge_sharing: 78,
        mentoring_hours: 8.5
      },
      ai_insights: {
        recommendations_followed: 68,
        coaching_effectiveness: 8.4,
        personalization_score: 91,
        goal_achievement_probability: 82,
        stress_indicators: [
          { metric: 'Workload', level: 'moderate', score: 6.2 },
          { metric: 'Deadlines', level: 'low', score: 3.1 },
          { metric: 'Complexity', level: 'moderate', score: 5.8 }
        ]
      },
      weekly_trends: [
        { day: 'Mon', productivity: 8.1, focus: 7.8, collaboration: 8.5 },
        { day: 'Tue', productivity: 8.7, focus: 8.9, collaboration: 8.2 },
        { day: 'Wed', productivity: 8.3, focus: 8.1, collaboration: 8.8 },
        { day: 'Thu', productivity: 8.9, focus: 9.2, collaboration: 8.6 },
        { day: 'Fri', productivity: 7.8, focus: 7.5, collaboration: 9.1 }
      ],
      monthly_comparison: [
        { month: 'Jan', productivity: 7.2, tasks_completed: 148, team_score: 8.1 },
        { month: 'Feb', productivity: 7.8, tasks_completed: 165, team_score: 8.4 },
        { month: 'Mar', productivity: 8.2, tasks_completed: 182, team_score: 8.7 },
        { month: 'Apr', productivity: 8.5, tasks_completed: 195, team_score: 8.9 }
      ],
      performance_predictions: {
        next_week_productivity: 8.6,
        goal_completion_likelihood: 85,
        burnout_risk: 15,
        optimal_workload: 85,
        recommended_adjustments: [
          'Increase deep work blocks by 20%',
          'Reduce meeting frequency on Thursdays',
          'Schedule break reminders every 90 minutes'
        ]
      },
      financial_impact: {
        time_saved_hours: 12.5,
        cost_savings: 25000,
        roi_percentage: 340,
        efficiency_gains: 28
      }
    };
  };

  const getProgressColor = (value, threshold = 70) => {
    if (value >= threshold) return 'text-green-600';
    if (value >= threshold * 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCircularProgress = (value, max = 10) => {
    const percentage = (value / max) * 100;
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (percentage / 100) * circumference;
    
    return (
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-gray-200"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="text-purple-600 transition-all duration-1000"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{value}</div>
            <div className="text-xs text-gray-500">/{max}</div>
          </div>
        </div>
      </div>
    );
  };

  if (loading || !analyticsData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">📊 Advanced Analytics</h2>
          <p className="text-gray-600 mt-1">Comprehensive productivity insights and performance tracking</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="select-field"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="select-field"
          >
            <option value="productivity">Productivity</option>
            <option value="focus">Focus Time</option>
            <option value="collaboration">Collaboration</option>
            <option value="wellbeing">Wellbeing</option>
          </select>
        </div>
      </div>

      {/* Executive Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stats-card bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Productivity Score</p>
              <p className="text-3xl font-bold">{analyticsData.productivity_overview.current_score}/10</p>
              <p className="text-sm text-purple-200">
                {analyticsData.productivity_overview.trend === 'increasing' ? '↗️' : '↘️'} 
                {analyticsData.productivity_overview.change_percentage}% vs last period
              </p>
            </div>
            <div className="text-4xl">🚀</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Focus Time</p>
              <p className="text-3xl font-bold">{analyticsData.time_analytics.total_focus_time}h</p>
              <p className="text-sm text-blue-200">
                Avg session: {analyticsData.time_analytics.average_session_length}min
              </p>
            </div>
            <div className="text-4xl">🎯</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Task Completion</p>
              <p className="text-3xl font-bold">{analyticsData.task_analytics.completion_rate}%</p>
              <p className="text-sm text-green-200">
                Avg time: {analyticsData.task_analytics.average_completion_time}h
              </p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Team Score</p>
              <p className="text-3xl font-bold">{analyticsData.team_analytics.collaboration_score}/10</p>
              <p className="text-sm text-orange-200">
                Satisfaction: {analyticsData.team_analytics.team_satisfaction}/10
              </p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>
      </div>

      {/* Detailed Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Productivity Breakdown */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Productivity Breakdown</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Deep Work Ratio</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${analyticsData.time_analytics.deep_work_ratio}%` }}
                  ></div>
                </div>
                <span className="font-medium">{analyticsData.time_analytics.deep_work_ratio}%</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-700">Break Compliance</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${analyticsData.time_analytics.break_compliance}%` }}
                  ></div>
                </div>
                <span className="font-medium">{analyticsData.time_analytics.break_compliance}%</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-gray-700">AI Recommendations Followed</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${analyticsData.ai_insights.recommendations_followed}%` }}
                  ></div>
                </div>
                <span className="font-medium">{analyticsData.ai_insights.recommendations_followed}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Eisenhower Matrix Distribution */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Task Priority Distribution</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-red-50 rounded-lg border border-red-200">
              <h4 className="font-medium text-red-900">🔥 Do First</h4>
              <div className="text-2xl font-bold text-red-600">
                {analyticsData.task_analytics.priority_distribution.urgent_important}%
              </div>
              <p className="text-sm text-red-700">Urgent & Important</p>
            </div>
            
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900">📅 Schedule</h4>
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData.task_analytics.priority_distribution.important_not_urgent}%
              </div>
              <p className="text-sm text-blue-700">Important, Not Urgent</p>
            </div>
            
            <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <h4 className="font-medium text-yellow-900">🤝 Delegate</h4>
              <div className="text-2xl font-bold text-yellow-600">
                {analyticsData.task_analytics.priority_distribution.urgent_not_important}%
              </div>
              <p className="text-sm text-yellow-700">Urgent, Not Important</p>
            </div>
            
            <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="font-medium text-gray-900">🗑️ Eliminate</h4>
              <div className="text-2xl font-bold text-gray-600">
                {analyticsData.task_analytics.priority_distribution.not_urgent_not_important}%
              </div>
              <p className="text-sm text-gray-700">Neither Urgent nor Important</p>
            </div>
          </div>
        </div>

        {/* Weekly Performance Trends */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📅 Weekly Performance Trends</h3>
          <div className="space-y-3">
            {analyticsData.weekly_trends.map((day, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className="w-12 text-sm font-medium text-gray-700">{day.day}</div>
                <div className="flex-1 grid grid-cols-3 gap-2">
                  <div className="text-center">
                    <div className="text-xs text-gray-500 mb-1">Productivity</div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${(day.productivity / 10) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs font-medium mt-1">{day.productivity}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500 mb-1">Focus</div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(day.focus / 10) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs font-medium mt-1">{day.focus}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-xs text-gray-500 mb-1">Team</div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full"
                        style={{ width: `${(day.collaboration / 10) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-xs font-medium mt-1">{day.collaboration}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI-Powered Predictions */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔮 AI Performance Predictions</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <div>
                <h4 className="font-medium text-green-900">Next Week Productivity</h4>
                <p className="text-sm text-green-700">Based on current trends</p>
              </div>
              <div className="text-2xl font-bold text-green-600">
                {analyticsData.performance_predictions.next_week_productivity}/10
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <div>
                <h4 className="font-medium text-blue-900">Goal Completion Likelihood</h4>
                <p className="text-sm text-blue-700">Current trajectory</p>
              </div>
              <div className="text-2xl font-bold text-blue-600">
                {analyticsData.performance_predictions.goal_completion_likelihood}%
              </div>
            </div>

            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <div>
                <h4 className="font-medium text-yellow-900">Burnout Risk</h4>
                <p className="text-sm text-yellow-700">Stress indicators</p>
              </div>
              <div className="text-2xl font-bold text-yellow-600">
                {analyticsData.performance_predictions.burnout_risk}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Financial Impact */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💰 Financial Impact (Indian Rupees)</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">₹{analyticsData.financial_impact.cost_savings.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Cost Savings</div>
            <div className="text-xs text-gray-500">Per month</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{analyticsData.financial_impact.time_saved_hours}h</div>
            <div className="text-sm text-gray-600">Time Saved</div>
            <div className="text-xs text-gray-500">Per week</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{analyticsData.financial_impact.roi_percentage}%</div>
            <div className="text-sm text-gray-600">ROI</div>
            <div className="text-xs text-gray-500">Annual</div>
          </div>
          
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{analyticsData.financial_impact.efficiency_gains}%</div>
            <div className="text-sm text-gray-600">Efficiency Gains</div>
            <div className="text-xs text-gray-500">Overall</div>
          </div>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI-Powered Recommendations</h3>
        <div className="space-y-3">
          {analyticsData.performance_predictions.recommended_adjustments.map((recommendation, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg border border-purple-200">
              <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9.664 1.319a.75.75 0 01.672 0 41.059 41.059 0 018.198 5.424.75.75 0 01-.254 1.285 31.372 31.372 0 00-7.86 3.83.75.75 0 01-.84 0 31.508 31.508 0 00-2.08-1.287V9.394c0-.244.116-.463.302-.592a35.504 35.504 0 013.305-2.033.75.75 0 00-.714-1.319 37 37 0 00-3.446 2.12A2.216 2.216 0 006 9.393v.38a31.293 31.293 0 00-4.28-1.746.75.75 0 01-.254-1.285 41.059 41.059 0 018.198-5.424zM6 11.459a29.848 29.848 0 00-2.455-1.158 41.029 41.029 0 00-.39 3.114.75.75 0 00.419.74c.528.256 1.046.53 1.554.82-.21-.899-.419-1.81-.628-2.716zM18 15.459c0-1.44-.275-2.824-.777-4.105.142.631.262 1.27.337 1.914.75.75 0 00.419-.74 41.029 41.029 0 00-.39-3.114 29.733 29.733 0 00-2.455 1.158 39.497 39.497 0 00-.628 2.716c.508-.29 1.026-.564 1.554-.82z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm text-purple-800">{recommendation}</p>
              </div>
              <button className="text-sm text-purple-600 hover:text-purple-800">Apply</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;