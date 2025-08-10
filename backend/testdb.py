from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

uri = "mongodb+srv://saranggp2018:f7LkNelqoejz0rWl@cluster0.rl03tpf.mongodb.net/webstatus?retryWrites=true&w=majority"

try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas!")
except ConnectionFailure as e:
    print(f"❌ Connection failed: {e}")
