"""
Test script to verify the Phase 2 integration

This script tests:
1. Database initialization
2. User creation and authentication
3. Health check endpoints
4. Basic API functionality
"""

import requests
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📊 Database: {'Connected' if data['database_connected'] else 'Disconnected'}")
            print(f"   🎯 Version: {data['version']}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   💡 Make sure the backend is running: python -m backend.main")
        return False


def test_authentication():
    """Test authentication endpoints"""
    print("\n🔐 Testing authentication...")
    
    # Test login with default admin
    try:
        print("   Attempting login with admin credentials...")
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print(f"   ✅ Login successful!")
            print(f"   🎟️  Token: {token[:50]}...")
            return token
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   💡 Make sure you ran: python init_db.py")
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🔒 Testing protected endpoint...")
    
    if not token:
        print("   ⏭️  Skipped (no token)")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
        
        if response.status_code == 200:
            user = response.json()
            print(f"   ✅ Authenticated as: {user['username']}")
            print(f"   📧 Email: {user['email']}")
            print(f"   👤 Role: {user['role']}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_detailed_health(token):
    """Test detailed health check (requires auth)"""
    print("\n📊 Testing detailed health check...")
    
    if not token:
        print("   ⏭️  Skipped (no token)")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/health/detailed", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   ⏱️  Uptime: {data['uptime_seconds']:.2f} seconds")
            print(f"   📹 Recordings: {data['total_recordings']}")
            print(f"   🎯 Events: {data['total_events']}")
            print(f"   💾 Disk usage: {data['disk_usage_percent']:.1f}%")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_api_docs():
    """Test API documentation endpoint"""
    print("\n📚 Testing API documentation...")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"   ✅ API docs available at: {BASE_URL}/docs")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Phase 2 Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed - stopping tests")
        print("💡 Make sure backend is running: python -m backend.main")
        return
    
    # Test 2: Authentication
    token = test_authentication()
    
    # Test 3: Protected endpoint
    test_protected_endpoint(token)
    
    # Test 4: Detailed health
    test_detailed_health(token)
    
    # Test 5: API docs
    test_api_docs()
    
    print("\n" + "=" * 60)
    print("✅ Phase 2 Integration Tests Complete!")
    print("=" * 60)
    print("\n📖 Next steps:")
    print("   1. Visit http://localhost:8000/docs for interactive API testing")
    print("   2. Try logging in with: admin / admin123")
    print("   3. Use create_user.py to add more users")
    print("\n⚠️  Remember to change the default admin password!")


if __name__ == "__main__":
    main()
