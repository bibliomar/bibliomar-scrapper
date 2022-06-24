from fastapi import HTTPException
from functions.database_functions import mongodb_search_connect
from models.query_models import ValidTopics
import re


async def save_search_index(topic: ValidTopics, lbr_data: list[dict]):
    # This will save the first 10 search results for indexing.
    connection = mongodb_search_connect()
    indexes_list = []
    language_array = ["Portuguese", "English"]
    if len(lbr_data) <= 10:
        for book in lbr_data:
            if book.get("language") in language_array:
                regex = "isbn.*$|asin.*$"
                reg_compiled = re.compile(regex, re.IGNORECASE)
                title: str = book.get("title")
                f_title: str = title.capitalize()
                last_char: str = ""
                for char in f_title:
                    if not (char.isalnum()):
                        if (char.isspace()) and (last_char.isspace()):
                            f_title = f_title.replace(char, "")
                    last_char = char

                f_title = re.sub(reg_compiled, "", f_title)
                search_index_document = {
                    "title": f_title,
                    "topic": book.get("topic")
                }
                indexes_list.append(search_index_document)

    else:
        for x in range(0, 9):
            if lbr_data[x].get("language") in language_array:
                regex = "isbn.*$|asin.*$"
                reg_compiled = re.compile(regex, re.IGNORECASE)
                title: str = lbr_data[x].get("title")
                f_title: str = title.capitalize()
                last_char: str = ""
                for char in f_title:
                    if not (char.isalnum()):
                        if (char.isspace()) and (last_char.isspace()):
                            f_title = f_title.replace(char, "")
                    last_char = char

                f_title = re.sub(reg_compiled, "", f_title)
                search_index_document = {
                    "title": f_title,
                    "topic": lbr_data[x].get("topic")
                }
                indexes_list.append(search_index_document)

    try:
        await connection.update_one({"data": "search_indexes"}, {"$addToSet": {topic: {"$each": indexes_list}}})
    except:
        raise ConnectionError("Couldn't update the specific search indexes array.")


async def get_search_index(topic: ValidTopics):
    connection = mongodb_search_connect()
    try:
        search_indexes: dict = await connection.find_one({"data": "search_indexes"}, {topic})

    except:
        raise HTTPException(500, "Couldn't find indexes for this given topic.")
    indexes_result = search_indexes.get(topic)
    return indexes_result
