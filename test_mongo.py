from pymongo import MongoClient
import sys

# Load your connection string from .env
from backend.config import settings

try:
    print("Attempting to connect to MongoDB...")
    print(f"URI: {settings.mongodb_uri[:30]}...")  # Don't print full URI (has password)
    
    client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # List databases
    dbs = client.list_database_names()
    print(f"📁 Available databases: {dbs}")
    
    # Test our database
    db = client[settings.mongodb_database]
    print(f"📊 Using database: {db.name}")
    
    client.close()
    print("\n🎉 Everything is working!")
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nPossible issues:")
    print("1. Check your MONGODB_URI in .env file")
    print("2. Check your username/password are correct")
    print("3. Check your IP is whitelisted in MongoDB Atlas")
    print("4. Check your internet connection")
    sys.exit(1)