import requests
import pytest
import os
import json
from datetime import datetime, timedelta
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"')
            break

# Ensure the URL doesn't have quotes
BACKEND_URL = BACKEND_URL.strip("'\"")
API_URL = f"{BACKEND_URL}/api"

logger.info(f"Using API URL: {API_URL}")

# Test data
test_users = []
test_projects = []
test_tasks = []

# Helper functions
def iso_format(dt):
    """Convert datetime to ISO format string"""
    if dt:
        return dt.isoformat()
    return None

# Test fixtures
@pytest.fixture(scope="module")
def cleanup():
    """Cleanup test data after tests"""
    yield
    # Clean up tasks
    for task in test_tasks:
        try:
            requests.delete(f"{API_URL}/tasks/{task['id']}")
        except Exception as e:
            logger.error(f"Error cleaning up task {task['id']}: {e}")
    
    # We don't delete users and projects as they might be referenced by other data

# Test cases
def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    logger.info("Health check passed")

def test_user_management():
    """Test user management endpoints"""
    # Create users
    for i in range(3):
        user_data = {
            "name": f"Test User {i}",
            "email": f"testuser{i}@example.com",
            "password": f"SecurePassword{i}!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        response = requests.post(f"{API_URL}/users", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        
        user = response.json()
        assert user["name"] == user_data["name"]
        assert user["email"] == user_data["email"]
        assert "id" in user
        
        test_users.append(user)
        logger.info(f"Created user: {user['name']} with ID: {user['id']}")
    
    # Get all users
    response = requests.get(f"{API_URL}/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= len(test_users)
    
    # Get specific user
    user_id = test_users[0]["id"]
    response = requests.get(f"{API_URL}/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    
    # Test non-existent user
    response = requests.get(f"{API_URL}/users/{str(uuid.uuid4())}")
    assert response.status_code == 404
    
    logger.info("User management tests passed")

def test_project_management():
    """Test project management endpoints"""
    # Create projects
    for i in range(2):
        project_data = {
            "name": f"Test Project {i}",
            "description": f"Description for test project {i}",
            "owner_id": test_users[2]["id"],  # Manager is the owner
            "team_members": [test_users[0]["id"], test_users[1]["id"]],
            "due_date": iso_format(datetime.utcnow() + timedelta(days=30))
        }
        
        response = requests.post(f"{API_URL}/projects", json=project_data)
        assert response.status_code == 200, f"Failed to create project: {response.text}"
        
        project = response.json()
        assert project["name"] == project_data["name"]
        assert project["description"] == project_data["description"]
        assert project["owner_id"] == project_data["owner_id"]
        assert set(project["team_members"]) == set(project_data["team_members"])
        assert "id" in project
        
        test_projects.append(project)
        logger.info(f"Created project: {project['name']} with ID: {project['id']}")
    
    # Get all projects
    response = requests.get(f"{API_URL}/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= len(test_projects)
    
    # Get specific project
    project_id = test_projects[0]["id"]
    response = requests.get(f"{API_URL}/projects/{project_id}")
    assert response.status_code == 200
    project = response.json()
    assert project["id"] == project_id
    
    # Test non-existent project
    response = requests.get(f"{API_URL}/projects/{str(uuid.uuid4())}")
    assert response.status_code == 404
    
    logger.info("Project management tests passed")

def test_task_management_and_eisenhower_matrix():
    """Test task management endpoints and Eisenhower Matrix categorization"""
    # Create tasks with different priorities and due dates to test Eisenhower Matrix
    task_scenarios = [
        # Urgent & Important (DO)
        {
            "title": "Urgent Important Task",
            "description": "This task is both urgent and important",
            "assigned_to": test_users[0]["id"],
            "project_id": test_projects[0]["id"],
            "priority": "high",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=1)),
            "tags": ["urgent", "important"]
        },
        # Important but Not Urgent (DECIDE)
        {
            "title": "Important Not Urgent Task",
            "description": "This task is important but not urgent",
            "assigned_to": test_users[1]["id"],
            "project_id": test_projects[0]["id"],
            "priority": "high",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=10)),
            "tags": ["important"]
        },
        # Urgent but Not Important (DELEGATE)
        {
            "title": "Urgent Not Important Task",
            "description": "This task is urgent but not important",
            "assigned_to": test_users[0]["id"],
            "project_id": test_projects[1]["id"],
            "priority": "low",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=1)),
            "tags": ["urgent"]
        },
        # Not Urgent & Not Important (DELETE)
        {
            "title": "Not Urgent Not Important Task",
            "description": "This task is neither urgent nor important",
            "assigned_to": test_users[1]["id"],
            "project_id": test_projects[1]["id"],
            "priority": "low",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=20)),
            "tags": ["low_priority"]
        }
    ]
    
    expected_quadrants = ["do", "decide", "delegate", "delete"]
    
    for i, task_data in enumerate(task_scenarios):
        response = requests.post(f"{API_URL}/tasks", json=task_data)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        
        task = response.json()
        assert task["title"] == task_data["title"]
        assert task["description"] == task_data["description"]
        assert task["assigned_to"] == task_data["assigned_to"]
        assert task["priority"] == task_data["priority"]
        assert "id" in task
        assert "eisenhower_quadrant" in task
        
        # Verify Eisenhower quadrant
        assert task["eisenhower_quadrant"] == expected_quadrants[i], f"Expected {expected_quadrants[i]} but got {task['eisenhower_quadrant']}"
        
        test_tasks.append(task)
        logger.info(f"Created task: {task['title']} with ID: {task['id']} in quadrant: {task['eisenhower_quadrant']}")
    
    # Get all tasks
    response = requests.get(f"{API_URL}/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= len(test_tasks)
    
    # Get tasks by assigned user
    user_id = test_users[0]["id"]
    response = requests.get(f"{API_URL}/tasks?assigned_to={user_id}")
    assert response.status_code == 200
    user_tasks = response.json()
    assert all(task["assigned_to"] == user_id for task in user_tasks)
    
    # Get tasks by project
    project_id = test_projects[0]["id"]
    response = requests.get(f"{API_URL}/tasks?project_id={project_id}")
    assert response.status_code == 200
    project_tasks = response.json()
    assert all(task["project_id"] == project_id for task in project_tasks)
    
    # Get specific task
    task_id = test_tasks[0]["id"]
    response = requests.get(f"{API_URL}/tasks/{task_id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == task_id
    
    # Update task status
    update_data = {
        "status": "in_progress"
    }
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == "in_progress"
    
    # Complete a task
    update_data = {
        "status": "completed",
        "quality_rating": 8
    }
    response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    completed_task = response.json()
    assert completed_task["status"] == "completed"
    assert completed_task["quality_rating"] == 8
    assert "completed_at" in completed_task
    
    # Test non-existent task
    response = requests.get(f"{API_URL}/tasks/{str(uuid.uuid4())}")
    assert response.status_code == 404
    
    logger.info("Task management and Eisenhower Matrix tests passed")

def test_analytics_endpoints():
    """Test analytics endpoints"""
    # Dashboard analytics
    response = requests.get(f"{API_URL}/analytics/dashboard")
    assert response.status_code == 200
    dashboard = response.json()
    assert "total_tasks" in dashboard
    assert "completed_tasks" in dashboard
    assert "overdue_tasks" in dashboard
    assert "in_progress_tasks" in dashboard
    assert "completion_rate" in dashboard
    assert "eisenhower_matrix" in dashboard
    
    # User performance
    user_id = test_users[0]["id"]
    response = requests.get(f"{API_URL}/analytics/performance/{user_id}")
    assert response.status_code == 200
    performance = response.json()
    assert performance["user_id"] == user_id
    assert "performance_score" in performance
    assert "tasks_assigned" in performance
    assert "tasks_completed" in performance
    assert "completion_rate" in performance
    
    # Team performance
    response = requests.get(f"{API_URL}/analytics/team-performance")
    assert response.status_code == 200
    team_performance = response.json()
    assert isinstance(team_performance, list)
    assert len(team_performance) >= len(test_users)
    for user_perf in team_performance:
        assert "user_id" in user_perf
        assert "performance_score" in user_perf
        assert "tasks_assigned" in user_perf
        assert "tasks_completed" in user_perf
    
    logger.info("Analytics endpoints tests passed")

def test_ai_coach_insights():
    """Test AI coach insights endpoint"""
    user_id = test_users[0]["id"]
    response = requests.get(f"{API_URL}/ai-coach/insights/{user_id}")
    assert response.status_code == 200
    insights = response.json()
    assert "insights" in insights
    assert "suggestions" in insights
    assert "performance_trend" in insights
    assert isinstance(insights["insights"], list)
    assert isinstance(insights["suggestions"], list)
    
    # Test non-existent user
    response = requests.get(f"{API_URL}/ai-coach/insights/{str(uuid.uuid4())}")
    assert response.status_code == 404
    
    logger.info("AI coach insights tests passed")

def test_task_deletion():
    """Test task deletion"""
    # Delete a task
    task_id = test_tasks[-1]["id"]
    response = requests.delete(f"{API_URL}/tasks/{task_id}")
    assert response.status_code == 200
    
    # Verify it's deleted
    response = requests.get(f"{API_URL}/tasks/{task_id}")
    assert response.status_code == 404
    
    # Remove from our test_tasks list
    test_tasks.pop()
    
    logger.info("Task deletion test passed")

def test_sample_data_population():
    """Test sample data population endpoint"""
    response = requests.post(f"{API_URL}/populate-sample-data")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "users_created" in data
    assert "projects_created" in data
    assert "tasks_created" in data
    assert data["users_created"] > 0
    assert data["projects_created"] > 0
    assert data["tasks_created"] > 0
    
    logger.info("Sample data population test passed")

def test_auth_endpoints():
    """Test authentication endpoints"""
    # Test signup
    signup_data = {
        "name": "Auth Test User",
        "email": "authtest@example.com",
        "password": "SecureAuthPassword!",
        "company": "Auth Test Company",
        "plan": "personal"
    }
    
    response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    assert response.status_code == 200, f"Failed to signup: {response.text}"
    signup_result = response.json()
    assert signup_result["success"] == True
    
    # Test login
    login_data = {
        "email": "authtest@example.com",
        "password": "SecureAuthPassword!"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    login_result = response.json()
    assert "access_token" in login_result
    assert "token_type" in login_result
    assert "user" in login_result
    assert login_result["token_type"] == "bearer"
    
    # Test auth/me endpoint with token
    token = login_result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{API_URL}/auth/me", headers=headers)
    assert response.status_code == 200, f"Failed to get current user: {response.text}"
    user_profile = response.json()
    assert user_profile["email"] == signup_data["email"]
    
    logger.info("Authentication endpoints tests passed")

if __name__ == "__main__":
    # Run all tests
    logger.info("Starting backend API tests...")
    
    try:
        test_health_check()
        test_user_management()
        test_project_management()
        test_task_management_and_eisenhower_matrix()
        test_analytics_endpoints()
        test_ai_coach_insights()
        test_task_deletion()
        test_sample_data_population()
        test_auth_endpoints()
        
        logger.info("All tests passed successfully!")
    except Exception as e:
        logger.error(f"Tests failed: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up test data...")
        for task in test_tasks:
            try:
                requests.delete(f"{API_URL}/tasks/{task['id']}")
                logger.info(f"Deleted task: {task['id']}")
            except Exception as e:
                logger.error(f"Error cleaning up task {task['id']}: {e}")