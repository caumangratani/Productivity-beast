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
      message: 'Hello! I\'m your Enhanced AI Productivity Coach powered by real AI! 🤖✨\n\nI can help you with:\n• Real-time productivity analysis\n• Personalized coaching based on your data\n• Task optimization and prioritization\n• Goal setting and habit formation\n\nTry these slash commands:\n• `/analyze` - Deep productivity analysis\n• `/optimize` - Task optimization plan\n• `/goals` - SMART goal setting\n• `/habits` - Productivity habit recommendations\n• `/report` - Comprehensive performance report\n• `/help` - Full command guide\n\nOr just ask me anything about productivity!',
      timestamp: new Date()
    }
  ]);
  const [newMessage, setNewMessage] = useState('');
  const [aiProvider, setAiProvider] = useState('openai');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    fetchUsers();
    if (currentUser) {
      setSelectedUserId(currentUser.id);
    }
  }, [currentUser]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
      if (response.data.length > 0 && !selectedUserId) {
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
        message: '❌ I encountered an error while analyzing your productivity data. Please try again or contact support if the issue persists.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  const generateInsightMessage = (data) => {
    const { insights, suggestions, performance_trend } = data;
    
    let message = "📊 **Productivity Analysis Complete!**\n\n";
    
    message += "**🔍 Key Insights:**\n";
    insights.forEach((insight, index) => {
      message += `${index + 1}. ${insight}\n`;
    });
    
    message += "\n**💡 My Recommendations:**\n";
    suggestions.forEach((suggestion, index) => {
      message += `• ${suggestion}\n`;
    });
    
    message += `\n**📈 Performance Trend:** ${performance_trend === 'improving' ? '📈 Improving' : '⚠️ Needs Attention'}`;
    
    if (performance_trend === 'improving') {
      message += "\n\n🎉 Excellent work! Keep up the momentum. Consider setting more challenging goals to continue growing.";
    } else {
      message += "\n\n💪 Let's work together to turn things around. Start with the recommendations above and track your progress daily.";
    }
    
    return message;
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !currentUser?.id) return;

    setLoading(true);
    
    const userMessage = {
      id: Date.now().toString(),
      text: newMessage.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setNewMessage('');

    try {
      const token = localStorage.getItem('token');
      
      // Send message with user context for personalized response
      const response = await axios.post(`${API}/ai-coach/chat`, {
        message: userMessage.text,
        user_id: currentUser.id,
        ai_provider: aiProvider,
        include_user_context: true  // Request real user data analysis
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data && response.data.response) {
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'ai',
          timestamp: new Date(),
          provider: selectedProvider
        };
        setChatMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Invalid response format');
      }
      
    } catch (error) {
      console.error('AI Coach error:', error);
      let errorMessage = 'Sorry, I encountered an error. ';
      
      if (error.response?.status === 401) {
        errorMessage += 'Please login again to continue our conversation.';
      } else if (error.response?.status === 429) {
        errorMessage += 'I\'m getting too many requests right now. Please try again in a moment.';
      } else if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else {
        errorMessage += 'Let me try to analyze your productivity data differently.';
      }
      
      const errorResponse = {
        id: (Date.now() + 1).toString(),
        text: errorMessage,
        sender: 'ai',
        timestamp: new Date(),
        provider: selectedProvider,
        isError: true
      };
      setChatMessages(prev => [...prev, errorResponse]);
    }
    
    setLoading(false);
  };

  const handleQuickMessage = (message) => {
    setNewMessage(message);
    // Auto-send after a short delay to show the message was set
    setTimeout(() => {
      handleSendMessage();
    }, 100);
  };

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : 'Unknown User';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'openai': return '🤖';
      case 'claude': return '🧠';
      case 'gemini': return '💎';
      case 'command': return '⚡';
      case 'enhanced_fallback': return '🛠️';
      default: return '🤖';
    }
  };

  const clearChat = () => {
    setChatMessages([
      {
        type: 'ai',
        message: 'Chat cleared! How can I help you with your productivity today? 🚀',
        timestamp: new Date()
      }
    ]);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🤖 AI Productivity Coach</h2>
          <p className="text-gray-600 mt-1">Enhanced with real AI - Get personalized insights and recommendations</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value)}
            className="select-field min-w-32"
          >
            <option value="openai">🤖 OpenAI GPT-4</option>
            <option value="claude">🧠 Claude</option>
            <option value="gemini">💎 Gemini</option>
          </select>
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
            Quick Analysis
          </button>
        </div>
      </div>

      {/* AI Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chat Messages */}
        <div className="stats-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">💬 AI Coach Chat</h3>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm text-green-600">AI Online</span>
              </div>
              <button
                onClick={clearChat}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear Chat
              </button>
            </div>
          </div>
          
          <div className="h-96 overflow-y-auto space-y-4 mb-4 p-3 bg-gray-50 rounded-lg">
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-purple-500 text-white'
                      : message.error
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.message}</div>
                  <div className={`text-xs mt-2 flex items-center justify-between ${
                    message.type === 'user' ? 'text-purple-100' : 'text-gray-500'
                  }`}>
                    <span>{formatTimestamp(message.timestamp)}</span>
                    {message.provider && (
                      <span className="flex items-center space-x-1">
                        <span>{getProviderIcon(message.provider)}</span>
                        <span className="capitalize">{message.provider}</span>
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex justify-start">
                <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-lg bg-white text-gray-900 border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm text-gray-500">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSendMessage()}
              placeholder="Ask me anything or use /commands..."
              className="input-field flex-1"
              disabled={isTyping}
            />
            <button
              onClick={handleSendMessage}
              disabled={isTyping || !newMessage.trim()}
              className="btn-primary px-4"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        {/* Enhanced Controls and Features */}
        <div className="space-y-4">
          {/* AI Commands */}
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ AI Commands</h3>
            <div className="grid grid-cols-1 gap-2">
              {[
                { command: "/analyze", description: "Deep productivity analysis", icon: "🔍" },
                { command: "/optimize", description: "Task optimization plan", icon: "⚡" },
                { command: "/goals", description: "SMART goal setting", icon: "🎯" },
                { command: "/habits", description: "Habit recommendations", icon: "🌱" },
                { command: "/report", description: "Performance report", icon: "📊" },
                { command: "/help", description: "Command guide", icon: "❓" }
              ].map((cmd, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickMessage(cmd.command)}
                  className="text-left p-3 bg-gradient-to-r from-purple-50 to-indigo-50 hover:from-purple-100 hover:to-indigo-100 rounded-lg transition-all border border-purple-200 hover:border-purple-300"
                  disabled={isTyping}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{cmd.icon}</span>
                    <div>
                      <div className="font-medium text-purple-900">{cmd.command}</div>
                      <div className="text-sm text-purple-700">{cmd.description}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Quick Topics */}
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">💬 Quick Topics</h3>
            <div className="grid grid-cols-1 gap-2">
              {[
                { text: "How can I improve my productivity?", icon: "📈" },
                { text: "Help me prioritize my tasks", icon: "🎯" },
                { text: "I'm feeling overwhelmed with work", icon: "😓" },
                { text: "What are best team collaboration practices?", icon: "👥" },
                { text: "How do I build better habits?", icon: "🌱" },
                { text: "Analyze my current performance", icon: "📊" }
              ].map((topic, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickMessage(topic.text)}
                  className="text-left p-3 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors border border-gray-200 hover:border-purple-200"
                  disabled={isTyping}
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
                📋 Latest Analysis for {getUserName(selectedUserId)}
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">🔍 Key Insights:</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {insights.insights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">💡 Recommendations:</h4>
                  <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                    {insights.suggestions.map((suggestion, index) => (
                      <li key={index}>{suggestion}</li>
                    ))}
                  </ul>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-700">📈 Trend:</span>
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

      {/* Working AI Features */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">✅ Live AI Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">🤖 Real AI Chat</h4>
            <p className="text-sm text-green-700">Powered by OpenAI GPT-4 with your productivity data</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">⚡ Slash Commands</h4>
            <p className="text-sm text-green-700">Advanced analysis, optimization, and reporting</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">📊 Data-Driven Insights</h4>
            <p className="text-sm text-green-700">Personalized recommendations based on your tasks</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">🎯 Smart Goals</h4>
            <p className="text-sm text-green-700">AI-generated SMART goals from your performance</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">🌱 Habit Formation</h4>
            <p className="text-sm text-green-700">Personalized habit stacks and tracking</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">📈 Performance Reports</h4>
            <p className="text-sm text-green-700">Comprehensive analytics and trend analysis</p>
          </div>
        </div>
      </div>

      {/* Coming Soon Features */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Additional Integrations (Coming Soon)</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <h4 className="font-medium text-yellow-900 mb-2">📅 Google Calendar</h4>
            <p className="text-sm text-yellow-700">Deadline sync and smart scheduling</p>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 mb-2">📊 Google Sheets</h4>
            <p className="text-sm text-blue-700">Data export and automated reports</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">📱 WhatsApp Bot</h4>
            <p className="text-sm text-green-700">Task management via messaging</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICoach;