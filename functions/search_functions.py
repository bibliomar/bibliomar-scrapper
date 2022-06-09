from fastapi import HTTPException
from grab_fork_from_libgen import AIOLibgenSearch
from grab_fork_from_libgen.exceptions import InvalidSearchParameter, LibgenError
from models.query_models import FictionSearchQuery, ScitechSearchQuery
from typing import OrderedDict
from keys import redis_provider

import aioredis
import json


# All functions receive an SearchParameters instance.
# Requests are cached for 24 hours by default.
# lbs stands for Libgen Search
# lbr stands for Libgen Results

# TODO
# Save search to database:
# Save inside a "searchindexes" collection, on which
# each document has a file's title and topic.
# this will be used by the frontend.


def ordered_to_list(lbr_data: OrderedDict):
    # This removes the keys in the OrderedDict, and returns a list of dictionaries.
    results = []
    for book in lbr_data.values():
        results.append(book)

    return results


async def fiction_handler(search_parameters: FictionSearchQuery):
    search_parameters = search_parameters.dict(exclude_none=True)
    if search_parameters.get("language"):
        # .get is used because it doesn't raise an error.
        search_parameters["language"] = search_parameters["language"].capitalize()
    # Try using the cached version, if it exists:
    try:
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()
    except aioredis.exceptions.RedisError:
        # If something goes wrong, and we can't connect to Redis.
        redis = None

    # This is the json string of the current search parameters
    search_parameters_str: str = json.dumps(search_parameters)

    if redis:
        possible_search_str: str = await redis.get(f"search:{search_parameters_str}")
        if possible_search_str:
            possible_search_dict: dict = json.loads(possible_search_str)
            cached = "true"
            await redis.close()
            return possible_search_dict, cached

    try:
        lbs = AIOLibgenSearch("fiction", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: OrderedDict = await lbs.get_results(pagination=False)

    except LibgenError as err:
        raise HTTPException(400, str(err))

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    libgen_results: list = ordered_to_list(lbr)

    if redis:
        lbr_str: str = json.dumps(lbr)
        await redis.set(f"search:{search_parameters_str}", lbr_str, 86400)
        await redis.close()

    cached = "false"

    return libgen_results, cached


async def scitech_handler(search_parameters: ScitechSearchQuery):
    search_parameters = search_parameters.dict(exclude_none=True)

    try:
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()
    except aioredis.exceptions.RedisError:
        # If something goes wrong, and we can't connect to Redis.
        redis = None

    # This is the json string of the current search parameters
    search_parameters_str: str = json.dumps(search_parameters)

    if redis:
        possible_search_str: str = await redis.get(f"search:{search_parameters_str}")
        if possible_search_str:
            possible_search_dict: dict = json.loads(possible_search_str)
            cached = "true"
            await redis.close()
            return possible_search_dict, cached

    try:
        lbs = AIOLibgenSearch("sci-tech", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: OrderedDict = await lbs.get_results(pagination=False)
    except LibgenError as err:
        raise HTTPException(400, str(err))

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    libgen_results: list = ordered_to_list(lbr)

    if redis:
        lbr_str: str = json.dumps(lbr)
        await redis.set(f"search:{search_parameters_str}", lbr_str, 86400)
        await redis.close()
    cached = "false"
    return libgen_results, cached
