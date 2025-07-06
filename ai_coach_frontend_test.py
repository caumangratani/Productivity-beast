import requests
import json
import logging
import os
import time
from datetime import datetime

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

def test_ai_coach_chat_with_user_id():
    """Test the AI Coach chat endpoint with a real message and user_id"""
    logger.info("Testing AI Coach chat endpoint with user_id...")
    
    # First, create a test user and authenticate
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"AI Coach Test User {timestamp}",
        "email": f"aicoach_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
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
    user_id = login_result["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    
    logger.info(f"Created test user with ID: {user_id}")
    
    # Create some sample tasks for the user to have data for AI analysis
    for i in range(5):
        task_data = {
            "title": f"Test Task {i} for AI Coach",
            "description": f"Description for test task {i}",
            "assigned_to": user_id,
            "priority": ["low", "medium", "high"][i % 3],
            "status": ["todo", "in_progress", "completed"][i % 3]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
    
    logger.info("Created sample tasks for AI analysis")
    
    # Test AI Coach chat with a real productivity question
    chat_data = {
        "message": "help me with productivity",
        "user_id": user_id,
        "provider": "openai"  # Try to use OpenAI first
    }
    
    logger.info(f"Sending chat request: {json.dumps(chat_data)}")
    
    response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
    logger.info(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        chat_result = response.json()
        logger.info(f"AI Coach response keys: {chat_result.keys()}")
        
        assert "response" in chat_result, "Response key missing in AI Coach response"
        assert len(chat_result["response"]) > 0, "Empty response from AI Coach"
        
        logger.info(f"AI Coach response: {chat_result['response'][:100]}...")  # Log first 100 chars
        logger.info("AI Coach chat test passed")
        return True
    else:
        logger.error(f"AI Coach chat test failed: {response.text}")
        return False

def test_ai_coach_chat_without_user_id():
    """Test the AI Coach chat endpoint without user_id (as the frontend does)"""
    logger.info("Testing AI Coach chat endpoint without user_id...")
    
    # First, create a test user and authenticate
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"AI Coach Test User {timestamp}",
        "email": f"aicoach_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
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
    
    # Test AI Coach chat with a real productivity question but without user_id
    # This is how the frontend is calling the endpoint
    chat_data = {
        "message": "help me with productivity",
        "provider": "openai"  # Try to use OpenAI first
    }
    
    logger.info(f"Sending chat request without user_id: {json.dumps(chat_data)}")
    
    response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
    logger.info(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        chat_result = response.json()
        logger.info(f"AI Coach response keys: {chat_result.keys()}")
        
        assert "response" in chat_result, "Response key missing in AI Coach response"
        assert len(chat_result["response"]) > 0, "Empty response from AI Coach"
        
        logger.info(f"AI Coach response: {chat_result['response'][:100]}...")  # Log first 100 chars
        logger.info("AI Coach chat test passed")
        return True
    else:
        logger.error(f"AI Coach chat test failed: {response.text}")
        return False

def test_ai_coach_command():
    """Test the AI Coach command endpoint with slash commands"""
    logger.info("Testing AI Coach command endpoint...")
    
    # Test help command
    command_data = {
        "command": "/help"
    }
    
    logger.info(f"Sending command request: {json.dumps(command_data)}")
    
    response = requests.post(f"{API_URL}/ai-coach/command", json=command_data)
    logger.info(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        command_result = response.json()
        logger.info(f"AI Coach command response keys: {command_result.keys()}")
        
        assert "response" in command_result, "Response key missing in AI Coach command response"
        assert len(command_result["response"]) > 0, "Empty response from AI Coach command"
        
        logger.info(f"AI Coach command response: {command_result['response'][:100]}...")  # Log first 100 chars
        logger.info("AI Coach command test passed")
        return True
    else:
        logger.error(f"AI Coach command test failed: {response.text}")
        return False

def test_frontend_ai_coach_simulation():
    """Simulate how the frontend is calling the AI Coach endpoints"""
    logger.info("Simulating frontend AI Coach interaction...")
    
    # First, create a test user and authenticate
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Frontend Sim User {timestamp}",
        "email": f"frontendsim_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
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
    user_id = login_result["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    
    logger.info(f"Created test user with ID: {user_id}")
    
    # Create some sample tasks for the user
    for i in range(3):
        task_data = {
            "title": f"Frontend Sim Task {i}",
            "description": f"Description for frontend sim task {i}",
            "assigned_to": user_id,
            "priority": ["low", "medium", "high"][i % 3],
            "status": ["todo", "in_progress", "completed"][i % 3]
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
    
    # Simulate the frontend chat interaction
    # Step 1: User sends a message
    user_message = "help me with productivity"
    
    # Step 2: Frontend sends the message to the AI Coach chat endpoint
    chat_data = {
        "message": user_message,
        "provider": "openai"
    }
    
    logger.info(f"Simulating frontend sending chat request: {json.dumps(chat_data)}")
    
    response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
    logger.info(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        chat_result = response.json()
        logger.info(f"AI Coach response keys: {chat_result.keys()}")
        
        assert "response" in chat_result, "Response key missing in AI Coach response"
        assert len(chat_result["response"]) > 0, "Empty response from AI Coach"
        
        logger.info(f"AI Coach response: {chat_result['response'][:100]}...")  # Log first 100 chars
        logger.info("Frontend simulation chat test passed")
        return True
    else:
        logger.error(f"Frontend simulation chat test failed: {response.text}")
        return False

if __name__ == "__main__":
    logger.info("Starting AI Coach frontend simulation tests...")
    
    # Test AI Coach chat with user_id
    with_user_id_success = test_ai_coach_chat_with_user_id()
    logger.info(f"AI Coach chat with user_id test successful: {with_user_id_success}")
    
    # Test AI Coach chat without user_id (as the frontend does)
    without_user_id_success = test_ai_coach_chat_without_user_id()
    logger.info(f"AI Coach chat without user_id test successful: {without_user_id_success}")
    
    # Test AI Coach command endpoint
    command_success = test_ai_coach_command()
    logger.info(f"AI Coach command test successful: {command_success}")
    
    # Test frontend simulation
    frontend_sim_success = test_frontend_ai_coach_simulation()
    logger.info(f"Frontend simulation test successful: {frontend_sim_success}")
    
    # Summary
    logger.info("\n=== AI Coach Frontend Simulation Test Summary ===")
    logger.info(f"AI Coach chat with user_id test: {'✅ PASSED' if with_user_id_success else '❌ FAILED'}")
    logger.info(f"AI Coach chat without user_id test: {'✅ PASSED' if without_user_id_success else '❌ FAILED'}")
    logger.info(f"AI Coach command test: {'✅ PASSED' if command_success else '❌ FAILED'}")
    logger.info(f"Frontend simulation test: {'✅ PASSED' if frontend_sim_success else '❌ FAILED'}")
    
    if with_user_id_success and without_user_id_success and command_success and frontend_sim_success:
        logger.info("All AI Coach frontend simulation tests passed!")
    else:
        logger.error("Some AI Coach frontend simulation tests failed!")