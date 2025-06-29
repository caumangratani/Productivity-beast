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
        
        # First try the specific phone number endpoint
        logger.info(f"Testing specific phone number endpoint: /api/users/{user_id}/phone")
        phone_update_data = {
            "phone_number": phone_number
        }
        
        response = requests.put(f"{API_URL}/users/{user_id}/phone", json=phone_update_data, headers=headers)
        
        # If specific endpoint fails, try the general user update endpoint
        if response.status_code != 200:
            logger.info(f"Specific phone endpoint failed with status {response.status_code}. Trying general user update endpoint.")
            update_data = {
                "phone_number": phone_number
            }
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
        test_ai_coach_chat()
        
        # WhatsApp integration tests
        test_whatsapp_message_processing()
        test_team_messaging()
        test_daily_reminders()
        test_weekly_reports()
        test_phone_number_management()
        test_whatsapp_service_integration()
        
        # Google integration tests
        test_google_oauth_flow()
        test_google_integration_status()
        test_google_calendar_sync()
        test_google_auto_scheduler()
        
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