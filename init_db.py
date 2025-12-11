"""Initialize MongoDB database with default admin user"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database.mongodb import get_database, init_db_mongo
from backend.database import crud_mongo as crud
from backend.auth import get_password_hash


def create_default_admin(db):
    """Create default admin user if it doesn't exist"""
    try:
        # Check if admin already exists
        existing_admin = crud.get_user_by_username(db, "admin")
        if existing_admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash("admin123")  # Change this!
        admin_user = crud.create_user(
            db=db,
            username="admin",
            email="admin@security-system.local",
            hashed_password=hashed_password,
            role="admin"
        )
        
        print(f"✓ Created admin user: {admin_user['username']}")
        print("  ⚠️  Default password: admin123 - PLEASE CHANGE THIS!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")


def main():
    """Initialize the MongoDB database and create default data"""
    print("🚀 Initializing AI Security System MongoDB Database...")
    print()
    
    try:
        # Get database connection
        print("Connecting to MongoDB...")
        db = get_database()
        print(f"✓ Connected to database: {db.name}")
        print()
        
        # Create collections and indexes
        print("Creating collections and indexes...")
        init_db_mongo()
        print()
        
        # Create default admin user
        print("Setting up default admin user...")
        create_default_admin(db)
        print()
        
        print("✅ MongoDB database initialization complete!")
        print()
        print("Next steps:")
        print("1. Update the admin password")
        print("2. Make sure your .env file has correct MONGODB_URI")
        print("3. Generate a secure SECRET_KEY")
        print("4. Start the backend: python -m backend.main")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print()
        print("Please check:")
        print("1. MongoDB is running (or MongoDB Atlas is accessible)")
        print("2. Your MONGODB_URI in .env is correct")
        print("3. Your internet connection (if using MongoDB Atlas)")
        sys.exit(1)


if __name__ == "__main__":
    main()
