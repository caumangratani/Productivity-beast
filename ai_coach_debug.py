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

def debug_ai_coach_chat_request():
    """Debug the AI Coach chat request with detailed error handling"""
    logger.info("Debugging AI Coach chat request...")
    
    # First, create a test user and authenticate
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Debug User {timestamp}",
        "email": f"debug_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
        "plan": "personal"
    }
    
    try:
        # Create user
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        if response.status_code != 200:
            logger.error(f"Failed to signup: {response.text}")
            return False
        
        # Login
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
        
        # Test AI Coach chat with a real productivity question
        # This is exactly how the frontend is calling the endpoint
        chat_data = {
            "message": "help me with productivity",
            "provider": "openai"
        }
        
        logger.info(f"Sending chat request: {json.dumps(chat_data)}")
        logger.info(f"Headers: {json.dumps({k: v for k, v in headers.items()})}")
        
        # Make the request with detailed debugging
        try:
            response = requests.post(
                f"{API_URL}/ai-coach/chat", 
                json=chat_data, 
                headers=headers,
                timeout=30  # Increase timeout to 30 seconds
            )
            
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {json.dumps(dict(response.headers))}")
            
            if response.status_code == 200:
                chat_result = response.json()
                logger.info(f"AI Coach response keys: {chat_result.keys()}")
                logger.info(f"AI Coach response: {chat_result['response'][:100]}...")  # Log first 100 chars
                return True
            else:
                logger.error(f"AI Coach chat request failed: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Request timed out after 30 seconds")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    except Exception as e:
        logger.error(f"Debug test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def compare_frontend_backend_requests():
    """Compare how the frontend is calling the endpoint vs. our test"""
    logger.info("Comparing frontend vs. backend requests...")
    
    # Create a test user
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Compare User {timestamp}",
        "email": f"compare_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
        "plan": "personal"
    }
    
    try:
        # Create user
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        if response.status_code != 200:
            logger.error(f"Failed to signup: {response.text}")
            return False
        
        # Login
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
        
        # Test 1: Frontend-style request (no user_id)
        frontend_data = {
            "message": "help me with productivity",
            "provider": "openai"
        }
        
        logger.info(f"Sending frontend-style request: {json.dumps(frontend_data)}")
        
        frontend_response = requests.post(
            f"{API_URL}/ai-coach/chat", 
            json=frontend_data, 
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Frontend-style response status: {frontend_response.status_code}")
        
        # Test 2: Backend-style request (with user_id)
        backend_data = {
            "message": "help me with productivity",
            "user_id": user_id,
            "provider": "openai"
        }
        
        logger.info(f"Sending backend-style request: {json.dumps(backend_data)}")
        
        backend_response = requests.post(
            f"{API_URL}/ai-coach/chat", 
            json=backend_data, 
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Backend-style response status: {backend_response.status_code}")
        
        # Compare results
        frontend_success = frontend_response.status_code == 200
        backend_success = backend_response.status_code == 200
        
        if frontend_success and backend_success:
            frontend_result = frontend_response.json()
            backend_result = backend_response.json()
            
            logger.info(f"Frontend response keys: {frontend_result.keys()}")
            logger.info(f"Backend response keys: {backend_result.keys()}")
            
            logger.info(f"Frontend response excerpt: {frontend_result['response'][:50]}...")
            logger.info(f"Backend response excerpt: {backend_result['response'][:50]}...")
            
            return True
        else:
            if not frontend_success:
                logger.error(f"Frontend-style request failed: {frontend_response.text}")
            if not backend_success:
                logger.error(f"Backend-style request failed: {backend_response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Comparison test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_with_current_user_extraction():
    """Test if the backend is correctly extracting the current user from the token"""
    logger.info("Testing with current user extraction from token...")
    
    # Create a test user
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    signup_data = {
        "name": f"Token User {timestamp}",
        "email": f"token_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "company": "Test Company",
        "plan": "personal"
    }
    
    try:
        # Create user
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        if response.status_code != 200:
            logger.error(f"Failed to signup: {response.text}")
            return False
        
        # Login
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
        
        # Create some tasks for the user
        for i in range(3):
            task_data = {
                "title": f"Token Test Task {i}",
                "description": f"Description for token test task {i}",
                "assigned_to": user_id,
                "priority": ["low", "medium", "high"][i % 3],
                "status": ["todo", "in_progress", "completed"][i % 3]
            }
            
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to create task: {response.text}")
                return False
        
        logger.info("Created tasks for the user")
        
        # Test the /auth/me endpoint to verify the token works
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get current user: {response.text}")
            return False
        
        me_result = response.json()
        logger.info(f"Current user from token: {me_result['name']} (ID: {me_result['id']})")
        
        # Now test the AI Coach chat endpoint with just the token
        chat_data = {
            "message": "help me with productivity",
            "provider": "openai"
        }
        
        logger.info(f"Sending chat request with token only: {json.dumps(chat_data)}")
        
        response = requests.post(
            f"{API_URL}/ai-coach/chat", 
            json=chat_data, 
            headers=headers,
            timeout=30
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            chat_result = response.json()
            logger.info(f"AI Coach response keys: {chat_result.keys()}")
            logger.info(f"AI Coach response: {chat_result['response'][:100]}...")
            return True
        else:
            logger.error(f"AI Coach chat request failed: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Token test failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting AI Coach debugging tests...")
    
    # Debug the AI Coach chat request
    debug_success = debug_ai_coach_chat_request()
    logger.info(f"Debug test successful: {debug_success}")
    
    # Compare frontend vs. backend requests
    compare_success = compare_frontend_backend_requests()
    logger.info(f"Comparison test successful: {compare_success}")
    
    # Test with current user extraction from token
    token_success = test_with_current_user_extraction()
    logger.info(f"Token test successful: {token_success}")
    
    # Summary
    logger.info("\n=== AI Coach Debugging Test Summary ===")
    logger.info(f"Debug test: {'✅ PASSED' if debug_success else '❌ FAILED'}")
    logger.info(f"Comparison test: {'✅ PASSED' if compare_success else '❌ FAILED'}")
    logger.info(f"Token test: {'✅ PASSED' if token_success else '❌ FAILED'}")
    
    if debug_success and compare_success and token_success:
        logger.info("All AI Coach debugging tests passed!")
        logger.info("\nCONCLUSION: The AI Coach endpoints are working correctly in our tests.")
        logger.info("The issue might be in the frontend React component or how it's handling the responses.")
    else:
        logger.error("Some AI Coach debugging tests failed!")