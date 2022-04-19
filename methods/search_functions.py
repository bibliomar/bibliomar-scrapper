from fastapi import HTTPException
from grab_fork_from_libgen import AIOLibgenSearch
from grab_fork_from_libgen.exceptions import InvalidSearchParameter, LibgenError
from models.query_models import FictionSearchQuery, ScitechSearchQuery


# All functions receive an SearchParameters instance.


async def fiction_handler(search_parameters: FictionSearchQuery):
    search_parameters = search_parameters.dict(exclude_none=True)
    if search_parameters.get("language"):
        # .get is used because it doesn't raise an error.
        search_parameters["language"] = search_parameters["language"].capitalize()

    try:
        lbs = AIOLibgenSearch("fiction", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: dict = await lbs.get_results(pagination=True)
    except KeyError:
        raise HTTPException(400, "No results found with the given query.")

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    # Transforms data into an ordinary dict, indexes are turned into values
    # and entries in values.
    lbr["data"] = dict(lbr.get("data"))

    return lbr


async def scitech_handler(search_parameters: ScitechSearchQuery):
    search_parameters = search_parameters.dict(exclude_none=True)
    try:
        lbs = AIOLibgenSearch("sci-tech", **search_parameters)
    except InvalidSearchParameter:
        raise HTTPException(400, "Invalid query parameter(s). Check the docs for more info.")
    except LibgenError:
        raise HTTPException(500, "LibraryGenesis is down or unreachable. This may be an internal issue.")

    try:
        lbr: dict = await lbs.get_results(pagination=True)
    except KeyError:
        raise HTTPException(400, "No results found with the given query.")

    if len(lbr) == 0:
        # in rare stances, LibgenSearch finds no results, yet returns an empty dict.
        # This is to avoid that.
        raise HTTPException(400, "No results found with the given query.")

    # Transforms data into an ordinary dict, indexes are turned into values
    # and entries in values.
    lbr["data"] = dict(lbr.get("data"))

    return lbr




