import requests
import json
import logging
import os
import time
from datetime import datetime
import traceback

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

def test_ai_coach_chat_comprehensive():
    """Comprehensive test of the AI Coach chat endpoint with detailed logging"""
    logger.info("Starting comprehensive AI Coach chat test...")
    
    # First, create a test user and authenticate
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Comprehensive Test User {timestamp}",
        "email": f"comprehensive_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
        "plan": "personal"
    }
    
    try:
        # Create user
        logger.info("Creating test user...")
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        if response.status_code != 200:
            logger.error(f"Failed to signup: {response.text}")
            return False
        
        # Login
        logger.info("Logging in...")
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            logger.error(f"Failed to login: {response.text}")
            return False
        
        login_result = response.json()
        token = login_result["access_token"]
        user_id = login_result["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # Create some sample tasks for the user
        logger.info("Creating sample tasks...")
        for i in range(3):
            task_data = {
                "title": f"Comprehensive Test Task {i}",
                "description": f"Description for comprehensive test task {i}",
                "assigned_to": user_id,
                "priority": ["low", "medium", "high"][i % 3],
                "status": ["todo", "in_progress", "completed"][i % 3]
            }
            
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to create task: {response.text}")
                return False
        
        # Test 1: Command endpoint
        logger.info("Test 1: Testing command endpoint...")
        command_data = {
            "command": "/help"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/command", json=command_data, headers=headers)
        if response.status_code != 200:
            logger.error(f"Command endpoint failed: {response.text}")
            return False
        
        command_result = response.json()
        logger.info(f"Command response keys: {command_result.keys()}")
        logger.info(f"Command response: {command_result['response'][:100]}...")
        
        # Test 2: Chat endpoint with user_id
        logger.info("Test 2: Testing chat endpoint with user_id...")
        chat_data_with_user_id = {
            "message": "help me with productivity",
            "user_id": user_id,
            "provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data_with_user_id, headers=headers)
        if response.status_code != 200:
            logger.error(f"Chat endpoint with user_id failed: {response.text}")
            return False
        
        chat_result_with_user_id = response.json()
        logger.info(f"Chat with user_id response keys: {chat_result_with_user_id.keys()}")
        logger.info(f"Chat with user_id response: {chat_result_with_user_id['response'][:100]}...")
        
        # Test 3: Chat endpoint without user_id (as the frontend does)
        logger.info("Test 3: Testing chat endpoint without user_id...")
        chat_data_without_user_id = {
            "message": "give me productivity tips",
            "provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data_without_user_id, headers=headers)
        if response.status_code != 200:
            logger.error(f"Chat endpoint without user_id failed: {response.text}")
            return False
        
        chat_result_without_user_id = response.json()
        logger.info(f"Chat without user_id response keys: {chat_result_without_user_id.keys()}")
        logger.info(f"Chat without user_id response: {chat_result_without_user_id['response'][:100]}...")
        
        # Test 4: Chat endpoint with invalid user_id
        logger.info("Test 4: Testing chat endpoint with invalid user_id...")
        chat_data_invalid_user_id = {
            "message": "help me focus",
            "user_id": "invalid_user_id",
            "provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data_invalid_user_id, headers=headers)
        # This should still work, just use a fallback user
        if response.status_code != 200:
            logger.error(f"Chat endpoint with invalid user_id failed: {response.text}")
            return False
        
        chat_result_invalid_user_id = response.json()
        logger.info(f"Chat with invalid user_id response keys: {chat_result_invalid_user_id.keys()}")
        logger.info(f"Chat with invalid user_id response: {chat_result_invalid_user_id['response'][:100]}...")
        
        # Test 5: Chat endpoint with no authentication
        logger.info("Test 5: Testing chat endpoint with no authentication...")
        chat_data_no_auth = {
            "message": "how to be more productive",
            "provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data_no_auth)
        # This might fail depending on the backend implementation
        logger.info(f"Chat endpoint with no authentication status: {response.status_code}")
        if response.status_code == 200:
            chat_result_no_auth = response.json()
            logger.info(f"Chat with no authentication response keys: {chat_result_no_auth.keys()}")
            logger.info(f"Chat with no authentication response: {chat_result_no_auth['response'][:100]}...")
        else:
            logger.info(f"Chat endpoint with no authentication failed as expected: {response.text}")
        
        # All tests passed
        logger.info("All AI Coach chat tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Comprehensive test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting comprehensive AI Coach tests...")
    
    # Run the comprehensive test
    comprehensive_success = test_ai_coach_chat_comprehensive()
    
    # Summary
    logger.info("\n=== Comprehensive AI Coach Test Summary ===")
    logger.info(f"Comprehensive test: {'✅ PASSED' if comprehensive_success else '❌ FAILED'}")
    
    if comprehensive_success:
        logger.info("\nCONCLUSION: The AI Coach endpoints are working correctly.")
        logger.info("The fix to the frontend component should resolve the issue.")
    else:
        logger.error("\nCONCLUSION: There are still issues with the AI Coach endpoints.")
        logger.error("Further investigation is needed.")