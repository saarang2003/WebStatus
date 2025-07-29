import motor.motor_asyncio
from model import Status
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status

async def fetch_one_status(name: str):
    document = await collection.find_one({"name": name})
    return document

async def fetch_all_statuses():
    statuses = []
    cursor = collection.find({})
    async for document in cursor:
        statuses.append(document)
    return statuses

async def create_status(status_data: dict):
    try:
        result = await collection.insert_one(status_data)
        if result.inserted_id:
            return status_data
        return None
    except Exception as e:
        print(f"Error creating status: {e}")
        return None

async def update_status(name: str, status: str):
    try:
        result = await collection.update_one(
            {"name": name}, 
            {"$set": {"status": status}}
        )
        if result.modified_count > 0:
            document = await collection.find_one({"name": name})
            return document
        return None
    except Exception as e:
        print(f"Error updating status: {e}")
        return None

async def remove_status(name: str):
    try:
        result = await collection.delete_one({"name": name})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing status: {e}")
        return False