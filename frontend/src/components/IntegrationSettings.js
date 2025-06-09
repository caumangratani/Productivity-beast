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
  
  const [activeTab, setActiveTab] = useState('ai');
  const [setupGuide, setSetupGuide] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSettings();
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

  const saveAiSettings = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/integrations/ai-settings`, aiSettings);
      alert('AI settings saved successfully!');
    } catch (error) {
      alert('Error saving AI settings: ' + error.message);
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
          <h2 className="text-3xl font-bold text-gray-900">Integration Settings</h2>
          <p className="text-gray-600 mt-1">Configure AI providers and external integrations</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
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
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
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