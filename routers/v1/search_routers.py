from fastapi import APIRouter, Depends, Query, HTTPException, Request, Response
from functions.search_functions import fiction_handler, scitech_handler
from models.query_models import FictionSearchQuery, ScitechSearchQuery
from models.response_models import SearchResponse

router = APIRouter(
    prefix="/v1"
)


@router.get("/fiction", tags=["search"], response_model=SearchResponse)
async def fiction_search(response: Response, search_parameters: FictionSearchQuery = Depends()):
    # Sends a dict with the search_parameters.
    # Also removes all none values, they will have a new value attached in the respective function.
    results_handler: tuple = await fiction_handler(search_parameters)
    results = results_handler[0]
    cached = results_handler[1]

    if type(results) != dict or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached
    return results


@router.get("/sci-tech", tags=["search"], response_model=SearchResponse)
async def scitech_search(response: Response, search_parameters: ScitechSearchQuery = Depends()):
    # Sends a dict with the search_parameters.
    # Also removes all none values, they will have a new value attached in the respective function.
    results_handler: tuple = await scitech_handler(search_parameters)
    results = results_handler[0]
    cached = results_handler[1]

    if type(results) != dict or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached
    return results


