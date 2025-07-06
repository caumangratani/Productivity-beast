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

def test_ai_coach_chat():
    """Test the AI Coach chat endpoint with a real message"""
    logger.info("Testing AI Coach chat endpoint...")
    
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

def test_openai_api_key():
    """Test if the OpenAI API key is accessible and valid"""
    logger.info("Testing OpenAI API key...")
    
    # Check if the OpenAI API key is set in the environment
    response = requests.get(f"{API_URL}/integrations/ai-settings")
    
    if response.status_code == 200:
        ai_settings = response.json()
        logger.info(f"AI settings: {json.dumps({k: '***' if 'key' in k else v for k, v in ai_settings.items()})}")
        
        if ai_settings.get("ai_enabled", False):
            logger.info("OpenAI API key is configured and enabled")
            return True
        else:
            logger.warning("OpenAI API key is not enabled")
            return False
    else:
        logger.error(f"Failed to get AI settings: {response.text}")
        return False

def test_direct_openai_call():
    """Test a direct call to OpenAI API to verify the key works"""
    try:
        # Get the OpenAI API key from the backend .env file
        with open('/app/backend/.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    openai_key = line.strip().split('=')[1].strip('"\'')
                    break
        
        if not openai_key:
            logger.error("OpenAI API key not found in backend .env file")
            return False
        
        logger.info("Found OpenAI API key in backend .env file")
        
        # Make a direct API call to OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}"
        }
        
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            "max_tokens": 50
        }
        
        logger.info("Making direct API call to OpenAI...")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"OpenAI API response: {result['choices'][0]['message']['content']}")
            logger.info("Direct OpenAI API call successful")
            return True
        else:
            logger.error(f"OpenAI API call failed: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"Error testing direct OpenAI call: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting AI Coach tests...")
    
    # Test OpenAI API key
    openai_key_valid = test_openai_api_key()
    logger.info(f"OpenAI API key valid: {openai_key_valid}")
    
    # Test direct OpenAI call
    direct_openai_call_success = test_direct_openai_call()
    logger.info(f"Direct OpenAI call successful: {direct_openai_call_success}")
    
    # Test AI Coach command endpoint
    command_success = test_ai_coach_command()
    logger.info(f"AI Coach command test successful: {command_success}")
    
    # Test AI Coach chat endpoint
    chat_success = test_ai_coach_chat()
    logger.info(f"AI Coach chat test successful: {chat_success}")
    
    # Summary
    logger.info("\n=== AI Coach Test Summary ===")
    logger.info(f"OpenAI API key valid: {openai_key_valid}")
    logger.info(f"Direct OpenAI call successful: {direct_openai_call_success}")
    logger.info(f"AI Coach command test successful: {command_success}")
    logger.info(f"AI Coach chat test successful: {chat_success}")
    
    if chat_success and command_success:
        logger.info("All AI Coach tests passed!")
    else:
        logger.error("Some AI Coach tests failed!")