from pydantic import BaseModel, HttpUrl
from typing import Optional

class Status(BaseModel):
    name: str
    url: str
    status: str = "Checking"
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Google",
                "url": "https://google.com",
                "status": "UP"
            }
        }
