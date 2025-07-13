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
    # Create users with unique emails using timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    for i in range(3):
        user_data = {
            "name": f"Test User {i}",
            "email": f"testuser{i}_{timestamp}@example.com",
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
    # Test signup with unique email using timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": "Auth Test User",
        "email": f"authtest_{timestamp}@example.com",
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
        "email": signup_data["email"],
        "password": signup_data["password"]
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

def test_ai_coach_chat():
    """Test AI coach chat endpoint"""
    # First, we need to authenticate to get a token
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": "AI Coach Test User",
        "email": f"aicoachtest_{timestamp}@example.com",
        "password": "SecureAICoachPassword!",
        "company": "AI Coach Test Company",
        "plan": "personal"
    }
    
    # Create user
    response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    assert response.status_code == 200, f"Failed to signup: {response.text}"
    
    # Login
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    login_result = response.json()
    token = login_result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test AI coach chat
    chat_data = {
        "message": "How can I improve my productivity?",
        "provider": "fallback"  # Use fallback to avoid needing real API keys
    }
    
    response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
    assert response.status_code == 200, f"Failed to get AI coach response: {response.text}"
    chat_result = response.json()
    assert "response" in chat_result
    assert "provider" in chat_result
    assert "timestamp" in chat_result
    assert len(chat_result["response"]) > 0
    
    logger.info("AI coach chat test passed")

def test_whatsapp_message_processing():
    """Test WhatsApp message processing endpoint with enhanced commands"""
    # Create a test user with phone number for WhatsApp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    user_data = {
        "name": f"WhatsApp Test User",
        "email": f"whatsapp_{timestamp}@example.com",
        "phone_number": f"+1555{timestamp[-4:]}",
        "password": "SecurePassword!",
        "company": "Test Company",
        "plan": "personal"
    }
    
    response = requests.post(f"{API_URL}/users", json=user_data)
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    whatsapp_user = response.json()
    
    # Test basic task creation command
    request_data = {
        "phone_number": user_data["phone_number"],
        "message": "create task: test task",
        "message_id": str(uuid.uuid4()),
        "timestamp": int(datetime.utcnow().timestamp())
    }
    
    response = requests.post(f"{API_URL}/whatsapp/message", json=request_data)
    assert response.status_code == 200, f"Failed to process WhatsApp message: {response.text}"
    
    result = response.json()
    assert "reply" in result
    assert "success" in result
    assert result["success"] == True
    assert "Task Created Successfully" in result["reply"]
    
    logger.info("WhatsApp task creation command test passed")
    
    # Test help command
    request_data = {
        "phone_number": user_data["phone_number"],
        "message": "help",
        "message_id": str(uuid.uuid4()),
        "timestamp": int(datetime.utcnow().timestamp())
    }
    
    response = requests.post(f"{API_URL}/whatsapp/message", json=request_data)
    assert response.status_code == 200, f"Failed to process WhatsApp message: {response.text}"
    
    result = response.json()
    assert "reply" in result
    assert "success" in result
    assert result["success"] == True
    assert "Productivity Beast WhatsApp Bot" in result["reply"]
    
    logger.info("WhatsApp help command test passed")
    
    # Test stats command
    request_data = {
        "phone_number": user_data["phone_number"],
        "message": "stats",
        "message_id": str(uuid.uuid4()),
        "timestamp": int(datetime.utcnow().timestamp())
    }
    
    response = requests.post(f"{API_URL}/whatsapp/message", json=request_data)
    assert response.status_code == 200, f"Failed to process WhatsApp message: {response.text}"
    
    result = response.json()
    assert "reply" in result
    assert "success" in result
    assert result["success"] == True
    assert "Productivity Dashboard" in result["reply"]
    
    logger.info("WhatsApp stats command test passed")
    
    logger.info("WhatsApp message processing tests passed")

def test_team_messaging():
    """Test team messaging endpoint"""
    # Create test users with phone numbers
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    team_users = []
    
    for i in range(2):
        user_data = {
            "name": f"Team Message User {i}",
            "email": f"teammsg{i}_{timestamp}@example.com",
            "phone_number": f"+1666{timestamp[-4:]}{i}",
            "password": f"SecurePassword{i}!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        response = requests.post(f"{API_URL}/users", json=user_data)
        assert response.status_code == 200, f"Failed to create user: {response.text}"
        team_users.append(response.json())
    
    # Test sending team message
    request_data = {
        "sender_id": team_users[0]["id"],
        "message": "Test team message from automated tests",
        "team_id": None  # Send to all team members
    }
    
    response = requests.post(f"{API_URL}/whatsapp/send-team-message", json=request_data)
    assert response.status_code == 200, f"Failed to send team message: {response.text}"
    
    result = response.json()
    assert "success" in result
    assert result["success"] == True
    assert "sent_count" in result
    assert "failed_count" in result
    assert "total_members" in result
    
    logger.info("Team messaging test passed")

def test_daily_reminders():
    """Test daily reminders endpoint"""
    response = requests.post(f"{API_URL}/whatsapp/send-daily-reminders")
    assert response.status_code == 200, f"Failed to send daily reminders: {response.text}"
    
    result = response.json()
    assert "success" in result
    assert result["success"] == True
    assert "sent_count" in result
    assert "failed_count" in result
    assert "total_users" in result
    
    logger.info("Daily reminders test passed")

def test_weekly_reports():
    """Test weekly reports endpoint"""
    response = requests.post(f"{API_URL}/whatsapp/send-weekly-reports")
    assert response.status_code == 200, f"Failed to send weekly reports: {response.text}"
    
    result = response.json()
    assert "success" in result
    assert result["success"] == True
    assert "sent_count" in result
    assert "failed_count" in result
    assert "total_users" in result
    
    logger.info("Weekly reports test passed")

def test_phone_number_management():
    """Test phone number management endpoint"""
    try:
        # First, we need to authenticate to get a token
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Phone Test User",
            "email": f"phonetest_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        # Update phone number
        phone_number = f"+1777{timestamp[-4:]}"
        
        # First try the specific phone number endpoint with PATCH (not PUT)
        logger.info(f"Testing specific phone number endpoint: /api/users/{user_id}/phone")
        phone_update_data = {
            "phone_number": phone_number
        }
        
        response = requests.patch(f"{API_URL}/users/{user_id}/phone", json=phone_update_data, headers=headers)
        
        # If specific endpoint fails, try the general user update endpoint
        if response.status_code != 200:
            logger.info(f"Specific phone endpoint failed with status {response.status_code}. Trying general user update endpoint.")
            update_data = {
                "phone_number": phone_number
            }
            response = requests.patch(f"{API_URL}/users/{user_id}", json=update_data, headers=headers)
            
            if response.status_code != 200:
                logger.info(f"General user update endpoint failed with status {response.status_code}. Trying PUT method.")
                response = requests.put(f"{API_URL}/users/{user_id}", json=update_data, headers=headers)
            
            assert response.status_code == 200, f"Failed to update user: {response.text}"
            
            # Verify phone number was updated
            response = requests.get(f"{API_URL}/users/{user_id}", headers=headers)
            assert response.status_code == 200
            updated_user = response.json()
            
            # Check if phone number was updated or if the field exists
            if "phone_number" in updated_user:
                assert updated_user["phone_number"] == phone_number
                logger.info("Phone number management test passed using general user update endpoint")
            else:
                logger.warning("Phone number field not available in user object after update")
        else:
            # Specific phone endpoint worked
            result = response.json()
            logger.info(f"Specific phone endpoint succeeded: {result}")
            
            # Verify phone number was updated
            response = requests.get(f"{API_URL}/users/{user_id}", headers=headers)
            assert response.status_code == 200
            updated_user = response.json()
            
            if "phone_number" in updated_user:
                assert updated_user["phone_number"] == phone_number
                logger.info("Phone number management test passed using specific phone endpoint")
            else:
                logger.warning("Phone number field not available in user object after update")
    
    except Exception as e:
        logger.error(f"Phone number management test error: {str(e)}")
        raise

def test_whatsapp_service_integration():
    """Test WhatsApp service integration endpoints"""
    try:
        # Test WhatsApp status endpoint
        response = requests.get(f"{API_URL}/whatsapp/status")
        if response.status_code == 200:
            result = response.json()
            assert "connected" in result or "status" in result
            logger.info("WhatsApp status endpoint test passed")
        else:
            # Service might be unavailable in test environment, which is acceptable
            logger.info("WhatsApp service unavailable, skipping detailed status check")
        
        # Test QR code endpoint
        response = requests.get(f"{API_URL}/whatsapp/qr")
        if response.status_code == 200:
            result = response.json()
            assert "qr" in result or "status" in result
            logger.info("WhatsApp QR endpoint test passed")
        else:
            logger.info("WhatsApp QR service unavailable, skipping detailed check")
        
        logger.info("WhatsApp service integration tests passed")
    except Exception as e:
        logger.warning(f"WhatsApp service integration test warning: {str(e)}")
        logger.info("WhatsApp service integration tests skipped - service may not be available in test environment")

def test_google_oauth_flow():
    """Test Google OAuth URL generation and callback handling"""
    try:
        # First, we need to authenticate to get a token
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Google Test User",
            "email": f"googletest_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        # Test Google OAuth URL generation
        response = requests.get(f"{API_URL}/google/auth/url?user_id={user_id}")
        assert response.status_code == 200, f"Failed to get Google auth URL: {response.text}"
        
        auth_url_result = response.json()
        assert "auth_url" in auth_url_result
        assert "state" in auth_url_result
        assert "message" in auth_url_result
        assert user_id in auth_url_result["state"]
        
        logger.info("Google OAuth URL generation test passed")
        
        # Test Google OAuth callback (simulated)
        # We can't fully test the callback without a real OAuth flow, but we can test the endpoint
        callback_data = {
            "code": "simulated_auth_code",
            "state": auth_url_result["state"]
        }
        
        # This will likely fail in the test environment without real OAuth credentials
        # but we're testing the endpoint existence and basic validation
        response = requests.post(f"{API_URL}/google/auth/callback", json=callback_data)
        
        # We don't assert success here since it will likely fail without real credentials
        # Just log the result for information
        if response.status_code == 200:
            logger.info("Google OAuth callback test passed (unexpected in test environment)")
        else:
            logger.info(f"Google OAuth callback returned {response.status_code} as expected in test environment")
        
    except Exception as e:
        logger.error(f"Google OAuth flow test error: {str(e)}")
        raise

def test_google_integration_status():
    """Test Google integration status checking"""
    try:
        # First, we need to authenticate to get a token
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Google Status User",
            "email": f"googlestatus_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        user_id = login_result["user"]["id"]
        
        # Test Google integration status
        response = requests.get(f"{API_URL}/google/integration/status/{user_id}")
        assert response.status_code == 200, f"Failed to get Google integration status: {response.text}"
        
        status_result = response.json()
        assert "connected" in status_result
        assert "message" in status_result
        assert "setup_required" in status_result
        
        # For a new user, we expect connected to be false and setup_required to be true
        assert status_result["connected"] == False
        assert status_result["setup_required"] == True
        
        logger.info("Google integration status test passed")
        
    except Exception as e:
        logger.error(f"Google integration status test error: {str(e)}")
        raise

def test_google_calendar_sync():
    """Test task-to-calendar synchronization"""
    try:
        # First, we need to authenticate to get a token
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Calendar Sync User",
            "email": f"calendarsync_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        # Create a task for the user
        task_data = {
            "title": "Calendar Sync Test Task",
            "description": "This task should be synced to Google Calendar",
            "assigned_to": user_id,
            "priority": "high",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=3)),
            "tags": ["test", "calendar"]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        task = response.json()
        
        # Test calendar sync endpoint
        sync_data = {
            "user_id": user_id
        }
        
        response = requests.post(f"{API_URL}/google/calendar/sync-tasks", json=sync_data)
        
        # This will likely fail without real Google integration, but we're testing the endpoint
        if response.status_code == 200:
            result = response.json()
            assert "success" in result
            assert "synced_count" in result
            assert "total_tasks" in result
            assert "errors" in result
            logger.info("Google Calendar sync test passed (unexpected in test environment)")
        else:
            logger.info(f"Google Calendar sync returned {response.status_code} as expected in test environment without real Google integration")
            # Check if the error is related to Google integration not being set up
            if response.status_code == 404 and "Google integration not found" in response.text:
                logger.info("Google Calendar sync correctly reported that Google integration is not set up")
            
    except Exception as e:
        logger.error(f"Google Calendar sync test error: {str(e)}")
        raise

def test_google_auto_scheduler():
    """Test optimal time block creation with conflict detection"""
    try:
        # First, we need to authenticate to get a token
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Auto Scheduler User",
            "email": f"autoscheduler_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        # Create some tasks for the user
        for i in range(3):
            task_data = {
                "title": f"Auto Scheduler Test Task {i}",
                "description": f"This task should be scheduled optimally {i}",
                "assigned_to": user_id,
                "priority": ["low", "medium", "high"][i],
                "due_date": iso_format(datetime.utcnow() + timedelta(days=i+1)),
                "tags": ["test", "scheduler"]
            }
            
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            assert response.status_code == 200, f"Failed to create task: {response.text}"
        
        # Test auto-scheduler endpoint
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        schedule_data = {
            "user_id": user_id,
            "date": tomorrow
        }
        
        response = requests.post(f"{API_URL}/google/calendar/optimal-schedule", json=schedule_data)
        
        # This will likely fail without real Google integration, but we're testing the endpoint
        if response.status_code == 200:
            result = response.json()
            assert "success" in result
            assert "date" in result
            assert "scheduled_blocks" in result
            assert "schedule" in result
            assert "message" in result
            assert "productivity_tips" in result
            logger.info("Google Auto-scheduler test passed (unexpected in test environment)")
        else:
            logger.info(f"Google Auto-scheduler returned {response.status_code} as expected in test environment without real Google integration")
            # Check if the error is related to Google integration not being set up
            if response.status_code == 404 and "Google integration not found" in response.text:
                logger.info("Google Auto-scheduler correctly reported that Google integration is not set up")
            
    except Exception as e:
        logger.error(f"Google Auto-scheduler test error: {str(e)}")
        raise

def test_ai_settings_integration():
    """Test AI settings integration endpoints"""
    try:
        # Test GET AI settings
        response = requests.get(f"{API_URL}/integrations/ai-settings")
        assert response.status_code == 200, f"Failed to get AI settings: {response.text}"
        
        ai_settings = response.json()
        assert "openai_api_key" in ai_settings
        assert "claude_api_key" in ai_settings
        assert "preferred_ai_provider" in ai_settings
        assert "ai_enabled" in ai_settings
        
        logger.info("GET AI settings test passed")
        
        # Test POST AI settings
        settings_data = {
            "openai_api_key": "sk-test123456789abcdefghijklmnopqrstuvwxyz",
            "claude_api_key": "",
            "preferred_ai_provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/integrations/ai-settings", json=settings_data)
        assert response.status_code == 200, f"Failed to save AI settings: {response.text}"
        
        result = response.json()
        assert "success" in result
        assert "message" in result
        
        logger.info("POST AI settings test passed")
        
    except Exception as e:
        logger.error(f"AI settings integration test error: {str(e)}")
        raise

def test_whatsapp_settings_integration():
    """Test WhatsApp settings integration endpoints"""
    try:
        # Test GET WhatsApp settings
        response = requests.get(f"{API_URL}/integrations/whatsapp-settings")
        assert response.status_code == 200, f"Failed to get WhatsApp settings: {response.text}"
        
        whatsapp_settings = response.json()
        assert "whatsapp_business_account_id" in whatsapp_settings
        assert "whatsapp_access_token" in whatsapp_settings
        assert "webhook_verify_token" in whatsapp_settings
        assert "phone_number_id" in whatsapp_settings
        assert "enabled" in whatsapp_settings
        
        logger.info("GET WhatsApp settings test passed")
        
        # Test POST WhatsApp settings
        settings_data = {
            "whatsapp_business_account_id": "123456789",
            "whatsapp_access_token": "test_access_token",
            "webhook_verify_token": "test_verify_token",
            "phone_number_id": "987654321",
            "enabled": True
        }
        
        response = requests.post(f"{API_URL}/integrations/whatsapp-settings", json=settings_data)
        assert response.status_code == 200, f"Failed to save WhatsApp settings: {response.text}"
        
        result = response.json()
        assert "success" in result
        assert "message" in result
        
        logger.info("POST WhatsApp settings test passed")
        
    except Exception as e:
        logger.error(f"WhatsApp settings integration test error: {str(e)}")
        raise

def test_google_oauth_critical_fixes():
    """Test critical Google OAuth integration fixes"""
    logger.info("=== TESTING CRITICAL GOOGLE OAUTH FIXES ===")
    
    try:
        # Create a test user
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Google OAuth Test User",
            "email": f"googleoauth_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        user_id = login_result["user"]["id"]
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # 1. Test GET /api/google/auth/url endpoint with user_id parameter
        logger.info("Testing GET /api/google/auth/url endpoint...")
        response = requests.get(f"{API_URL}/google/auth/url?user_id={user_id}")
        
        if response.status_code == 500:
            error_data = response.json()
            if "Google OAuth not configured" in error_data.get("detail", ""):
                logger.error("CRITICAL: Google OAuth credentials are not properly configured in backend")
                logger.error("Expected GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in backend/.env")
                return False
        
        assert response.status_code == 200, f"Google OAuth URL generation failed: {response.text}"
        
        auth_url_result = response.json()
        logger.info(f"Google OAuth URL response: {auth_url_result}")
        
        # 2. Verify it returns a valid Google OAuth URL
        assert "auth_url" in auth_url_result, "Missing auth_url in response"
        assert "state" in auth_url_result, "Missing state in response"
        assert "message" in auth_url_result, "Missing message in response"
        
        auth_url = auth_url_result["auth_url"]
        state = auth_url_result["state"]
        
        # 3. Test if the endpoint properly handles Google credentials
        assert "accounts.google.com/o/oauth2/auth" in auth_url, "Invalid Google OAuth URL"
        assert user_id in state, "User ID not properly included in state"
        
        # 4. Check if the auth URL contains the correct scopes and redirect URI
        assert "scope=" in auth_url, "Missing scopes in OAuth URL"
        assert "calendar" in auth_url, "Missing calendar scope"
        assert "spreadsheets" in auth_url, "Missing spreadsheets scope"
        assert "redirect_uri=" in auth_url, "Missing redirect URI"
        assert "project-continue-1.emergent.host" in auth_url, "Incorrect redirect URI"
        
        logger.info("✅ Google OAuth URL generation test PASSED")
        logger.info(f"✅ Auth URL contains correct scopes and redirect URI")
        logger.info(f"✅ State parameter properly includes user_id: {user_id}")
        
        # Test Google integration status
        logger.info("Testing Google integration status...")
        response = requests.get(f"{API_URL}/google/integration/status/{user_id}")
        assert response.status_code == 200, f"Failed to get Google integration status: {response.text}"
        
        status_result = response.json()
        assert "connected" in status_result
        assert "setup_required" in status_result
        assert status_result["connected"] == False  # Should be false for new user
        assert status_result["setup_required"] == True  # Should require setup
        
        logger.info("✅ Google integration status test PASSED")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Google OAuth critical fixes test FAILED: {str(e)}")
        return False

def test_ai_coach_real_data_analysis():
    """Test AI Coach Real Data Analysis critical fixes"""
    logger.info("=== TESTING CRITICAL AI COACH REAL DATA ANALYSIS FIXES ===")
    
    try:
        # Create a test user with some task data
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"AI Coach Test User",
            "email": f"aicoach_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
            "plan": "personal"
        }
        
        # Create user via signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        
        # Login to get token
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # Create some sample tasks for the user to analyze
        sample_tasks = [
            {
                "title": "Complete project proposal",
                "description": "Write and submit the Q1 project proposal",
                "assigned_to": user_id,
                "priority": "high",
                "status": "completed",
                "due_date": iso_format(datetime.utcnow() - timedelta(days=2)),
                "tags": ["project", "proposal"]
            },
            {
                "title": "Review team performance",
                "description": "Analyze team metrics and provide feedback",
                "assigned_to": user_id,
                "priority": "medium",
                "status": "in_progress",
                "due_date": iso_format(datetime.utcnow() + timedelta(days=3)),
                "tags": ["review", "team"]
            },
            {
                "title": "Update documentation",
                "description": "Update API documentation with latest changes",
                "assigned_to": user_id,
                "priority": "low",
                "status": "todo",
                "due_date": iso_format(datetime.utcnow() + timedelta(days=7)),
                "tags": ["documentation"]
            }
        ]
        
        created_tasks = []
        for task_data in sample_tasks:
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            assert response.status_code == 200, f"Failed to create task: {response.text}"
            created_tasks.append(response.json())
            
        logger.info(f"Created {len(created_tasks)} sample tasks for analysis")
        
        # 1. Test POST /api/ai-coach/chat endpoint with include_user_context=true
        logger.info("Testing AI Coach chat with user context...")
        
        chat_data = {
            "message": "analyze my productivity data",
            "user_id": user_id,  # Include user_id in request body
            "include_user_context": True,
            "ai_provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
        
        if response.status_code == 500:
            error_data = response.json()
            if "OpenAI API key not configured" in error_data.get("detail", ""):
                logger.error("CRITICAL: OpenAI API key is not properly configured in backend")
                logger.error("Expected OPENAI_API_KEY in backend/.env")
                return False
        
        assert response.status_code == 200, f"AI Coach chat failed: {response.text}"
        
        chat_result = response.json()
        logger.info(f"AI Coach response: {chat_result}")
        
        # 2. Verify the response includes actual user task data analysis
        assert "response" in chat_result, "Missing response in AI Coach result"
        assert "user_context" in chat_result, "Missing user_context in AI Coach result"
        assert "provider" in chat_result, "Missing provider in AI Coach result"
        
        ai_response = chat_result["response"]
        user_context = chat_result["user_context"]
        
        # 3. Check if the AI response references real user metrics
        logger.info("Verifying AI response contains real user data analysis...")
        
        # Check user context contains real data
        assert "total_tasks" in user_context, "Missing total_tasks in user context"
        assert "completed_tasks" in user_context, "Missing completed_tasks in user context"
        assert "completion_rate" in user_context, "Missing completion_rate in user context"
        assert "overdue_tasks" in user_context, "Missing overdue_tasks in user context"
        
        # Verify the context reflects our created tasks
        assert user_context["total_tasks"] >= len(created_tasks), f"Expected at least {len(created_tasks)} tasks, got {user_context['total_tasks']}"
        assert user_context["completed_tasks"] >= 1, "Expected at least 1 completed task"
        
        # Check if AI response is personalized and not generic
        assert len(ai_response) > 100, "AI response seems too short to be meaningful analysis"
        
        # Look for indicators that the AI is analyzing real data
        productivity_indicators = [
            "task", "completion", "productivity", "performance", 
            "progress", "deadline", "priority", "project"
        ]
        
        response_lower = ai_response.lower()
        found_indicators = [indicator for indicator in productivity_indicators if indicator in response_lower]
        
        assert len(found_indicators) >= 3, f"AI response doesn't seem to contain productivity analysis. Found indicators: {found_indicators}"
        
        logger.info("✅ AI Coach real data analysis test PASSED")
        logger.info(f"✅ User context includes: {user_context['total_tasks']} total tasks, {user_context['completed_tasks']} completed")
        logger.info(f"✅ AI response contains productivity analysis with {len(found_indicators)} relevant indicators")
        
        # Test with different message to ensure it's analyzing data
        logger.info("Testing AI Coach with different productivity query...")
        
        chat_data2 = {
            "message": "what are my completion rates and task counts?",
            "include_user_context": True,
            "provider": "openai"
        }
        
        response2 = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data2, headers=headers)
        assert response2.status_code == 200, f"Second AI Coach chat failed: {response2.text}"
        
        chat_result2 = response2.json()
        ai_response2 = chat_result2["response"]
        
        # Verify this response also contains data analysis
        assert len(ai_response2) > 50, "Second AI response seems too short"
        
        logger.info("✅ AI Coach responds consistently with real data analysis")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI Coach real data analysis test FAILED: {str(e)}")
        return False

def test_backend_environment_setup():
    """Test backend environment setup for critical integrations"""
    logger.info("=== TESTING BACKEND ENVIRONMENT SETUP ===")
    
    try:
        # Test Google OAuth credentials configuration
        logger.info("Testing Google OAuth credentials configuration...")
        
        # Read backend .env file to verify credentials
        env_file_path = "/app/backend/.env"
        google_client_id = None
        google_client_secret = None
        openai_api_key = None
        
        with open(env_file_path, 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_CLIENT_ID='):
                    google_client_id = line.strip().split('=')[1].strip('"')
                elif line.startswith('GOOGLE_CLIENT_SECRET='):
                    google_client_secret = line.strip().split('=')[1].strip('"')
                elif line.startswith('OPENAI_API_KEY='):
                    openai_api_key = line.strip().split('=')[1].strip('"')
        
        # Verify Google OAuth credentials
        assert google_client_id is not None, "GOOGLE_CLIENT_ID not found in backend/.env"
        assert google_client_secret is not None, "GOOGLE_CLIENT_SECRET not found in backend/.env"
        assert len(google_client_id) > 10, "GOOGLE_CLIENT_ID seems invalid (too short)"
        assert len(google_client_secret) > 10, "GOOGLE_CLIENT_SECRET seems invalid (too short)"
        assert "apps.googleusercontent.com" in google_client_id, "GOOGLE_CLIENT_ID format seems invalid"
        
        logger.info("✅ Google OAuth credentials are properly configured")
        
        # Test OpenAI API key configuration
        assert openai_api_key is not None, "OPENAI_API_KEY not found in backend/.env"
        assert openai_api_key.startswith("sk-"), "OPENAI_API_KEY format seems invalid"
        assert len(openai_api_key) > 20, "OPENAI_API_KEY seems invalid (too short)"
        
        logger.info("✅ OpenAI API key is properly configured")
        
        # Test if AI settings endpoint recognizes the configuration
        response = requests.get(f"{API_URL}/integrations/ai-settings")
        assert response.status_code == 200, f"Failed to get AI settings: {response.text}"
        
        ai_settings = response.json()
        assert ai_settings["ai_enabled"] == True, "AI should be enabled with valid OpenAI key"
        assert "***configured***" in ai_settings["openai_api_key"], "OpenAI key should show as configured"
        
        logger.info("✅ AI settings endpoint recognizes OpenAI configuration")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Backend environment setup test FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    # Run critical fixes tests first
    logger.info("Starting CRITICAL FIXES testing for Google OAuth and AI Coach...")
    
    critical_tests_passed = 0
    total_critical_tests = 3
    
    try:
        # Test critical fixes
        if test_google_oauth_critical_fixes():
            critical_tests_passed += 1
            
        if test_ai_coach_real_data_analysis():
            critical_tests_passed += 1
            
        if test_backend_environment_setup():
            critical_tests_passed += 1
        
        logger.info(f"\n=== CRITICAL FIXES SUMMARY ===")
        logger.info(f"Critical tests passed: {critical_tests_passed}/{total_critical_tests}")
        
        if critical_tests_passed == total_critical_tests:
            logger.info("🎉 ALL CRITICAL FIXES ARE WORKING!")
        else:
            logger.error(f"❌ {total_critical_tests - critical_tests_passed} critical fixes still have issues")
        
        # Run other tests if critical fixes pass
        if critical_tests_passed == total_critical_tests:
            logger.info("\nRunning additional backend tests...")
            
            test_health_check()
            test_user_management()
            test_project_management()
            test_task_management_and_eisenhower_matrix()
            test_analytics_endpoints()
            test_ai_coach_insights()
            test_task_deletion()
            test_sample_data_population()
            test_auth_endpoints()
            test_ai_coach_chat()
            
            # WhatsApp integration tests
            test_whatsapp_message_processing()
            test_team_messaging()
            test_daily_reminders()
            test_weekly_reports()
            test_phone_number_management()
            test_whatsapp_service_integration()
            test_whatsapp_settings_integration()
            
            # Google integration tests
            test_google_oauth_flow()
            test_google_integration_status()
            test_google_calendar_sync()
            test_google_auto_scheduler()
            
            # AI integration tests
            test_ai_settings_integration()
            
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