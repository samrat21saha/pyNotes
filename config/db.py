import os
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
MONGO_URI = os.getenv("MONGO_URI")

conn = MongoClient(MONGO_URI)