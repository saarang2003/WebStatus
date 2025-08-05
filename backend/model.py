from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Status(BaseModel):
    name: str
    url: str
    status: str = "Checking"
    last_updated: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Google",
                "url": "https://google.com",
                "status": "UP",
                "last_updated": "2025-08-05T12:34:56Z"
            }
        }

class StatusHistory(BaseModel):
    name: str
    url: str
    status: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    checked_at: datetime
    event_type: Optional[str] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_at: Optional[datetime] = None

class UptimeAnalytics(BaseModel):
    uptime_percentage: float
    total_checks: int
    up_checks: int
    down_checks: int

class ResponseTimeAnalytics(BaseModel):
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    total_measurements: int

class HourlyTrend(BaseModel):
    hour: str
    total_checks: int
    up_count: int
    down_count: int
    uptime_percentage: float

class WebsiteSummary(BaseModel):
    name: str
    url: str
    current_status: str
    last_updated: Optional[datetime] = None
    uptime_24h: float
    avg_response_time: float
    total_checks_24h: int

class AnalyticsData(BaseModel):
    name: str
    uptime_analytics: UptimeAnalytics
    response_time_analytics: ResponseTimeAnalytics
    hourly_trends: List[HourlyTrend]
    history: List[StatusHistory]

class StatusCheckRequest(BaseModel):
    hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week
    limit: int = Field(default=100, ge=1, le=1000)

class EmailAlert(BaseModel):
    name: str
    old_status: str
    new_status: str
    timestamp: datetime
    url: str