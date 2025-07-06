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

def test_signup_with_form_data():
    """Test signup with the exact form data from the review request"""
    # Add timestamp to email to ensure uniqueness
    timestamp = int(time.time())
    
    # Use the exact data from the form as mentioned in the review request
    # But convert the plan to the expected format (lowercase without price)
    signup_data = {
        "name": "Umang Ratani",
        "email": f"caumangjratani+{timestamp}@gmail.com",
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
        
        # Now test login with the same credentials
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        logger.info(f"Testing login with data: {json.dumps(login_data, indent=2)}")
        
        # Make the login request
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        # Log the full response for debugging
        logger.info(f"Login response status code: {login_response.status_code}")
        logger.info(f"Login response headers: {login_response.headers}")
        logger.info(f"Login response body: {login_response.text}")
        
        # Check if login is successful
        if login_response.status_code == 200:
            login_result = login_response.json()
            logger.info(f"Login successful: {json.dumps(login_result, indent=2)}")
            assert "access_token" in login_result, "Login response should contain access_token"
            assert "token_type" in login_result, "Login response should contain token_type"
            assert "user" in login_result, "Login response should contain user data"
            
            # Test JWT validation
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            logger.info("Testing JWT validation with /auth/me endpoint")
            
            # Make the request
            me_response = requests.get(f"{API_URL}/auth/me", headers=headers)
            
            # Log the full response for debugging
            logger.info(f"JWT validation response status code: {me_response.status_code}")
            logger.info(f"JWT validation response headers: {me_response.headers}")
            logger.info(f"JWT validation response body: {me_response.text}")
            
            # Check if JWT validation is successful
            if me_response.status_code == 200:
                me_result = me_response.json()
                logger.info(f"JWT validation successful: {json.dumps(me_result, indent=2)}")
                assert me_result["email"] == signup_data["email"], "JWT validation should return correct user data"
                return True, "All authentication steps passed successfully"
            else:
                return False, f"JWT validation failed with status code {me_response.status_code}: {me_response.text}"
        else:
            return False, f"Login failed with status code {login_response.status_code}: {login_response.text}"
    else:
        return False, f"Signup failed with status code {response.status_code}: {response.text}"

if __name__ == "__main__":
    logger.info("Starting comprehensive authentication test...")
    
    # Run the test
    success, message = test_signup_with_form_data()
    
    # Print summary
    logger.info("\n=== Comprehensive Authentication Test Result ===")
    logger.info(f"Test Result: {'PASSED' if success else 'FAILED'}")
    logger.info(f"Message: {message}")
    
    if success:
        logger.info("\nROOT CAUSE ANALYSIS:")
        logger.info("The issue 'Error creating account: undefined' was likely caused by:")
        logger.info("1. The frontend form sends 'Personal (₹2,000/month)' as the plan value")
        logger.info("2. The backend expects one of: 'personal', 'team', or 'enterprise'")
        logger.info("3. This causes a validation error (422) which may not be properly handled in the frontend")
        logger.info("\nRECOMMENDED FIX:")
        logger.info("1. Update the frontend to map display values to backend values:")
        logger.info("   - 'Personal (₹2,000/month)' → 'personal'")
        logger.info("   - 'Team (₹5,000/month)' → 'team'")
        logger.info("   - 'Enterprise (Custom)' → 'enterprise'")
        logger.info("2. Ensure proper error handling in the frontend to display validation errors")
    else:
        logger.error("Comprehensive authentication test FAILED!")