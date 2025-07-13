#!/usr/bin/env python3
"""
Critical Features Testing for Productivity Beast
Testing the specific functionality mentioned in the review request:
1. Google OAuth Integration Testing (Fixed)
2. AI Coach Real Data Analysis Testing (Fixed) 
3. Simple WhatsApp Integration Testing (New Feature)
4. Core Application Features
"""

import requests
import json
import logging
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

BACKEND_URL = BACKEND_URL.strip("'\"")
API_URL = f"{BACKEND_URL}/api"

logger.info(f"Using API URL: {API_URL}")

def iso_format(dt):
    """Convert datetime to ISO format string"""
    if dt:
        return dt.isoformat()
    return None

def test_google_oauth_integration():
    """Test Google OAuth Integration (Fixed)"""
    logger.info("=== TESTING GOOGLE OAUTH INTEGRATION (FIXED) ===")
    
    try:
        # Create a test user
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Google OAuth Test User",
            "email": f"googleoauth_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
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
        user_id = login_result["user"]["id"]
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # 1. Test GET /api/google/auth/url endpoint
        logger.info("Testing GET /api/google/auth/url endpoint...")
        response = requests.get(f"{API_URL}/google/auth/url?user_id={user_id}")
        
        if response.status_code == 500:
            error_data = response.json()
            if "Google OAuth not configured" in error_data.get("detail", ""):
                logger.error("❌ CRITICAL: Google OAuth credentials are not properly configured")
                return False
        
        assert response.status_code == 200, f"Google OAuth URL generation failed: {response.text}"
        
        auth_url_result = response.json()
        logger.info(f"Google OAuth URL response keys: {list(auth_url_result.keys())}")
        
        # 2. Verify it returns proper Google OAuth URL
        assert "auth_url" in auth_url_result, "Missing auth_url in response"
        assert "state" in auth_url_result, "Missing state in response"
        assert "message" in auth_url_result, "Missing message in response"
        
        auth_url = auth_url_result["auth_url"]
        state = auth_url_result["state"]
        
        # 3. Confirm the endpoint works without errors
        assert "accounts.google.com/o/oauth2/auth" in auth_url, "Invalid Google OAuth URL"
        assert user_id in state, "User ID not properly included in state"
        
        # Verify correct scopes and redirect URI
        assert "scope=" in auth_url, "Missing scopes in OAuth URL"
        assert "calendar" in auth_url, "Missing calendar scope"
        assert "spreadsheets" in auth_url, "Missing spreadsheets scope"
        assert "redirect_uri=" in auth_url, "Missing redirect URI"
        assert "project-continue-1.emergent.host" in auth_url, "Incorrect redirect URI"
        
        logger.info("✅ Google OAuth Integration Test PASSED")
        logger.info(f"✅ Auth URL contains correct scopes (calendar, spreadsheets)")
        logger.info(f"✅ Redirect URI is correct (project-continue-1.emergent.host)")
        logger.info(f"✅ State parameter properly includes user_id: {user_id}")
        
        # Test Google integration status
        logger.info("Testing Google integration status...")
        response = requests.get(f"{API_URL}/google/integration/status/{user_id}")
        assert response.status_code == 200, f"Failed to get Google integration status: {response.text}"
        
        status_result = response.json()
        assert "connected" in status_result
        assert "setup_required" in status_result
        assert status_result["connected"] == False  # Should be false for new user
        assert status_result["setup_required"] == True  # Should require setup
        
        logger.info("✅ Google integration status endpoint working correctly")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Google OAuth Integration test FAILED: {str(e)}")
        return False

def test_ai_coach_real_data_analysis():
    """Test AI Coach Real Data Analysis (Fixed)"""
    logger.info("=== TESTING AI COACH REAL DATA ANALYSIS (FIXED) ===")
    
    try:
        # Create a test user with some task data
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"AI Coach Test User",
            "email": f"aicoach_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Test Company",
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
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        logger.info(f"Created test user with ID: {user_id}")
        
        # Create some sample tasks for the user to analyze
        sample_tasks = [
            {
                "title": "Complete project proposal",
                "description": "Write and submit the Q1 project proposal",
                "assigned_to": user_id,
                "priority": "high",
                "status": "completed",
                "due_date": iso_format(datetime.utcnow() - timedelta(days=2)),
                "tags": ["project", "proposal"]
            },
            {
                "title": "Review team performance",
                "description": "Analyze team metrics and provide feedback",
                "assigned_to": user_id,
                "priority": "medium",
                "status": "in_progress",
                "due_date": iso_format(datetime.utcnow() + timedelta(days=3)),
                "tags": ["review", "team"]
            },
            {
                "title": "Update documentation",
                "description": "Update API documentation with latest changes",
                "assigned_to": user_id,
                "priority": "low",
                "status": "todo",
                "due_date": iso_format(datetime.utcnow() + timedelta(days=7)),
                "tags": ["documentation"]
            }
        ]
        
        created_tasks = []
        for task_data in sample_tasks:
            response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
            assert response.status_code == 200, f"Failed to create task: {response.text}"
            created_tasks.append(response.json())
            
        logger.info(f"Created {len(created_tasks)} sample tasks for analysis")
        
        # 1. Test POST /api/ai-coach/chat endpoint with actual user data
        logger.info("Testing AI Coach chat with actual user data...")
        
        chat_data = {
            "message": "analyze my productivity",
            "user_id": user_id,
            "include_user_context": True,
            "ai_provider": "openai"
        }
        
        response = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data, headers=headers)
        
        if response.status_code == 500:
            error_data = response.json()
            if "OpenAI API key not configured" in error_data.get("detail", ""):
                logger.error("❌ CRITICAL: OpenAI API key is not properly configured")
                return False
        
        assert response.status_code == 200, f"AI Coach chat failed: {response.text}"
        
        chat_result = response.json()
        logger.info(f"AI Coach response keys: {list(chat_result.keys())}")
        
        # 2. Verify it analyzes real task data and provides personalized insights
        assert "response" in chat_result, "Missing response in AI Coach result"
        assert "user_context_used" in chat_result, "Missing user_context_used flag"
        assert "analysis_summary" in chat_result, "Missing analysis_summary"
        
        ai_response = chat_result["response"]
        user_context_used = chat_result["user_context_used"]
        analysis_summary = chat_result["analysis_summary"]
        
        # 3. Test with a message like "analyze my productivity"
        assert user_context_used == True, "AI Coach should use user context for analysis"
        assert "3 tasks" in analysis_summary or "tasks" in analysis_summary, "Analysis summary should mention task count"
        
        # Check if AI response is personalized and not generic
        assert len(ai_response) > 100, "AI response seems too short to be meaningful analysis"
        
        # Look for indicators that the AI is analyzing real data
        productivity_indicators = [
            "task", "completion", "productivity", "performance", 
            "progress", "deadline", "priority", "project"
        ]
        
        response_lower = ai_response.lower()
        found_indicators = [indicator for indicator in productivity_indicators if indicator in response_lower]
        
        assert len(found_indicators) >= 3, f"AI response doesn't contain productivity analysis. Found: {found_indicators}"
        
        logger.info("✅ AI Coach Real Data Analysis Test PASSED")
        logger.info(f"✅ User context used: {user_context_used}")
        logger.info(f"✅ Analysis summary: {analysis_summary}")
        logger.info(f"✅ AI response contains productivity analysis with {len(found_indicators)} relevant indicators")
        
        # Test with different productivity query
        logger.info("Testing with different productivity query...")
        
        chat_data2 = {
            "message": "what are my completion rates and task patterns?",
            "user_id": user_id,
            "include_user_context": True,
            "ai_provider": "openai"
        }
        
        response2 = requests.post(f"{API_URL}/ai-coach/chat", json=chat_data2, headers=headers)
        assert response2.status_code == 200, f"Second AI Coach chat failed: {response2.text}"
        
        chat_result2 = response2.json()
        assert chat_result2["user_context_used"] == True, "Second query should also use user context"
        
        logger.info("✅ AI Coach consistently analyzes real user data")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ AI Coach Real Data Analysis test FAILED: {str(e)}")
        return False

def test_simple_whatsapp_integration():
    """Test Simple WhatsApp Integration (New Feature)"""
    logger.info("=== TESTING SIMPLE WHATSAPP INTEGRATION (NEW FEATURE) ===")
    
    try:
        # 1. Test POST /api/whatsapp/start-connection endpoint
        logger.info("Testing POST /api/whatsapp/start-connection endpoint...")
        response = requests.post(f"{API_URL}/whatsapp/start-connection")
        assert response.status_code == 200, f"WhatsApp start connection failed: {response.text}"
        
        start_result = response.json()
        assert "success" in start_result, "Missing success field in start connection response"
        assert "message" in start_result, "Missing message field in start connection response"
        assert "status" in start_result, "Missing status field in start connection response"
        assert start_result["success"] == True, "Start connection should return success=True"
        
        logger.info("✅ WhatsApp start connection endpoint working")
        
        # 2. Test GET /api/whatsapp/qr-code endpoint (should generate QR code)
        logger.info("Testing GET /api/whatsapp/qr-code endpoint...")
        response = requests.get(f"{API_URL}/whatsapp/qr-code")
        assert response.status_code == 200, f"WhatsApp QR code generation failed: {response.text}"
        
        qr_result = response.json()
        assert "success" in qr_result, "Missing success field in QR code response"
        assert "qr_code" in qr_result, "Missing qr_code field in QR code response"
        assert "message" in qr_result, "Missing message field in QR code response"
        assert qr_result["success"] == True, "QR code generation should return success=True"
        assert len(qr_result["qr_code"]) > 100, "QR code should be a base64 encoded image"
        
        logger.info("✅ WhatsApp QR code generation endpoint working")
        
        # 3. Test GET /api/whatsapp/status endpoint
        logger.info("Testing GET /api/whatsapp/status endpoint...")
        response = requests.get(f"{API_URL}/whatsapp/status")
        assert response.status_code == 200, f"WhatsApp status check failed: {response.text}"
        
        status_result = response.json()
        assert "connected" in status_result, "Missing connected field in status response"
        assert "status" in status_result, "Missing status field in status response"
        assert "message" in status_result, "Missing message field in status response"
        
        # In test environment, WhatsApp service might not be available, which is acceptable
        logger.info(f"WhatsApp status: {status_result['status']}")
        logger.info(f"WhatsApp connected: {status_result['connected']}")
        
        logger.info("✅ WhatsApp status endpoint working")
        
        # 4. Test POST /api/whatsapp/disconnect endpoint
        logger.info("Testing POST /api/whatsapp/disconnect endpoint...")
        response = requests.post(f"{API_URL}/whatsapp/disconnect")
        assert response.status_code == 200, f"WhatsApp disconnect failed: {response.text}"
        
        disconnect_result = response.json()
        assert "success" in disconnect_result, "Missing success field in disconnect response"
        assert "message" in disconnect_result, "Missing message field in disconnect response"
        assert disconnect_result["success"] == True, "Disconnect should return success=True"
        
        logger.info("✅ WhatsApp disconnect endpoint working")
        
        logger.info("✅ Simple WhatsApp Integration Test PASSED")
        logger.info("✅ All WhatsApp endpoints (start-connection, qr-code, status, disconnect) working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Simple WhatsApp Integration test FAILED: {str(e)}")
        return False

def test_core_application_features():
    """Test Core Application Features"""
    logger.info("=== TESTING CORE APPLICATION FEATURES ===")
    
    try:
        # 1. Test user authentication (signup/login)
        logger.info("Testing user authentication (signup/login)...")
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        signup_data = {
            "name": f"Core Test User",
            "email": f"coretest_{timestamp}@example.com",
            "password": "SecurePassword!",
            "company": "Core Test Company",
            "plan": "personal"
        }
        
        # Test signup
        response = requests.post(f"{API_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200, f"Failed to signup: {response.text}"
        signup_result = response.json()
        assert signup_result["success"] == True, "Signup should return success=True"
        
        # Test login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        assert response.status_code == 200, f"Failed to login: {response.text}"
        login_result = response.json()
        assert "access_token" in login_result, "Login should return access token"
        assert "user" in login_result, "Login should return user data"
        
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = login_result["user"]["id"]
        
        logger.info("✅ User authentication working")
        
        # 2. Test task creation and management
        logger.info("Testing task creation and management...")
        task_data = {
            "title": "Core Test Task",
            "description": "Testing core task management functionality",
            "assigned_to": user_id,
            "priority": "high",
            "due_date": iso_format(datetime.utcnow() + timedelta(days=5)),
            "tags": ["core", "test"]
        }
        
        # Create task
        response = requests.post(f"{API_URL}/tasks", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task: {response.text}"
        task = response.json()
        assert task["title"] == task_data["title"], "Task title should match"
        assert "eisenhower_quadrant" in task, "Task should have Eisenhower quadrant"
        
        task_id = task["id"]
        
        # Update task status
        update_data = {"status": "in_progress"}
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data, headers=headers)
        assert response.status_code == 200, f"Failed to update task: {response.text}"
        updated_task = response.json()
        assert updated_task["status"] == "in_progress", "Task status should be updated"
        
        # Complete task
        complete_data = {"status": "completed", "quality_rating": 9}
        response = requests.put(f"{API_URL}/tasks/{task_id}", json=complete_data, headers=headers)
        assert response.status_code == 200, f"Failed to complete task: {response.text}"
        completed_task = response.json()
        assert completed_task["status"] == "completed", "Task should be completed"
        assert completed_task["quality_rating"] == 9, "Quality rating should be set"
        
        logger.info("✅ Task creation and management working")
        
        # 3. Test dashboard analytics with real data
        logger.info("Testing dashboard analytics with real data...")
        response = requests.get(f"{API_URL}/analytics/dashboard", headers=headers)
        assert response.status_code == 200, f"Failed to get dashboard analytics: {response.text}"
        
        dashboard = response.json()
        assert "total_tasks" in dashboard, "Dashboard should include total tasks"
        assert "completed_tasks" in dashboard, "Dashboard should include completed tasks"
        assert "completion_rate" in dashboard, "Dashboard should include completion rate"
        assert "eisenhower_matrix" in dashboard, "Dashboard should include Eisenhower matrix"
        
        # Verify real data is reflected
        assert dashboard["total_tasks"] >= 1, "Should have at least 1 task from our test"
        assert dashboard["completed_tasks"] >= 1, "Should have at least 1 completed task"
        
        logger.info("✅ Dashboard analytics working with real data")
        
        # 4. Test performance metrics calculation
        logger.info("Testing performance metrics calculation...")
        response = requests.get(f"{API_URL}/analytics/performance/{user_id}", headers=headers)
        assert response.status_code == 200, f"Failed to get performance metrics: {response.text}"
        
        performance = response.json()
        assert "performance_score" in performance, "Performance should include score"
        assert "tasks_assigned" in performance, "Performance should include tasks assigned"
        assert "tasks_completed" in performance, "Performance should include tasks completed"
        assert "completion_rate" in performance, "Performance should include completion rate"
        
        # Verify metrics are calculated correctly
        assert performance["tasks_assigned"] >= 1, "Should have at least 1 assigned task"
        assert performance["tasks_completed"] >= 1, "Should have at least 1 completed task"
        assert performance["performance_score"] > 0, "Performance score should be greater than 0"
        
        logger.info("✅ Performance metrics calculation working")
        
        logger.info("✅ Core Application Features Test PASSED")
        logger.info("✅ Authentication, task management, dashboard analytics, and performance metrics all working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Core Application Features test FAILED: {str(e)}")
        return False

def main():
    """Run all critical feature tests"""
    logger.info("🚀 STARTING CRITICAL FEATURES TESTING")
    logger.info("Testing all critical functionality that was just fixed and implemented")
    
    test_results = {
        "Google OAuth Integration": False,
        "AI Coach Real Data Analysis": False,
        "Simple WhatsApp Integration": False,
        "Core Application Features": False
    }
    
    # Run all tests
    test_results["Google OAuth Integration"] = test_google_oauth_integration()
    test_results["AI Coach Real Data Analysis"] = test_ai_coach_real_data_analysis()
    test_results["Simple WhatsApp Integration"] = test_simple_whatsapp_integration()
    test_results["Core Application Features"] = test_core_application_features()
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("🎯 CRITICAL FEATURES TESTING SUMMARY")
    logger.info("="*60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for feature, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{feature}: {status}")
        if passed:
            passed_tests += 1
    
    logger.info(f"\nOverall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL CRITICAL FEATURES ARE WORKING!")
        logger.info("✅ Google OAuth is working (no more 'feature coming' error)")
        logger.info("✅ AI Coach analyzes real user data (no more random answers)")
        logger.info("✅ WhatsApp integration is simplified with QR code scanning")
        logger.info("✅ All core features are functional")
        logger.info("\n🚀 APPLICATION IS READY FOR PRODUCTION USE!")
    else:
        logger.error(f"❌ {total_tests - passed_tests} critical features still have issues")
        logger.error("🔧 Please review the failed tests above and fix the issues")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)