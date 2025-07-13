import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SimpleWhatsAppIntegration from './SimpleWhatsAppIntegration';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const WhatsAppIntegration = ({ currentUser }) => {
  const [whatsappStatus, setWhatsappStatus] = useState(null);
  const [qrCode, setQrCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [connectionHistory, setConnectionHistory] = useState([]);
  const [testMessage, setTestMessage] = useState('');
  const [testPhone, setTestPhone] = useState('');
  const [phoneNumber, setPhoneNumber] = useState(currentUser?.phone_number || '');
  const [teamMessage, setTeamMessage] = useState('');
  const [sendingTeamMessage, setSendingTeamMessage] = useState(false);

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

  const updatePhoneNumber = async () => {
    if (!phoneNumber.trim()) {
      alert('Please enter a phone number');
      return;
    }
    
    if (!phoneNumber.startsWith('+')) {
      alert('Phone number must include country code (e.g., +1234567890)');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.patch(`${API}/users/${currentUser.id}/phone`, 
        { phone_number: phoneNumber },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        alert('Phone number updated successfully! You can now receive WhatsApp notifications.');
        
        setConnectionHistory(prev => [...prev, {
          timestamp: new Date(),
          action: 'phone_updated',
          message: `Phone number updated to ${phoneNumber}`
        }]);
      } else {
        alert('Failed to update phone number: ' + (response.data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error updating phone number:', error);
      let errorMessage = 'Failed to update phone number';
      
      if (error.response?.data?.detail) {
        errorMessage += ': ' + error.response.data.detail;
      } else if (error.message) {
        errorMessage += ': ' + error.message;
      }
      
      alert(errorMessage);
    }
    setLoading(false);
  };

  const sendTeamMessage = async () => {
    if (!teamMessage.trim()) {
      alert('Please enter a message to send');
      return;
    }

    setSendingTeamMessage(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/whatsapp/send-team-message`, 
        { 
          sender_id: currentUser.id,
          message: teamMessage
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setConnectionHistory(prev => [...prev, {
          timestamp: new Date(),
          action: 'team_message',
          message: `Team message sent to ${response.data.sent_count} members`
        }]);
        setTeamMessage('');
        alert(`Message sent to ${response.data.sent_count} team members!`);
      } else {
        alert('Failed to send team message');
      }
    } catch (error) {
      console.error('Error sending team message:', error);
      alert('Error sending team message');
    }
    setSendingTeamMessage(false);
  };

  const sendDailyReminders = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/whatsapp/send-daily-reminders`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setConnectionHistory(prev => [...prev, {
          timestamp: new Date(),
          action: 'daily_reminders',
          message: `Daily reminders sent to ${response.data.sent_count} users`
        }]);
        alert(`Daily reminders sent to ${response.data.sent_count} users!`);
      }
    } catch (error) {
      console.error('Error sending daily reminders:', error);
      alert('Error sending daily reminders');
    }
    setLoading(false);
  };

  const sendWeeklyReports = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/whatsapp/send-weekly-reports`, {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        setConnectionHistory(prev => [...prev, {
          timestamp: new Date(),
          action: 'weekly_reports',
          message: `Weekly reports sent to ${response.data.sent_count} users`
        }]);
        alert(`Weekly reports sent to ${response.data.sent_count} users!`);
      }
    } catch (error) {
      console.error('Error sending weekly reports:', error);
      alert('Error sending weekly reports');
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
    <SimpleWhatsAppIntegration currentUser={currentUser} />
  );
};

export default WhatsAppIntegration;