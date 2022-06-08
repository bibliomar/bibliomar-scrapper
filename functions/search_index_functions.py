from fastapi import HTTPException
from functions.database_functions import mongodb_search_connect
from models.query_models import ValidTopics


async def save_search_index(topic: ValidTopics, lbr_data: list[dict]):
    connection = mongodb_search_connect()
    indexes_list = []
    for book in lbr_data:
        search_index_document = {
            "title": book.get("title"),
            "topic": book.get("topic")
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
