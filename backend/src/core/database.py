# Mongo & Qdrant factories
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie  
from qdrant_client import QdrantClient

# Import the models to register in the module

from modules.retrieval.models import Conversation
