import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectManager = ({ currentUser, users }) => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectTasks, setProjectTasks] = useState([]);
  const [customColumns, setCustomColumns] = useState([
    { id: 'todo', title: 'To Do', tasks: [], color: 'blue' },
    { id: 'in_progress', title: 'In Progress', tasks: [], color: 'yellow' },
    { id: 'completed', title: 'Completed', tasks: [], color: 'green' }
  ]);
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [showColumnModal, setShowColumnModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    owner_id: '',
    team_members: [],
    due_date: ''
  });
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    assigned_to: '',
    priority: 'medium',
    due_date: '',
    status: 'todo'
  });
  const [newColumn, setNewColumn] = useState({
    title: '',
    color: 'blue'
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchProjectTasks(selectedProject.id);
    }
  }, [selectedProject]);

  useEffect(() => {
    // Update custom columns with tasks whenever projectTasks changes
    const updatedColumns = customColumns.map(column => ({
      ...column,
      tasks: projectTasks.filter(task => task.status === column.id)
    }));
    setCustomColumns(updatedColumns);
  }, [projectTasks]);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
      if (response.data.length > 0 && !selectedProject) {
        setSelectedProject(response.data[0]);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchProjectTasks = async (projectId) => {
    try {
      const response = await axios.get(`${API}/tasks?project_id=${projectId}`);
      setProjectTasks(response.data);
    } catch (error) {
      console.error('Error fetching project tasks:', error);
    }
  };

  const createProject = async () => {
    try {
      const projectData = {
        ...newProject,
        due_date: newProject.due_date ? new Date(newProject.due_date).toISOString() : null
      };
      const response = await axios.post(`${API}/projects`, projectData);
      setProjects([...projects, response.data]);
      setNewProject({
        name: '',
        description: '',
        owner_id: '',
        team_members: [],
        due_date: ''
      });
      setShowProjectModal(false);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const createProjectTask = async () => {
    try {
      const taskData = {
        ...newTask,
        project_id: selectedProject.id,
        due_date: newTask.due_date ? new Date(newTask.due_date).toISOString() : null
      };
      await axios.post(`${API}/tasks`, taskData);
      setNewTask({
        title: '',
        description: '',
        assigned_to: '',
        priority: 'medium',
        due_date: '',
        status: 'todo'
      });
      setShowTaskModal(false);
      fetchProjectTasks(selectedProject.id);
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      await axios.put(`${API}/tasks/${taskId}`, { status: newStatus });
      // Update local state immediately for smooth UX
      setProjectTasks(prev => 
        prev.map(task => 
          task.id === taskId ? { ...task, status: newStatus } : task
        )
      );
    } catch (error) {
      console.error('Error updating task status:', error);
      // Revert changes on error
      fetchProjectTasks(selectedProject.id);
    }
  };

  const addCustomColumn = () => {
    const columnId = newColumn.title.toLowerCase().replace(/\s+/g, '_');
    const newCol = {
      id: columnId,
      title: newColumn.title,
      tasks: [],
      color: newColumn.color
    };
    
    setCustomColumns([...customColumns, newCol]);
    setNewColumn({ title: '', color: 'blue' });
    setShowColumnModal(false);
  };

  const deleteColumn = (columnId) => {
    if (['todo', 'in_progress', 'completed'].includes(columnId)) {
      alert('Cannot delete default columns');
      return;
    }
    
    if (confirm('Are you sure you want to delete this column? Tasks in this column will be moved to "To Do".')) {
      // Move all tasks from deleted column to 'todo'
      customColumns.find(col => col.id === columnId)?.tasks.forEach(task => {
        updateTaskStatus(task.id, 'todo');
      });
      
      setCustomColumns(customColumns.filter(col => col.id !== columnId));
    }
  };

  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;

    // If dropped outside a droppable area
    if (!destination) return;

    // If dropped in the same position
    if (destination.droppableId === source.droppableId && destination.index === source.index) {
      return;
    }

    // Find the task being moved
    const taskId = draggableId;
    const newStatus = destination.droppableId;

    // Update task status in backend
    updateTaskStatus(taskId, newStatus);
  };

  const getUserName = (userId) => {
    const user = users.find(u => u.id === userId);
    return user ? user.name : 'Unassigned';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString();
  };

  const getColumnColor = (color) => {
    const colorMap = {
      blue: 'bg-blue-100 border-blue-300 text-blue-800',
      yellow: 'bg-yellow-100 border-yellow-300 text-yellow-800',
      green: 'bg-green-100 border-green-300 text-green-800',
      red: 'bg-red-100 border-red-300 text-red-800',
      purple: 'bg-purple-100 border-purple-300 text-purple-800',
      indigo: 'bg-indigo-100 border-indigo-300 text-indigo-800',
      pink: 'bg-pink-100 border-pink-300 text-pink-800'
    };
    return colorMap[color] || colorMap.blue;
  };

  const TaskCard = ({ task, index }) => (
    <Draggable draggableId={task.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`task-card bg-white border border-gray-200 p-4 rounded-lg shadow-sm transition-all ${
            snapshot.isDragging ? 'shadow-lg rotate-1 scale-105' : 'hover:shadow-md'
          }`}
        >
          <div className="flex items-start justify-between mb-2">
            <h4 className="font-semibold text-gray-900 flex-1">{task.title}</h4>
            <div className="flex items-center space-x-1 text-gray-400">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </div>
          </div>
          
          {task.description && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">{task.description}</p>
          )}
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className={`badge badge-${task.priority} text-xs`}>{task.priority}</span>
              <span className="text-xs text-gray-500">{formatDate(task.due_date)}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                  <span className="text-xs font-medium text-purple-600">
                    {getUserName(task.assigned_to).charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-xs text-gray-600 truncate">
                  {getUserName(task.assigned_to)}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </Draggable>
  );

  const KanbanColumn = ({ column, index }) => (
    <div className="kanban-column flex-shrink-0 w-80">
      <div className={`kanban-column-header p-3 rounded-t-lg border-2 ${getColumnColor(column.color)} flex items-center justify-between`}>
        <div className="flex items-center space-x-2">
          <h3 className="font-semibold">{column.title}</h3>
          <span className="badge bg-white bg-opacity-50 text-xs">
            {column.tasks.length}
          </span>
        </div>
        
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setNewTask({ ...newTask, status: column.id })}
            className="text-current hover:bg-white hover:bg-opacity-20 p-1 rounded"
            title="Add task to this column"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
          </button>
          
          {!['todo', 'in_progress', 'completed'].includes(column.id) && (
            <button
              onClick={() => deleteColumn(column.id)}
              className="text-current hover:bg-white hover:bg-opacity-20 p-1 rounded"
              title="Delete column"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
      </div>
      
      <Droppable droppableId={column.id}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`kanban-column-content min-h-96 p-3 bg-gray-50 border-2 border-t-0 rounded-b-lg space-y-3 ${
              snapshot.isDraggingOver ? 'bg-blue-50 border-blue-300' : 'border-gray-200'
            }`}
          >
            {column.tasks.map((task, index) => (
              <TaskCard key={task.id} task={task} index={index} />
            ))}
            {provided.placeholder}
            
            {column.tasks.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                <p className="text-sm">Drop tasks here</p>
                <p className="text-xs mt-1">or click + to add</p>
              </div>
            )}
          </div>
        )}
      </Droppable>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🚀 Advanced Project Management</h2>
          <p className="text-gray-600 mt-1">Drag & drop Kanban boards with custom workflow columns</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowColumnModal(true)}
            className="btn-secondary"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            Add Column
          </button>
          <button
            onClick={() => setShowProjectModal(true)}
            className="btn-secondary"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
            </svg>
            New Project
          </button>
          {selectedProject && (
            <button
              onClick={() => setShowTaskModal(true)}
              className="btn-primary"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
              Add Task
            </button>
          )}
        </div>
      </div>

      {/* Project Selector */}
      {projects.length > 0 && (
        <div className="stats-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Active Projects</h3>
            <span className="text-sm text-gray-500">{projects.length} projects</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map(project => (
              <div
                key={project.id}
                onClick={() => setSelectedProject(project)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedProject?.id === project.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <h4 className="font-semibold text-gray-900 mb-2">{project.name}</h4>
                <p className="text-gray-600 text-sm mb-3">{project.description}</p>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">
                    Owner: {getUserName(project.owner_id)}
                  </span>
                  <span className="text-gray-500">
                    {project.team_members?.length || 0} members
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enhanced Kanban Board */}
      {selectedProject ? (
        <div className="space-y-4">
          <div className="stats-card">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-900">{selectedProject.name}</h3>
                <p className="text-gray-600">{selectedProject.description}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Due: {formatDate(selectedProject.due_date)}</p>
                <p className="text-sm text-gray-500">{projectTasks.length} tasks</p>
              </div>
            </div>
          </div>

          <DragDropContext onDragEnd={onDragEnd}>
            <div className="kanban-board-container mobile-scroll">
              <div className="kanban-board flex space-x-6 pb-4 lg:flex-row flex-col lg:space-x-6 lg:space-y-0 space-y-4 space-x-0" style={{ minWidth: 'max-content' }}>
                {customColumns.map((column, index) => (
                  <KanbanColumn key={column.id} column={column} index={index} />
                ))}
              </div>
            </div>
          </DragDropContext>
        </div>
      ) : (
        <div className="stats-card text-center py-12">
          <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fillRule="evenodd" d="M4 5a2 2 0 012-2v1a1 1 0 001 1h6a1 1 0 001-1V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No Projects Yet</h3>
          <p className="text-gray-600 mb-4">Create your first project to start collaborating with your team</p>
          <button
            onClick={() => setShowProjectModal(true)}
            className="btn-primary"
          >
            Create First Project
          </button>
        </div>
      )}

      {/* Add Custom Column Modal */}
      {showColumnModal && (
        <div className="modal-overlay" onClick={() => setShowColumnModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Add Custom Column</h3>
              <button
                onClick={() => setShowColumnModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Column Title</label>
                <input
                  type="text"
                  value={newColumn.title}
                  onChange={(e) => setNewColumn({ ...newColumn, title: e.target.value })}
                  className="input-field"
                  placeholder="e.g., Assigned, Under Review, Testing"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Color Theme</label>
                <div className="grid grid-cols-4 gap-3">
                  {['blue', 'yellow', 'green', 'red', 'purple', 'indigo', 'pink'].map((color) => (
                    <button
                      key={color}
                      onClick={() => setNewColumn({ ...newColumn, color })}
                      className={`p-3 rounded-lg border-2 transition-all ${
                        newColumn.color === color ? 'ring-2 ring-purple-500' : ''
                      } ${getColumnColor(color)}`}
                    >
                      <div className="w-full h-2 rounded"></div>
                      <p className="text-xs mt-1 capitalize">{color}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={addCustomColumn}
                  disabled={!newColumn.title.trim()}
                  className="btn-primary flex-1"
                >
                  Add Column
                </button>
                <button
                  onClick={() => setShowColumnModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Project Modal */}
      {showProjectModal && (
        <div className="modal-overlay" onClick={() => setShowProjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Create New Project</h3>
              <button
                onClick={() => setShowProjectModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  className="input-field"
                  placeholder="Enter project name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  className="textarea-field"
                  placeholder="Enter project description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Project Owner</label>
                  <select
                    value={newProject.owner_id}
                    onChange={(e) => setNewProject({ ...newProject, owner_id: e.target.value })}
                    className="select-field"
                  >
                    <option value="">Select owner</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
                  <input
                    type="date"
                    value={newProject.due_date}
                    onChange={(e) => setNewProject({ ...newProject, due_date: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  onClick={createProject}
                  className="btn-primary flex-1"
                >
                  Create Project
                </button>
                <button
                  onClick={() => setShowProjectModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Task Modal */}
      {showTaskModal && (
        <div className="modal-overlay" onClick={() => setShowTaskModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold">Add Task to {selectedProject?.name}</h3>
              <button
                onClick={() => setShowTaskModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Task Title</label>
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

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Assign to</label>
                  <select
                    value={newTask.assigned_to}
                    onChange={(e) => setNewTask({ ...newTask, assigned_to: e.target.value })}
                    className="select-field"
                  >
                    <option value="">Select team member</option>
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

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Column</label>
                  <select
                    value={newTask.status}
                    onChange={(e) => setNewTask({ ...newTask, status: e.target.value })}
                    className="select-field"
                  >
                    {customColumns.map((column) => (
                      <option key={column.id} value={column.id}>
                        {column.title}
                      </option>
                    ))}
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
                  onClick={createProjectTask}
                  className="btn-primary flex-1"
                >
                  Add Task
                </button>
                <button
                  onClick={() => setShowTaskModal(false)}
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

export default ProjectManager;