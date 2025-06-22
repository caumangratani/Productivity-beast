import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const OKRManagement = ({ currentUser }) => {
  const [okrs, setOkrs] = useState([]);
  const [objectives, setObjectives] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showOKRModal, setShowOKRModal] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('Q1 2025');
  const [newOKR, setNewOKR] = useState({
    title: '',
    description: '',
    target_value: 100,
    current_value: 0,
    metric: 'percentage',
    due_date: '',
    objective_id: '',
    owner: '',
    priority: 'high'
  });

  useEffect(() => {
    fetchOKRs();
  }, []);

  const fetchOKRs = async () => {
    try {
      // For demo, create sample OKR data
      const sampleOKRs = [
        {
          id: '1',
          title: 'Increase Team Productivity',
          description: 'Improve overall team efficiency and output quality',
          target_value: 85,
          current_value: 72,
          metric: 'percentage',
          due_date: '2025-03-31',
          status: 'on_track',
          owner: 'Sarah Johnson',
          priority: 'high',
          key_results: [
            {
              id: '1a',
              title: 'Reduce average task completion time by 20%',
              target_value: 20,
              current_value: 15,
              metric: 'percentage',
              status: 'on_track'
            },
            {
              id: '1b', 
              title: 'Achieve 90% on-time project delivery',
              target_value: 90,
              current_value: 82,
              metric: 'percentage',
              status: 'on_track'
            },
            {
              id: '1c',
              title: 'Implement AI coaching for all team members',
              target_value: 100,
              current_value: 68,
              metric: 'percentage',
              status: 'at_risk'
            }
          ]
        },
        {
          id: '2',
          title: 'Enhance Customer Satisfaction',
          description: 'Improve customer experience and satisfaction scores',
          target_value: 95,
          current_value: 88,
          metric: 'score',
          due_date: '2025-03-31',
          status: 'on_track',
          owner: 'Mike Chen',
          priority: 'high',
          key_results: [
            {
              id: '2a',
              title: 'Achieve NPS score of 75+',
              target_value: 75,
              current_value: 68,
              metric: 'score',
              status: 'on_track'
            },
            {
              id: '2b',
              title: 'Reduce customer support response time to <2 hours',
              target_value: 2,
              current_value: 3.2,
              metric: 'hours',
              status: 'at_risk'
            }
          ]
        },
        {
          id: '3',
          title: 'Revenue Growth',
          description: 'Increase quarterly revenue through new features and market expansion',
          target_value: 1000000,
          current_value: 720000,
          metric: 'currency',
          due_date: '2025-03-31', 
          status: 'on_track',
          owner: 'Alex Rodriguez',
          priority: 'critical',
          key_results: [
            {
              id: '3a',
              title: 'Launch 3 new premium features',
              target_value: 3,
              current_value: 2,
              metric: 'count',
              status: 'on_track'
            },
            {
              id: '3b',
              title: 'Acquire 500 new paying customers',
              target_value: 500,
              current_value: 342,
              metric: 'count',
              status: 'on_track'
            }
          ]
        }
      ];
      
      setOkrs(sampleOKRs);
    } catch (error) {
      console.error('Error fetching OKRs:', error);
    }
  };

  const createOKR = async () => {
    if (!newOKR.title || !newOKR.description) {
      alert('Please fill in required fields');
      return;
    }

    setLoading(true);
    try {
      // For demo, add to local state
      const okr = {
        ...newOKR,
        id: Date.now().toString(),
        current_value: 0,
        status: 'not_started',
        key_results: []
      };
      
      setOkrs(prev => [...prev, okr]);
      setShowOKRModal(false);
      setNewOKR({
        title: '',
        description: '',
        target_value: 100,
        current_value: 0,
        metric: 'percentage',
        due_date: '',
        objective_id: '',
        owner: '',
        priority: 'high'
      });
    } catch (error) {
      console.error('Error creating OKR:', error);
      alert('Error creating OKR');
    }
    setLoading(false);
  };

  const updateProgress = async (okrId, keyResultId, newValue) => {
    setOkrs(prev => 
      prev.map(okr => {
        if (okr.id === okrId) {
          if (keyResultId) {
            // Update key result
            return {
              ...okr,
              key_results: okr.key_results.map(kr =>
                kr.id === keyResultId 
                  ? { ...kr, current_value: newValue, status: calculateStatus(newValue, kr.target_value) }
                  : kr
              )
            };
          } else {
            // Update main OKR
            return {
              ...okr,
              current_value: newValue,
              status: calculateStatus(newValue, okr.target_value)
            };
          }
        }
        return okr;
      })
    );
  };

  const calculateStatus = (current, target) => {
    const progress = (current / target) * 100;
    if (progress >= 90) return 'on_track';
    if (progress >= 70) return 'on_track';
    if (progress >= 50) return 'at_risk';
    return 'off_track';
  };

  const getStatusColor = (status) => {
    const colors = {
      'on_track': 'bg-green-100 text-green-800 border-green-200',
      'at_risk': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'off_track': 'bg-red-100 text-red-800 border-red-200',
      'not_started': 'bg-gray-100 text-gray-800 border-gray-200',
      'completed': 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[status] || colors['not_started'];
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'critical': 'bg-red-100 text-red-800',
      'high': 'bg-orange-100 text-orange-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'low': 'bg-green-100 text-green-800'
    };
    return colors[priority] || colors['medium'];
  };

  const formatValue = (value, metric) => {
    switch (metric) {
      case 'percentage': return `${value}%`;
      case 'currency': return `₹${(value/100000).toFixed(1)}L`;
      case 'hours': return `${value}h`;
      case 'score': return value;
      case 'count': return value;
      default: return value;
    }
  };

  const calculateOverallProgress = () => {
    if (okrs.length === 0) return 0;
    const totalProgress = okrs.reduce((sum, okr) => {
      return sum + ((okr.current_value / okr.target_value) * 100);
    }, 0);
    return Math.round(totalProgress / okrs.length);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🎯 OKR Management</h2>
          <p className="text-gray-600 mt-1">Objectives and Key Results tracking for {selectedPeriod}</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="select-field"
          >
            <option value="Q1 2025">Q1 2025</option>
            <option value="Q2 2025">Q2 2025</option>
            <option value="2025 Annual">2025 Annual</option>
          </select>
          <button
            onClick={() => setShowOKRModal(true)}
            className="btn-primary"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Create OKR
          </button>
        </div>
      </div>

      {/* OKR Overview Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stats-card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total OKRs</p>
              <p className="text-3xl font-bold">{okrs.length}</p>
            </div>
            <div className="text-4xl">🎯</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Overall Progress</p>
              <p className="text-3xl font-bold">{calculateOverallProgress()}%</p>
            </div>
            <div className="text-4xl">📈</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-yellow-500 to-yellow-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100">On Track</p>
              <p className="text-3xl font-bold">{okrs.filter(o => o.status === 'on_track').length}</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-red-500 to-red-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-red-100">At Risk</p>
              <p className="text-3xl font-bold">{okrs.filter(o => o.status === 'at_risk').length}</p>
            </div>
            <div className="text-4xl">⚠️</div>
          </div>
        </div>
      </div>

      {/* OKRs List */}
      <div className="space-y-6">
        {okrs.map((okr) => (
          <div key={okr.id} className="stats-card">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">{okr.title}</h3>
                  <span className={`badge ${getStatusColor(okr.status)}`}>
                    {okr.status.replace('_', ' ').toUpperCase()}
                  </span>
                  <span className={`badge ${getPriorityColor(okr.priority)}`}>
                    {okr.priority.toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-600 mb-3">{okr.description}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-700">
                  <span>👤 {okr.owner}</span>
                  <span>📅 Due: {new Date(okr.due_date).toLocaleDateString()}</span>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold text-purple-600">
                  {formatValue(okr.current_value, okr.metric)} / {formatValue(okr.target_value, okr.metric)}
                </div>
                <div className="text-sm text-gray-500">
                  {Math.round((okr.current_value / okr.target_value) * 100)}% Complete
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-300 ${
                    okr.status === 'on_track' ? 'bg-green-500' :
                    okr.status === 'at_risk' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(100, (okr.current_value / okr.target_value) * 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Key Results */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">🔑 Key Results:</h4>
              <div className="space-y-3">
                {okr.key_results.map((kr) => (
                  <div key={kr.id} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <h5 className="font-medium text-gray-900">{kr.title}</h5>
                      <div className="flex items-center space-x-2">
                        <span className={`badge ${getStatusColor(kr.status)}`}>
                          {kr.status.replace('_', ' ')}
                        </span>
                        <div className="text-sm font-medium">
                          {formatValue(kr.current_value, kr.metric)} / {formatValue(kr.target_value, kr.metric)}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <div className="flex-1">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              kr.status === 'on_track' ? 'bg-green-500' :
                              kr.status === 'at_risk' ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(100, (kr.current_value / kr.target_value) * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          const newValue = prompt(`Update progress for: ${kr.title}\nCurrent: ${kr.current_value}\nTarget: ${kr.target_value}`, kr.current_value);
                          if (newValue !== null) {
                            updateProgress(okr.id, kr.id, parseFloat(newValue) || 0);
                          }
                        }}
                        className="text-sm text-purple-600 hover:text-purple-800"
                      >
                        Update
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Create OKR Modal */}
      {showOKRModal && (
        <div className="modal-overlay" onClick={() => setShowOKRModal(false)}>
          <div className="modal-content max-w-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Create New OKR</h3>
              <button
                onClick={() => setShowOKRModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Objective Title *</label>
                <input
                  type="text"
                  value={newOKR.title}
                  onChange={(e) => setNewOKR({...newOKR, title: e.target.value})}
                  className="input-field"
                  placeholder="e.g., Increase team productivity"
                />
              </div>
              
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
                <textarea
                  value={newOKR.description}
                  onChange={(e) => setNewOKR({...newOKR, description: e.target.value})}
                  className="textarea-field"
                  rows="3"
                  placeholder="Describe the objective and its impact"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target Value</label>
                <input
                  type="number"
                  value={newOKR.target_value}
                  onChange={(e) => setNewOKR({...newOKR, target_value: parseFloat(e.target.value)})}
                  className="input-field"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Metric Type</label>
                <select
                  value={newOKR.metric}
                  onChange={(e) => setNewOKR({...newOKR, metric: e.target.value})}
                  className="select-field"
                >
                  <option value="percentage">Percentage (%)</option>
                  <option value="currency">Currency (₹)</option>
                  <option value="count">Count</option>
                  <option value="score">Score</option>
                  <option value="hours">Hours</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                <input
                  type="date"
                  value={newOKR.due_date}
                  onChange={(e) => setNewOKR({...newOKR, due_date: e.target.value})}
                  className="input-field"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                <select
                  value={newOKR.priority}
                  onChange={(e) => setNewOKR({...newOKR, priority: e.target.value})}
                  className="select-field"
                >
                  <option value="critical">🔴 Critical</option>
                  <option value="high">🟠 High</option>
                  <option value="medium">🟡 Medium</option>
                  <option value="low">🟢 Low</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-3 pt-6">
              <button
                onClick={createOKR}
                disabled={loading || !newOKR.title || !newOKR.description}
                className="btn-primary flex-1"
              >
                {loading ? (
                  <div className="loading-spinner"></div>
                ) : (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                )}
                Create OKR
              </button>
              <button
                onClick={() => setShowOKRModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* OKR Tips */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">💡 OKR Best Practices</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Ambitious but Achievable</h4>
                <p className="text-sm text-gray-600">Set targets that stretch your capabilities but remain realistic</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Measurable Results</h4>
                <p className="text-sm text-gray-600">Every key result should have clear, quantifiable metrics</p>
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
                <h4 className="font-medium text-gray-900">Regular Check-ins</h4>
                <p className="text-sm text-gray-600">Review progress weekly and adjust strategies as needed</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Transparent Tracking</h4>
                <p className="text-sm text-gray-600">Keep progress visible to all stakeholders for accountability</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OKRManagement;