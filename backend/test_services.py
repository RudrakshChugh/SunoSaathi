"""
Quick test script to verify all services are running and responding
Run this before the demo to ensure everything works!
"""
import requests
import time

SERVICES = {
    "API Gateway": "http://localhost:8000",
    "ISL Recognition": "http://localhost:8001",
    "Translation": "http://localhost:8002",
    "TTS": "http://localhost:8003",
    "Safety": "http://localhost:8004",
}

def test_service(name, url, endpoint="/"):
    """Test if a service is running"""
    try:
        response = requests.get(f"{url}{endpoint}", timeout=2)
        if response.status_code in [200, 404]:  # 404 is ok, means service is running
            print(f"✅ {name:20} - RUNNING")
            return True
        else:
            print(f"⚠️  {name:20} - UNEXPECTED STATUS: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:20} - NOT RUNNING")
        return False
    except Exception as e:
        print(f"❌ {name:20} - ERROR: {str(e)[:50]}")
        return False

def test_hearing_user_endpoint():
    """Test the hearing user endpoint specifically"""
    try:
        response = requests.post(
            "http://localhost:8000/hearing-user/process",
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "text": "hello",
                "source_language": "en",
                "target_language": "hi"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "signs" in data and len(data["signs"]) > 0:
                print(f"✅ Hearing User Endpoint - WORKING (detected signs: {data['signs']})")
                return True
            else:
                print(f"⚠️  Hearing User Endpoint - WORKING but no signs detected")
                return True
        else:
            print(f"❌ Hearing User Endpoint - FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Hearing User Endpoint - ERROR: {str(e)[:50]}")
        return False

def main():
    print("=" * 60)
    print("🚀 SunoSaathi Service Health Check")
    print("=" * 60)
    print()
    
    results = {}
    
    # Test all services
    for name, url in SERVICES.items():
        results[name] = test_service(name, url)
    
    print()
    print("-" * 60)
    print("Testing Critical Endpoints:")
    print("-" * 60)
    
    # Test hearing user endpoint
    results["Hearing User Endpoint"] = test_hearing_user_endpoint()
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Services Running: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL SERVICES READY FOR DEMO!")
    elif passed >= total - 1:
        print("⚠️  MOSTLY READY - Check failed services")
    else:
        print("❌ CRITICAL ISSUES - Multiple services down")
    
    print()
    print("Next Steps:")
    if passed < total:
        print("1. Start missing services (see backend/SETUP.md)")
        print("2. Run this test again")
    else:
        print("1. Start frontend: cd frontend && npm run dev")
        print("2. Open http://localhost:5173")
        print("3. Test both user interfaces")
    
    print()

if __name__ == "__main__":
    main()
