# test_system.py - Test the complete website monitor system
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    """Test if backend is working"""
    print("🧪 Testing Backend API...")
    
    try:
        # Test health check
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend is running!")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Start backend with: python main.py")
        return False

def test_add_websites():
    """Test adding websites"""
    print("\n📝 Testing Add Websites...")
    
    test_sites = [
        {"name": "Google", "url": "google.com"},
        {"name": "GitHub", "url": "github.com"},
        {"name": "Example", "url": "example.com"},
        {"name": "Bad Site", "url": "thisdomaindoesnotexist12345.com"}
    ]
    
    for site in test_sites:
        try:
            response = requests.post(
                f"{BASE_URL}/api/websites",
                json=site
            )
            if response.status_code == 200:
                data = response.json()
                status_emoji = "🟢" if data['status'] == "UP" else "🔴"
                print(f"{status_emoji} {site['name']}: {data['status']} ({data['response_time']}s) - {data['traffic_info']}")
            else:
                print(f"❌ Failed to add {site['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error adding {site['name']}: {e}")

def test_get_all():
    """Test getting all websites"""
    print("\n📋 Current Websites:")
    
    try:
        response = requests.get(f"{BASE_URL}/api/websites")
        if response.status_code == 200:
            websites = response.json()
            if not websites:
                print("  No websites found")
                return
            
            print(f"  Found {len(websites)} websites:")
            for site in websites:
                status_emoji = "🟢" if site['status'] == "UP" else "🔴"
                print(f"  {status_emoji} {site['name']:<15} | {site['status']:<4} | {site['response_time']}s | {site['traffic_info']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing Stats...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"📈 Total: {stats['total_websites']}")
            print(f"🟢 Up: {stats['websites_up']}")
            print(f"🔴 Down: {stats['websites_down']}")
            print(f"⏱️  Avg Response: {stats['average_response_time']}s")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_recheck():
    """Test rechecking a website"""
    print("\n🔄 Testing Recheck...")
    
    try:
        # Get first website
        response = requests.get(f"{BASE_URL}/api/websites")
        if response.status_code == 200:
            websites = response.json()
            if websites:
                first_site = websites[0]['name']
                print(f"Rechecking {first_site}...")
                
                recheck_response = requests.get(f"{BASE_URL}/api/check/{first_site}")
                if recheck_response.status_code == 200:
                    data = recheck_response.json()
                    status_emoji = "🟢" if data['status'] == "UP" else "🔴"
                    print(f"  {status_emoji} {first_site}: {data['status']} ({data['response_time']}s)")
                    print(f"  📊 {data['traffic_info']}")
                else:
                    print(f"❌ Recheck failed: {recheck_response.status_code}")
            else:
                print("  No websites to recheck")
    except Exception as e:
        print(f"❌ Error: {e}")

def run_complete_test():
    """Run complete system test"""
    print("🚀 Complete Website Monitor System Test")
    print("=" * 50)
    
    # Test backend
    if not test_backend():
        return
    
    # Clear any existing data first
    try:
        response = requests.get(f"{BASE_URL}/api/websites")
        if response.status_code == 200:
            existing = response.json()
            for site in existing:
                requests.delete(f"{BASE_URL}/api/websites/{site['name']}")
            print("🧹 Cleared existing test data")
    except:
        pass
    
    # Run tests
    test_add_websites()
    test_get_all()
    test_stats()
    test_recheck()
    
    print("\n✨ Test Complete!")
    print("💡 Frontend URL: http://localhost:3000 (if running React)")
    print("📖 Backend Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    run_complete_test()