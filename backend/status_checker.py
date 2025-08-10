import asyncio
import schedule
import time
import requests
from http import HTTPStatus
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import smtplib
from email.message import EmailMessage

load_dotenv()

# Database setup
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status
history_collection = database.status_history

# Email configuration (optional)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

def get_website_status_with_metrics(url: str) -> tuple:
    """Get website status with response time and status code - with proper error handling"""
    start_time = time.time()
    try:
        # Add timeout and proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Website Monitor Bot)'
        }
        response = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        response_time = time.time() - start_time
        
        # Consider 2xx and 3xx as UP, everything else as Down
        status = 'UP' if 200 <= response.status_code < 400 else 'Down'
        return status, response_time, response.status_code
        
    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time
        print(f"Error checking {url}: {e}")
        return 'Down', response_time, None

async def get_websites_from_db():
    """Get ALL websites from database - including ones with 'Checking' status"""
    try:
        websites = []
        # ✅ FIXED: Don't filter out any status - get ALL websites
        cursor = collection.find({})  # No filter to exclude "Checking"
        async for doc in cursor:
            websites.append({
                'name': doc['name'], 
                'url': doc['url'],
                'current_status': doc.get('status', 'Checking')
            })
        return websites
    except Exception as e:
        print(f"Error fetching websites from database: {e}")
        return []

async def log_status_history(name: str, url: str, status: str, response_time: float = None, status_code: int = None):
    """Log each status check with detailed information"""
    try:
        await history_collection.insert_one({
            "name": name,
            "url": url,
            "status": status,
            "response_time": response_time,
            "status_code": status_code,
            "checked_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error logging status history: {e}")

async def log_status_change(name: str, old_status: str, new_status: str):
    """Log when a website status changes"""
    try:
        await history_collection.insert_one({
            "name": name,
            "event_type": "status_change",
            "old_status": old_status,
            "new_status": new_status,
            "changed_at": datetime.utcnow()
        })
    except Exception as e:
        print(f"Error logging status change: {e}")

async def send_email_alert(name: str, url: str, old_status: str, new_status: str):
    """Send email alert when status changes"""
    if not all([EMAIL_ADDRESS, EMAIL_PASSWORD, ALERT_EMAIL]):
        print("Email configuration not complete, skipping email alert")
        return
    
    try:
        subject = f"🚨 Status Alert: {name} is {new_status}"
        body = f"""
Website Status Change Alert

Website: {name}
URL: {url}
Status Changed: {old_status} → {new_status}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

This is an automated alert from your website monitoring system.
        """
        
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = ALERT_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            
        print(f"Email alert sent for {name}: {old_status} → {new_status}")
    except Exception as e:
        print(f"Error sending email alert: {e}")

async def update_website_status_with_alerts(name: str, url: str, status: str, response_time: float, status_code: int):
    """✅ FIXED: Always update website status, even from 'Checking' state"""
    try:
        # Get current status before updating
        old_doc = await collection.find_one({"name": name})
        old_status = old_doc["status"] if old_doc else "Unknown"
        
        # ✅ FIXED: Always update the status with proper timestamp
        result = await collection.update_one(
            {"name": name}, 
            {"$set": {
                "status": status,
                "last_updated": datetime.utcnow(),
                "last_response_time": response_time,
                "last_status_code": status_code
            }}
        )
        
        # Log the status check
        await log_status_history(name, url, status, response_time, status_code)
        
        # Send email alert if status changed AND it's not the first check
        if old_status and old_status != "Checking" and old_status != status:
            print(f"Status change detected for {name}: {old_status} → {status}")
            await send_email_alert(name, url, old_status, status)
            await log_status_change(name, old_status, status)
        elif old_status == "Checking":
            print(f"Initial check complete for {name}: {status} (Response: {response_time:.3f}s)")
        else:
            print(f"Updated {name}: {status} (Response: {response_time:.3f}s)")
        
    except Exception as e:
        print(f"Error updating {name}: {e}")

async def check_all_websites():
    """✅ FIXED: Check ALL websites including those with 'Checking' status"""
    websites = await get_websites_from_db()
    if not websites:
        print("No websites to check")
        return

    print(f"Checking {len(websites)} websites...")
    
    # Check all websites concurrently for better performance
    tasks = []
    for site in websites:
        task = check_single_website(site)
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)
    print("Finished checking all websites")

async def check_single_website(site):
    """Check a single website with proper error handling"""
    try:
        print(f"Checking {site['name']} ({site['url']})...")
        status, response_time, status_code = get_website_status_with_metrics(site['url'])
        await update_website_status_with_alerts(
            site['name'], 
            site['url'], 
            status, 
            response_time, 
            status_code
        )
    except Exception as e:
        print(f"Error checking {site['name']}: {e}")
        # ✅ FIXED: Even on error, update status to Down
        try:
            await update_website_status_with_alerts(
                site['name'], 
                site['url'], 
                'Down', 
                None, 
                None
            )
        except Exception as inner_e:
            print(f"Error updating failed check for {site['name']}: {inner_e}")

async def cleanup_old_history(days_to_keep: int = 30):
    """Clean up old history data to prevent database bloat"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        result = await history_collection.delete_many({
            "checked_at": {"$lt": cutoff_date}
        })
        
        print(f"Cleaned up {result.deleted_count} old history records")
    except Exception as e:
        print(f"Error cleaning up old history: {e}")

# ✅ FIXED: Simple continuous monitoring without schedule library issues
async def continuous_monitoring():
    """Continuous monitoring approach with configurable intervals"""
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", "2")) * 60  # Convert to seconds
    CLEANUP_INTERVAL = 24 * 3600  # 24 hours in seconds
    
    last_cleanup = time.time()
    
    print(f"Starting continuous monitoring (check every {CHECK_INTERVAL//60} minutes)")
    
    # Run initial check immediately
    print("Running initial check...")
    await check_all_websites()
    
    while True:
        try:
            # Wait for next check
            await asyncio.sleep(CHECK_INTERVAL)
            
            # Run website checks
            await check_all_websites()
            
            # Run cleanup if needed (once per day)
            current_time = time.time()
            if current_time - last_cleanup >= CLEANUP_INTERVAL:
                await cleanup_old_history()
                last_cleanup = current_time
            
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
            break
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# ✅ FIXED: One-time check function for testing
async def run_single_check():
    """Run a single check of all websites (useful for testing)"""
    print("Running single check of all websites...")
    await check_all_websites()
    print("Single check complete!")

if __name__ == "__main__":
    print("Website Status Checker with Analytics")
    print("=====================================")
    
    # Choose what to run
    run_mode = os.getenv("RUN_MODE", "continuous")  # Options: continuous, single
    
    try:
        if run_mode == "single":
            # For testing - just run once and exit
            asyncio.run(run_single_check())
        else:
            # Default - continuous monitoring
            asyncio.run(continuous_monitoring())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Check your database connection and try again.")