import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SimpleWhatsAppIntegration = ({ currentUser }) => {
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [qrCode, setQrCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    checkWhatsAppStatus();
    // Auto-refresh status every 5 seconds
    const interval = setInterval(checkWhatsAppStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkWhatsAppStatus = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/status`);
      if (response.data.connected) {
        setConnectionStatus('connected');
        setIsConnected(true);
        setPhoneNumber(response.data.phone_number || '');
      } else {
        setConnectionStatus('disconnected');
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Error checking WhatsApp status:', error);
      setConnectionStatus('unavailable');
    }
  };

  const startConnection = async () => {
    setLoading(true);
    try {
      // Start WhatsApp connection process
      const response = await axios.post(`${API}/whatsapp/start-connection`);
      
      if (response.data.success) {
        setConnectionStatus('waiting_for_qr');
        // Get QR code
        await getQRCode();
      } else {
        alert('Failed to start WhatsApp connection');
      }
    } catch (error) {
      console.error('Error starting WhatsApp connection:', error);
      alert('Failed to start WhatsApp connection: ' + error.message);
    }
    setLoading(false);
  };

  const getQRCode = async () => {
    try {
      const response = await axios.get(`${API}/whatsapp/qr-code`);
      if (response.data.qr_code) {
        setQrCode(response.data.qr_code);
        setConnectionStatus('scanning');
      }
    } catch (error) {
      console.error('Error getting QR code:', error);
      setConnectionStatus('error');
    }
  };

  const disconnectWhatsApp = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/whatsapp/disconnect`);
      if (response.data.success) {
        setConnectionStatus('disconnected');
        setIsConnected(false);
        setQrCode(null);
        setPhoneNumber('');
        alert('WhatsApp disconnected successfully');
      }
    } catch (error) {
      console.error('Error disconnecting WhatsApp:', error);
      alert('Failed to disconnect WhatsApp');
    }
    setLoading(false);
  };

  const updatePhoneNumber = async () => {
    if (!currentUser?.id) return;
    
    try {
      const response = await axios.patch(`${API}/users/${currentUser.id}/phone`, {
        phone_number: phoneNumber
      });
      
      if (response.data.success) {
        alert('Phone number updated successfully!');
      }
    } catch (error) {
      console.error('Error updating phone number:', error);
      alert('Failed to update phone number');
    }
  };

  const renderConnectionStatus = () => {
    switch (connectionStatus) {
      case 'connected':
        return (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                <h3 className="text-lg font-semibold text-green-900">WhatsApp Connected</h3>
              </div>
              <button
                onClick={disconnectWhatsApp}
                disabled={loading}
                className="btn-secondary text-sm"
              >
                {loading ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-green-700">📱 Phone Number:</span>
                <span className="font-mono text-sm text-green-900">{phoneNumber || 'Not set'}</span>
              </div>
              <div className="text-sm text-green-700">
                ✅ WhatsApp is ready for productivity notifications!
              </div>
              <div className="text-sm text-green-600">
                💡 You can now receive task reminders, team updates, and performance reports via WhatsApp.
              </div>
            </div>
          </div>
        );
        
      case 'scanning':
        return (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
                <h3 className="text-lg font-semibold text-blue-900">Scan QR Code</h3>
              </div>
              
              {qrCode ? (
                <div className="space-y-4">
                  <div className="bg-white p-4 rounded-lg inline-block">
                    <img 
                      src={`data:image/png;base64,${qrCode}`} 
                      alt="WhatsApp QR Code"
                      className="w-64 h-64 mx-auto"
                    />
                  </div>
                  <div className="text-sm text-blue-700">
                    📱 <strong>Steps:</strong>
                    <ol className="list-decimal list-inside mt-2 space-y-1 text-left">
                      <li>Open WhatsApp on your phone</li>
                      <li>Tap Menu (⋮) → Linked Devices</li>
                      <li>Tap "Link a device"</li>
                      <li>Scan this QR code</li>
                    </ol>
                  </div>
                </div>
              ) : (
                <div className="text-center">
                  <div className="loading-spinner mx-auto mb-4"></div>
                  <p className="text-blue-700">Generating QR code...</p>
                </div>
              )}
              
              <button
                onClick={checkWhatsAppStatus}
                className="btn-secondary text-sm mt-4"
              >
                Check Connection Status
              </button>
            </div>
          </div>
        );
        
      case 'waiting_for_qr':
        return (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <div className="text-center">
              <div className="loading-spinner mx-auto mb-4"></div>
              <h3 className="text-lg font-semibold text-yellow-900">Starting WhatsApp Connection</h3>
              <p className="text-sm text-yellow-700 mt-2">Preparing QR code for scanning...</p>
            </div>
          </div>
        );
        
      case 'error':
        return (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-red-900">Connection Error</h3>
              <p className="text-sm text-red-700 mt-2">
                Failed to connect to WhatsApp. Please try again.
              </p>
              <button
                onClick={startConnection}
                className="btn-primary mt-4"
              >
                Try Again
              </button>
            </div>
          </div>
        );
        
      case 'unavailable':
        return (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900">Service Unavailable</h3>
              <p className="text-sm text-gray-700 mt-2">
                WhatsApp service is not available at the moment. Please try again later.
              </p>
              <button
                onClick={checkWhatsAppStatus}
                className="btn-secondary mt-4"
              >
                Retry
              </button>
            </div>
          </div>
        );
        
      default: // disconnected
        return (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <div className="text-center">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Connect WhatsApp</h3>
              <p className="text-sm text-gray-600 mb-4">
                Get productivity notifications and manage tasks directly through WhatsApp
              </p>
              <button
                onClick={startConnection}
                disabled={loading}
                className="btn-primary"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="loading-spinner"></div>
                    <span>Connecting...</span>
                  </div>
                ) : (
                  'Connect WhatsApp'
                )}
              </button>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">📱 WhatsApp Integration</h2>
        <p className="text-gray-600 mt-1">Simple scan and ready - Connect your WhatsApp in seconds</p>
      </div>

      {/* Connection Status */}
      {renderConnectionStatus()}

      {/* Phone Number Setup */}
      {isConnected && (
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📞 Phone Number Setup</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Phone Number
              </label>
              <div className="flex space-x-3">
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  className="input-field flex-1"
                  placeholder="+1234567890"
                />
                <button
                  onClick={updatePhoneNumber}
                  className="btn-primary"
                >
                  Update
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Include country code (e.g., +1 for US, +91 for India)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Features */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 What You'll Get</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">📅 Task Reminders</h4>
            <p className="text-sm text-blue-700">Daily notifications for pending and overdue tasks</p>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg">
            <h4 className="font-medium text-green-900 mb-2">📊 Progress Reports</h4>
            <p className="text-sm text-green-700">Weekly performance summaries and insights</p>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg">
            <h4 className="font-medium text-purple-900 mb-2">👥 Team Updates</h4>
            <p className="text-sm text-purple-700">Instant notifications for team activities</p>
          </div>
          
          <div className="p-4 bg-yellow-50 rounded-lg">
            <h4 className="font-medium text-yellow-900 mb-2">🎯 Quick Commands</h4>
            <p className="text-sm text-yellow-700">Create tasks and check stats via WhatsApp</p>
          </div>
        </div>
      </div>

      {/* Quick Commands Guide */}
      {isConnected && (
        <div className="stats-card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Quick Commands</h3>
          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">create task: [description]</code>
              <span className="text-sm text-gray-600">Create a new task</span>
            </div>
            <div className="flex items-start space-x-3">
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">list tasks</code>
              <span className="text-sm text-gray-600">Show all pending tasks</span>
            </div>
            <div className="flex items-start space-x-3">
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">complete task [number]</code>
              <span className="text-sm text-gray-600">Mark task as completed</span>
            </div>
            <div className="flex items-start space-x-3">
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">stats</code>
              <span className="text-sm text-gray-600">Get performance statistics</span>
            </div>
            <div className="flex items-start space-x-3">
              <code className="bg-gray-100 px-2 py-1 rounded text-sm">help</code>
              <span className="text-sm text-gray-600">Show all available commands</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleWhatsAppIntegration;