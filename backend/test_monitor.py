# test_monitor.py - Test the simple website monitor
import requests
import json

BASE_URL = "http://localhost:8000"

def test_website_check(domain):
    """Test checking a website"""
    print(f"\n🔍 Checking {domain}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/check/{domain}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"⏱️  Response Time: {data['response_time']}s")
            print(f"📊 Traffic Info: {data['traffic_info']}")
            print(f"🔢 Status Code: {data['status_code']}")
            print(f"🕐 Checked At: {data['timestamp']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_multiple_websites():
    """Test multiple websites at once"""
    test_sites = [
        "google.com",
        "github.com", 
        "example.com",
        "httpstat.us/200",  # Always returns 200
        "httpstat.us/500",  # Always returns 500
        "thisdomaindoesnotexist12345.com"  # Should fail
    ]
    
    print("🧪 Testing multiple websites...")
    for site in test_sites:
        test_website_check(site)
    
    # Get all recent checks
    print(f"\n📋 Recent checks:")
    try:
        response = requests.get(f"{BASE_URL}/api/recent")
        if response.status_code == 200:
            recent = response.json()
            for check in recent:
                status_emoji = "🟢" if check['status'] == "UP" else "🔴"
                print(f"  {status_emoji} {check['url']} - {check['status']} ({check['response_time']}s)")
    except Exception as e:
        print(f"Error getting recent checks: {e}")

if __name__ == "__main__":
    print("🚀 Simple Website Monitor Tester")
    print("=" * 40)
    
    # Test if API is running
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ API is running!")
            test_multiple_websites()
        else:
            print("❌ API not responding correctly")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure to run: python main.py")