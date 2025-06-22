import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import LandingPage from "./components/LandingPage";
import TaskManager from "./components/TaskManager";
import ProjectManager from "./components/ProjectManager";
import Dashboard from "./components/Dashboard";
import TeamPerformance from "./components/TeamPerformance";
import AICoach from "./components/AICoach";
import IntegrationSettings from "./components/IntegrationSettings";
import WhatsAppIntegration from "./components/WhatsAppIntegration";
import TeamManagement from "./components/TeamManagement";
import AutoScheduler from "./components/AutoScheduler";
import OKRManagement from "./components/OKRManagement";
import AdvancedAnalytics from "./components/AdvancedAnalytics";
import UserManual from "./components/UserManual";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = ({ activeSection, setActiveSection, onLogout, user }) => {
  const [showMoreMenu, setShowMoreMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-purple-600">Productivity Beast</h1>
          </div>
          
          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {[
              { key: 'dashboard', label: 'Dashboard', icon: '📊' },
              { key: 'tasks', label: 'Tasks', icon: '✅' },
              { key: 'projects', label: 'Projects', icon: '📋' },
              { key: 'ai-coach', label: 'AI Coach', icon: '🤖' }
            ].map((item) => (
              <button
                key={item.key}
                onClick={() => setActiveSection(item.key)}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeSection === item.key
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.label}
              </button>
            ))}
            
            {/* Dropdown for More Features */}
            <div className="relative">
              <button
                onClick={() => setShowMoreMenu(!showMoreMenu)}
                className="px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-50 flex items-center"
              >
                <span className="mr-1">⚡</span>
                More
                <svg className="ml-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
              
              {showMoreMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    {[
                      { key: 'auto-scheduler', label: 'Auto-Scheduler', icon: '⏰', desc: 'AI time optimization' },
                      { key: 'okr', label: 'OKR Management', icon: '🎯', desc: 'Goals & objectives' },
                      { key: 'analytics', label: 'Analytics', icon: '📊', desc: 'Advanced insights' },
                      { key: 'performance', label: 'Team Performance', icon: '📈', desc: 'Team metrics' },
                      { key: 'team', label: 'Team Management', icon: '👥', desc: 'User management' },
                      { key: 'whatsapp', label: 'WhatsApp Bot', icon: '📱', desc: 'Messaging automation' },
                      { key: 'integrations', label: 'Integrations', icon: '🔗', desc: 'Connect apps' },
                      { key: 'manual', label: 'User Guide', icon: '📚', desc: 'Help & support' }
                    ].map((item) => (
                      <button
                        key={item.key}
                        onClick={() => {
                          setActiveSection(item.key);
                          setShowMoreMenu(false);
                        }}
                        className={`w-full text-left px-4 py-3 text-sm hover:bg-gray-50 flex items-start space-x-3 ${
                          activeSection === item.key ? 'bg-purple-50 text-purple-700' : 'text-gray-700'
                        }`}
                      >
                        <span className="text-lg">{item.icon}</span>
                        <div>
                          <div className="font-medium">{item.label}</div>
                          <div className="text-xs text-gray-500">{item.desc}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Mobile Navigation */}
          <div className="lg:hidden">
            <button
              onClick={() => setShowMobileMenu(!showMobileMenu)}
              className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-50"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Welcome, <span className="font-medium">{user?.name || 'User'}</span>
            </div>
            <button
              onClick={onLogout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {showMobileMenu && (
        <div className="lg:hidden border-t border-gray-200 bg-white">
          <div className="px-2 py-3 space-y-1">
            {[
              { key: 'dashboard', label: 'Dashboard', icon: '📊' },
              { key: 'tasks', label: 'Tasks', icon: '✅' },
              { key: 'projects', label: 'Projects', icon: '📋' },
              { key: 'ai-coach', label: 'AI Coach', icon: '🤖' },
              { key: 'auto-scheduler', label: 'Auto-Scheduler', icon: '⏰' },
              { key: 'okr', label: 'OKR Management', icon: '🎯' },
              { key: 'analytics', label: 'Analytics', icon: '📊' },
              { key: 'performance', label: 'Team Performance', icon: '📈' },
              { key: 'team', label: 'Team Management', icon: '👥' },
              { key: 'whatsapp', label: 'WhatsApp Bot', icon: '📱' },
              { key: 'integrations', label: 'Integrations', icon: '🔗' },
              { key: 'manual', label: 'User Guide', icon: '📚' }
            ].map((item) => (
              <button
                key={item.key}
                onClick={() => {
                  setActiveSection(item.key);
                  setShowMobileMenu(false);
                }}
                className={`w-full text-left px-3 py-2 text-sm font-medium rounded-md transition-colors flex items-center space-x-2 ${
                  activeSection === item.key
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};

// Main App Component
function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [users, setUsers] = useState([]);
  const [showMoreMenu, setShowMoreMenu] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetchUsers();
    }
  }, [isAuthenticated]);

  const checkAuthStatus = () => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
      setIsAuthenticated(true);
    }
    setLoading(false);
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    setActiveSection('dashboard');
  };

  const fetchUsers = async () => {
    try {
      console.log('Fetching users...');
      const response = await axios.get(`${API}/users`);
      console.log('Users fetched:', response.data);
      setUsers(response.data);
      if (response.data.length > 0 && !user) {
        setUser(response.data[0]);
        console.log('Current user set to:', response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const renderActiveSection = () => {
    switch (activeSection) {
      case 'dashboard':
        return <Dashboard />;
      case 'tasks':
        return <TaskManager currentUser={user} users={users} />;
      case 'projects':
        return <ProjectManager currentUser={user} users={users} />;
      case 'performance':
        return <TeamPerformance users={users} />;
      case 'ai-coach':
        return <AICoach currentUser={user} />;
      case 'auto-scheduler':
        return <AutoScheduler currentUser={user} />;
      case 'okr':
        return <OKRManagement currentUser={user} />;
      case 'analytics':
        return <AdvancedAnalytics currentUser={user} />;
      case 'team':
        return <TeamManagement currentUser={user} />;
      case 'whatsapp':
        return <WhatsAppIntegration currentUser={user} />;
      case 'integrations':
        return <IntegrationSettings currentUser={user} />;
      case 'manual':
        return <UserManual />;
      default:
        return <Dashboard />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LandingPage onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      <Navigation 
        activeSection={activeSection} 
        setActiveSection={setActiveSection}
        onLogout={handleLogout}
        user={user}
      />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderActiveSection()}
      </main>
      
      {/* Quick Action Button */}
      <div className="fixed bottom-6 right-6">
        <button className="w-14 h-14 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center justify-center">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default App;