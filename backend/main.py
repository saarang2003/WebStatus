from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta

from model import (
    Status, StatusHistory, UptimeAnalytics, ResponseTimeAnalytics, 
    HourlyTrend, WebsiteSummary, AnalyticsData, StatusCheckRequest
)
from database import (
    fetch_one_status, fetch_all_statuses, create_status, update_status, remove_status,
    get_status_history, get_uptime_analytics, get_response_time_analytics,
    get_hourly_status_trend, get_all_websites_summary, initialize_database,
    log_status_history
)

app = FastAPI(
    title="Website Status Monitor API",
    description="Enhanced API for website monitoring with analytics and logging",
    version="2.0.0"
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    await initialize_database()
    print("Database initialized with proper indexes")

@app.get("/")
async def read_root():
    return {
        "message": "Website Status Monitor API v2.0",
        "features": [
            "Real-time status monitoring",
            "Historical analytics",
            "Uptime tracking",
            "Response time metrics",
            "Email alerts",
            "Trend analysis"
        ]
    }

# Original status endpoints
@app.get("/api/status", response_model=List[Status])
async def get_all_statuses():
    """Get all website statuses"""
    response = await fetch_all_statuses()
    return response

@app.get("/api/status/{name}", response_model=Status)
async def get_status_by_name(name: str):
    """Get status for a specific website"""
    response = await fetch_one_status(name)
    if response:
        return response
    raise HTTPException(404, f"No website found with name: {name}")

@app.post("/api/status", response_model=Status)
async def create_new_status(status: Status):
    """Add a new website to monitor"""
    # Check if website already exists
    existing = await fetch_one_status(status.name)
    if existing:
        raise HTTPException(400, f"Website with name '{status.name}' already exists")
    
    response = await create_status(status.dict())
    if response:
        return response
    raise HTTPException(400, "Failed to create website status")

@app.put("/api/status/{name}", response_model=Status)
async def update_website_status(name: str, status: str):
    """Update status for a specific website"""
    response = await update_status(name, status)
    if response:
        return response
    raise HTTPException(404, f"No website found with name: {name}")

@app.delete("/api/status/{name}")
async def delete_website(name: str):
    """Delete a website from monitoring"""
    response = await remove_status(name)
    if response:
        return {"message": f"Successfully deleted website: {name}"}
    raise HTTPException(404, f"No website found with name: {name}")

# New analytics endpoints
@app.get("/api/analytics/summary", response_model=List[WebsiteSummary])
async def get_websites_summary():
    """Get summary analytics for all websites"""
    summary = await get_all_websites_summary()
    return summary

@app.get("/api/analytics/{name}/uptime", response_model=UptimeAnalytics)
async def get_website_uptime(
    name: str, 
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze (1-168)")
):
    """Get uptime analytics for a specific website"""
    # Verify website exists
    website = await fetch_one_status(name)
    if not website:
        raise HTTPException(404, f"No website found with name: {name}")
    
    analytics = await get_uptime_analytics(name, hours)
    return analytics

@app.get("/api/analytics/{name}/response-time", response_model=ResponseTimeAnalytics)
async def get_website_response_time(
    name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze (1-168)")
):
    """Get response time analytics for a specific website"""
    # Verify website exists
    website = await fetch_one_status(name)
    if not website:
        raise HTTPException(404, f"No website found with name: {name}")
    
    analytics = await get_response_time_analytics(name, hours)
    return analytics

@app.get("/api/analytics/{name}/trends", response_model=List[HourlyTrend])
async def get_website_trends(
    name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze (1-168)")
):
    """Get hourly status trends for charts"""
    # Verify website exists
    website = await fetch_one_status(name)
    if not website:
        raise HTTPException(404, f"No website found with name: {name}")
    
    trends = await get_hourly_status_trend(name, hours)
    return trends

@app.get("/api/analytics/{name}/history", response_model=List[StatusHistory])
async def get_website_history(
    name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history to fetch"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records")
):
    """Get detailed status history for a website"""
    # Verify website exists
    website = await fetch_one_status(name)
    if not website:
        raise HTTPException(404, f"No website found with name: {name}")
    
    history = await get_status_history(name, hours, limit)
    return history

@app.get("/api/analytics/{name}/complete", response_model=AnalyticsData)
async def get_complete_analytics(
    name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """Get complete analytics data for a website"""
    # Verify website exists
    website = await fetch_one_status(name)
    if not website:
        raise HTTPException(404, f"No website found with name: {name}")
    
    # Fetch all analytics data
    uptime_analytics = await get_uptime_analytics(name, hours)
    response_time_analytics = await get_response_time_analytics(name, hours)
    hourly_trends = await get_hourly_status_trend(name, hours)
    history = await get_status_history(name, hours, 50)  # Limited history for complete view
    
    return AnalyticsData(
        name=name,
        uptime_analytics=UptimeAnalytics(**uptime_analytics),
        response_time_analytics=ResponseTimeAnalytics(**response_time_analytics),
        hourly_trends=[HourlyTrend(**trend) for trend in hourly_trends],
        history=[StatusHistory(**record) for record in history]
    )

# Health and monitoring endpoints
@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0"
    }

@app.get("/api/stats")
async def get_api_stats():
    """Get general API statistics"""
    try:
        from database import collection, history_collection
        
        total_websites = await collection.count_documents({})
        total_checks = await history_collection.count_documents({})
        
        # Get websites by status
        up_websites = await collection.count_documents({"status": "UP"})
        down_websites = await collection.count_documents({"status": "Down"})
        
        # Get recent activity (last 24 hours)
        since_24h = datetime.utcnow() - timedelta(hours=24)
        recent_checks = await history_collection.count_documents({
            "checked_at": {"$gte": since_24h}
        })
        
        return {
            "total_websites": total_websites,
            "websites_up": up_websites,
            "websites_down": down_websites,
            "total_checks_all_time": total_checks,
            "checks_last_24h": recent_checks,
            "last_updated": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(500, f"Error fetching stats: {str(e)}")

# Batch operations
@app.post("/api/batch/check")
async def trigger_batch_check(background_tasks: BackgroundTasks):
    """Manually trigger a check of all websites"""
    try:
        from status_checker import check_all_websites
        background_tasks.add_task(check_all_websites)
        return {"message": "Batch check initiated", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(500, f"Error initiating batch check: {str(e)}")

@app.get("/api/websites/down")
async def get_down_websites():
    """Get all websites that are currently down"""
    try:
        from database import collection
        cursor = collection.find({"status": "Down"})
        down_websites = []
        async for doc in cursor:
            down_websites.append({
                "name": doc["name"],
                "url": doc["url"],
                "status": doc["status"],
                "last_updated": doc.get("last_updated")
            })
        return down_websites
    except Exception as e:
        raise HTTPException(500, f"Error fetching down websites: {str(e)}")

@app.get("/api/websites/up")
async def get_up_websites():
    """Get all websites that are currently up"""
    try:
        from database import collection
        cursor = collection.find({"status": "UP"})
        up_websites = []
        async for doc in cursor:
            up_websites.append({
                "name": doc["name"],
                "url": doc["url"],
                "status": doc["status"],
                "last_updated": doc.get("last_updated")
            })
        return up_websites
    except Exception as e:
        raise HTTPException(500, f"Error fetching up websites: {str(e)}")

# Advanced analytics endpoints
@app.get("/api/analytics/global/uptime")
async def get_global_uptime_stats(
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """Get global uptime statistics across all websites"""
    try:
        websites = await fetch_all_statuses()
        if not websites:
            return {"message": "No websites found"}
        
        total_uptime = 0
        website_count = 0
        detailed_stats = []
        
        for website in websites:
            uptime_data = await get_uptime_analytics(website["name"], hours)
            if uptime_data["total_checks"] > 0:
                total_uptime += uptime_data["uptime_percentage"]
                website_count += 1
                detailed_stats.append({
                    "name": website["name"],
                    "uptime_percentage": uptime_data["uptime_percentage"],
                    "total_checks": uptime_data["total_checks"]
                })
        
        average_uptime = total_uptime / website_count if website_count > 0 else 0
        
        return {
            "average_uptime_percentage": round(average_uptime, 2),
            "total_websites": len(websites),
            "websites_with_data": website_count,
            "period_hours": hours,
            "detailed_stats": detailed_stats
        }
    except Exception as e:
        raise HTTPException(500, f"Error calculating global uptime: {str(e)}")

@app.get("/api/analytics/alerts/recent")
async def get_recent_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(50, ge=1, le=200, description="Maximum alerts to return")
):
    """Get recent status change alerts"""
    try:
        from database import history_collection
        since = datetime.utcnow() - timedelta(hours=hours)
        
        cursor = history_collection.find({
            "event_type": "status_change",
            "changed_at": {"$gte": since}
        }).sort("changed_at", -1).limit(limit)
        
        alerts = []
        async for doc in cursor:
            alerts.append({
                "name": doc["name"],
                "old_status": doc["old_status"],
                "new_status": doc["new_status"],
                "changed_at": doc["changed_at"],
                "alert_type": "improvement" if doc["new_status"] == "UP" else "degradation"
            })
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(500, f"Error fetching recent alerts: {str(e)}")

# Export endpoints
@app.get("/api/export/{name}/csv")
async def export_website_data_csv(
    name: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of data to export")
):
    """Export website data as CSV"""
    try:
        from fastapi.responses import StreamingResponse
        import io
        import csv
        
        # Verify website exists
        website = await fetch_one_status(name)
        if not website:
            raise HTTPException(404, f"No website found with name: {name}")
        
        # Get history data
        history = await get_status_history(name, hours, 10000)  # Large limit for export
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["timestamp", "status", "response_time", "status_code"])
        
        # Write data
        for record in history:
            writer.writerow([
                record.get("checked_at", ""),
                record.get("status", ""),
                record.get("response_time", ""),
                record.get("status_code", "")
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={name}_status_data.csv"}
        )
    except Exception as e:
        raise HTTPException(500, f"Error exporting data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)