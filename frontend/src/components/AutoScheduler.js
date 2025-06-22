import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AutoScheduler = ({ currentUser }) => {
  const [tasks, setTasks] = useState([]);
  const [scheduleResults, setScheduleResults] = useState(null);
  const [optimalTimeResults, setOptimalTimeResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState({
    task_title: '',
    duration_minutes: 60,
    priority: 'medium',
    eisenhower_quadrant: 'decide'
  });

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const findOptimalTime = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auto-scheduler/optimal-time`, selectedTask);
      setOptimalTimeResults(response.data);
    } catch (error) {
      console.error('Error finding optimal time:', error);
      alert('Error finding optimal time: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const createEisenhowerSchedule = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auto-scheduler/eisenhower-schedule`, {
        tasks: tasks,
        date_range_days: 7,
        work_hours_start: 9,
        work_hours_end: 17
      });
      setScheduleResults(response.data);
    } catch (error) {
      console.error('Error creating schedule:', error);
      alert('Error creating schedule: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const formatDateTime = (isoString) => {
    return new Date(isoString).toLocaleString([], {
      weekday: 'short',
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getQuadrantColor = (quadrant) => {
    const colors = {
      'do': 'bg-red-100 text-red-800 border-red-200',
      'decide': 'bg-blue-100 text-blue-800 border-blue-200', 
      'delegate': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'delete': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return colors[quadrant] || colors['decide'];
  };

  const getEnergyColor = (level) => {
    const colors = {
      'High': 'text-green-600',
      'Medium': 'text-yellow-600',
      'Low': 'text-gray-600'
    };
    return colors[level] || colors['Medium'];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🤖 AI Auto-Scheduler</h2>
          <p className="text-gray-600 mt-1">Optimal time-block scheduling based on Eisenhower Matrix priority</p>
        </div>
      </div>

      {/* Single Task Optimal Time Finder */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Find Optimal Time Slot</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Task Title</label>
            <input
              type="text"
              value={selectedTask.task_title}
              onChange={(e) => setSelectedTask({...selectedTask, task_title: e.target.value})}
              className="input-field"
              placeholder="Enter task name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
            <input
              type="number"
              value={selectedTask.duration_minutes}
              onChange={(e) => setSelectedTask({...selectedTask, duration_minutes: parseInt(e.target.value)})}
              className="input-field"
              min="15"
              max="480"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Priority Level</label>
            <select
              value={selectedTask.priority}
              onChange={(e) => setSelectedTask({...selectedTask, priority: e.target.value})}
              className="select-field"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
              <option value="urgent">Urgent Priority</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Eisenhower Quadrant</label>
            <select
              value={selectedTask.eisenhower_quadrant}
              onChange={(e) => setSelectedTask({...selectedTask, eisenhower_quadrant: e.target.value})}
              className="select-field"
            >
              <option value="do">🔥 Do First (Urgent & Important)</option>
              <option value="decide">📅 Schedule (Important, Not Urgent)</option>
              <option value="delegate">🤝 Delegate (Urgent, Not Important)</option>
              <option value="delete">🗑️ Eliminate (Neither Urgent nor Important)</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={findOptimalTime}
          disabled={loading || !selectedTask.task_title}
          className="btn-primary"
        >
          {loading ? (
            <div className="loading-spinner"></div>
          ) : (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
          )}
          Find Optimal Time
        </button>

        {/* Optimal Time Results */}
        {optimalTimeResults && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <h4 className="font-semibold text-green-900 mb-3">⚡ Optimal Time Suggestions for: {optimalTimeResults.task_title}</h4>
            
            <div className="space-y-3">
              {optimalTimeResults.optimal_suggestions.map((suggestion, index) => (
                <div key={index} className={`p-3 rounded-lg border ${suggestion.recommended ? 'bg-white border-green-300' : 'bg-gray-50 border-gray-200'}`}>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h5 className="font-medium text-gray-900">{suggestion.slot_name}</h5>
                        {suggestion.recommended && (
                          <span className="badge badge-completed">⭐ Recommended</span>
                        )}
                        <span className={`text-sm font-medium ${getEnergyColor(suggestion.energy_level)}`}>
                          {suggestion.energy_level} Energy
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{suggestion.reasoning}</p>
                      <p className="text-sm font-medium text-gray-800">
                        📅 {formatDateTime(suggestion.start_time)} - {formatDateTime(suggestion.end_time)}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-purple-600">{suggestion.optimization_score}/10</div>
                      <div className="text-xs text-gray-500">Score</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">💡 Productivity Tips:</h5>
              <ul className="text-sm text-blue-800 space-y-1">
                {optimalTimeResults.productivity_tips.map((tip, index) => (
                  <li key={index}>• {tip}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Full Eisenhower Schedule */}
      <div className="stats-card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">📊 Eisenhower Matrix Auto-Schedule</h3>
          <button
            onClick={createEisenhowerSchedule}
            disabled={loading || tasks.length === 0}
            className="btn-primary"
          >
            {loading ? (
              <div className="loading-spinner"></div>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            )}
            Generate Smart Schedule
          </button>
        </div>
        
        <p className="text-gray-600 mb-4">
          Create an optimal weekly schedule for all your tasks based on Eisenhower Matrix prioritization
        </p>
        
        {scheduleResults && (
          <div className="space-y-6">
            {/* Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="stats-card bg-gradient-to-r from-red-500 to-red-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-red-100">Scheduled Tasks</p>
                    <p className="text-2xl font-bold">{scheduleResults.productivity_summary.tasks_scheduled}</p>
                  </div>
                  <div className="text-3xl">📅</div>
                </div>
              </div>
              
              <div className="stats-card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-100">Total Hours</p>
                    <p className="text-2xl font-bold">{scheduleResults.productivity_summary.total_scheduled_hours}</p>
                  </div>
                  <div className="text-3xl">⏰</div>
                </div>
              </div>
              
              <div className="stats-card bg-gradient-to-r from-green-500 to-green-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-100">Time Saved</p>
                    <p className="text-2xl font-bold">{scheduleResults.productivity_summary.potential_time_saved_hours}h</p>
                  </div>
                  <div className="text-3xl">💰</div>
                </div>
              </div>
              
              <div className="stats-card bg-gradient-to-r from-purple-500 to-purple-600 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-100">Efficiency Gain</p>
                    <p className="text-2xl font-bold">{scheduleResults.productivity_summary.efficiency_gain}</p>
                  </div>
                  <div className="text-3xl">🚀</div>
                </div>
              </div>
            </div>

            {/* Scheduled Tasks */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3">📅 Scheduled Tasks</h4>
              <div className="space-y-3">
                {scheduleResults.scheduled_tasks.map((task, index) => (
                  <div key={index} className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h5 className="font-medium text-gray-900">{task.task_title}</h5>
                          <span className={`badge ${getQuadrantColor(task.quadrant)}`}>
                            {task.quadrant.toUpperCase()}
                          </span>
                          <span className="badge badge-in_progress">
                            {task.energy_requirement} Energy
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{task.scheduling_rationale}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-700">
                          <span>📅 {formatDateTime(task.start_time)}</span>
                          <span>⏱️ {task.duration_minutes} min</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Delegation Suggestions */}
            {scheduleResults.delegation_suggestions.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">🤝 Delegation Suggestions</h4>
                <div className="space-y-3">
                  {scheduleResults.delegation_suggestions.map((task, index) => (
                    <div key={index} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <h5 className="font-medium text-yellow-900 mb-2">{task.task_title}</h5>
                      <p className="text-sm text-yellow-800 mb-2">{task.recommendation}</p>
                      <div className="text-sm text-yellow-700">
                        <p className="font-medium mb-1">Options:</p>
                        <ul className="list-disc list-inside space-y-1">
                          {task.delegation_options.map((option, optIndex) => (
                            <li key={optIndex}>{option}</li>
                          ))}
                        </ul>
                        <p className="mt-2">💰 Time saved: {task.estimated_time_saved} minutes</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Elimination Suggestions */}
            {scheduleResults.elimination_suggestions.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">🗑️ Elimination Suggestions</h4>
                <div className="space-y-3">
                  {scheduleResults.elimination_suggestions.map((task, index) => (
                    <div key={index} className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                      <h5 className="font-medium text-gray-900 mb-2">{task.task_title}</h5>
                      <p className="text-sm text-gray-700 mb-2">{task.recommendation}</p>
                      <div className="text-sm text-gray-600">
                        <p className="font-medium mb-1">Options:</p>
                        <ul className="list-disc list-inside space-y-1">
                          {task.elimination_options.map((option, optIndex) => (
                            <li key={optIndex}>{option}</li>
                          ))}
                        </ul>
                        <p className="mt-2">💰 Time saved: {task.potential_time_saved} minutes</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Insights and Next Steps */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-3">📈 Optimization Insights</h4>
                <ul className="text-sm text-blue-800 space-y-2">
                  {scheduleResults.optimization_insights.map((insight, index) => (
                    <li key={index}>• {insight}</li>
                  ))}
                </ul>
              </div>
              
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-3">🎯 Next Steps</h4>
                <ul className="text-sm text-green-800 space-y-2">
                  {scheduleResults.next_steps.map((step, index) => (
                    <li key={index}>• {step}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Feature Information */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Auto-Scheduler Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Eisenhower Matrix Optimization</h4>
                <p className="text-sm text-gray-600">Automatically prioritizes tasks based on urgency and importance</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Peak Performance Scheduling</h4>
                <p className="text-sm text-gray-600">Schedules important tasks during peak focus hours (9-11 AM)</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Smart Delegation</h4>
                <p className="text-sm text-gray-600">Identifies tasks suitable for delegation or automation</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Time Block Optimization</h4>
                <p className="text-sm text-gray-600">Creates optimal time blocks based on energy levels and task complexity</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Calendar Integration Ready</h4>
                <p className="text-sm text-gray-600 italic">Ready for Google Calendar sync with OAuth setup</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Productivity Analytics</h4>
                <p className="text-sm text-gray-600">Tracks efficiency gains and optimization opportunities</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoScheduler;