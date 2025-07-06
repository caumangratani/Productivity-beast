import requests
import json
import logging
import os
import uuid
from datetime import datetime, timedelta

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
test_tasks = []

def iso_format(dt):
    """Convert datetime to ISO format string"""
    if dt:
        return dt.isoformat()
    return None

def create_test_user():
    """Create a test user for verification"""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    user_data = {
        "name": f"Launch Verification User {timestamp}",
        "email": f"launch_verify_{timestamp}@example.com",
        "password": "SecureLaunchTest2025!",
        "company": "Launch Verification Company",
        "plan": "personal"
    }
    
    response = requests.post(f"{API_URL}/auth/signup", json=user_data)
    assert response.status_code == 200, f"Failed to create user: {response.text}"
    
    # Login to get token
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.text}"
    login_result = response.json()
    
    user = login_result["user"]
    user["token"] = login_result["access_token"]
    
    return user

def test_whatsapp_integration():
    """Test WhatsApp Integration (Port Fix Applied)"""
    logger.info("Testing WhatsApp Integration...")
    
    # 1. Test WhatsApp service connectivity on port 3002
    try:
        response = requests.get("http://localhost:3002/status")
        if response.status_code == 200:
            logger.info("✅ WhatsApp service is running on port 3002")
            whatsapp_status = response.json()
            logger.info(f"WhatsApp status: {whatsapp_status}")
        else:
            logger.warning(f"⚠️ WhatsApp service returned status code {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp service connectivity test failed: {str(e)}")
    
    # 2. Verify `/api/whatsapp/status` endpoint
    try:
        response = requests.get(f"{API_URL}/whatsapp/status")
        if response.status_code == 200:
            logger.info("✅ WhatsApp status endpoint is working")
            status_data = response.json()
            logger.info(f"WhatsApp API status: {status_data}")
        else:
            logger.warning(f"⚠️ WhatsApp status endpoint returned status code {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp status endpoint test failed: {str(e)}")
    
    # 3. Test WhatsApp message processing
    try:
        # Create a test user with phone number
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
        
        # Test message processing
        request_data = {
            "phone_number": user_data["phone_number"],
            "message": "create task: launch verification task",
            "message_id": str(uuid.uuid4()),
            "timestamp": int(datetime.utcnow().timestamp())
        }
        
        response = requests.post(f"{API_URL}/whatsapp/message", json=request_data)
        assert response.status_code == 200, f"Failed to process WhatsApp message: {response.text}"
        
        result = response.json()
        assert "reply" in result
        assert "success" in result
        assert result["success"] == True
        
        logger.info("✅ WhatsApp message processing is working")
    except Exception as e:
        logger.error(f"❌ WhatsApp message processing test failed: {str(e)}")
    
    # 4. Test team messaging
    try:
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
            "message": "Launch verification team message",
            "team_id": None  # Send to all team members
        }
        
        response = requests.post(f"{API_URL}/whatsapp/send-team-message", json=request_data)
        assert response.status_code == 200, f"Failed to send team message: {response.text}"
        
        result = response.json()
        assert "success" in result
        assert result["success"] == True
        
        logger.info("✅ Team messaging is working")
    except Exception as e:
        logger.error(f"❌ Team messaging test failed: {str(e)}")
    
    # 5. Test phone number updates
    try:
        # Create a test user
        user = create_test_user()
        user_id = user["id"]
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update phone number using PATCH method
        phone_number = f"+1777{datetime.utcnow().strftime('%Y%m%d%H%M%S')[-4:]}"
        phone_update_data = {
            "phone_number": phone_number
        }
        
        response = requests.patch(f"{API_URL}/users/{user_id}/phone", json=phone_update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update phone number: {response.text}"
        
        # Verify phone number was updated
        response = requests.get(f"{API_URL}/users/{user_id}", headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user["phone_number"] == phone_number
        
        logger.info("✅ Phone number updates are working correctly")
    except Exception as e:
        logger.error(f"❌ Phone number update test failed: {str(e)}")

def test_ai_coach_system():
    """Test AI Coach System"""
    logger.info("Testing AI Coach System...")
    
    try:
        # Create a test user
        user = create_test_user()
        user_id = user["id"]
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Test AI Coach chat
        chat_data = {
            "message": "How can I improve my productivity for the launch tomorrow?",
            "provider": "openai"  # Try with real OpenAI integration
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
        assert response.status_code == 200, f"Failed to get AI coach response: {response.text}"
        
        chat_result = response.json()
        assert "response" in chat_result
        assert "provider" in chat_result
        assert "timestamp" in chat_result
        assert len(chat_result["response"]) > 0
        
        logger.info(f"✅ AI Coach chat is working with provider: {chat_result['provider']}")
        
        # 2. Test AI settings endpoints
        response = requests.get(f"{API_URL}/integrations/ai-settings")
        assert response.status_code == 200, f"Failed to get AI settings: {response.text}"
        
        ai_settings = response.json()
        assert "openai_api_key" in ai_settings
        assert "preferred_ai_provider" in ai_settings
        assert "ai_enabled" in ai_settings
        
        logger.info(f"✅ AI settings retrieval is working. AI enabled: {ai_settings['ai_enabled']}")
        
        # 3. Test saving AI settings
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
        
        logger.info("✅ AI settings save functionality is working")
        
        # 4. Test AI coach insights
        response = requests.get(f"{API_URL}/ai-coach/insights/{user_id}")
        assert response.status_code == 200, f"Failed to get AI coach insights: {response.text}"
        
        insights = response.json()
        assert "insights" in insights
        assert "suggestions" in insights
        assert "performance_trend" in insights
        assert isinstance(insights["insights"], list)
        assert isinstance(insights["suggestions"], list)
        
        logger.info("✅ AI coach insights generation is working")
        
    except Exception as e:
        logger.error(f"❌ AI Coach system test failed: {str(e)}")

def test_google_integration():
    """Test Google Integration"""
    logger.info("Testing Google Integration...")
    
    try:
        # Create a test user
        user = create_test_user()
        user_id = user["id"]
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Test Google OAuth URL generation
        response = requests.get(f"{API_URL}/google/auth/url?user_id={user_id}")
        assert response.status_code == 200, f"Failed to get Google auth URL: {response.text}"
        
        auth_url_result = response.json()
        assert "auth_url" in auth_url_result
        assert "state" in auth_url_result
        assert "message" in auth_url_result
        assert user_id in auth_url_result["state"]
        
        logger.info("✅ Google OAuth URL generation is working")
        
        # 2. Test Google integration status
        response = requests.get(f"{API_URL}/google/integration/status/{user_id}")
        assert response.status_code == 200, f"Failed to get Google integration status: {response.text}"
        
        status_result = response.json()
        assert "connected" in status_result
        assert "message" in status_result
        assert "setup_required" in status_result
        
        logger.info(f"✅ Google integration status checking is working. Connected: {status_result['connected']}")
        
        # 3. Test calendar sync endpoint
        sync_data = {
            "user_id": user_id
        }
        
        response = requests.post(f"{API_URL}/google/calendar/sync-tasks", json=sync_data)
        
        # This will likely fail without real Google integration, but we're testing the endpoint
        if response.status_code == 200:
            logger.info("✅ Google Calendar sync endpoint is working")
        elif response.status_code == 404 and "Google integration not found" in response.text:
            logger.info("✅ Google Calendar sync endpoint correctly reports that Google integration is not set up")
        else:
            logger.warning(f"⚠️ Google Calendar sync endpoint returned unexpected status: {response.status_code}")
        
        # 4. Test auto-scheduler endpoint
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        schedule_data = {
            "user_id": user_id,
            "date": tomorrow
        }
        
        response = requests.post(f"{API_URL}/google/calendar/optimal-schedule", json=schedule_data)
        
        if response.status_code == 200:
            logger.info("✅ Google Auto-scheduler endpoint is working")
        elif response.status_code == 404 and "Google integration not found" in response.text:
            logger.info("✅ Google Auto-scheduler endpoint correctly reports that Google integration is not set up")
        else:
            logger.warning(f"⚠️ Google Auto-scheduler endpoint returned unexpected status: {response.status_code}")
        
    except Exception as e:
        logger.error(f"❌ Google Integration test failed: {str(e)}")

def test_task_management():
    """Test Task Management & Database"""
    logger.info("Testing Task Management & Database...")
    
    try:
        # Create a test user
        user = create_test_user()
        user_id = user["id"]
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 1. Test task creation
        tasks = []
        for i in range(3):
            task_data = {
                "title": f"Launch Verification Task {i}",
                "description": f"Description for launch verification task {i}",
                "assigned_to": user_id,
                "priority": ["low", "medium", "high"][i % 3],
                "due_date": iso_format(datetime.utcnow() + timedelta(days=i+1)),
                "tags": ["launch", "verification"]
            }
            
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            assert response.status_code == 200, f"Failed to create task: {response.text}"
            
            task = response.json()
            assert task["title"] == task_data["title"]
            assert task["description"] == task_data["description"]
            assert task["assigned_to"] == task_data["assigned_to"]
            assert task["priority"] == task_data["priority"]
            assert "id" in task
            assert "eisenhower_quadrant" in task
            
            tasks.append(task)
        
        logger.info(f"✅ Task creation is working. Created {len(tasks)} tasks")
        
        # 2. Test task updates
        task_id = tasks[0]["id"]
        update_data = {
            "title": "Updated Launch Task",
            "description": "Updated description for launch verification"
        }
        
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update task: {response.text}"
        
        updated_task = response.json()
        assert updated_task["title"] == update_data["title"]
        assert updated_task["description"] == update_data["description"]
        
        logger.info("✅ Task updates are working")
        
        # 3. Test drag-drop status changes
        status_update = {
            "status": "in_progress"
        }
        
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=status_update, headers=headers)
        assert response.status_code == 200, f"Failed to update task status: {response.text}"
        
        status_updated_task = response.json()
        assert status_updated_task["status"] == "in_progress"
        
        # Complete the task
        complete_update = {
            "status": "completed"
        }
        
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=complete_update, headers=headers)
        assert response.status_code == 200, f"Failed to complete task: {response.text}"
        
        completed_task = response.json()
        assert completed_task["status"] == "completed"
        assert "completed_at" in completed_task
        
        logger.info("✅ Task status changes (drag-drop simulation) are working")
        
        # 4. Test custom column functionality
        # Create a project with custom columns
        project_data = {
            "name": "Launch Verification Project",
            "description": "Project for testing custom columns",
            "owner_id": user_id,
            "team_members": [user_id],
            "custom_columns": ["Planning", "Development", "Testing", "Deployment"]
        }
        
        response = requests.post(f"{API_URL}/projects", json=project_data, headers=headers)
        assert response.status_code == 200, f"Failed to create project: {response.text}"
        
        project = response.json()
        assert "id" in project
        assert "custom_columns" in project
        assert len(project["custom_columns"]) == 4
        
        # Create a task in the project with custom column
        task_data = {
            "title": "Custom Column Task",
            "description": "Task for testing custom columns",
            "assigned_to": user_id,
            "project_id": project["id"],
            "priority": "high",
            "status": "Planning"  # Using custom column as status
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task with custom column: {response.text}"
        
        custom_task = response.json()
        assert custom_task["status"] == "Planning"
        
        # Move to another custom column
        column_update = {
            "status": "Development"
        }
        
        response = requests.put(f"{API_URL}/tasks/{custom_task['id']}", json=column_update, headers=headers)
        assert response.status_code == 200, f"Failed to update task custom column: {response.text}"
        
        updated_custom_task = response.json()
        assert updated_custom_task["status"] == "Development"
        
        logger.info("✅ Custom column functionality is working")
        
    except Exception as e:
        logger.error(f"❌ Task Management test failed: {str(e)}")

def test_performance_analytics():
    """Test Performance Analytics"""
    logger.info("Testing Performance Analytics...")
    
    try:
        # Create a test user
        user = create_test_user()
        user_id = user["id"]
        token = user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create and complete some tasks to generate analytics data
        for i in range(5):
            task_data = {
                "title": f"Analytics Test Task {i}",
                "description": f"Description for analytics test task {i}",
                "assigned_to": user_id,
                "priority": ["low", "medium", "high"][i % 3],
                "due_date": iso_format(datetime.utcnow() + timedelta(days=i+1)),
                "tags": ["analytics", "test"]
            }
            
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            assert response.status_code == 200, f"Failed to create task: {response.text}"
            
            task = response.json()
            
            # Complete some tasks
            if i % 2 == 0:
                complete_data = {
                    "status": "completed",
                    "quality_rating": 8
                }
                
                response = requests.put(f"{API_URL}/tasks/{task['id']}", json=complete_data, headers=headers)
                assert response.status_code == 200, f"Failed to complete task: {response.text}"
        
        # 1. Test performance score calculations
        response = requests.get(f"{API_URL}/analytics/performance/{user_id}")
        assert response.status_code == 200, f"Failed to get performance analytics: {response.text}"
        
        performance = response.json()
        assert performance["user_id"] == user_id
        assert "performance_score" in performance
        assert "tasks_assigned" in performance
        assert "tasks_completed" in performance
        assert "completion_rate" in performance
        
        # Verify performance score is not 0.0/10
        assert performance["performance_score"] > 0, "Performance score should not be 0.0/10"
        
        logger.info(f"✅ Performance score calculation is working. Score: {performance['performance_score']}/10")
        
        # 2. Test dashboard analytics
        response = requests.get(f"{API_URL}/analytics/dashboard")
        assert response.status_code == 200, f"Failed to get dashboard analytics: {response.text}"
        
        dashboard = response.json()
        assert "total_tasks" in dashboard
        assert "completed_tasks" in dashboard
        assert "overdue_tasks" in dashboard
        assert "in_progress_tasks" in dashboard
        assert "completion_rate" in dashboard
        assert "eisenhower_matrix" in dashboard
        
        logger.info("✅ Dashboard analytics display is working")
        
        # 3. Test team performance analytics
        response = requests.get(f"{API_URL}/analytics/team-performance")
        assert response.status_code == 200, f"Failed to get team performance analytics: {response.text}"
        
        team_performance = response.json()
        assert isinstance(team_performance, list)
        
        # Find our test user in the results
        user_found = False
        for user_perf in team_performance:
            if user_perf.get("user_id") == user_id:
                user_found = True
                assert user_perf["performance_score"] > 0, "User performance score should not be 0.0/10"
                break
        
        assert user_found, "Test user not found in team performance results"
        
        logger.info("✅ Team performance tracking is working")
        
    except Exception as e:
        logger.error(f"❌ Performance Analytics test failed: {str(e)}")

def test_authentication():
    """Test Authentication & Error Handling"""
    logger.info("Testing Authentication & Error Handling...")
    
    try:
        # 1. Test signup
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": "Auth Verification User",
            "email": f"authverify_{timestamp}@example.com",
            "password": "SecureAuthPassword!",
            "company": "Auth Verification Company",
            "plan": "personal"
        }
        
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        signup_result = response.json()
        assert signup_result["success"] == True
        
        logger.info("✅ Signup functionality is working")
        
        # 2. Test login
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
        
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        logger.info("✅ Login functionality is working")
        
        # 3. Test JWT token validation
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        assert response.status_code == 200, f"Failed to validate JWT token: {response.text}"
        user_profile = response.json()
        assert user_profile["email"] == signup_data["email"]
        
        logger.info("✅ JWT token validation is working")
        
        # 4. Test error handling with invalid token
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{API_URL}/auth/me", headers=invalid_headers)
        assert response.status_code == 401, f"Expected 401 for invalid token, got: {response.status_code}"
        
        logger.info("✅ Error handling for invalid tokens is working")
        
        # 5. Test error handling with invalid credentials
        invalid_login = {
            "email": signup_data["email"],
            "password": "WrongPassword!"
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=invalid_login)
        assert response.status_code == 401, f"Expected 401 for invalid credentials, got: {response.status_code}"
        
        logger.info("✅ Error handling for invalid credentials is working")
        
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {str(e)}")

def run_all_tests():
    """Run all verification tests"""
    logger.info("Starting launch verification testing...")
    
    # Test all critical systems
    test_whatsapp_integration()
    test_ai_coach_system()
    test_google_integration()
    test_task_management()
    test_performance_analytics()
    test_authentication()
    
    logger.info("Launch verification testing completed!")

if __name__ == "__main__":
    run_all_tests()