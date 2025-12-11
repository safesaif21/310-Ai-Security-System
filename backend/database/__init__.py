"""Database package - MongoDB"""

# MongoDB imports
from backend.database.mongodb import (
    get_database,
    get_db_mongo,
    init_db_mongo,
    close_mongo_connection
)

# MongoDB CRUD and models
from backend.database import crud_mongo as crud
from backend.database import models_mongo as models

__all__ = [
    "get_database",
    "get_db_mongo",
    "init_db_mongo",
    "close_mongo_connection",
    "crud",
    "models"
]
