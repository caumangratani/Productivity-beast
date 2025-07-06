import requests
import json
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

def test_login_with_specific_user():
    """Test login with the specific user created in the previous test"""
    login_data = {
        "email": "caumangjratani+1751812097@gmail.com",
        "password": "some_password"
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

if __name__ == "__main__":
    logger.info("Testing login with specific user...")
    
    # Run the test
    login_result = test_login_with_specific_user()
    
    # Print summary
    logger.info("\n=== Login Test Result ===")
    logger.info(f"Login Test: {'PASSED' if login_result else 'FAILED'}")
    
    if login_result:
        logger.info("Login test PASSED!")
    else:
        logger.error("Login test FAILED!")