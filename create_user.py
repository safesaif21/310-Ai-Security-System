"""Script to create a new user in MongoDB"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database.mongodb import get_database
from backend.database import crud
from backend.auth import get_password_hash


def create_new_user(username: str, email: str, password: str, role: str = "user"):
    """Create a new user"""
    db = get_database()
    try:
        # Check if user exists
        existing = crud.get_user_by_username(db, username)
        if existing:
            print(f"❌ User '{username}' already exists!")
            return
        
        # Check if email exists
        existing_email = crud.get_user_by_email(db, email)
        if existing_email:
            print(f"❌ Email '{email}' is already registered!")
            return
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        # Create user
        user = crud.create_user(
            db=db,
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role
        )
        
        print(f"✅ Created user: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
        print(f"   User ID: {user['_id']}")
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        raise


if __name__ == "__main__":
    # Example: Create a new viewer user
    print("Creating new users...")
    print()
    
    create_new_user(
        username="admin",
        email="admin@example.com",
        password="admin123",
        role="admin"
    )
