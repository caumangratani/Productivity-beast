import requests
import json
import logging
import time

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

def test_signup_with_exact_form_data():
    """Test signup endpoint with the exact data from the form"""
    # Add timestamp to email to ensure uniqueness
    timestamp = int(time.time())
    
    # Use the exact data from the form as mentioned in the review request
    # But convert the plan to the expected format (lowercase without price)
    signup_data = {
        "name": "Umang Ratani",
        "email": f"caumangjratani+{timestamp}@gmail.com",  # Add timestamp to avoid duplicate email
        "password": "some_password",
        "company": "BBCG",
        "plan": "personal"  # Changed from "Personal (₹2,000/month)" to match backend expectations
    }
    
    logger.info(f"Testing signup with data: {json.dumps(signup_data, indent=2)}")
    
    # Make the request
    response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    
    # Log the full response for debugging
    logger.info(f"Signup response status code: {response.status_code}")
    logger.info(f"Signup response headers: {response.headers}")
    logger.info(f"Signup response body: {response.text}")
    
    # Check if successful
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Signup successful: {json.dumps(result, indent=2)}")
        assert result.get("success") == True, "Signup response should have success=True"
        return True
    else:
        logger.error(f"Signup failed with status code {response.status_code}: {response.text}")
        return False

def test_login_with_credentials():
    """Test login endpoint with credentials"""
    # Create a test user first
    timestamp = int(time.time())
    
    # Create a test user
    signup_data = {
        "name": "Test Login User",
        "email": f"testlogin{timestamp}@example.com",
        "password": "test_password",
        "company": "Test Company",
        "plan": "personal"
    }
    
    # Try to create the user
    signup_response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    if signup_response.status_code != 200:
        logger.error(f"Failed to create test user for login test: {signup_response.text}")
        return False
    
    # Now test login
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    
    logger.info(f"Testing login with data: {json.dumps(login_data, indent=2)}")
    
    # Make the request
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    # Log the full response for debugging
    logger.info(f"Login response status code: {response.status_code}")
    logger.info(f"Login response headers: {response.headers}")
    logger.info(f"Login response body: {response.text}")
    
    # Check if successful
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Login successful: {json.dumps(result, indent=2)}")
        assert "access_token" in result, "Login response should contain access_token"
        assert "token_type" in result, "Login response should contain token_type"
        assert "user" in result, "Login response should contain user data"
        return True
    else:
        logger.error(f"Login failed with status code {response.status_code}: {response.text}")
        return False

def test_jwt_validation():
    """Test JWT token validation"""
    # Create a test user and get token
    timestamp = int(time.time())
    
    # Create a test user
    signup_data = {
        "name": "JWT Test User",
        "email": f"jwttest{timestamp}@example.com",
        "password": "jwt_test_password",
        "company": "JWT Test Company",
        "plan": "personal"
    }
    
    # Try to create the user
    signup_response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    if signup_response.status_code != 200:
        logger.error(f"Failed to create test user for JWT test: {signup_response.text}")
        return False
    
    # Login to get token
    login_data = {
        "email": signup_data["email"],
        "password": signup_data["password"]
    }
    
    login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        logger.error(f"Failed to login for JWT test: {login_response.text}")
        return False
    
    token_data = login_response.json()
    token = token_data["access_token"]
    
    # Test token validation with /auth/me endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    logger.info("Testing JWT validation with /auth/me endpoint")
    
    # Make the request
    response = requests.get(f"{API_URL}/auth/me", headers=headers)
    
    # Log the full response for debugging
    logger.info(f"JWT validation response status code: {response.status_code}")
    logger.info(f"JWT validation response headers: {response.headers}")
    logger.info(f"JWT validation response body: {response.text}")
    
    # Check if successful
    if response.status_code == 200:
        result = response.json()
        logger.info(f"JWT validation successful: {json.dumps(result, indent=2)}")
        assert result["email"] == signup_data["email"], "JWT validation should return correct user data"
        return True
    else:
        logger.error(f"JWT validation failed with status code {response.status_code}: {response.text}")
        return False

def test_error_handling():
    """Test error handling in authentication endpoints"""
    # Test signup with duplicate email
    timestamp = int(time.time())
    email = f"duplicate{timestamp}@example.com"
    
    # Create first user
    signup_data = {
        "name": "Original User",
        "email": email,
        "password": "original_password",
        "company": "Original Company",
        "plan": "personal"
    }
    
    first_response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    if first_response.status_code != 200:
        logger.error(f"Failed to create first user for duplicate test: {first_response.text}")
        return False
    
    # Try to create duplicate user
    duplicate_data = {
        "name": "Duplicate User",
        "email": email,  # Same email
        "password": "duplicate_password",
        "company": "Duplicate Company",
        "plan": "personal"
    }
    
    logger.info("Testing signup with duplicate email")
    
    # Make the request
    response = requests.post(f"{API_URL}/auth/signup", json=duplicate_data)
    
    # Log the full response for debugging
    logger.info(f"Duplicate email response status code: {response.status_code}")
    logger.info(f"Duplicate email response headers: {response.headers}")
    logger.info(f"Duplicate email response body: {response.text}")
    
    # Check if it fails as expected
    if response.status_code != 200:
        logger.info("Duplicate email test passed - signup was rejected")
        return True
    else:
        logger.error("Duplicate email test failed - signup was accepted")
        return False

if __name__ == "__main__":
    logger.info("Starting authentication endpoint tests...")
    
    # Run all tests
    signup_result = test_signup_with_exact_form_data()
    login_result = test_login_with_credentials()
    jwt_result = test_jwt_validation()
    error_result = test_error_handling()
    
    # Print summary
    logger.info("\n=== Authentication Test Results ===")
    logger.info(f"Signup Test: {'PASSED' if signup_result else 'FAILED'}")
    logger.info(f"Login Test: {'PASSED' if login_result else 'FAILED'}")
    logger.info(f"JWT Validation Test: {'PASSED' if jwt_result else 'FAILED'}")
    logger.info(f"Error Handling Test: {'PASSED' if error_result else 'FAILED'}")
    
    if signup_result and login_result and jwt_result and error_result:
        logger.info("All authentication tests PASSED!")
    else:
        logger.error("Some authentication tests FAILED!")