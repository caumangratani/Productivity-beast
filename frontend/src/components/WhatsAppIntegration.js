import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WhatsAppIntegration = ({ currentUser }) => {
  const [whatsappStatus, setWhatsappStatus] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [connectionHistory, setConnectionHistory] = useState([]);
  const [testMessage, setTestMessage] = useState('');
  const [testPhone, setTestPhone] = useState('');

  useEffect(() => {
    checkWhatsAppStatus();
    const interval = setInterval(checkWhatsAppStatus, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const checkWhatsAppStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      setWhatsappStatus(response.data);
      
      // If QR code is needed, fetch it
      if (response.data.status === 'qr_ready' || (!response.data.connected && !qrCode)) {
        fetchQRCode();
      } else if (response.data.connected) {
        setQrCode(null);
      }
    } catch (error) {
      console.error('Error checking WhatsApp status:', error);
      setWhatsappStatus({
        connected: false,
        status: 'service_unavailable',
        error: 'Failed to connect to WhatsApp service'
      });
    }
  };

  const fetchQRCode = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/qr`);
      if (response.data.qr) {
        setQrCode(response.data.qr);
      }
    } catch (error) {
      console.error('Error fetching QR code:', error);
    }
  };

  const restartWhatsApp = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/whatsapp/restart`);
      setConnectionHistory(prev => [...prev, {
        timestamp: new Date(),
        action: 'restart',
        message: 'WhatsApp service restart initiated'
      }]);
      
      // Clear QR code and wait for new one
      setQrCode(null);
      setTimeout(checkWhatsAppStatus, 3000);
    } catch (error) {
      console.error('Error restarting WhatsApp:', error);
    }
    setLoading(false);
  };

  const sendTestMessage = async () => {
    if (!testPhone || !testMessage) {
      alert('Please enter both phone number and message');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/whatsapp/send`, {
        phone_number: testPhone,
        message: testMessage
      });
      
      if (response.data.success) {
        setConnectionHistory(prev => [...prev, {
          timestamp: new Date(),
          action: 'message_sent',
          message: `Test message sent to ${testPhone}`
        }]);
        setTestMessage('');
        setTestPhone('');
      } else {
        alert('Failed to send message: ' + response.data.error);
      }
    } catch (error) {
      console.error('Error sending test message:', error);
      alert('Error sending message');
    }
    setLoading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'text-green-600 bg-green-100';
      case 'qr_ready': return 'text-yellow-600 bg-yellow-100';
      case 'disconnected': return 'text-gray-600 bg-gray-100';
      case 'service_unavailable': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return '✅';
      case 'qr_ready': return '📱';
      case 'disconnected': return '❌';
      case 'service_unavailable': return '🚫';
      default: return '❓';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">📱 WhatsApp Integration</h2>
          <p className="text-gray-600 mt-1">Manage tasks and get productivity updates via WhatsApp</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={restartWhatsApp}
            disabled={loading}
            className="btn-secondary"
          >
            {loading ? (
              <div className="loading-spinner"></div>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
              </svg>
            )}
            Restart Service
          </button>
          <button
            onClick={checkWhatsAppStatus}
            className="btn-primary"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Refresh Status
          </button>
        </div>
      </div>

      {/* Status Card */}
      <div className="stats-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Connection Status</h3>
          {whatsappStatus && (
            <span className={`badge ${getStatusColor(whatsappStatus.status)}`}>
              {getStatusIcon(whatsappStatus.status)} {whatsappStatus.status.replace('_', ' ').toUpperCase()}
            </span>
          )}
        </div>

        {whatsappStatus?.connected && whatsappStatus.user && (
          <div className="p-4 bg-green-50 rounded-lg border border-green-200 mb-4">
            <h4 className="font-medium text-green-900 mb-2">✅ Connected Successfully!</h4>
            <p className="text-sm text-green-700">
              WhatsApp account: <strong>{whatsappStatus.user.name || whatsappStatus.user.id}</strong>
            </p>
            <p className="text-sm text-green-600 mt-1">
              You can now send WhatsApp messages to manage your tasks!
            </p>
          </div>
        )}

        {whatsappStatus?.status === 'service_unavailable' && (
          <div className="p-4 bg-red-50 rounded-lg border border-red-200 mb-4">
            <h4 className="font-medium text-red-900 mb-2">🚫 Service Unavailable</h4>
            <p className="text-sm text-red-700">
              WhatsApp service is not running. Please check the server configuration.
            </p>
            {whatsappStatus.error && (
              <p className="text-xs text-red-600 mt-1">Error: {whatsappStatus.error}</p>
            )}
          </div>
        )}
      </div>

      {/* QR Code Section */}
      {qrCode && (
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📱 Connect Your WhatsApp</h3>
          <div className="text-center">
            <div className="inline-block p-4 bg-white border-2 border-gray-300 rounded-lg">
              <img 
                src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrCode)}`}
                alt="WhatsApp QR Code"
                className="w-48 h-48 mx-auto"
              />
            </div>
            <div className="mt-4 max-w-md mx-auto">
              <h4 className="font-medium text-gray-900 mb-2">How to connect:</h4>
              <ol className="text-sm text-gray-600 text-left space-y-1">
                <li>1. Open WhatsApp on your phone</li>
                <li>2. Go to Settings → Linked Devices</li>
                <li>3. Tap "Link a Device"</li>
                <li>4. Scan the QR code above</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Available Commands */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🤖 WhatsApp Bot Commands</h3>
          <div className="space-y-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 text-sm">Task Management</h4>
              <div className="text-xs text-gray-600 mt-1 space-y-1">
                <div><code>create task: [description]</code> - Add new task</div>
                <div><code>list tasks</code> - Show pending tasks</div>
                <div><code>complete task [number]</code> - Mark task as done</div>
              </div>
            </div>
            
            <div className="p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 text-sm">Analytics & Coaching</h4>
              <div className="text-xs text-gray-600 mt-1 space-y-1">
                <div><code>stats</code> - View performance stats</div>
                <div><code>coach</code> - Get productivity tips</div>
                <div><code>help</code> - Show all commands</div>
              </div>
            </div>
          </div>
        </div>

        {/* Test Message */}
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🧪 Test WhatsApp Messaging</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="text"
                value={testPhone}
                onChange={(e) => setTestPhone(e.target.value)}
                placeholder="e.g., 1234567890"
                className="input-field"
                disabled={!whatsappStatus?.connected}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Test Message</label>
              <textarea
                value={testMessage}
                onChange={(e) => setTestMessage(e.target.value)}
                placeholder="Type your test message..."
                className="textarea-field"
                rows="3"
                disabled={!whatsappStatus?.connected}
              />
            </div>
            
            <button
              onClick={sendTestMessage}
              disabled={!whatsappStatus?.connected || loading || !testPhone || !testMessage}
              className="btn-primary w-full"
            >
              {loading ? (
                <div className="loading-spinner"></div>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              )}
              Send Test Message
            </button>
          </div>
        </div>
      </div>

      {/* Connection History */}
      {connectionHistory.length > 0 && (
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Activity Log</h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {connectionHistory.slice().reverse().map((entry, index) => (
              <div key={index} className="flex items-center space-x-3 text-sm">
                <span className="text-gray-500">
                  {entry.timestamp.toLocaleTimeString()}
                </span>
                <span className={`badge ${
                  entry.action === 'restart' ? 'badge-in_progress' : 'badge-completed'
                }`}>
                  {entry.action.replace('_', ' ')}
                </span>
                <span className="text-gray-700">{entry.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Features List */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 WhatsApp Integration Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Task Management</h4>
                <p className="text-sm text-gray-600">Create, list, and complete tasks via WhatsApp messages</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Performance Tracking</h4>
                <p className="text-sm text-gray-600">Get productivity stats and completion rates on demand</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">AI Coaching</h4>
                <p className="text-sm text-gray-600">Receive productivity tips and coaching advice</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Smart Reminders</h4>
                <p className="text-sm text-gray-600 italic">Coming Soon - Automated task deadline reminders</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Daily Reports</h4>
                <p className="text-sm text-gray-600 italic">Coming Soon - Automated daily productivity summaries</p>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                <svg className="w-3 h-3 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Team Notifications</h4>
                <p className="text-sm text-gray-600 italic">Coming Soon - Team task updates and collaboration</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppIntegration;