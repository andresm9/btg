
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.config import logging

logger = logging.getLogger(__name__)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "BTG_DB")

logger.info(f"Connecting to MongoDB at {MONGO_URI}, DB: {MONGO_DB_NAME}")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
