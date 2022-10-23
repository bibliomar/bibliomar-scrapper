from fastapi import HTTPException
from config.mongodb_connection import mongodb_search_connect
from models.path_models import ValidIndexesTopic
from models.query_models import ValidTopics
import re


async def save_search_index(topic: ValidTopics, lbr_data: list[dict]):
    # This will save the first 10 search results for indexing.
    connection = mongodb_search_connect()
    indexes_list = []
    language_array = ["Portuguese", "English"]

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



    try:
        await connection.update_one({"data": "search_indexes"}, {"$addToSet": {topic: {"$each": indexes_list}}})
    except:
        raise ConnectionError("Couldn't update the specific search indexes array.")


async def get_search_index(topic: ValidIndexesTopic):
    connection = mongodb_search_connect()
    try:
        if topic is ValidIndexesTopic.any:
            search_indexes: dict = await connection.find_one({"data": "search_indexes"})
            fiction_indexes: list = search_indexes.get("fiction")
            sci_tech_indexes: list = search_indexes.get("sci-tech")
            any_indexes = fiction_indexes + sci_tech_indexes
            return any_indexes
        else:
            search_indexes: dict = await connection.find_one({"data": "search_indexes"}, {topic})
            return search_indexes.get(topic)

    except:
        raise HTTPException(500, "Couldn't find indexes for this given topic.")

