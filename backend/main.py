# main.py - Simple Website Monitor Backend (Fixed)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI(title="Simple Website Monitor", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class Website(BaseModel):
    name: str
    url: str

class WebsiteStatus(BaseModel):
    name: str
    url: str
    status: str  # "UP" or "DOWN"
    response_time: float  # in seconds
    status_code: int = Field(default=0)  # 0 = unreachable, with explicit default
    traffic_info: str
    last_checked: str

# In-memory storage
websites: Dict[str, WebsiteStatus] = {}

def check_website_status(url: str) -> tuple:
    """Check website and return status, response_time, status_code"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    start_time = time.time()
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Website Monitor)'}
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        response_time = time.time() - start_time
        status_code = response.status_code
        status = "UP" if 200 <= response.status_code < 400 else "DOWN"
        
        # Ensure status_code is always an integer
        status_code = int(status_code) if status_code is not None else 0
        print(f"SUCCESS: {url} -> status_code: {status_code}, type: {type(status_code)}")
        return status, response_time, status_code
        
    except requests.exceptions.Timeout:
        print(f"Timeout checking {url}")
        response_time = time.time() - start_time
        return "DOWN", response_time, 0
        
    except requests.exceptions.ConnectionError:
        print(f"Connection error checking {url}")
        response_time = time.time() - start_time
        return "DOWN", response_time, 0
        
    except requests.exceptions.RequestException as e:
        print(f"Request error checking {url}: {e}")
        response_time = time.time() - start_time
        return "DOWN", response_time, 0
        
    except Exception as e:
        print(f"Unexpected error checking {url}: {e}")
        response_time = time.time() - start_time
        return "DOWN", response_time, 0
def get_traffic_info(response_time: float, status: str) -> str:
    """Estimate traffic/load based on response time"""
    if status == "DOWN":
        return "Server Down or Unreachable"
    if response_time < 0.5:
        return "Fast Response (Low Traffic)"
    elif response_time < 1.5:
        return "Good Response (Normal Traffic)"
    elif response_time < 3.0:
        return "Slow Response (High Traffic)"
    else:
        return "Very Slow (Heavy Traffic or Server Issues)"

@app.get("/")
def read_root():
    return {
        "message": "Simple Website Monitor API",
        "endpoints": {
            "add_website": "POST /api/websites",
            "get_all": "GET /api/websites", 
            "check_one": "GET /api/check/{name}",
            "delete": "DELETE /api/websites/{name}"
        }
    }

@app.post("/api/websites")
def add_website(website: Website):
    """Add a new website to monitor"""
    try:
        if website.name in websites:
            raise HTTPException(400, f"Website '{website.name}' already exists")

        # Immediately check
        status, response_time, status_code = check_website_status(website.url)
        traffic_info = get_traffic_info(response_time, status)

        # CRITICAL FIX: Ensure status_code is never None
        if status_code is None:
            status_code = 0
        
        website_status = WebsiteStatus(
            name=website.name,
            url=website.url,
            status=status,
            response_time=round(response_time, 3),
            status_code=int(status_code),  # Now guaranteed to be an integer
            traffic_info=traffic_info,
            last_checked=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        websites[website.name] = website_status
        return website_status
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding website {website.name}: {e}")
        raise HTTPException(500, f"Failed to add website: {str(e)}")


@app.get("/api/websites")
def get_all_websites():
    """Get all monitored websites"""
    return list(websites.values())

@app.get("/api/check/{name}")
def check_single_website(name: str):
    """Re-check a specific website"""
    try:
        if name not in websites:
            raise HTTPException(404, f"Website '{name}' not found")

        website = websites[name]
        status, response_time, status_code = check_website_status(website.url)
        traffic_info = get_traffic_info(response_time, status)

        # Update the website status with maximum safety
        safe_status_code = 0
        if status_code is not None:
            try:
                safe_status_code = int(status_code)
            except (ValueError, TypeError):
                safe_status_code = 0

        websites[name].status = status
        websites[name].response_time = round(response_time, 3)
        websites[name].status_code = safe_status_code
        websites[name].traffic_info = traffic_info
        websites[name].last_checked = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return websites[name]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error checking website {name}: {e}")
        raise HTTPException(500, f"Failed to check website: {str(e)}")

@app.delete("/api/websites/{name}")
def delete_website(name: str):
    """Delete a website"""
    if name not in websites:
        raise HTTPException(404, f"Website '{name}' not found")
    del websites[name]
    return {"message": f"Website '{name}' deleted successfully"}

@app.post("/api/check-all")
def check_all_websites():
    """Re-check all websites"""
    if not websites:
        return {"message": "No websites to check"}

    results = []
    for name in list(websites.keys()):
        try:
            updated_website = check_single_website(name)
            results.append({
                "name": name,
                "status": "success", 
                "data": updated_website
            })
        except Exception as e:
            print(f"Error checking {name}: {e}")
            results.append({
                "name": name,
                "status": "error",
                "error": str(e)
            })

    return {
        "message": f"Checked {len(websites)} websites",
        "results": results
    }

@app.get("/api/stats")
def get_stats():
    """Get statistics"""
    total = len(websites)
    up = sum(1 for w in websites.values() if w.status == "UP")
    down = total - up
    avg_response_time = 0
    
    if websites:
        up_websites = [w for w in websites.values() if w.status == "UP"]
        if up_websites:
            total_time = sum(w.response_time for w in up_websites)
            avg_response_time = round(total_time / len(up_websites), 3)

    return {
        "total_websites": total,
        "websites_up": up,
        "websites_down": down,
        "average_response_time": avg_response_time
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Website Monitor...")
    print("📊 Features: Status | Response Time | Traffic Estimation")
    print("🌐 Server: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)