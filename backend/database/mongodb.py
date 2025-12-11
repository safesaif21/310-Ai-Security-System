"""MongoDB connection and database setup"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from backend.config import settings
from typing import Generator

# MongoDB client (singleton)
_mongo_client: MongoClient = None
_database: Database = None


def get_mongo_client() -> MongoClient:
    """Get or create MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
    return _mongo_client


def get_database() -> Database:
    """Get MongoDB database"""
    global _database
    if _database is None:
        client = get_mongo_client()
        _database = client[settings.mongodb_database]
    return _database


def get_db_mongo() -> Generator[Database, None, None]:
    """
    Dependency for FastAPI routes to get MongoDB database.
    Usage:
        @app.get("/items")
        def read_items(db: Database = Depends(get_db_mongo)):
            ...
    """
    db = get_database()
    try:
        yield db
    finally:
        # MongoDB connections are pooled, no need to close per request
        pass


def close_mongo_connection():
    """Close MongoDB connection (call on app shutdown)"""
    global _mongo_client, _database
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _database = None


def init_db_mongo():
    """Initialize MongoDB - create users collection and indexes"""
    db = get_database()
    
    # Users collection (only collection we're using)
    if "users" not in db.list_collection_names():
        db.create_collection("users")
    
    users: Collection = db.users
    users.create_index([("username", ASCENDING)], unique=True)
    users.create_index([("email", ASCENDING)], unique=True)
    users.create_index([("created_at", DESCENDING)])
    
    print("✓ MongoDB users collection and indexes created")
    print("  ℹ️  Only 'users' collection created (others not needed yet)")

