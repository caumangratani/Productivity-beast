import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AICoach = ({ currentUser }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [users, setUsers] = useState([]);
  const [chatMessages, setChatMessages] = useState([
    {
      type: 'ai',
      message: 'Hello! I\'m your AI Productivity Coach. I analyze your task patterns, performance metrics, and productivity trends to provide personalized insights and recommendations. How can I help you improve your productivity today?',
      timestamp: new Date()
    }
  ]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
      if (response.data.length > 0) {
        setSelectedUserId(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const fetchInsights = async (userId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/ai-coach/insights/${userId}`);
      setInsights(response.data);
      
      // Add AI insight to chat
      const aiMessage = {
        type: 'ai',
        message: generateInsightMessage(response.data),
        timestamp: new Date(),
        insights: response.data
      };
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error fetching insights:', error);
      const errorMessage = {
        type: 'ai',
        message: 'I encountered an error while analyzing your productivity data. Please try again or contact support if the issue persists.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const generateInsightMessage = (data) => {
    const { insights, suggestions, performance_trend } = data;
    
    let message = "📊 **Productivity Analysis Complete!**\n\n";
    
    message += "**Key Insights:**\n";
    insights.forEach((insight, index) => {
      message += `${index + 1}. ${insight}\n`;
    });
    
    message += "\n**My Recommendations:**\n";
    suggestions.forEach((suggestion, index) => {
      message += `• ${suggestion}\n`;
    });
    
    message += `\n**Performance Trend:** ${performance_trend === 'improving' ? '📈 Improving' : '⚠️ Needs Attention'}`;
    
    if (performance_trend === 'improving') {
      message += "\n\nGreat work! Keep up the momentum. Consider setting more challenging goals to continue growing.";
    } else {
      message += "\n\nLet's work together to turn things around. Start with the recommendations above and track your progress daily.";
    }
    
    return message;
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;
    
    // Add user message
    const userMessage = {
      type: 'user',
      message: newMessage,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    
    // Generate AI response based on message content
    setTimeout(() => {
      const aiResponse = generateAIResponse(newMessage);
      const aiMessage = {
        type: 'ai',
        message: aiResponse,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, aiMessage]);
    }, 1000);
    
    setNewMessage('');
  };

  const generateAIResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('help') || lowerMessage.includes('stuck')) {
      return "I understand you're looking for help! Here are some strategies I recommend:\n\n• **Time Blocking**: Dedicate specific time slots for different types of tasks\n• **Eisenhower Matrix**: Prioritize tasks by urgency and importance\n• **Pomodoro Technique**: Work in 25-minute focused intervals\n• **Daily Reviews**: Spend 10 minutes each evening planning the next day\n\nWhich of these would you like me to explain in more detail?";
    }
    
    if (lowerMessage.includes('priority') || lowerMessage.includes('prioritize')) {
      return "Great question about prioritization! I use the Eisenhower Matrix to help you focus:\n\n🔴 **DO FIRST** (Urgent + Important): Crisis situations, deadlines today\n🟡 **SCHEDULE** (Important + Not Urgent): Planning, skill development, prevention\n🔵 **DELEGATE** (Urgent + Not Important): Interruptions, some emails, non-essential meetings\n⚪ **DON'T DO** (Not Urgent + Not Important): Time wasters, excessive social media\n\nI automatically categorize your tasks using this system. Focus on the 'Schedule' quadrant to prevent tasks from becoming urgent!";
    }
    
    if (lowerMessage.includes('productivity') || lowerMessage.includes('improve')) {
      return "Here's my personalized productivity improvement plan:\n\n**Daily Habits:**\n• Start each day by reviewing your top 3 priorities\n• Use the 2-minute rule: If it takes less than 2 minutes, do it now\n• Batch similar tasks together\n• Take regular breaks to maintain focus\n\n**Weekly Reviews:**\n• Analyze what worked and what didn't\n• Adjust your systems based on results\n• Celebrate completed tasks and progress\n\nWould you like me to analyze your current productivity patterns?";
    }
    
    if (lowerMessage.includes('team') || lowerMessage.includes('collaboration')) {
      return "Team productivity is crucial! Here are my top recommendations:\n\n**Communication:**\n• Set clear expectations and deadlines\n• Use project management tools effectively\n• Hold regular check-ins, not just meetings\n\n**Task Management:**\n• Clearly define roles and responsibilities\n• Use collaborative workflows\n• Track progress transparently\n\n**Performance:**\n• Provide regular, constructive feedback\n• Recognize achievements promptly\n• Address bottlenecks quickly\n\nWant me to analyze your team's current performance metrics?";
    }
    
    if (lowerMessage.includes('goals') || lowerMessage.includes('target')) {
      return "Goal setting is fundamental to productivity! Here's my framework:\n\n**SMART Goals:**\n• **Specific**: Clear, well-defined objectives\n• **Measurable**: Trackable metrics and milestones\n• **Achievable**: Realistic given your resources\n• **Relevant**: Aligned with your priorities\n• **Time-bound**: Clear deadlines\n\n**Pro Tips:**\n• Break large goals into smaller, weekly tasks\n• Review progress daily\n• Adjust goals based on new information\n• Celebrate small wins along the way\n\nWhat specific goal would you like help structuring?";
    }
    
    return "That's an interesting point! Based on my analysis of productivity patterns, I'd recommend:\n\n• **Focus on one priority at a time** - multitasking reduces efficiency by up to 40%\n• **Use data to drive decisions** - track your time and energy patterns\n• **Build sustainable systems** - consistency beats intensity in the long run\n• **Regular reviews and adjustments** - what works today might need tweaking tomorrow\n\nIs there a specific productivity challenge you're facing that I can help address? I can analyze your task patterns and provide personalized recommendations.";
  };

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : 'Unknown User';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">AI Productivity Coach</h2>
          <p className="text-gray-600 mt-1">Get personalized insights and recommendations based on your productivity patterns</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            className="select-field min-w-40"
          >
            <option value="">Select user</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
          <button
            onClick={() => selectedUserId && fetchInsights(selectedUserId)}
            disabled={!selectedUserId || loading}
            className="btn-primary"
          >
            {loading ? (
              <div className="loading-spinner"></div>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
              </svg>
            )}
            Analyze Performance
          </button>
        </div>
      </div>

      {/* AI Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat Messages */}
        <div className="stats-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">AI Coach Chat</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-green-600">Online</span>
            </div>
          </div>
          
          <div className="h-96 overflow-y-auto space-y-4 mb-4 p-2 bg-gray-50 rounded-lg">
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-purple-500 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm">{message.message}</div>
                  <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-purple-100' : 'text-gray-500'}`}>
                    {formatTimestamp(message.timestamp)}
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask me about productivity strategies..."
              className="input-field flex-1"
            />
            <button
              onClick={handleSendMessage}
              className="btn-primary px-4"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        {/* Quick Insights Panel */}
        <div className="space-y-4">
          {/* AI Coach Features */}
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 AI Coach Capabilities</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Pattern Analysis</h4>
                  <p className="text-sm text-gray-600">Identifies productivity patterns and bottlenecks</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Smart Prioritization</h4>
                  <p className="text-sm text-gray-600">Eisenhower Matrix-based task categorization</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Personalized Recommendations</h4>
                  <p className="text-sm text-gray-600">Tailored advice based on your work style</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-3 h-3 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Performance Tracking</h4>
                  <p className="text-sm text-gray-600">Continuous monitoring and improvement suggestions</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Coaching Topics</h3>
            <div className="grid grid-cols-1 gap-2">
              {[
                { text: "How can I improve my productivity?", icon: "📈" },
                { text: "Help me prioritize my tasks", icon: "🎯" },
                { text: "I'm feeling stuck and overwhelmed", icon: "😓" },
                { text: "What are best team collaboration practices?", icon: "👥" },
                { text: "How do I set better goals?", icon: "🏆" }
              ].map((topic, index) => (
                <button
                  key={index}
                  onClick={() => setNewMessage(topic.text)}
                  className="text-left p-3 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors"
                >
                  <span className="mr-2">{topic.icon}</span>
                  <span className="text-sm text-gray-700">{topic.text}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Latest Insights Summary */}
          {insights && (
            <div className="stats-card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Latest Analysis for {getUserName(selectedUserId)}
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Key Insights:</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {insights.insights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Recommendations:</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {insights.suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-700">Trend:</span>
                  <span className={`badge ${
                    insights.performance_trend === 'improving' ? 'badge-completed' : 'badge-overdue'
                  }`}>
                    {insights.performance_trend === 'improving' ? '📈 Improving' : '⚠️ Needs Attention'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Features Coming Soon */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Advanced AI Features (Coming Soon)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h4 className="font-medium text-yellow-900 mb-2">📅 Smart Scheduling</h4>
            <p className="text-sm text-yellow-700">AI-powered calendar optimization and meeting scheduling</p>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 mb-2">🎯 Goal Prediction</h4>
            <p className="text-sm text-blue-700">Predictive analytics for goal achievement likelihood</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">🤝 Team Dynamics</h4>
            <p className="text-sm text-green-700">AI analysis of team collaboration patterns</p>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <h4 className="font-medium text-purple-900 mb-2">📱 Mobile Coaching</h4>
            <p className="text-sm text-purple-700">WhatsApp integration for real-time productivity tips</p>
          </div>
          
          <div className="p-4 bg-pink-50 rounded-lg border border-pink-200">
            <h4 className="font-medium text-pink-900 mb-2">🧠 Learning Adaptation</h4>
            <p className="text-sm text-pink-700">Personalized coaching that adapts to your learning style</p>
          </div>
          
          <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <h4 className="font-medium text-indigo-900 mb-2">📊 Advanced Analytics</h4>
            <p className="text-sm text-indigo-700">Deep insights with machine learning predictions</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICoach;