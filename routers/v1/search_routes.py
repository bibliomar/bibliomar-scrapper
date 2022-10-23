from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from services.search.search_functions import fiction_handler, scitech_handler
from services.search.search_index_functions import save_search_index
from models.query_models import FictionSearchQuery, ScitechSearchQuery, ValidTopics
from models.response_models import SearchResponse

router = APIRouter(
    prefix="/v1"
)


@router.get("/search/fiction", tags=["search"], response_model=SearchResponse)
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


@router.get("/search/sci-tech", tags=["search"], response_model=SearchResponse)
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


