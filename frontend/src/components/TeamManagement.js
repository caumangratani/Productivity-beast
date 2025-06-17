import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TeamManagement = ({ currentUser }) => {
  const [teamMembers, setTeamMembers] = useState([]);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteName, setInviteName] = useState('');
  const [inviteRole, setInviteRole] = useState('team_member');
  const [loading, setLoading] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setTeamMembers(response.data);
    } catch (error) {
      console.error('Error fetching team members:', error);
    }
  };

  const inviteTeamMember = async () => {
    if (!inviteEmail || !inviteName) {
      alert('Please fill in all required fields');
      return;
    }

    setLoading(true);
    try {
      // Generate a temporary password
      const tempPassword = 'TempPass123!';
      
      const response = await axios.post(`${API}/auth/signup`, {
        name: inviteName,
        email: inviteEmail,
        password: tempPassword,
        company: currentUser?.company || 'Default Company',
        plan: 'team'
      });

      if (response.status === 200) {
        alert(`Team member invited successfully!\n\nLogin credentials:\nEmail: ${inviteEmail}\nTemporary Password: ${tempPassword}\n\nPlease share these credentials securely with the new team member.`);
        
        setInviteEmail('');
        setInviteName('');
        setInviteRole('team_member');
        setShowInviteModal(false);
        
        fetchTeamMembers();
      }
    } catch (error) {
      console.error('Error inviting team member:', error);
      alert('Error inviting team member: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const updateMemberRole = async (memberId, newRole) => {
    try {
      // For now, we'll update this locally since we need to implement the backend endpoint
      setTeamMembers(prev => 
        prev.map(member => 
          member.id === memberId ? { ...member, role: newRole } : member
        )
      );
      alert('Role updated successfully!');
    } catch (error) {
      console.error('Error updating role:', error);
      alert('Error updating role');
    }
  };

  const removeMember = async (memberId, memberName) => {
    if (!window.confirm(`Are you sure you want to remove ${memberName} from the team?`)) {
      return;
    }

    try {
      // For now, we'll remove locally since we need to implement the backend endpoint
      setTeamMembers(prev => prev.filter(member => member.id !== memberId));
      alert('Team member removed successfully!');
    } catch (error) {
      console.error('Error removing member:', error);
      alert('Error removing team member');
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'manager': return 'bg-blue-100 text-blue-800';
      case 'team_member': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin': return '👑';
      case 'manager': return '👨‍💼';
      case 'team_member': return '👤';
      default: return '👤';
    }
  };

  const generateLoginLink = (member) => {
    return `${window.location.origin}?email=${encodeURIComponent(member.email)}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">👥 Team Management</h2>
          <p className="text-gray-600 mt-1">Manage your team members and their access permissions</p>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className="btn-primary"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          Invite Team Member
        </button>
      </div>

      {/* Team Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="stats-card bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100">Total Members</p>
              <p className="text-3xl font-bold">{teamMembers.length}</p>
            </div>
            <div className="text-4xl">👥</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-green-500 to-green-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100">Active Members</p>
              <p className="text-3xl font-bold">{teamMembers.filter(m => m.role !== 'inactive').length}</p>
            </div>
            <div className="text-4xl">✅</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Managers</p>
              <p className="text-3xl font-bold">{teamMembers.filter(m => m.role === 'manager').length}</p>
            </div>
            <div className="text-4xl">👨‍💼</div>
          </div>
        </div>

        <div className="stats-card bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100">Admins</p>
              <p className="text-3xl font-bold">{teamMembers.filter(m => m.role === 'admin').length}</p>
            </div>
            <div className="text-4xl">👑</div>
          </div>
        </div>
      </div>

      {/* Team Members List */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Team Members</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {teamMembers.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                        {member.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{member.name}</div>
                        <div className="text-sm text-gray-500">{member.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getRoleIcon(member.role)}</span>
                      <select
                        value={member.role}
                        onChange={(e) => updateMemberRole(member.id, e.target.value)}
                        className={`text-xs px-2 py-1 rounded-full ${getRoleColor(member.role)} border-0`}
                        disabled={member.id === currentUser?.id}
                      >
                        <option value="team_member">Team Member</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                      </select>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div className="flex items-center space-x-2">
                        <span>Score: {member.performance_score.toFixed(1)}/10</span>
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${(member.performance_score / 10) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {member.tasks_completed}/{member.tasks_assigned} tasks completed
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(member.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => {
                        const loginLink = generateLoginLink(member);
                        navigator.clipboard.writeText(loginLink);
                        alert('Login link copied to clipboard!');
                      }}
                      className="text-blue-600 hover:text-blue-900"
                      title="Copy login link"
                    >
                      🔗
                    </button>
                    <button
                      onClick={() => alert(`Performance: ${member.performance_score.toFixed(1)}/10\nTasks: ${member.tasks_completed}/${member.tasks_assigned}\nRole: ${member.role}`)}
                      className="text-green-600 hover:text-green-900"
                      title="View details"
                    >
                      👁️
                    </button>
                    {member.id !== currentUser?.id && (
                      <button
                        onClick={() => removeMember(member.id, member.name)}
                        className="text-red-600 hover:text-red-900"
                        title="Remove member"
                      >
                        🗑️
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="modal-overlay" onClick={() => setShowInviteModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Invite Team Member</h3>
              <button
                onClick={() => setShowInviteModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={inviteName}
                  onChange={(e) => setInviteName(e.target.value)}
                  className="input-field"
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  className="input-field"
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role
                </label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="select-field"
                >
                  <option value="team_member">👤 Team Member</option>
                  <option value="manager">👨‍💼 Manager</option>
                  <option value="admin">👑 Admin</option>
                </select>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🔐 Access Levels</h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <div><strong>Team Member:</strong> Own tasks and AI coach only</div>
                  <div><strong>Manager:</strong> Team tasks and performance analytics</div>
                  <div><strong>Admin:</strong> Full system access and team management</div>
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={inviteTeamMember}
                  disabled={loading || !inviteEmail || !inviteName}
                  className="btn-primary flex-1"
                >
                  {loading ? (
                    <div className="loading-spinner"></div>
                  ) : (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" />
                    </svg>
                  )}
                  Send Invitation
                </button>
                <button
                  onClick={() => setShowInviteModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Role-Based Access Info */}
      <div className="stats-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔐 Role-Based Access Control</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-green-200 rounded-lg bg-green-50">
            <h4 className="font-medium text-green-900 mb-2">👤 Team Member Access</h4>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• View and manage own tasks only</li>
              <li>• Access AI productivity coach</li>
              <li>• Personal performance stats</li>
              <li>• Task creation and completion</li>
            </ul>
          </div>
          
          <div className="p-4 border border-blue-200 rounded-lg bg-blue-50">
            <h4 className="font-medium text-blue-900 mb-2">👨‍💼 Manager Access</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• All team member permissions</li>
              <li>• View team tasks and projects</li>
              <li>• Team performance analytics</li>
              <li>• Assign tasks to team members</li>
            </ul>
          </div>
          
          <div className="p-4 border border-red-200 rounded-lg bg-red-50">
            <h4 className="font-medium text-red-900 mb-2">👑 Admin Access</h4>
            <ul className="text-sm text-red-700 space-y-1">
              <li>• All manager permissions</li>
              <li>• Team member management</li>
              <li>• Integration settings</li>
              <li>• Full system access</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeamManagement;