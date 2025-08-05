import motor.motor_asyncio
from model import Status, StatusHistory, AnalyticsData
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DB_URL", "mongodb://localhost:27017")

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
database = client.StatusList
collection = database.status
history_collection = database.status_history
analytics_collection = database.analytics

def fix_mongo_id(document):
    """Convert ObjectId to string in a MongoDB document"""
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document

# Original status functions
async def fetch_all_statuses():
    statuses = []
    cursor = collection.find({})
    async for document in cursor:
        statuses.append(fix_mongo_id(document))
    return statuses

async def fetch_one_status(name):
    document = await collection.find_one({"name": name})
    return fix_mongo_id(document) if document else None

async def create_status(status_data):
    result = await collection.insert_one(status_data)
    new_status = await collection.find_one({"_id": result.inserted_id})
    return fix_mongo_id(new_status)

async def update_status(name: str, status: str):
    try:
        # Get old status for comparison
        old_doc = await collection.find_one({"name": name})
        old_status = old_doc["status"] if old_doc else None
        
        result = await collection.update_one(
            {"name": name}, 
            {"$set": {"status": status, "last_updated": datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            document = await collection.find_one({"name": name})
            
            # Log status change if different
            if old_status != status:
                await log_status_change(name, old_status, status)
            
            return fix_mongo_id(document)
        return None
    except Exception as e:
        print(f"Error updating status: {e}")
        return None

async def remove_status(name: str):
    try:
        result = await collection.delete_one({"name": name})
        if result.deleted_count > 0:
            # Clean up history for this website
            await history_collection.delete_many({"name": name})
            await analytics_collection.delete_many({"name": name})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing status: {e}")
        return False

# New analytics and logging functions
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

async def get_status_history(name: str, hours: int = 24, limit: int = 100):
    """Get status history for a website"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        cursor = history_collection.find({
            "name": name,
            "checked_at": {"$gte": since}
        }).sort("checked_at", -1).limit(limit)
        
        history = []
        async for document in cursor:
            history.append(fix_mongo_id(document))
        return history
    except Exception as e:
        print(f"Error fetching status history: {e}")
        return []

async def get_uptime_analytics(name: str, hours: int = 24):
    """Calculate uptime statistics for a website"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Count total checks and UP status
        total_checks = await history_collection.count_documents({
            "name": name,
            "checked_at": {"$gte": since},
            "status": {"$exists": True}
        })
        
        up_checks = await history_collection.count_documents({
            "name": name,
            "checked_at": {"$gte": since},
            "status": "UP"
        })
        
        if total_checks == 0:
            return {"uptime_percentage": 0, "total_checks": 0, "up_checks": 0, "down_checks": 0}
        
        uptime_percentage = (up_checks / total_checks) * 100
        down_checks = total_checks - up_checks
        
        return {
            "uptime_percentage": round(uptime_percentage, 2),
            "total_checks": total_checks,
            "up_checks": up_checks,
            "down_checks": down_checks
        }
    except Exception as e:
        print(f"Error calculating uptime analytics: {e}")
        return {"uptime_percentage": 0, "total_checks": 0, "up_checks": 0, "down_checks": 0}

async def get_response_time_analytics(name: str, hours: int = 24):
    """Get response time analytics for a website"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {
                "$match": {
                    "name": name,
                    "checked_at": {"$gte": since},
                    "response_time": {"$exists": True, "$ne": None}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_response_time": {"$avg": "$response_time"},
                    "min_response_time": {"$min": "$response_time"},
                    "max_response_time": {"$max": "$response_time"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        result = await history_collection.aggregate(pipeline).to_list(length=1)
        
        if result:
            data = result[0]
            return {
                "avg_response_time": round(data["avg_response_time"], 3) if data["avg_response_time"] else 0,
                "min_response_time": round(data["min_response_time"], 3) if data["min_response_time"] else 0,
                "max_response_time": round(data["max_response_time"], 3) if data["max_response_time"] else 0,
                "total_measurements": data["count"]
            }
        
        return {"avg_response_time": 0, "min_response_time": 0, "max_response_time": 0, "total_measurements": 0}
    except Exception as e:
        print(f"Error calculating response time analytics: {e}")
        return {"avg_response_time": 0, "min_response_time": 0, "max_response_time": 0, "total_measurements": 0}

async def get_hourly_status_trend(name: str, hours: int = 24):
    """Get hourly status trends for charts"""
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {
                "$match": {
                    "name": name,
                    "checked_at": {"$gte": since},
                    "status": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "hour": {"$dateToString": {"format": "%Y-%m-%d %H:00", "date": "$checked_at"}},
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$group": {
                    "_id": "$_id.hour",
                    "statuses": {
                        "$push": {
                            "status": "$_id.status",
                            "count": "$count"
                        }
                    },
                    "total_checks": {"$sum": "$count"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        result = await history_collection.aggregate(pipeline).to_list(length=None)
        
        trend_data = []
        for item in result:
            hour_data = {"hour": item["_id"], "total_checks": item["total_checks"]}
            
            # Initialize status counts
            up_count = 0
            down_count = 0
            
            for status_info in item["statuses"]:
                if status_info["status"] == "UP":
                    up_count = status_info["count"]
                elif status_info["status"] == "Down":
                    down_count = status_info["count"]
            
            hour_data["up_count"] = up_count
            hour_data["down_count"] = down_count
            hour_data["uptime_percentage"] = (up_count / item["total_checks"]) * 100 if item["total_checks"] > 0 else 0
            
            trend_data.append(hour_data)
        
        return trend_data
    except Exception as e:
        print(f"Error getting hourly trend: {e}")
        return []

async def get_all_websites_summary():
    """Get summary analytics for all websites"""
    try:
        websites = await fetch_all_statuses()
        summary = []
        
        for website in websites:
            name = website["name"]
            uptime_data = await get_uptime_analytics(name, 24)
            response_time_data = await get_response_time_analytics(name, 24)
            
            summary.append({
                "name": name,
                "url": website["url"],
                "current_status": website["status"],
                "last_updated": website.get("last_updated"),
                "uptime_24h": uptime_data["uptime_percentage"],
                "avg_response_time": response_time_data["avg_response_time"],
                "total_checks_24h": uptime_data["total_checks"]
            })
        
        return summary
    except Exception as e:
        print(f"Error getting websites summary: {e}")
        return []

# Database indexes for better performance
async def create_indexes():
    """Create database indexes for better query performance"""
    try:
        # Index for history collection
        await history_collection.create_index([("name", 1), ("checked_at", -1)])
        await history_collection.create_index([("name", 1), ("status", 1), ("checked_at", -1)])
        
        # Index for main collection
        await collection.create_index([("name", 1)])
        
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

# Call this when starting the application
async def initialize_database():
    """Initialize database with indexes"""
    await create_indexes()