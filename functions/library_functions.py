from fastapi import HTTPException

from functions.database_functions import mongodb_connect


async def remove_by_md5(connection, username, md5: str):
    try:
        # Needs a better implementation.
        await connection.update_one({"username": username}, {"$pull": {"reading": {"md5": md5}}})
        await connection.update_one({"username": username}, {"$pull": {"to-read": {"md5": md5}}})
        await connection.update_one({"username": username}, {"$pull": {"backlog": {"md5": md5}}})
    except:
        # Too broad.
        raise HTTPException(500, "An error occurred while removing old entries, aborting operation.")


async def remove_books(username, remove_list: list):
    connection = mongodb_connect()
    try:
        for md5 in remove_list:
            await remove_by_md5(username, md5, connection)
    except:
        pass


async def add_books(username: str, add_list: list[dict], category: str):
    connection = mongodb_connect()
    try:
        # Adds each book in add_list to the user's specified category, if it doesn't already exist.
        await connection.update_one({"username": username}, {"$addToSet": {category: {"$each": add_list}}})
    except:
        pass


async def move_books(username, move_list: list, new_category):
    connection = mongodb_connect()
    pass
