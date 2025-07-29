# status_checker.py (Background monitoring script)
import schedule
import time
import requests
from http import HTTPStatus
import motor.motor_asyncio
from model import Status
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status

def get_website_status(url: str) -> str:
    """Check the status of a website"""
    try:
        # Add timeout to prevent hanging
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == HTTPStatus.OK:
            return 'UP'
        else:
            return 'Down'
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
        return 'Down'
    except Exception as e:
        print(f"Unexpected error checking {url}: {e}")
        return 'Down'

async def get_websites_from_db():
    """Fetch all websites from database"""
    try:
        websites = []
        cursor = collection.find({})
        async for document in cursor:
            websites.append({
                'name': document['name'],
                'url': document['url']
            })
        return websites
    except Exception as e:
        print(f"Error fetching websites from database: {e}")
        return []

async def update_website_status(name: str, status: str):
    """Update website status in database"""
    try:
        await collection.update_one(
            {"name": name}, 
            {"$set": {"status": status}}
        )
        print(f"Updated {name}: {status}")
    except Exception as e:
        print(f"Error updating {name}: {e}")

async def check_all_websites():
    """Check status of all websites and update database"""
    websites = await get_websites_from_db()
    
    if not websites:
        print("No websites to check")
        return
    
    print(f"Checking {len(websites)} websites...")
    
    for website in websites:
        name = website['name']
        url = website['url']
        
        print(f"Checking {name} ({url})...")
        status = get_website_status(url)
        await update_website_status(name, status)
    
    print("Finished checking all websites")

def run_async_check():
    """Wrapper to run async function in sync context"""
    asyncio.run(check_all_websites())

# Schedule the job to run every 5 minutes
schedule.every(5).minutes.do(run_async_check)

# Run initial check
print("Starting website status checker...")
print("Running initial check...")
run_async_check()

print("Scheduling checks every 5 minutes...")
while True:
    schedule.run_pending()
    time.sleep(1)