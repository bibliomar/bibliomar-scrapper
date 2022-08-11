from fastapi import HTTPException

from models.body_models import ValidEntry, ValidCategories
from functions.database_functions import mongodb_connect


async def get_books(username: str):
    # This functions retrieves all books in a user's library.
    connection = mongodb_connect()
    try:
        user_info: dict = await connection.find_one({"username": username})
    except:
        # Too broad.
        raise HTTPException(500, "Couldn't retrieve the user's library.")
    user_library = {
        "reading": user_info.get("reading"),
        "to-read": user_info.get("to-read"),
        "backlog": user_info.get("backlog")
    }
    return user_library


async def remove_books(username: str, remove_list: list[str]):
    connection = mongodb_connect()
    for md5 in remove_list:
        try:

            await connection.update_one(
                {"username": username},
                {"$pull": {"reading": {"md5": md5}, "to-read": {"md5": md5}, "backlog": {"md5": md5}}}
            )
        except:
            # Too broad.
            raise HTTPException(500, "An error occurred while removing old entries, aborting operation.")


async def add_books(username: str, add_list: list[ValidEntry], category: str):
    """
    Adds a book to a category, if it already exists, remove it before adding it again.
    Can also be used for updating.
    """

    connection = mongodb_connect()
    # Adds every md5 in add_list to a md5_list
    md5_list = []
    book_list = []
    for book in add_list:
        book_list.append(book.dict())
        md5_list.append(book.md5)

    # Removes said books using their md5 before proceeding.
    # This is done so every book in a user's library is unique.
    await remove_books(username, md5_list)

    try:
        # Adds each book in add_list to the user's specified category.
        await connection.update_one({"username": username}, {"$addToSet": {category: {"$each": book_list}}})
    except:
        # Too broad.
        raise HTTPException(500, "An error occurred while adding new entries, aborting operation.")
