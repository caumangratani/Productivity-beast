import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TeamPerformance = ({ users }) => {
  const [teamPerformance, setTeamPerformance] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userPerformance, setUserPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTeamPerformance();
  }, []);

  const fetchTeamPerformance = async () => {
    try {
      const response = await axios.get(`${API}/analytics/team-performance`);
      setTeamPerformance(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching team performance:', error);
      setLoading(false);
    }
  };

  const fetchUserPerformance = async (userId) => {
    try {
      const response = await axios.get(`${API}/analytics/performance/${userId}`);
      setUserPerformance(response.data);
      setSelectedUser(userId);
    } catch (error) {
      console.error('Error fetching user performance:', error);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    if (score >= 4) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getPerformanceGrade = (score) => {
    if (score >= 9) return 'A+';
    if (score >= 8) return 'A';
    if (score >= 7) return 'B+';
    if (score >= 6) return 'B';
    if (score >= 5) return 'C+';
    if (score >= 4) return 'C';
    return 'D';
  };

  const generateFeedback = (performance) => {
    const { performance_score, completion_rate, tasks_overdue } = performance;
    
    if (performance_score >= 8 && completion_rate >= 80) {
      return {
        type: 'excellent',
        message: 'Outstanding performance! Keep up the excellent work.',
        suggestions: [
          'Consider mentoring team members with lower performance',
          'Take on more challenging or leadership tasks',
          'Share your productivity strategies with the team'
        ]
      };
    } else if (performance_score >= 6 && completion_rate >= 60) {
      return {
        type: 'good',
        message: 'Good performance with room for improvement.',
        suggestions: [
          'Focus on completing tasks before deadlines',
          'Break large tasks into smaller, manageable subtasks',
          'Use time-blocking techniques for better focus'
        ]
      };
    } else if (tasks_overdue > 0) {
      return {
        type: 'needs_attention',
        message: 'Performance needs attention due to overdue tasks.',
        suggestions: [
          'Prioritize overdue tasks immediately',
          'Set up daily reminder systems',
          'Consider requesting help or deadline extensions',
          'Review and adjust workload distribution'
        ]
      };
    } else {
      return {
        type: 'improvement',
        message: 'Performance below expectations. Let\'s work together to improve.',
        suggestions: [
          'Schedule a one-on-one meeting to discuss challenges',
          'Consider time management training',
          'Break tasks into smaller, achievable goals',
          'Set up more frequent check-ins and support'
        ]
      };
    }
  };

  if (loading) {
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
          <h2 className="text-3xl font-bold text-gray-900">Team Performance Analytics</h2>
          <p className="text-gray-600 mt-1">Monitor team productivity and provide targeted feedback</p>
        </div>
        <button
          onClick={fetchTeamPerformance}
          className="btn-primary"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
          Refresh Data
        </button>
      </div>

      {/* Team Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stats-card stats-card-total">
          <div className="text-center">
            <p className="text-2xl font-bold">{teamPerformance.length}</p>
            <p className="text-sm opacity-90">Team Members</p>
          </div>
        </div>
        
        <div className="stats-card stats-card-completed">
          <div className="text-center">
            <p className="text-2xl font-bold">
              {teamPerformance.filter(p => p.performance_score >= 8).length}
            </p>
            <p className="text-sm opacity-90">Top Performers</p>
          </div>
        </div>

        <div className="stats-card stats-card-progress">
          <div className="text-center">
            <p className="text-2xl font-bold">
              {teamPerformance.length > 0 ? 
                (teamPerformance.reduce((sum, p) => sum + p.completion_rate, 0) / teamPerformance.length).toFixed(1) 
                : 0}%
            </p>
            <p className="text-sm opacity-90">Avg Completion Rate</p>
          </div>
        </div>

        <div className="stats-card stats-card-overdue">
          <div className="text-center">
            <p className="text-2xl font-bold">
              {teamPerformance.reduce((sum, p) => sum + p.tasks_overdue, 0)}
            </p>
            <p className="text-sm opacity-90">Total Overdue Tasks</p>
          </div>
        </div>
      </div>

      {/* Performance Ranking */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Performance Ranking</h3>
        <div className="space-y-4">
          {teamPerformance.map((member, index) => (
            <div
              key={member.user_id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              onClick={() => fetchUserPerformance(member.user_id)}
            >
              <div className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                  index === 0 ? 'bg-yellow-500' : 
                  index === 1 ? 'bg-gray-400' : 
                  index === 2 ? 'bg-yellow-600' : 
                  'bg-purple-500'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{member.user_name}</h4>
                  <p className="text-sm text-gray-600">
                    {member.tasks_completed}/{member.tasks_assigned} tasks completed
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="flex items-center space-x-2">
                    <span className={`badge ${getPerformanceColor(member.performance_score)}`}>
                      {getPerformanceGrade(member.performance_score)}
                    </span>
                    <span className="font-bold text-lg">
                      {member.performance_score.toFixed(1)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {member.completion_rate.toFixed(1)}% completion
                  </p>
                </div>
                
                <div className="w-24">
                  <div className="performance-bar">
                    <div 
                      className="performance-fill" 
                      style={{ width: `${member.performance_score * 10}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Individual Performance Detail */}
      {userPerformance && (
        <div className="stats-card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-gray-900">
              {userPerformance.user_name}'s Performance Details
            </h3>
            <button
              onClick={() => {
                setSelectedUser(null);
                setUserPerformance(null);
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center">
              <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full text-2xl font-bold ${getPerformanceColor(userPerformance.performance_score)}`}>
                {getPerformanceGrade(userPerformance.performance_score)}
              </div>
              <p className="mt-2 font-semibold">Performance Grade</p>
              <p className="text-2xl font-bold text-purple-600">
                {userPerformance.performance_score.toFixed(1)}/10
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="mt-2 font-semibold">Completion Rate</p>
              <p className="text-2xl font-bold text-blue-600">
                {userPerformance.completion_rate.toFixed(1)}%
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="mt-2 font-semibold">Overdue Tasks</p>
              <p className="text-2xl font-bold text-red-600">
                {userPerformance.tasks_overdue}
              </p>
            </div>
          </div>

          {/* AI Feedback */}
          {(() => {
            const feedback = generateFeedback(userPerformance);
            return (
              <div className={`p-4 rounded-lg border-l-4 ${
                feedback.type === 'excellent' ? 'bg-green-50 border-green-400' :
                feedback.type === 'good' ? 'bg-blue-50 border-blue-400' :
                feedback.type === 'needs_attention' ? 'bg-yellow-50 border-yellow-400' :
                'bg-red-50 border-red-400'
              }`}>
                <div className="flex items-start space-x-3">
                  <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
                    feedback.type === 'excellent' ? 'bg-green-100 text-green-600' :
                    feedback.type === 'good' ? 'bg-blue-100 text-blue-600' :
                    feedback.type === 'needs_attention' ? 'bg-yellow-100 text-yellow-600' :
                    'bg-red-100 text-red-600'
                  }`}>
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-2">AI Performance Analysis</h4>
                    <p className="text-gray-700 mb-3">{feedback.message}</p>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Recommendations:</h5>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                        {feedback.suggestions.map((suggestion, index) => (
                          <li key={index}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}

          {/* Task Breakdown */}
          <div className="mt-6 grid grid-cols-3 gap-4 text-center">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{userPerformance.tasks_assigned}</p>
              <p className="text-sm text-gray-600">Total Assigned</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{userPerformance.tasks_completed}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-2xl font-bold text-red-600">{userPerformance.tasks_overdue}</p>
              <p className="text-sm text-gray-600">Overdue</p>
            </div>
          </div>
        </div>
      )}

      {/* Team Insights */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Insights & Recommendations</h3>
        <div className="space-y-4">
          {teamPerformance.length > 0 && (
            <>
              <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg">
                <svg className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-medium text-green-900">Top Performers</h4>
                  <p className="text-green-700">
                    {teamPerformance.filter(p => p.performance_score >= 8).map(p => p.user_name).join(', ') || 'None'} 
                    {teamPerformance.filter(p => p.performance_score >= 8).length > 0 && ' - Consider them for mentoring roles'}
                  </p>
                </div>
              </div>

              {teamPerformance.filter(p => p.performance_score < 6).length > 0 && (
                <div className="flex items-start space-x-3 p-4 bg-yellow-50 rounded-lg">
                  <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="font-medium text-yellow-900">Needs Support</h4>
                    <p className="text-yellow-700">
                      {teamPerformance.filter(p => p.performance_score < 6).map(p => p.user_name).join(', ')} 
                      - Schedule one-on-one meetings and provide additional support
                    </p>
                  </div>
                </div>
              )}

              {teamPerformance.reduce((sum, p) => sum + p.tasks_overdue, 0) > 0 && (
                <div className="flex items-start space-x-3 p-4 bg-red-50 rounded-lg">
                  <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <h4 className="font-medium text-red-900">Overdue Tasks Alert</h4>
                    <p className="text-red-700">
                      Team has {teamPerformance.reduce((sum, p) => sum + p.tasks_overdue, 0)} overdue tasks. 
                      Consider workload rebalancing or deadline adjustments.
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeamPerformance;