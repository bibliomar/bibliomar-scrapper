from fastapi import HTTPException
from grab_fork_from_libgen import AIOLibgenSearch
from grab_fork_from_libgen.exceptions import InvalidSearchParameter, LibgenError, MetadataError
from models.query_models import LegacyFictionSearchQuery, LegacyScitechSearchQuery
from models.body_models import LibraryEntry
from typing import OrderedDict
from keys import redis_provider

import aioredis
import json


# All services receive an SearchParameters instance.
# Requests are cached for 24 hours by default.
# lbs stands for Libgen Search
# lbr stands for Libgen Results

# TODO
# Save search to database:
# Save inside a "searchindexes" collection, on which
# each document has a file's title and topic.
# this will be used by the frontend.


def format_item(lbr_data: OrderedDict):
    # This removes the keys in the OrderedDict, and returns a list of dictionaries. Also formats authors value for
    # better consistency.
    results = []
    for book in lbr_data.values():
        f_item = book
        try:

            f_item.update({"authors": book["author(s)"]})
            if book.get("series") == "":
                # If series is an empty string, change it to a None value.
                f_item.pop("series")
                f_item.update({"series": None})
            f_item.pop("author(s)")
        except KeyError:
            # Returns f_item to it's initial state.
            f_item = book

        results.append(f_item)

    return results


async def fiction_handler(search_parameters: LegacyFictionSearchQuery):
    search_parameters = search_parameters.dict(exclude_none=True)
    if search_parameters.get("language"):
        # .get is used because it doesn't raise an error.
        search_parameters["language"] = search_parameters["language"].capitalize()
    # Try using the cached version, if it exists:
    try:
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()
    except aioredis.exceptions.RedisError as e:
        print(e)
        # If something goes wrong, and we can't connect to Redis.
        redis = None

    # This is the json string of the current search parameters
    search_parameters_str: str = json.dumps(search_parameters)

    if redis:
        possible_search_str: str = await redis.get(f"search:{search_parameters_str}")
        if possible_search_str:
            possible_search_list: list = json.loads(possible_search_str)
            cached = "true"
            await redis.close()
            return possible_search_list, cached

    try:
        lbs = AIOLibgenSearch("fiction", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(
            400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(
            500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: OrderedDict = await lbs.get_results(pagination=False)

    except LibgenError as err:
        if str(err).find("did not have status code 200") != -1:
            raise HTTPException(503, "Our servers are probably down.")
        raise HTTPException(400, str(err))

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    libgen_results: list = format_item(lbr)

    if redis:
        lbr_str: str = json.dumps(libgen_results)
        await redis.set(f"search:{search_parameters_str}", lbr_str, 86400)
        await redis.close()

    cached = "false"

    return libgen_results, cached


async def scitech_handler(search_parameters: LegacyScitechSearchQuery):
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
            possible_search_list: list = json.loads(possible_search_str)
            cached = "true"
            await redis.close()
            return possible_search_list, cached

    try:
        lbs = AIOLibgenSearch("sci-tech", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(
            400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(
            500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: OrderedDict = await lbs.get_results(pagination=False)
    except LibgenError as err:
        if str(err).find("did not have status code 200") != -1:
            raise HTTPException(503, "Our servers are probably down.")
        raise HTTPException(400, str(err))

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    libgen_results: list = format_item(lbr)

    if redis:
        lbr_str: str = json.dumps(libgen_results)
        await redis.set(f"search:{search_parameters_str}", lbr_str, 86400)
        await redis.close()
    cached = "false"
    return libgen_results, cached
