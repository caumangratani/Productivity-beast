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

def test_signup_with_original_form_data():
    """Test signup with the exact original form data to confirm the issue"""
    # Use the exact data from the form as mentioned in the review request
    signup_data = {
        "name": "Umang Ratani",
        "email": "caumangjratani@gmail.com", 
        "password": "some_password",
        "company": "BBCG",
        "plan": "Personal (₹2,000/month)"
    }
    
    logger.info(f"Testing signup with original form data: {json.dumps(signup_data, indent=2)}")
    
    # Make the request
    response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
    
    # Log the full response for debugging
    logger.info(f"Signup response status code: {response.status_code}")
    logger.info(f"Signup response headers: {response.headers}")
    logger.info(f"Signup response body: {response.text}")
    
    # Check the response
    if response.status_code == 422:
        logger.info("CONFIRMED: The issue is that the backend rejects the plan value 'Personal (₹2,000/month)'")
        logger.info("The backend expects one of: 'personal', 'team', or 'enterprise'")
        
        # Parse the error details
        error_details = response.json()
        logger.info(f"Error details: {json.dumps(error_details, indent=2)}")
        
        return True
    else:
        logger.error(f"Unexpected response status code: {response.status_code}")
        return False

if __name__ == "__main__":
    logger.info("Testing signup with original form data to confirm the issue...")
    
    # Run the test
    result = test_signup_with_original_form_data()
    
    # Print summary
    logger.info("\n=== Original Form Data Test Result ===")
    logger.info(f"Issue Confirmed: {'YES' if result else 'NO'}")
    
    if result:
        logger.info("\nROOT CAUSE CONFIRMED:")
        logger.info("The issue 'Error creating account: undefined' is caused by:")
        logger.info("1. The frontend form sends 'Personal (₹2,000/month)' as the plan value")
        logger.info("2. The backend expects one of: 'personal', 'team', or 'enterprise'")
        logger.info("3. This causes a validation error (422) which is not properly handled in the frontend")
        logger.info("\nRECOMMENDED FIX:")
        logger.info("1. Update the frontend to map display values to backend values:")
        logger.info("   - 'Personal (₹2,000/month)' → 'personal'")
        logger.info("   - 'Team (₹5,000/month)' → 'team'")
        logger.info("   - 'Enterprise (Custom)' → 'enterprise'")
        logger.info("2. Ensure proper error handling in the frontend to display validation errors")
    else:
        logger.error("Could not confirm the issue with the original form data")