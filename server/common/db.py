"""Database Module."""

import certifi
import os 

from dotenv import load_dotenv
from pymongo import MongoClient

from server.common.logging import logger

load_dotenv()

try:
    MONGO_CLIENT_URL = os.getenv("MONGO_CLIENT_URI")
    client = MongoClient(
        MONGO_CLIENT_URL,
        tls=True,
        tlsCAFile=certifi.where(), 
    )
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error("MongoDB Connection Failed.")
    raise RuntimeError("Unexpected error accessing MongoDB client.") from e


def get_collection(database_name: str, collection_name: str):
    """Get collection from MongoDB.
    
    Args:
        database_name (str): Database of MongoDB cluster. 
        collection_name (str): Collection name. 
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        logger.info("MongoDB Connection to Collection Successful.")
        return collection
    except Exception as e:
        logger.info("MongoDB Connection to Collection Failed.")
        raise RuntimeError("Unexpected error accessing MongoDB collection.") from e
