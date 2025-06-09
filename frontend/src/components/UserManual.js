import React, { useState } from 'react';

const UserManual = () => {
  const [activeSection, setActiveSection] = useState('getting-started');

  const sections = {
    'getting-started': {
      title: 'Getting Started',
      icon: '🚀',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Welcome to Productivity Beast!</h3>
          
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-900 mb-2">🎯 What is Productivity Beast?</h4>
            <p className="text-purple-700">
              Productivity Beast is an AI-powered productivity management platform that combines personal task management, 
              team collaboration, and intelligent coaching to boost your organization's efficiency by 40%.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="stats-card">
              <h4 className="font-semibold text-gray-900 mb-3">✅ Personal Productivity</h4>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• AI-powered task prioritization using Eisenhower Matrix</li>
                <li>• Smart deadline tracking and reminders</li>
                <li>• Personal performance analytics</li>
                <li>• Productivity insights and recommendations</li>
              </ul>
            </div>

            <div className="stats-card">
              <h4 className="font-semibold text-gray-900 mb-3">👥 Team Collaboration</h4>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Project management with Kanban boards</li>
                <li>• Team performance tracking and ratings</li>
                <li>• Task assignment and delegation</li>
                <li>• Real-time collaboration tools</li>
              </ul>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🤖 AI-Powered Features</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">🎯</span>
                </div>
                <h5 className="font-medium text-gray-900">Smart Prioritization</h5>
                <p className="text-xs text-gray-600">Automatic task categorization by urgency and importance</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">📊</span>
                </div>
                <h5 className="font-medium text-gray-900">Performance Analytics</h5>
                <p className="text-xs text-gray-600">1-10 scale ratings with actionable insights</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">🧠</span>
                </div>
                <h5 className="font-medium text-gray-900">AI Coaching</h5>
                <p className="text-xs text-gray-600">Personalized productivity recommendations</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    'dashboard': {
      title: 'Dashboard Overview',
      icon: '📊',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Understanding Your Dashboard</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📈 Stats Cards</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-4 rounded-lg">
                <h5 className="font-medium opacity-90">Total Tasks</h5>
                <p className="text-2xl font-bold">24</p>
                <p className="text-sm opacity-80">All tasks across projects</p>
              </div>
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-4 rounded-lg">
                <h5 className="font-medium opacity-90">Completed</h5>
                <p className="text-2xl font-bold">18</p>
                <p className="text-sm opacity-80">Successfully finished tasks</p>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🎯 Eisenhower Matrix</h4>
            <p className="text-gray-600 mb-4">
              The AI automatically categorizes your tasks based on urgency and importance:
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                <h5 className="font-semibold text-red-800">DO FIRST</h5>
                <p className="text-sm text-red-600">Urgent & Important - Handle immediately</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
                <h5 className="font-semibold text-yellow-800">SCHEDULE</h5>
                <p className="text-sm text-yellow-600">Important & Not Urgent - Plan ahead</p>
              </div>
              <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
                <h5 className="font-semibold text-blue-800">DELEGATE</h5>
                <p className="text-sm text-blue-600">Urgent & Not Important - Assign to others</p>
              </div>
              <div className="bg-gray-50 border border-gray-200 p-3 rounded-lg">
                <h5 className="font-semibold text-gray-800">DON'T DO</h5>
                <p className="text-sm text-gray-600">Not Urgent & Not Important - Eliminate</p>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🔄 Quick Actions</h4>
            <p className="text-gray-600 mb-3">Use the dashboard quick action cards to:</p>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Create new tasks quickly</li>
              <li>Start new team projects</li>
              <li>Access AI insights immediately</li>
              <li>Load sample data for testing</li>
            </ul>
          </div>
        </div>
      )
    },
    'tasks': {
      title: 'Personal Task Management',
      icon: '✅',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Managing Personal Tasks</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">➕ Creating Tasks</h4>
            <ol className="list-decimal list-inside space-y-2 text-gray-600">
              <li>Click the "Add Task" button in the Personal Tasks section</li>
              <li>Fill in the task details:
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                  <li><strong>Title:</strong> Brief, descriptive name for the task</li>
                  <li><strong>Description:</strong> Detailed information about what needs to be done</li>
                  <li><strong>Assigned to:</strong> Select team member (or leave for yourself)</li>
                  <li><strong>Priority:</strong> Low, Medium, High, or Urgent</li>
                  <li><strong>Due Date:</strong> When the task should be completed</li>
                  <li><strong>Tags:</strong> Categories for easy filtering</li>
                </ul>
              </li>
              <li>Click "Create Task" to save</li>
            </ol>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🔍 Filtering and Searching</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-gray-900 mb-2">Filter Options:</h5>
                <ul className="text-gray-600 space-y-1 text-sm">
                  <li>• <strong>All Tasks:</strong> View everything</li>
                  <li>• <strong>To Do:</strong> Pending tasks</li>
                  <li>• <strong>In Progress:</strong> Currently working on</li>
                  <li>• <strong>Completed:</strong> Finished tasks</li>
                  <li>• <strong>Overdue:</strong> Past due date</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900 mb-2">Task Information:</h5>
                <ul className="text-gray-600 space-y-1 text-sm">
                  <li>• <strong>Priority Badge:</strong> Color-coded urgency</li>
                  <li>• <strong>Eisenhower Label:</strong> AI categorization</li>
                  <li>• <strong>Due Date:</strong> Deadline information</li>
                  <li>• <strong>Status Dropdown:</strong> Update progress</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">✏️ Editing and Managing Tasks</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">Quick Status Updates:</h5>
                <p className="text-gray-600 text-sm">Use the dropdown menu on each task card to quickly change status from To Do → In Progress → Completed</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Full Editing:</h5>
                <p className="text-gray-600 text-sm">Click the edit icon (pencil) to modify all task details including title, description, priority, and due date</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Deletion:</h5>
                <p className="text-gray-600 text-sm">Click the delete icon (trash) to permanently remove a task. This action cannot be undone.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    'projects': {
      title: 'Team Project Management',
      icon: '📋',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Managing Team Projects</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🏗️ Creating Projects</h4>
            <ol className="list-decimal list-inside space-y-2 text-gray-600">
              <li>Click "New Project" in the Team Projects section</li>
              <li>Enter project details:
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                  <li><strong>Project Name:</strong> Clear, descriptive title</li>
                  <li><strong>Description:</strong> Project goals and scope</li>
                  <li><strong>Project Owner:</strong> Team member responsible for oversight</li>
                  <li><strong>Team Members:</strong> Select participants</li>
                  <li><strong>Due Date:</strong> Project completion deadline</li>
                </ul>
              </li>
              <li>Click "Create Project" to start</li>
            </ol>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📋 Kanban Board System</h4>
            <p className="text-gray-600 mb-4">Each project has a three-column Kanban board for task management:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg border">
                <h5 className="font-semibold text-gray-900 mb-2">📝 To Do</h5>
                <p className="text-sm text-gray-600">
                  New tasks that haven't been started yet. Tasks automatically appear here when created.
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h5 className="font-semibold text-blue-900 mb-2">⏳ In Progress</h5>
                <p className="text-sm text-blue-700">
                  Tasks currently being worked on. Move tasks here when you start working.
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h5 className="font-semibold text-green-900 mb-2">✅ Completed</h5>
                <p className="text-sm text-green-700">
                  Finished tasks. Moving tasks here updates performance metrics.
                </p>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">➕ Adding Project Tasks</h4>
            <ol className="list-decimal list-inside space-y-2 text-gray-600">
              <li>Select a project from the project list</li>
              <li>Click "Add Task" in the project view</li>
              <li>Fill in task details (same as personal tasks)</li>
              <li>The task will automatically be associated with the project</li>
              <li>Assign the task to project team members</li>
            </ol>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🔄 Moving Tasks Between Columns</h4>
            <p className="text-gray-600 mb-3">
              Use the status dropdown on each task card to move between columns:
            </p>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Change status to "In Progress" to move to the middle column</li>
              <li>Change status to "Completed" to move to the final column</li>
              <li>Status changes automatically update team performance metrics</li>
              <li>Completed tasks contribute to individual and team scores</li>
            </ul>
          </div>
        </div>
      )
    },
    'performance': {
      title: 'Team Performance Analytics',
      icon: '📈',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Understanding Team Performance</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🏆 Performance Scoring System</h4>
            <p className="text-gray-600 mb-4">
              Productivity Beast uses a comprehensive 1-10 scoring system based on:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">📊</span>
                </div>
                <h5 className="font-semibold text-gray-900">Completion Rate (40%)</h5>
                <p className="text-sm text-gray-600">Percentage of assigned tasks completed</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">⏰</span>
                </div>
                <h5 className="font-semibold text-gray-900">Timeliness (40%)</h5>
                <p className="text-sm text-gray-600">Tasks completed before deadline</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">⭐</span>
                </div>
                <h5 className="font-semibold text-gray-900">Quality (20%)</h5>
                <p className="text-sm text-gray-600">Average quality ratings received</p>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📊 Performance Grades</h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="text-center p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-2xl font-bold text-green-600">A+</div>
                <div className="text-sm text-green-700">9.0-10.0</div>
              </div>
              <div className="text-center p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-2xl font-bold text-green-600">A</div>
                <div className="text-sm text-green-700">8.0-8.9</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">B+</div>
                <div className="text-sm text-yellow-700">7.0-7.9</div>
              </div>
              <div className="text-center p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">B</div>
                <div className="text-sm text-orange-700">6.0-6.9</div>
              </div>
              <div className="text-center p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-2xl font-bold text-red-600">C</div>
                <div className="text-sm text-red-700">&lt; 6.0</div>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🤖 AI-Generated Feedback</h4>
            <p className="text-gray-600 mb-4">
              The system automatically generates personalized feedback based on performance patterns:
            </p>
            <div className="space-y-3">
              <div className="flex items-start space-x-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 text-sm">A+</span>
                </div>
                <div>
                  <h5 className="font-medium text-green-900">Excellent Performance</h5>
                  <p className="text-sm text-green-700">Positive reinforcement and growth opportunities</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-yellow-600 text-sm">B</span>
                </div>
                <div>
                  <h5 className="font-medium text-yellow-900">Good with Improvement Areas</h5>
                  <p className="text-sm text-yellow-700">Specific suggestions for optimization</p>
                </div>
              </div>
              <div className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-red-600 text-sm">C</span>
                </div>
                <div>
                  <h5 className="font-medium text-red-900">Needs Support</h5>
                  <p className="text-sm text-red-700">Action plans and additional resources</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    'ai-coach': {
      title: 'AI Productivity Coach',
      icon: '🤖',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Using Your AI Productivity Coach</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">💬 Chat Interface</h4>
            <p className="text-gray-600 mb-4">
              The AI Coach provides personalized productivity guidance through an interactive chat interface:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="font-medium text-gray-900 mb-2">Quick Topics:</h5>
                <ul className="text-gray-600 space-y-1 text-sm">
                  <li>• "How can I improve my productivity?"</li>
                  <li>• "Help me prioritize my tasks"</li>
                  <li>• "I'm feeling stuck and overwhelmed"</li>
                  <li>• "What are best team practices?"</li>
                  <li>• "How do I set better goals?"</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900 mb-2">AI Capabilities:</h5>
                <ul className="text-gray-600 space-y-1 text-sm">
                  <li>• Pattern analysis and insights</li>
                  <li>• Personalized recommendations</li>
                  <li>• Productivity strategy guidance</li>
                  <li>• Goal setting frameworks</li>
                  <li>• Stress management tips</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📊 Performance Analysis</h4>
            <ol className="list-decimal list-inside space-y-2 text-gray-600">
              <li>Select a team member from the dropdown</li>
              <li>Click "Analyze Performance" to get detailed insights</li>
              <li>Review AI-generated recommendations</li>
              <li>Use insights to guide productivity improvements</li>
            </ol>
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                <strong>Pro Tip:</strong> The AI learns from your task patterns and provides increasingly personalized advice over time.
              </p>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🎯 Best Practices for AI Coaching</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">Be Specific with Questions:</h5>
                <p className="text-gray-600 text-sm">Instead of "Help me," try "How can I better manage my email overload?"</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Regular Check-ins:</h5>
                <p className="text-gray-600 text-sm">Schedule weekly conversations with the AI to review progress and adjust strategies</p>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Act on Recommendations:</h5>
                <p className="text-gray-600 text-sm">The AI's suggestions improve as you implement and report back on what works</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    'integrations': {
      title: 'Setting Up Integrations',
      icon: '🔗',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Configuring External Integrations</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🤖 AI Provider Setup</h4>
            <div className="space-y-4">
              <div>
                <h5 className="font-medium text-gray-900">OpenAI Configuration:</h5>
                <ol className="list-decimal list-inside text-gray-600 text-sm space-y-1">
                  <li>Visit <a href="https://platform.openai.com" className="text-purple-600">platform.openai.com</a></li>
                  <li>Create account and generate API key</li>
                  <li>Copy key to Productivity Beast settings</li>
                  <li>Test integration in AI Coach section</li>
                </ol>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Anthropic Claude Setup:</h5>
                <ol className="list-decimal list-inside text-gray-600 text-sm space-y-1">
                  <li>Visit <a href="https://console.anthropic.com" className="text-purple-600">console.anthropic.com</a></li>
                  <li>Generate API key from dashboard</li>
                  <li>Configure in integration settings</li>
                  <li>Choose Claude as preferred provider</li>
                </ol>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📱 WhatsApp Business API</h4>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <p className="text-sm text-yellow-700">
                <strong>Note:</strong> WhatsApp Business API requires approval from Meta and has specific requirements for business accounts.
              </p>
            </div>
            <ol className="list-decimal list-inside space-y-2 text-gray-600">
              <li>Create WhatsApp Business Account</li>
              <li>Set up Facebook Developer Account</li>
              <li>Create new app and add WhatsApp product</li>
              <li>Configure webhook URL (provided in settings)</li>
              <li>Generate access tokens and configure phone number</li>
              <li>Test integration with simple message</li>
            </ol>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🔐 Security Best Practices</h4>
            <ul className="list-disc list-inside space-y-2 text-gray-600">
              <li>Never share API keys publicly or in screenshots</li>
              <li>Rotate API keys regularly (every 90 days recommended)</li>
              <li>Use environment variables for key storage</li>
              <li>Monitor API usage and set billing limits</li>
              <li>Revoke keys immediately if compromised</li>
            </ul>
          </div>
        </div>
      )
    },
    'troubleshooting': {
      title: 'Troubleshooting',
      icon: '🔧',
      content: (
        <div className="space-y-6">
          <h3 className="text-2xl font-bold text-gray-900">Common Issues and Solutions</h3>
          
          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🚫 Login Issues</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">Can't Sign In:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Check email and password spelling</li>
                  <li>Try password reset if available</li>
                  <li>Clear browser cache and cookies</li>
                  <li>Try incognito/private browsing mode</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Account Locked:</h5>
                <p className="text-gray-600 text-sm">Contact support if your account appears to be locked after multiple failed attempts.</p>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📱 Performance Issues</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">Slow Loading:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Check internet connection speed</li>
                  <li>Refresh the page (F5 or Ctrl+R)</li>
                  <li>Clear browser cache</li>
                  <li>Close unnecessary browser tabs</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Features Not Working:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Ensure JavaScript is enabled</li>
                  <li>Update to latest browser version</li>
                  <li>Disable browser extensions temporarily</li>
                  <li>Try a different browser</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">🤖 AI Integration Issues</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">AI Not Responding:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Check API key configuration in settings</li>
                  <li>Verify API key has sufficient credits</li>
                  <li>Test with simple messages first</li>
                  <li>Check API service status pages</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Poor AI Responses:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Be more specific with questions</li>
                  <li>Provide context about your situation</li>
                  <li>Try rephrasing your request</li>
                  <li>Switch between AI providers</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="stats-card">
            <h4 className="font-semibold text-gray-900 mb-3">📞 Getting Help</h4>
            <div className="space-y-3">
              <div>
                <h5 className="font-medium text-gray-900">Before Contacting Support:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>Check this troubleshooting guide</li>
                  <li>Note your browser and version</li>
                  <li>Document steps to reproduce the issue</li>
                  <li>Take screenshots if helpful</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Support Channels:</h5>
                <ul className="list-disc list-inside text-gray-600 text-sm space-y-1">
                  <li>In-app help chat (bottom right corner)</li>
                  <li>Email support (check footer for contact)</li>
                  <li>Documentation and guides</li>
                  <li>Community forums</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">User Manual & Guide</h2>
          <p className="text-gray-600 mt-1">Complete guide to using Productivity Beast effectively</p>
        </div>
        <button className="btn-primary" onClick={() => window.print()}>
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zM5 14H4v-2h1v2zm7 0v2H8v-2h4zm0-2H8v-2h4v2z" clipRule="evenodd" />
          </svg>
          Print Guide
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="stats-card">
            <h3 className="font-semibold text-gray-900 mb-4">📚 Table of Contents</h3>
            <nav className="space-y-2">
              {Object.entries(sections).map(([key, section]) => (
                <button
                  key={key}
                  onClick={() => setActiveSection(key)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    activeSection === key
                      ? 'bg-purple-100 text-purple-700 font-medium'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-2">{section.icon}</span>
                  {section.title}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          <div className="stats-card">
            {sections[activeSection].content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserManual;