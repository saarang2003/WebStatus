from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
from urllib.parse import urlparse
import requests
import time
import ssl
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Website Monitor", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# ---------- Data Models ----------

class Website(BaseModel):
    name: str
    url: str

class WebsiteStatus(BaseModel):
    name: str
    url: str
    status: str  # "UP" or "DOWN"
    response_time: float
    status_code: int = Field(default=0)
    traffic_info: str
    last_checked: str
    ssl_expiry_days: Optional[int] = Field(default=None, description="Days until SSL certificate expires")
    ssl_status: Optional[str] = Field(default=None, description="SSL certificate status")

# ---------- In-Memory Storage ----------
websites: Dict[str, WebsiteStatus] = {}

# ---------- Utility Functions ----------

def extract_hostname(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        return parsed.hostname
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return None

def check_website_status(url: str) -> tuple:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    start = time.time()
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Website Monitor)"},
            allow_redirects=True
        )
        response_time = time.time() - start
        status_code = int(response.status_code or 0)
        status = "UP" if 200 <= status_code < 400 else "DOWN"
        return status, response_time, status_code
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return "DOWN", time.time() - start, 0

def get_traffic_info(response_time: float, status: str) -> str:
    if status == "DOWN":
        return "Server Down or Unreachable"
    if response_time < 0.5:
        return "Fast Response (Low Traffic)"
    if response_time < 1.5:
        return "Good Response (Normal Traffic)"
    if response_time < 3.0:
        return "Slow Response (High Traffic)"
    return "Very Slow (Heavy Traffic or Server Issues)"

def get_ssl_expiry_days(hostname: str) -> Optional[int]:
    if not hostname:
        return None
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
        
        if not cert or "notAfter" not in cert:
            print(f"[SSL] No certificate found for {hostname}")
            return None
            
        expiry = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        days_left = (expiry - datetime.utcnow()).days
        print(f"[SSL] {hostname} SSL expires in {days_left} days")
        return days_left
    except Exception as e:
        print(f"[SSL ERROR] {hostname}: {e}")
        return None

# ---------- API Endpoints ----------

@app.get("/")
def read_root():
    return {
        "message": "Simple Website Monitor API",
        "endpoints": {
            "add_website": "POST /api/websites",
            "get_all": "GET /api/websites",
            "check_one": "GET /api/check/{name}",
            "delete": "DELETE /api/websites/{name}",
            "check_all": "POST /api/check-all",
            "stats": "GET /api/stats"
        }
    }

@app.post("/api/websites", response_model=WebsiteStatus)
def add_website(website: Website):
    if website.name in websites:
        raise HTTPException(400, f"Website '{website.name}' already exists")
    try:
        status, rt, code = check_website_status(website.url)
        traffic = get_traffic_info(rt, status)

        hostname = extract_hostname(website.url)
        ssl_days = None
        if hostname and website.url.startswith("https://"):
            ssl_days = get_ssl_expiry_days(hostname)

        ws = WebsiteStatus(
            name=website.name,
            url=website.url,
            status=status,
            response_time=round(rt, 3),
            status_code=code,
            traffic_info=traffic,
            last_checked=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ssl_expiry_days=ssl_days
        )
        websites[website.name] = ws
        print(f"[DEBUG] Added website: {ws.model_dump()}")  # Debug output
        return ws
    except Exception as e:
        print(f"Error adding website {website.name}: {e}")
        raise HTTPException(500, f"Failed to add website: {e}")

@app.get("/api/websites", response_model=List[WebsiteStatus])
def get_all_websites():
    result = list(websites.values())
    print(f"[DEBUG] Returning {len(result)} websites")  # Debug output
    for site in result:
        print(f"[DEBUG] Site: {site.name}, SSL Days: {site.ssl_expiry_days}")
    return result

@app.get("/api/check/{name}", response_model=WebsiteStatus)
def check_single_website(name: str):
    if name not in websites:
        raise HTTPException(404, f"Website '{name}' not found")
    try:
        current = websites[name]
        status, rt, code = check_website_status(current.url)
        traffic = get_traffic_info(rt, status)

        hostname = extract_hostname(current.url)
        ssl_days = None
        if hostname and current.url.startswith("https://"):
            ssl_days = get_ssl_expiry_days(hostname)

        current.status = status
        current.response_time = round(rt, 3)
        current.status_code = code
        current.traffic_info = traffic
        current.last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current.ssl_expiry_days = ssl_days

        print(f"[DEBUG] Updated website: {current.model_dump()}")  # Debug output
        return current
    except Exception as e:
        print(f"Error checking website {name}: {e}")
        raise HTTPException(500, f"Failed to check website: {e}")

@app.delete("/api/websites/{name}")
def delete_website(name: str):
    if name not in websites:
        raise HTTPException(404, f"Website '{name}' not found")
    del websites[name]
    return {"message": f"Website '{name}' deleted successfully"}

@app.post("/api/check-all")
def check_all_websites():
    results = []
    for name in list(websites):
        try:
            data = check_single_website(name)
            results.append({"name": name, "status": "success", "data": data})
        except Exception as e:
            results.append({"name": name, "status": "error", "error": str(e)})
    return {"message": f"Checked {len(websites)} websites", "results": results}

@app.get("/api/stats")
def get_stats():
    total = len(websites)
    up = sum(1 for w in websites.values() if w.status == "UP")
    down = total - up
    avg = (
        round(sum(w.response_time for w in websites.values() if w.status == "UP") / up, 3)
        if up > 0
        else 0
    )
    
    # SSL certificate stats
    ssl_expiring_soon = sum(1 for w in websites.values() if w.ssl_expiry_days is not None and w.ssl_expiry_days <= 30)
    ssl_expired = sum(1 for w in websites.values() if w.ssl_expiry_days is not None and w.ssl_expiry_days <= 0)
    
    return {
        "total_websites": total,
        "websites_up": up,
        "websites_down": down,
        "average_response_time": avg,
        "ssl_expiring_soon": ssl_expiring_soon,
        "ssl_expired": ssl_expired
    }

# ---------- Run App ----------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Website Monitor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)