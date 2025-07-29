import asyncio
import schedule
import time
import requests
from http import HTTPStatus
import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status

def get_website_status(url: str) -> str:
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return 'UP' if response.status_code == HTTPStatus.OK else 'Down'
    except requests.exceptions.RequestException:
        return 'Down'

async def get_websites_from_db():
    try:
        websites = []
        cursor = collection.find({})
        async for doc in cursor:
            websites.append({'name': doc['name'], 'url': doc['url']})
        return websites
    except Exception as e:
        print(f"Error fetching websites from database: {e}")
        return []

async def update_website_status(name: str, status: str):
    try:
        await collection.update_one({"name": name}, {"$set": {"status": status}})
        print(f"Updated {name}: {status}")
    except Exception as e:
        print(f"Error updating {name}: {e}")

async def check_all_websites():
    websites = await get_websites_from_db()
    if not websites:
        print("No websites to check")
        return

    print(f"Checking {len(websites)} websites...")
    for site in websites:
        status = get_website_status(site['url'])
        await update_website_status(site['name'], status)
    print("Finished checking all websites")

# Main loop using a persistent asyncio event loop
async def scheduler_loop():
    print("Starting website status checker...")
    print("Running initial check...")
    await check_all_websites()

    schedule.every(5).minutes.do(lambda: asyncio.create_task(check_all_websites()))
    print("Scheduling checks every 5 minutes...")

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(scheduler_loop())
    except KeyboardInterrupt:
        print("Shutting down.")
