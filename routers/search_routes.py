from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from pydantic import ValidationError

from services.search.search_functions import fiction_handler, scitech_handler
from services.search.search_index_functions import save_search_index
from models.query_models import FictionSearchQuery, ScitechSearchQuery, ValidTopics, SearchQuery
from models.response_models import SearchResponse
from services.search.search_service import SearchService

router = APIRouter(
)


@router.get("/v1/search/fiction", tags=["search"])
async def fiction_search(response: Response, bg_tasks: BackgroundTasks,
                         search_parameters: FictionSearchQuery = Depends()):
    # Sends the search_parameters.
    results_handler: tuple = await fiction_handler(search_parameters)
    results: list = results_handler[0]
    cached = results_handler[1]

    if type(results) != list or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached

    bg_tasks.add_task(save_search_index, ValidTopics.fiction, results)
    return {"results": results}


@router.get("/v1/search/sci-tech", tags=["search"])
async def scitech_search(response: Response, bg_tasks: BackgroundTasks,
                         search_parameters: ScitechSearchQuery = Depends()):
    # Sends the search_parameters.
    results_handler: tuple = await scitech_handler(search_parameters)
    results: list = results_handler[0]
    cached = results_handler[1]

    if type(results) != list or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached

    bg_tasks.add_task(save_search_index, ValidTopics.scitech, results)
    return {"results": results}


# Should be migrated to v2
@router.get("/v2/neosearch/{topic}", tags=["search"], response_model=SearchResponse)
async def new_search(response: Response, bg_tasks: BackgroundTasks, handler: SearchService = Depends()):
    possible_cache = await handler.retrieve_from_cache()
    if possible_cache:
        return possible_cache

    results = await handler.make_search()
    pagination = await handler.get_pagination_info()
    try:
        search_response = SearchResponse(pagination=pagination, results=results)
    except ValidationError:
        raise HTTPException(500, "Couldn't validate search's response.")

    bg_tasks.add_task(handler.save_on_cache, search_response)

    return search_response
