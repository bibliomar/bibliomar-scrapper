from motor.motor_asyncio import AsyncIOMotorClient

from keys import mongodb_provider

print(mongodb_provider)

# Establishes an database "connection".


def mongodb_connect():
    # This makes no actual I/O.
    client = AsyncIOMotorClient(mongodb_provider)
    database = client["biblioterra"]
    collection = database["users"]
    return collection


def mongodb_search_connect():
    # This makes no actual I/O.
    client = AsyncIOMotorClient(mongodb_provider)
    database = client["biblioterra"]
    collection = database["search"]
    return collection


def mongodb_comments_connect():
    client = AsyncIOMotorClient(mongodb_provider)
    database = client["biblioterra"]
    collection = database["comments"]
    return collection
