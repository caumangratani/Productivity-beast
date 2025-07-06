import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const IntegrationSettings = ({ currentUser }) => {
  const [aiSettings, setAiSettings] = useState({
    openai_api_key: '',
    claude_api_key: '',
    preferred_ai_provider: 'openai',
    ai_enabled: false
  });
  
  const [whatsappSettings, setWhatsappSettings] = useState({
    whatsapp_business_account_id: '',
    whatsapp_access_token: '',
    webhook_verify_token: '',
    phone_number_id: '',
    enabled: false
  });

  const [googleStatus, setGoogleStatus] = useState({
    connected: false,
    loading: false,
    features_available: []
  });
  
  const [activeTab, setActiveTab] = useState('google');
  const [setupGuide, setSetupGuide] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSettings();
    checkGoogleStatus();
  }, []);

  const fetchSettings = async () => {
    try {
      const [aiResponse, whatsappResponse] = await Promise.all([
        axios.get(`${API}/integrations/ai-settings`),
        axios.get(`${API}/integrations/whatsapp-settings`)
      ]);
      
      setAiSettings(aiResponse.data);
      setWhatsappSettings(whatsappResponse.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const checkGoogleStatus = async () => {
    if (!currentUser?.id) return;
    
    try {
      const response = await axios.get(`${API}/google/integration/status/${currentUser.id}`);
      setGoogleStatus(response.data);
    } catch (error) {
      console.error('Error checking Google status:', error);
      setGoogleStatus({ connected: false, loading: false, features_available: [] });
    }
  };

  const connectGoogle = async () => {
    if (!currentUser?.id) {
      alert('Please login first');
      return;
    }

    setGoogleStatus(prev => ({ ...prev, loading: true }));
    
    try {
      const response = await axios.get(`${API}/google/auth/url?user_id=${currentUser.id}`);
      
      if (response.data.auth_url) {
        // Open Google OAuth in a popup
        const popup = window.open(
          response.data.auth_url,
          'google-oauth',
          'width=500,height=600,scrollbars=yes,resizable=yes'
        );
        
        // Listen for popup messages
        const messageListener = (event) => {
          if (event.origin !== window.location.origin) return;
          
          if (event.data.type === 'google-oauth-success') {
            popup.close();
            checkGoogleStatus(); // Refresh status
            alert('Google integration successful!');
            window.removeEventListener('message', messageListener);
          } else if (event.data.type === 'google-oauth-error') {
            popup.close();
            alert('Google integration failed: ' + event.data.error);
            window.removeEventListener('message', messageListener);
          }
        };
        
        window.addEventListener('message', messageListener);
        
        // Check if popup was closed manually
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            window.removeEventListener('message', messageListener);
            setGoogleStatus(prev => ({ ...prev, loading: false }));
          }
        }, 1000);
        
      } else {
        alert('Failed to get Google authorization URL');
      }
    } catch (error) {
      console.error('Error initiating Google OAuth:', error);
      alert('Error connecting to Google: ' + error.message);
    } finally {
      setGoogleStatus(prev => ({ ...prev, loading: false }));
    }
  };

  const syncTasksToCalendar = async () => {
    if (!currentUser?.id) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/google/calendar/sync-tasks`, {
        user_id: currentUser.id
      });
      
      if (response.data.success) {
        alert(`Successfully synced ${response.data.synced_count} tasks to Google Calendar!`);
      } else {
        alert('Failed to sync tasks');
      }
    } catch (error) {
      console.error('Error syncing tasks:', error);
      alert('Error syncing tasks: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const createOptimalSchedule = async () => {
    if (!currentUser?.id) return;
    
    const today = new Date().toISOString().split('T')[0];
    
    setLoading(true);
    try {
      const response = await axios.post(`${API}/google/calendar/optimal-schedule`, {
        user_id: currentUser.id,
        date: today
      });
      
      if (response.data.success) {
        alert(`Created ${response.data.scheduled_blocks} optimal time blocks for today!`);
      } else {
        alert('Failed to create optimal schedule');
      }
    } catch (error) {
      console.error('Error creating schedule:', error);
      alert('Error creating schedule: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const saveAiSettings = async () => {
    if (aiSettings.openai_api_key && !aiSettings.openai_api_key.startsWith('sk-')) {
      alert('Invalid OpenAI API key format. It should start with "sk-"');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/integrations/ai-settings`, aiSettings);
      
      if (response.data.success) {
        alert('✅ AI settings saved successfully! Your AI Coach is now configured and ready to help boost your productivity.');
      } else {
        alert('❌ Failed to save AI settings: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error saving AI settings:', error);
      let errorMessage = 'Failed to save AI settings';
      
      if (error.response?.status === 401) {
        errorMessage = 'Authentication error. Please login again.';
      } else if (error.response?.data?.detail) {
        errorMessage += ': ' + error.response.data.detail;
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      alert('❌ ' + errorMessage);
    }
    setLoading(false);
  };

  const saveWhatsappSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/integrations/whatsapp-settings`, whatsappSettings);
      alert('WhatsApp settings saved successfully!');
    } catch (error) {
      alert('Error saving WhatsApp settings: ' + error.message);
    }
    setLoading(false);
  };

  const getSetupGuide = async (integrationType) => {
    try {
      const response = await axios.get(`${API}/integrations/setup-guide/${integrationType}`);
      setSetupGuide(response.data);
    } catch (error) {
      console.error('Error fetching setup guide:', error);
    }
  };

  const webhookUrl = `${BACKEND_URL}/api/integrations/whatsapp/webhook`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🔗 Integration Settings</h2>
          <p className="text-gray-600 mt-1">Connect external services to supercharge your productivity</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'google', label: 'Google Workspace', icon: '📅' },
            { key: 'ai', label: 'AI Providers', icon: '🤖' },
            { key: 'whatsapp', label: 'WhatsApp Business', icon: '📱' },
            { key: 'guides', label: 'Setup Guides', icon: '📚' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Google Integration Tab */}
      {activeTab === 'google' && (
        <div className="space-y-6">
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Google Workspace Integration</h3>
            
            {/* Connection Status */}
            <div className="p-4 border border-gray-200 rounded-lg mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="font-medium text-gray-900">Connection Status</h4>
                  <p className="text-sm text-gray-600">
                    {googleStatus.connected ? 'Connected to Google Workspace' : 'Not connected to Google'}
                  </p>
                </div>
                <span className={`badge ${googleStatus.connected ? 'badge-completed' : 'badge-todo'}`}>
                  {googleStatus.connected ? '✅ Connected' : '❌ Disconnected'}
                </span>
              </div>
              
              {!googleStatus.connected ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h5 className="font-medium text-blue-900 mb-2">🔗 Connect Google Workspace</h5>
                    <p className="text-sm text-blue-700 mb-3">
                      Connect your Google account to enable Calendar sync, auto-scheduling, and Sheets reporting.
                    </p>
                    <ul className="text-sm text-blue-600 space-y-1 mb-4">
                      <li>• Sync tasks to Google Calendar automatically</li>
                      <li>• Create optimal time blocks based on priorities</li>
                      <li>• Export productivity reports to Google Sheets</li>
                      <li>• Intelligent meeting scheduling and conflict detection</li>
                    </ul>
                  </div>
                  
                  <button
                    onClick={connectGoogle}
                    disabled={googleStatus.loading}
                    className="btn-primary w-full"
                  >
                    {googleStatus.loading ? (
                      <div className="loading-spinner"></div>
                    ) : (
                      <>
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                          <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                          <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                          <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                          <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        Connect Google Account
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h5 className="font-medium text-green-900 mb-2">✅ Google Integration Active</h5>
                    <p className="text-sm text-green-700 mb-3">
                      Your Google Workspace is connected and ready to use!
                    </p>
                    <div className="text-sm text-green-600">
                      <strong>Available Features:</strong>
                      <ul className="list-disc list-inside mt-1 space-y-1">
                        {googleStatus.features_available.map((feature, index) => (
                          <li key={index}>{feature}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  {/* Google Actions */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-900 mb-2">📅 Calendar Sync</h5>
                      <p className="text-sm text-gray-600 mb-3">
                        Sync your pending tasks to Google Calendar with automatic reminders.
                      </p>
                      <button
                        onClick={syncTasksToCalendar}
                        disabled={loading}
                        className="btn-secondary w-full"
                      >
                        {loading ? 'Syncing...' : 'Sync Tasks to Calendar'}
                      </button>
                    </div>
                    
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-900 mb-2">🎯 Auto-Scheduler</h5>
                      <p className="text-sm text-gray-600 mb-3">
                        Create optimal time blocks for today based on task priorities.
                      </p>
                      <button
                        onClick={createOptimalSchedule}
                        disabled={loading}
                        className="btn-secondary w-full"
                      >
                        {loading ? 'Creating...' : 'Create Optimal Schedule'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Feature Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl mb-2">📅</div>
                <h5 className="font-medium text-gray-900 mb-1">Calendar Integration</h5>
                <p className="text-sm text-gray-600">Automatic task-to-calendar sync with smart reminders</p>
              </div>
              
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-2xl mb-2">🎯</div>
                <h5 className="font-medium text-gray-900 mb-1">Auto-Scheduler</h5>
                <p className="text-sm text-gray-600">AI-powered optimal time blocking based on priorities</p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl mb-2">📊</div>
                <h5 className="font-medium text-gray-900 mb-1">Sheets Reporting</h5>
                <p className="text-sm text-gray-600">Automated productivity reports and analytics export</p>
              </div>
              
              <div className="p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl mb-2">🤝</div>
                <h5 className="font-medium text-gray-900 mb-1">Meeting Intelligence</h5>
                <p className="text-sm text-gray-600">Extract action items and schedule follow-ups</p>
              </div>
              
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="text-2xl mb-2">⚡</div>
                <h5 className="font-medium text-gray-900 mb-1">Conflict Detection</h5>
                <p className="text-sm text-gray-600">Smart scheduling that avoids existing commitments</p>
              </div>
              
              <div className="p-4 bg-indigo-50 rounded-lg">
                <div className="text-2xl mb-2">📈</div>
                <h5 className="font-medium text-gray-900 mb-1">Productivity Analytics</h5>
                <p className="text-sm text-gray-600">Track time spent and identify optimization opportunities</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Settings Tab */}
      {activeTab === 'ai' && (
        <div className="space-y-6">
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Provider Configuration</h3>
            
            <div className="space-y-6">
              {/* AI Provider Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred AI Provider
                </label>
                <select
                  value={aiSettings.preferred_ai_provider}
                  onChange={(e) => setAiSettings({...aiSettings, preferred_ai_provider: e.target.value})}
                  className="select-field"
                >
                  <option value="openai">OpenAI GPT-4</option>
                  <option value="claude">Anthropic Claude</option>
                  <option value="both">Let users choose</option>
                </select>
              </div>

              {/* OpenAI Settings */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">OpenAI Configuration</h4>
                  <button
                    onClick={() => getSetupGuide('openai')}
                    className="text-purple-600 hover:text-purple-700 text-sm"
                  >
                    Setup Guide
                  </button>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={aiSettings.openai_api_key || ''}
                    onChange={(e) => setAiSettings({...aiSettings, openai_api_key: e.target.value})}
                    className="input-field"
                    placeholder="sk-..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-purple-600">platform.openai.com</a>
                  </p>
                </div>
              </div>

              {/* Claude Settings */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-gray-900">Anthropic Claude Configuration</h4>
                  <button
                    onClick={() => getSetupGuide('claude')}
                    className="text-purple-600 hover:text-purple-700 text-sm"
                  >
                    Setup Guide
                  </button>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Claude API Key
                  </label>
                  <input
                    type="password"
                    value={aiSettings.claude_api_key || ''}
                    onChange={(e) => setAiSettings({...aiSettings, claude_api_key: e.target.value})}
                    className="input-field"
                    placeholder="sk-ant-..."
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your API key from <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer" className="text-purple-600">console.anthropic.com</a>
                  </p>
                </div>
              </div>

              {/* AI Enable Toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Enable AI Features</h4>
                  <p className="text-sm text-gray-600">Turn on AI-powered coaching and insights</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiSettings.ai_enabled}
                    onChange={(e) => setAiSettings({...aiSettings, ai_enabled: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <button
                onClick={saveAiSettings}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Saving...' : 'Save AI Settings'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* WhatsApp Settings Tab */}
      {activeTab === 'whatsapp' && (
        <div className="space-y-6">
          <div className="stats-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">WhatsApp Business API Configuration</h3>
            
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🔗 Webhook URL</h4>
                <p className="text-sm text-blue-700 mb-2">
                  Use this URL in your WhatsApp Business API configuration:
                </p>
                <div className="bg-white p-2 rounded border text-sm font-mono break-all">
                  {webhookUrl}
                </div>
                <button
                  onClick={() => navigator.clipboard.writeText(webhookUrl)}
                  className="btn-secondary text-xs mt-2"
                >
                  Copy URL
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Account ID
                  </label>
                  <input
                    type="text"
                    value={whatsappSettings.whatsapp_business_account_id || ''}
                    onChange={(e) => setWhatsappSettings({...whatsappSettings, whatsapp_business_account_id: e.target.value})}
                    className="input-field"
                    placeholder="Your WhatsApp Business Account ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number ID
                  </label>
                  <input
                    type="text"
                    value={whatsappSettings.phone_number_id || ''}
                    onChange={(e) => setWhatsappSettings({...whatsappSettings, phone_number_id: e.target.value})}
                    className="input-field"
                    placeholder="WhatsApp Phone Number ID"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Access Token
                </label>
                <input
                  type="password"
                  value={whatsappSettings.whatsapp_access_token || ''}
                  onChange={(e) => setWhatsappSettings({...whatsappSettings, whatsapp_access_token: e.target.value})}
                  className="input-field"
                  placeholder="Your WhatsApp API Access Token"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Webhook Verify Token
                </label>
                <input
                  type="text"
                  value={whatsappSettings.webhook_verify_token || ''}
                  onChange={(e) => setWhatsappSettings({...whatsappSettings, webhook_verify_token: e.target.value})}
                  className="input-field"
                  placeholder="Custom verify token for webhook security"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">Enable WhatsApp Integration</h4>
                  <p className="text-sm text-gray-600">Turn on WhatsApp notifications and task management</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={whatsappSettings.enabled}
                    onChange={(e) => setWhatsappSettings({...whatsappSettings, enabled: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <button
                onClick={saveWhatsappSettings}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Saving...' : 'Save WhatsApp Settings'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Setup Guides Tab */}
      {activeTab === 'guides' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Google Workspace',
                description: 'Connect Calendar & Sheets for automation',
                icon: '📅',
                type: 'google'
              },
              {
                title: 'OpenAI Setup',
                description: 'Configure OpenAI GPT-4 for AI coaching',
                icon: '🤖',
                type: 'openai'
              },
              {
                title: 'Claude Setup',
                description: 'Setup Anthropic Claude for AI assistance',
                icon: '🧠',
                type: 'claude'
              },
              {
                title: 'WhatsApp Business',
                description: 'Connect WhatsApp for notifications',
                icon: '📱',
                type: 'whatsapp'
              }
            ].map((guide) => (
              <div
                key={guide.type}
                className="stats-card hover:scale-105 transition-transform cursor-pointer"
                onClick={() => getSetupGuide(guide.type)}
              >
                <div className="text-center">
                  <div className="text-4xl mb-3">{guide.icon}</div>
                  <h3 className="font-semibold text-gray-900 mb-2">{guide.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{guide.description}</p>
                  <button className="btn-secondary text-sm">
                    View Setup Guide
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Setup Guide Details */}
          {setupGuide && (
            <div className="stats-card">
              <h3 className="text-xl font-bold text-gray-900 mb-4">{setupGuide.title}</h3>
              
              {setupGuide.requirements && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-2">Requirements:</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    {setupGuide.requirements.map((req, index) => (
                      <li key={index}>{req}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="mb-6">
                <h4 className="font-semibold text-gray-900 mb-2">Setup Steps:</h4>
                <ol className="list-decimal list-inside space-y-2 text-gray-600">
                  {setupGuide.steps.map((step, index) => (
                    <li key={index} className="leading-relaxed">{step}</li>
                  ))}
                </ol>
              </div>

              <button
                onClick={() => setSetupGuide(null)}
                className="btn-secondary"
              >
                Close Guide
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IntegrationSettings;