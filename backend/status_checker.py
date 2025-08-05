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
from database import (
    log_status_history, 
    update_status, 
    get_websites_from_db,
    log_status_change
)

load_dotenv()

# Database setup
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status

# Email configuration (optional)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

def get_website_status_with_metrics(url: str) -> tuple:
    """Get website status with response time and status code"""
    try:
        start_time = time.time()
        response = requests.head(url, timeout=10, allow_redirects=True)
        response_time = time.time() - start_time
        
        status = 'UP' if response.status_code == HTTPStatus.OK else 'Down'
        return status, response_time, response.status_code
        
    except requests.exceptions.RequestException as e:
        response_time = time.time() - start_time if 'start_time' in locals() else None
        print(f"Error checking {url}: {e}")
        return 'Down', response_time, None

async def get_websites_from_db():
    """Get all websites from database"""
    try:
        websites = []
        cursor = collection.find({})
        async for doc in cursor:
            websites.append({
                'name': doc['name'], 
                'url': doc['url'],
                'current_status': doc.get('status', 'Unknown')
            })
        return websites
    except Exception as e:
        print(f"Error fetching websites from database: {e}")
        return []

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
    """Update website status and send alerts if status changed"""
    try:
        # Get current status before updating
        old_doc = await collection.find_one({"name": name})
        old_status = old_doc["status"] if old_doc else None
        
        # Update the status
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
        
        # Send email alert if status changed
        if old_status and old_status != status:
            print(f"Status change detected for {name}: {old_status} → {status}")
            await send_email_alert(name, url, old_status, status)
            await log_status_change(name, old_status, status)
        
        print(f"Updated {name}: {status} (Response: {response_time:.3f}s)")
        
    except Exception as e:
        print(f"Error updating {name}: {e}")

async def check_all_websites():
    """Check all websites and update their status with analytics"""
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
    
    await asyncio.gather(*tasks)
    print("Finished checking all websites")

async def check_single_website(site):
    """Check a single website"""
    try:
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

async def cleanup_old_history(days_to_keep: int = 30):
    """Clean up old history data to prevent database bloat"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        history_collection = database.status_history
        result = await history_collection.delete_many({
            "checked_at": {"$lt": cutoff_date}
        })
        
        print(f"Cleaned up {result.deleted_count} old history records")
    except Exception as e:
        print(f"Error cleaning up old history: {e}")

# Enhanced scheduler with different intervals
async def scheduler_loop():
    """Main scheduler loop with multiple check intervals"""
    print("Starting enhanced website status checker...")
    
    # Run initial check
    print("Running initial check...")
    await check_all_websites()
    
    # Schedule different tasks
    schedule.every(2).minutes.do(lambda: asyncio.create_task(check_all_websites()))
    schedule.every().day.at("02:00").do(lambda: asyncio.create_task(cleanup_old_history()))
    
    print("Scheduled tasks:")
    print("- Website checks: Every 2 minutes")
    print("- Cleanup old data: Daily at 2:00 AM")
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(30)  # Check every 30 seconds for pending tasks

# Alternative: Run checks at specific intervals without schedule library
async def continuous_monitoring():
    """Alternative monitoring approach with configurable intervals"""
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", "2")) * 60  # Convert to seconds
    CLEANUP_INTERVAL = 24 * 3600  # 24 hours in seconds
    
    last_cleanup = time.time()
    
    print(f"Starting continuous monitoring (check every {CHECK_INTERVAL//60} minutes)")
    
    while True:
        try:
            # Run website checks
            await check_all_websites()
            
            # Run cleanup if needed (once per day)
            current_time = time.time()
            if current_time - last_cleanup >= CLEANUP_INTERVAL:
                await cleanup_old_history()
                last_cleanup = current_time
            
            # Wait for next check
            await asyncio.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    print("Website Status Checker with Analytics")
    print("=====================================")
    
    # Choose monitoring method
    monitoring_method = os.getenv("MONITORING_METHOD", "continuous")  # or "schedule"
    
    try:
        if monitoring_method == "schedule":
            asyncio.run(scheduler_loop())
        else:
            asyncio.run(continuous_monitoring())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Restarting in 10 seconds...")
        time.sleep(10)