import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "data_server")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]


def get_database():
    return db
