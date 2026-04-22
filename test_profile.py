#!/usr/bin/env python3
"""Quick test script to verify profile page functionality"""

import requests
from requests.cookies import RequestsCookieJar

BASE_URL = "http://localhost:5001"

def test_unauthenticated_redirect():
    """Test that unauthenticated users are redirected to login"""
    response = requests.get(f"{BASE_URL}/profile", allow_redirects=False)
    print(f"✓ Unauthenticated access: {response.status_code} (redirect to {response.headers.get('Location')})")
    assert response.status_code == 302
    assert "/login" in response.headers.get("Location", "")

def test_authenticated_access():
    """Test that authenticated users can access profile"""
    # Create a session
    session = requests.Session()

    # Register a new user with unique email
    import time
    email = f"testuser{int(time.time())}@example.com"

    register_data = {
        "name": "Test User",
        "email": email,
        "password": "testpass123"
    }

    response = session.post(f"{BASE_URL}/register", data=register_data, allow_redirects=True)

    if response.status_code == 200 and "profile" in response.url:
        print(f"✓ Registration successful, redirected to profile")

        # Check if profile page loads
        profile_response = session.get(f"{BASE_URL}/profile")
        if profile_response.status_code == 200:
            print(f"✓ Profile page loads: 200 OK")

            # Check for key elements
            content = profile_response.text
            checks = [
                ("User info card", "user-card" in content),
                ("Summary stats", "profile-stats" in content),
                ("Transaction table", "transaction-table" in content),
                ("Category breakdown", "category-breakdown" in content),
                ("No hex colors", "#" not in content or "color:#" not in content),
                ("Logged-in navbar", "Welcome" in content or "Sign out" in content)
            ]

            for check_name, result in checks:
                status = "✓" if result else "✗"
                print(f"{status} {check_name}: {'PASS' if result else 'FAIL'}")

            return all(result for _, result in checks)
    else:
        print(f"✗ Registration failed or didn't redirect properly")
        return False

if __name__ == "__main__":
    print("Testing Profile Page Implementation\n")
    print("=" * 50)

    try:
        test_unauthenticated_redirect()
        print()
        authenticated_ok = test_authenticated_access()
        print()
        print("=" * 50)
        print("✓ All tests passed!" if authenticated_ok else "✗ Some tests failed")
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
