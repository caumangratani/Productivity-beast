import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import axios from "axios";
import TaskManager from "./components/TaskManager";
import ProjectManager from "./components/ProjectManager";
import Dashboard from "./components/Dashboard";
import TeamPerformance from "./components/TeamPerformance";
import AICoach from "./components/AICoach";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Navigation Component
const Navigation = ({ activeSection, setActiveSection }) => {
  return (
    <nav className="bg-white shadow-sm border-b border-purple-100">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Productivity Beast
              </h1>
            </div>
            
            <div className="flex space-x-1">
              {[
                { key: 'dashboard', label: 'Dashboard', icon: '📊' },
                { key: 'tasks', label: 'Personal Tasks', icon: '✅' },
                { key: 'projects', label: 'Team Projects', icon: '📋' },
                { key: 'performance', label: 'Team Performance', icon: '📈' },
                { key: 'ai-coach', label: 'AI Coach', icon: '🤖' }
              ].map((item) => (
                <button
                  key={item.key}
                  onClick={() => setActiveSection(item.key)}
                  className={`nav-item px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                    activeSection === item.key
                      ? 'nav-item-active bg-purple-100 text-purple-700'
                      : 'nav-item-inactive text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button className="p-2 rounded-full bg-purple-100 text-purple-600 hover:bg-purple-200 transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
              </svg>
            </button>
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">U</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

// Main App Component
function App() {
  const [activeSection, setActiveSection] = useState('dashboard');
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
      if (response.data.length > 0 && !currentUser) {
        setCurrentUser(response.data[0]);
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
        return <TaskManager currentUser={currentUser} users={users} />;
      case 'projects':
        return <ProjectManager currentUser={currentUser} users={users} />;
      case 'performance':
        return <TeamPerformance users={users} />;
      case 'ai-coach':
        return <AICoach currentUser={currentUser} />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      <Navigation activeSection={activeSection} setActiveSection={setActiveSection} />
      
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