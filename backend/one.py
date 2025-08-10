# main.py - Simple Website Monitor API
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time
from typing import Dict, List
import asyncio

app = FastAPI(title="Simple Website Monitor", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class WebsiteCheck(BaseModel):
    url: str

class WebsiteStatus(BaseModel):
    url: str
    status: str  # "UP" or "DOWN"
    response_time: float  # in seconds
    status_code: int = None
    traffic_info: str  # Simple traffic description
    timestamp: str

# In-memory storage (no database for now)
website_cache: Dict[str, WebsiteStatus] = {}

def check_website(url: str) -> WebsiteStatus:
    """Check a website and return its status with metrics"""
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    start_time = time.time()
    
    try:
        # Make request with timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Website Monitor Bot)'
        }
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        response_time = time.time() - start_time
        
        # Determine status
        if 200 <= response.status_code < 400:
            status = "UP"
        else:
            status = "DOWN"
        
        # Simple traffic estimation based on response time
        if response_time < 0.5:
            traffic_info = "Fast (Low traffic or good server)"
        elif response_time < 2.0:
            traffic_info = "Normal (Moderate traffic)"
        elif response_time < 5.0:
            traffic_info = "Slow (High traffic or slow server)"
        else:
            traffic_info = "Very Slow (Heavy traffic or server issues)"
        
        return WebsiteStatus(
            url=url,
            status=status,
            response_time=round(response_time, 3),
            status_code=response.status_code,
            traffic_info=traffic_info,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        )
        
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        return WebsiteStatus(
            url=url,
            status="DOWN",
            response_time=round(response_time, 3),
            status_code=None,
            traffic_info="Timeout (Server not responding)",
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        )
        
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        return WebsiteStatus(
            url=url,
            status="DOWN",
            response_time=round(response_time, 3),
            status_code=None,
            traffic_info="Connection Failed (Server unreachable)",
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        )
        
    except Exception as e:
        response_time = time.time() - start_time
        return WebsiteStatus(
            url=url,
            status="DOWN",
            response_time=round(response_time, 3),
            status_code=None,
            traffic_info=f"Error: {str(e)[:50]}",
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        )

@app.get("/")
def read_root():
    return {
        "message": "Simple Website Monitor API",
        "features": [
            "Check if website is UP or DOWN",
            "Measure response time",
            "Estimate traffic/load based on response time"
        ]
    }

@app.post("/api/check")
def check_website_status(website: WebsiteCheck):
    """Check a website and return its status, response time, and traffic info"""
    try:
        result = check_website(website.url)
        
        # Cache the result
        website_cache[website.url] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking website: {str(e)}")

@app.get("/api/check/{domain}")
def check_website_by_domain(domain: str):
    """Check a website by domain name"""
    try:
        result = check_website(domain)
        
        # Cache the result
        website_cache[domain] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking website: {str(e)}")

@app.get("/api/recent")
def get_recent_checks():
    """Get all recently checked websites"""
    return list(website_cache.values())

@app.delete("/api/cache")
def clear_cache():
    """Clear the cache of checked websites"""
    global website_cache
    website_cache = {}
    return {"message": "Cache cleared"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Website Monitor...")
    print("📊 Features: Status Check | Response Time | Traffic Estimation")
    print("🌐 Access at: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)