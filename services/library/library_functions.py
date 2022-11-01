from fastapi import HTTPException
from pydantic import ValidationError

from models.body_models import LibraryEntry
from config.mongodb_connection import mongodb_connect


# These services should only receive valid usernames, authentication is done inside the endpoints.

async def get_all_books(username: str):
    # This services retrieves all books in a user's library.
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


async def get_book(username: str, md5: str):
    connection = mongodb_connect()
    try:
        # Motor optimizes requests by batch requesting all of this.
        book_on_reading: dict = await connection.find_one(
            {"username": username, "reading.md5": md5}, {"reading.$"})
        book_on_toread: dict = await connection.find_one(
            {"username": username, "to-read.md5": md5}, {"to-read.$"})
        book_on_backlog: dict = await connection.find_one(
            {"username": username, "backlog.md5": md5}, {"backlog.$"})

        categories = [book_on_reading, book_on_toread, book_on_backlog]
        valid_entry = None
        for category in categories:
            if category:
                valid_entry = category.values()

        if valid_entry is None:
            raise HTTPException(400, "No book found with the given MD5.")

        # If there's a valid entry, build a list with it's values.
        # This list includes an "_id" and "{category-name} keys, but we are only retrieving their values."
        entry_list = list(valid_entry)
        # The "{category-name}" value is an array of only one element, because we are projecting on our queries.
        # So we use [1] to access it's values, and [0] to retrieve the first and only document.
        result: dict = entry_list[1][0]
        # We will be performing validation before returning to the user.
        try:
            valid_result = LibraryEntry(**result)
            return valid_result
        except (ValidationError, TypeError):
            raise HTTPException(500, "Error while validating the results.")

    except:
        raise HTTPException(400, "Could not find this specific book. This may be an internal error.")


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
            raise HTTPException(500, "An error occurred while removing entries, aborting operation.")


async def add_books(username: str, add_list: list[LibraryEntry], category: str):
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
