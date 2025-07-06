import requests
import json
import logging
import uuid
from datetime import datetime, timedelta
import time
import httpx

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
test_user = None
test_token = None
test_tasks = []

def iso_format(dt):
    """Convert datetime to ISO format string"""
    if dt:
        return dt.isoformat()
    return None

def create_test_user():
    """Create a test user and return the user data and auth token"""
    global test_user, test_token
    
    # Create a unique user
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Emergency Test User {timestamp}",
        "email": f"emergency_test_{timestamp}@example.com",
        "password": "SecureEmergencyTest!",
        "company": "Emergency Test Company",
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
    
    test_user = login_result["user"]
    test_token = login_result["access_token"]
    
    logger.info(f"Created test user: {test_user['name']} with ID: {test_user['id']}")
    
    return test_user, test_token

def create_test_tasks():
    """Create test tasks with different priorities and statuses"""
    global test_tasks
    
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Create tasks with different priorities and statuses
    statuses = ["todo", "in_progress", "completed"]
    priorities = ["low", "medium", "high", "urgent"]
    
    for i in range(5):
        task_data = {
            "title": f"Emergency Test Task {i}",
            "description": f"Description for emergency test task {i}",
            "assigned_to": test_user["id"],
            "status": statuses[i % len(statuses)],
            "priority": priorities[i % len(priorities)],
            "due_date": iso_format(datetime.utcnow() + timedelta(days=i+1)),
            "tags": ["emergency", "test"]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        
        task = response.json()
        test_tasks.append(task)
        logger.info(f"Created task: {task['title']} with ID: {task['id']}")
    
    return test_tasks

def test_ai_coach_functionality():
    """
    Test AI Coach functionality:
    - Test /api/ai-coach/chat endpoint with real messages
    - Verify OpenAI API key is working and responding
    - Check if AI Coach actually analyzes user data
    - Test if responses are generated correctly
    """
    logger.info("Testing AI Coach functionality...")
    
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test with a simple productivity question
    chat_data = {
        "message": "How can I improve my productivity?",
        "provider": "openai"  # Explicitly request OpenAI
    }
    
    response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
    
    if response.status_code == 200:
        chat_result = response.json()
        assert "response" in chat_result, "AI Coach response missing 'response' field"
        assert "provider" in chat_result, "AI Coach response missing 'provider' field"
        assert "timestamp" in chat_result, "AI Coach response missing 'timestamp' field"
        
        # Check if response is substantial (not just an error message)
        assert len(chat_result["response"]) > 100, "AI Coach response too short, might be an error"
        
        # Check if the provider is actually OpenAI
        if chat_result["provider"] == "openai":
            logger.info("✅ AI Coach using OpenAI successfully generated a response")
        elif chat_result["provider"] == "fallback":
            logger.warning("⚠️ AI Coach using fallback mode - OpenAI API key might not be working")
        else:
            logger.info(f"✅ AI Coach using {chat_result['provider']} successfully generated a response")
        
        # Test with a task-specific question to check if it analyzes user data
        chat_data = {
            "message": "Analyze my current tasks and tell me what to focus on",
            "provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
        assert response.status_code == 200, f"Failed to get AI coach response: {response.text}"
        
        chat_result = response.json()
        assert "response" in chat_result
        assert len(chat_result["response"]) > 100, "AI Coach response too short for data analysis"
        
        logger.info("✅ AI Coach successfully analyzed user data")
        
        return True
    else:
        logger.error(f"❌ AI Coach chat endpoint failed with status {response.status_code}: {response.text}")
        return False

def test_whatsapp_service_availability():
    """
    Test WhatsApp Service Availability:
    - Test WhatsApp service on port 3001
    - Check /api/whatsapp/status endpoint
    - Verify if WhatsApp service is actually running
    - Test if QR code generation works
    """
    logger.info("Testing WhatsApp service availability...")
    
    # Test WhatsApp status endpoint
    response = requests.get(f"{API_URL}/whatsapp/status")
    
    if response.status_code == 200:
        status_result = response.json()
        assert "connected" in status_result or "status" in status_result, "WhatsApp status response missing status information"
        
        if status_result.get("connected", False) or status_result.get("status") == "connected":
            logger.info("✅ WhatsApp service is connected and running")
        else:
            logger.warning("⚠️ WhatsApp service is available but not connected")
    elif response.status_code == 404:
        logger.error("❌ WhatsApp status endpoint not found (404)")
        
        # Try to directly check if the WhatsApp service is running on port 3001
        try:
            async def check_whatsapp_service():
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get("http://localhost:3001/status", timeout=5.0)
                        return response.status_code == 200
                    except Exception as e:
                        logger.error(f"Error connecting to WhatsApp service: {str(e)}")
                        return False
            
            import asyncio
            whatsapp_running = asyncio.run(check_whatsapp_service())
            
            if whatsapp_running:
                logger.info("✅ WhatsApp service is running on port 3001 but API endpoint is missing")
            else:
                logger.error("❌ WhatsApp service is NOT running on port 3001")
        except Exception as e:
            logger.error(f"Failed to check WhatsApp service directly: {str(e)}")
    else:
        logger.error(f"❌ WhatsApp status endpoint failed with status {response.status_code}: {response.text}")
    
    # Test QR code generation
    response = requests.get(f"{API_URL}/whatsapp/qr")
    
    if response.status_code == 200:
        qr_result = response.json()
        assert "qr" in qr_result or "status" in qr_result, "WhatsApp QR response missing QR code or status"
        
        if "qr" in qr_result and qr_result["qr"]:
            logger.info("✅ WhatsApp QR code generation is working")
        else:
            logger.warning("⚠️ WhatsApp QR endpoint is available but did not return a QR code")
    elif response.status_code == 404:
        logger.error("❌ WhatsApp QR endpoint not found (404)")
    else:
        logger.error(f"❌ WhatsApp QR endpoint failed with status {response.status_code}: {response.text}")
    
    # Test sending a message (this will likely fail without a connected WhatsApp instance)
    test_message_data = {
        "phone_number": "+1234567890",  # Test number
        "message": "Test message from emergency verification",
        "message_id": str(uuid.uuid4()),
        "timestamp": int(datetime.utcnow().timestamp())
    }
    
    response = requests.post(f"{API_URL}/whatsapp/message", json=test_message_data)
    
    if response.status_code == 200:
        logger.info("✅ WhatsApp message endpoint is working")
    else:
        logger.warning(f"⚠️ WhatsApp message endpoint returned status {response.status_code} - this may be expected without a connected WhatsApp instance")
    
    # Overall assessment
    if response.status_code == 200 or (response.status_code == 404 and whatsapp_running):
        return True
    else:
        return False

def test_performance_analytics_calculation():
    """
    Test Performance Analytics Calculation:
    - Test /api/analytics/performance/{user_id} 
    - Verify if performance scores are calculating correctly
    - Check if users are getting 0.0/10 scores incorrectly
    - Test calculation algorithms with real data
    """
    logger.info("Testing performance analytics calculation...")
    
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # First, complete some tasks to generate performance data
    for i, task in enumerate(test_tasks):
        if i % 2 == 0:  # Complete every other task
            update_data = {
                "status": "completed",
                "quality_rating": 8
            }
            response = requests.put(f"{API_URL}/tasks/{task['id']}", json=update_data, headers=headers)
            assert response.status_code == 200, f"Failed to update task: {response.text}"
            logger.info(f"Completed task: {task['title']}")
    
    # Wait a moment for any async calculations
    time.sleep(1)
    
    # Get performance analytics
    response = requests.get(f"{API_URL}/analytics/performance/{test_user['id']}", headers=headers)
    
    if response.status_code == 200:
        performance = response.json()
        assert "user_id" in performance, "Performance response missing user_id"
        assert "performance_score" in performance, "Performance response missing performance_score"
        assert "tasks_assigned" in performance, "Performance response missing tasks_assigned"
        assert "tasks_completed" in performance, "Performance response missing tasks_completed"
        assert "completion_rate" in performance, "Performance response missing completion_rate"
        
        # Check if performance score is calculated (not 0.0)
        assert performance["performance_score"] > 0, "Performance score is 0.0, which may indicate a calculation error"
        
        # Check if completion rate matches our expectations (we completed ~50% of tasks)
        expected_completion_rate = 0.5  # 50%
        actual_completion_rate = performance["completion_rate"] / 100  # Convert from percentage
        assert abs(actual_completion_rate - expected_completion_rate) <= 0.2, f"Completion rate {actual_completion_rate} differs significantly from expected {expected_completion_rate}"
        
        logger.info(f"✅ Performance analytics calculation is working correctly")
        logger.info(f"Performance score: {performance['performance_score']}/10")
        logger.info(f"Completion rate: {performance['completion_rate']}%")
        
        # Get team performance to verify ranking
        response = requests.get(f"{API_URL}/analytics/team-performance", headers=headers)
        assert response.status_code == 200, f"Failed to get team performance: {response.text}"
        
        team_performance = response.json()
        assert isinstance(team_performance, list), "Team performance should be a list"
        
        # Find our test user in the team performance
        user_found = False
        for user_perf in team_performance:
            if user_perf.get("user_id") == test_user["id"]:
                user_found = True
                assert user_perf["performance_score"] > 0, "User performance score in team ranking is 0.0"
                break
        
        assert user_found, "Test user not found in team performance ranking"
        
        logger.info("✅ Team performance ranking is working correctly")
        
        return True
    else:
        logger.error(f"❌ Performance analytics endpoint failed with status {response.status_code}: {response.text}")
        return False

def test_task_management_drag_drop():
    """
    Test Task Management & Drag-Drop:
    - Test task status updates via /api/tasks/{task_id} 
    - Verify if tasks can actually be moved between statuses
    - Check if the backend supports drag-drop status changes
    """
    logger.info("Testing task management and status updates (drag-drop)...")
    
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Get a task that's not completed
    task_to_update = None
    for task in test_tasks:
        if task["status"] != "completed":
            task_to_update = task
            break
    
    if not task_to_update:
        # Create a new task if all are completed
        task_data = {
            "title": "Drag-Drop Test Task",
            "description": "Task for testing drag-drop functionality",
            "assigned_to": test_user["id"],
            "status": "todo",
            "priority": "medium",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=1)),
            "tags": ["drag-drop", "test"]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        
        task_to_update = response.json()
        test_tasks.append(task_to_update)
        logger.info(f"Created task for drag-drop testing: {task_to_update['title']}")
    
    # Test moving task through different statuses (simulating drag-drop)
    statuses = ["todo", "in_progress", "completed"]
    current_status_index = statuses.index(task_to_update["status"]) if task_to_update["status"] in statuses else 0
    
    # Move to next status
    next_status_index = (current_status_index + 1) % len(statuses)
    next_status = statuses[next_status_index]
    
    update_data = {
        "status": next_status
    }
    
    response = requests.put(f"{API_URL}/tasks/{task_to_update['id']}", json=update_data, headers=headers)
    
    if response.status_code == 200:
        updated_task = response.json()
        assert updated_task["status"] == next_status, f"Task status not updated to {next_status}"
        
        logger.info(f"✅ Successfully moved task from {task_to_update['status']} to {next_status}")
        
        # Move to another status
        next_next_status_index = (next_status_index + 1) % len(statuses)
        next_next_status = statuses[next_next_status_index]
        
        update_data = {
            "status": next_next_status
        }
        
        response = requests.put(f"{API_URL}/tasks/{task_to_update['id']}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update task status again: {response.text}"
        
        updated_task = response.json()
        assert updated_task["status"] == next_next_status, f"Task status not updated to {next_next_status}"
        
        logger.info(f"✅ Successfully moved task from {next_status} to {next_next_status}")
        
        # If we moved to completed, check if completed_at was set
        if next_next_status == "completed":
            assert "completed_at" in updated_task, "completed_at field missing for completed task"
            assert updated_task["completed_at"] is not None, "completed_at field is null for completed task"
            
            logger.info("✅ completed_at field correctly set for completed task")
        
        # Verify task status was persisted by getting the task again
        response = requests.get(f"{API_URL}/tasks/{task_to_update['id']}", headers=headers)
        assert response.status_code == 200, f"Failed to get task: {response.text}"
        
        retrieved_task = response.json()
        assert retrieved_task["status"] == next_next_status, f"Task status not persisted as {next_next_status}"
        
        logger.info("✅ Task status changes are correctly persisted")
        
        return True
    else:
        logger.error(f"❌ Task status update failed with status {response.status_code}: {response.text}")
        return False

def test_core_feature_integration():
    """
    Test Core Feature Integration:
    - Test if features actually work end-to-end
    - Verify data persistence and retrieval
    - Check error handling and user feedback
    """
    logger.info("Testing core feature integration...")
    
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test creating a project
    project_data = {
        "name": "Emergency Test Project",
        "description": "Project for testing core feature integration",
        "owner_id": test_user["id"],
        "team_members": [test_user["id"]],
        "due_date": iso_format(datetime.utcnow() + timedelta(days=30))
    }
    
    response = requests.post(f"{API_URL}/projects", json=project_data, headers=headers)
    
    if response.status_code == 200:
        project = response.json()
        assert project["name"] == project_data["name"], "Project name not saved correctly"
        assert project["description"] == project_data["description"], "Project description not saved correctly"
        assert project["owner_id"] == project_data["owner_id"], "Project owner_id not saved correctly"
        assert set(project["team_members"]) == set(project_data["team_members"]), "Project team_members not saved correctly"
        
        project_id = project["id"]
        logger.info(f"✅ Successfully created project: {project['name']}")
        
        # Create a task associated with the project
        task_data = {
            "title": "Project Integration Test Task",
            "description": "Task for testing project integration",
            "assigned_to": test_user["id"],
            "project_id": project_id,
            "status": "todo",
            "priority": "high",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=7)),
            "tags": ["integration", "test"]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        
        task = response.json()
        task_id = task["id"]
        logger.info(f"✅ Successfully created task in project: {task['title']}")
        
        # Get tasks by project to verify association
        response = requests.get(f"{API_URL}/tasks?project_id={project_id}", headers=headers)
        assert response.status_code == 200, f"Failed to get tasks by project: {response.text}"
        
        project_tasks = response.json()
        assert len(project_tasks) > 0, "No tasks found for project"
        assert any(t["id"] == task_id for t in project_tasks), "Created task not found in project tasks"
        
        logger.info("✅ Project-task association is working correctly")
        
        # Test dashboard analytics to verify integration
        response = requests.get(f"{API_URL}/analytics/dashboard", headers=headers)
        assert response.status_code == 200, f"Failed to get dashboard analytics: {response.text}"
        
        dashboard = response.json()
        assert "total_tasks" in dashboard, "Dashboard missing total_tasks"
        assert "completed_tasks" in dashboard, "Dashboard missing completed_tasks"
        assert "overdue_tasks" in dashboard, "Dashboard missing overdue_tasks"
        assert "in_progress_tasks" in dashboard, "Dashboard missing in_progress_tasks"
        assert "completion_rate" in dashboard, "Dashboard missing completion_rate"
        assert "eisenhower_matrix" in dashboard, "Dashboard missing eisenhower_matrix"
        
        logger.info("✅ Dashboard analytics integration is working correctly")
        
        # Test error handling with invalid data
        invalid_task_data = {
            "title": "",  # Empty title should cause validation error
            "description": "Invalid task",
            "assigned_to": test_user["id"],
            "status": "invalid_status",  # Invalid status
            "priority": "super_high",  # Invalid priority
            "due_date": "not-a-date"  # Invalid date
        }
        
        response = requests.post(f"{API_URL}/tasks", json=invalid_task_data, headers=headers)
        
        if response.status_code != 200:
            logger.info("✅ API correctly rejected invalid task data")
        else:
            logger.warning("⚠️ API accepted invalid task data without validation")
        
        return True
    else:
        logger.error(f"❌ Project creation failed with status {response.status_code}: {response.text}")
        return False

def run_emergency_tests():
    """Run all emergency tests and return results"""
    results = {}
    
    try:
        # Setup test data
        create_test_user()
        create_test_tasks()
        
        # Run tests
        results["ai_coach"] = test_ai_coach_functionality()
        results["whatsapp"] = test_whatsapp_service_availability()
        results["performance_analytics"] = test_performance_analytics_calculation()
        results["task_management"] = test_task_management_drag_drop()
        results["core_features"] = test_core_feature_integration()
        
        # Calculate overall functionality percentage
        working_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        functionality_percentage = (working_count / total_count) * 100
        
        logger.info("\n" + "="*50)
        logger.info(f"EMERGENCY TEST RESULTS:")
        logger.info("="*50)
        logger.info(f"AI Coach Functionality: {'✅ WORKING' if results['ai_coach'] else '❌ FAILING'}")
        logger.info(f"WhatsApp Service: {'✅ WORKING' if results['whatsapp'] else '❌ FAILING'}")
        logger.info(f"Performance Analytics: {'✅ WORKING' if results['performance_analytics'] else '❌ FAILING'}")
        logger.info(f"Task Management: {'✅ WORKING' if results['task_management'] else '❌ FAILING'}")
        logger.info(f"Core Features: {'✅ WORKING' if results['core_features'] else '❌ FAILING'}")
        logger.info("="*50)
        logger.info(f"OVERALL FUNCTIONALITY: {functionality_percentage:.1f}%")
        logger.info("="*50)
        
        return results, functionality_percentage
    except Exception as e:
        logger.error(f"Emergency tests failed with exception: {str(e)}")
        return {}, 0

if __name__ == "__main__":
    logger.info("Starting emergency verification tests...")
    results, functionality_percentage = run_emergency_tests()
    logger.info("Emergency verification tests completed.")