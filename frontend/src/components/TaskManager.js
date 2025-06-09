import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TaskManager = ({ currentUser, users }) => {
  const [tasks, setTasks] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filter, setFilter] = useState('all');
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    assigned_to: '',
    priority: 'medium',
    due_date: '',
    tags: []
  });

  useEffect(() => {
    fetchTasks();
  }, [filter]);

  const fetchTasks = async () => {
    try {
      let url = `${API}/tasks`;
      if (filter !== 'all') {
        url += `?status=${filter}`;
      }
      const response = await axios.get(url);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const createTask = async () => {
    try {
      console.log('Creating task with data:', newTask);
      const taskData = {
        ...newTask,
        due_date: newTask.due_date ? new Date(newTask.due_date).toISOString() : null
      };
      console.log('Sending task data:', taskData);
      const response = await axios.post(`${API}/tasks`, taskData);
      console.log('Task created successfully:', response.data);
      setNewTask({
        title: '',
        description: '',
        assigned_to: '',
        priority: 'medium',
        due_date: '',
        tags: []
      });
      setShowModal(false);
      fetchTasks();
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Error creating task: ' + error.message);
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      await axios.put(`${API}/tasks/${taskId}`, updates);
      fetchTasks();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await axios.delete(`${API}/tasks/${taskId}`);
      fetchTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : 'Unassigned';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'overdue': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getEisenhowerQuadrant = (quadrant) => {
    switch (quadrant) {
      case 'do': return { label: 'Do First', color: 'bg-red-100 text-red-800' };
      case 'decide': return { label: 'Schedule', color: 'bg-yellow-100 text-yellow-800' };
      case 'delegate': return { label: 'Delegate', color: 'bg-blue-100 text-blue-800' };
      case 'delete': return { label: 'Don\'t Do', color: 'bg-gray-100 text-gray-800' };
      default: return { label: 'Unclassified', color: 'bg-gray-100 text-gray-600' };
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Personal Task Management</h2>
          <p className="text-gray-600 mt-1">
            Manage your individual tasks with AI-powered prioritization
            {showModal && <span className="text-red-500 ml-2">(Modal Open)</span>}
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              console.log('Add Task button clicked, showModal currently:', showModal);
              setShowModal(true);
              console.log('setShowModal(true) called');
            }}
            className="btn-primary"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Add Task
          </button>
          <button
            onClick={() => alert(`Users loaded: ${users.length}, Show modal: ${showModal}`)}
            className="btn-secondary"
          >
            Debug Info
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex space-x-2">
        {[
          { key: 'all', label: 'All Tasks' },
          { key: 'todo', label: 'To Do' },
          { key: 'in_progress', label: 'In Progress' },
          { key: 'completed', label: 'Completed' },
          { key: 'overdue', label: 'Overdue' }
        ].map((filterOption) => (
          <button
            key={filterOption.key}
            onClick={() => setFilter(filterOption.key)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              filter === filterOption.key
                ? 'bg-purple-100 text-purple-700'
                : 'bg-white text-gray-600 hover:bg-purple-50'
            }`}
          >
            {filterOption.label}
          </button>
        ))}
      </div>

      {/* Tasks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {tasks.map((task) => {
          const eisenhower = getEisenhowerQuadrant(task.eisenhower_quadrant);
          return (
            <div
              key={task.id}
              className={`task-card priority-${task.priority}`}
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900 text-lg">{task.title}</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setEditingTask(task);
                      setNewTask(task);
                      setShowModal(true);
                    }}
                    className="text-gray-400 hover:text-purple-600"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="text-gray-400 hover:text-red-600"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" clipRule="evenodd" />
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414L7.586 12l-1.293 1.293a1 1 0 101.414 1.414L9 13.414l2.293 2.293a1 1 0 001.414-1.414L11.414 12l1.293-1.293z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>

              <p className="text-gray-600 mb-4 text-sm">{task.description}</p>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className={`badge badge-${task.priority}`}>{task.priority}</span>
                  <span className={`badge ${eisenhower.color} text-xs`}>{eisenhower.label}</span>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Assigned to:</span>
                  <span className="font-medium">{getUserName(task.assigned_to)}</span>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Due date:</span>
                  <span className="font-medium">{formatDate(task.due_date)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className={`badge badge-${task.status}`}>{task.status.replace('_', ' ')}</span>
                  <select
                    value={task.status}
                    onChange={(e) => updateTask(task.id, { status: e.target.value })}
                    className="text-xs border border-gray-300 rounded px-2 py-1"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create/Edit Task Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => {
          console.log('Modal overlay clicked');
          setShowModal(false);
        }}>
          <div className="modal-content" onClick={(e) => {
            console.log('Modal content clicked');
            e.stopPropagation();
          }}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">
                {editingTask ? 'Edit Task' : 'Create New Task'}
              </h3>
              <button
                onClick={() => {
                  console.log('Close button clicked');
                  setShowModal(false);
                  setEditingTask(null);
                  setNewTask({
                    title: '',
                    description: '',
                    assigned_to: '',
                    priority: 'medium',
                    due_date: '',
                    tags: []
                  });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                <input
                  type="text"
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="input-field"
                  placeholder="Enter task title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  className="textarea-field"
                  placeholder="Enter task description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Assign to</label>
                  <select
                    value={newTask.assigned_to}
                    onChange={(e) => setNewTask({ ...newTask, assigned_to: e.target.value })}
                    className="select-field"
                  >
                    <option value="">Select user</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                  <select
                    value={newTask.priority}
                    onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                    className="select-field"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                <input
                  type="datetime-local"
                  value={newTask.due_date}
                  onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                  className="input-field"
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={editingTask ? () => updateTask(editingTask.id, newTask) : createTask}
                  className="btn-primary flex-1"
                >
                  {editingTask ? 'Update Task' : 'Create Task'}
                </button>
                <button
                  onClick={() => {
                    setShowModal(false);
                    setEditingTask(null);
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskManager;