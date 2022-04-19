from fastapi import APIRouter, Depends, Query, HTTPException, Request, Response
from methods.search_functions import fiction_handler, scitech_handler
from models.query_models import FictionSearchQuery, ScitechSearchQuery
from models.response_models import SearchResponse

router = APIRouter(
    prefix="/v1"
)


@router.get("/fiction", response_model=SearchResponse)
async def fiction_search(search_parameters: FictionSearchQuery = Depends()):
    # Sends a dict with the search_parameters.
    # Also removes all none values, they will have a new value attached in the respective function.
    results: dict = await fiction_handler(search_parameters)
    if type(results) != dict or bool(results) is False:
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")

    return results


@router.get("/scitech", response_model=SearchResponse)
async def scitech_search(search_parameters: ScitechSearchQuery = Depends()):
    # Sends a dict with the search_parameters.
    # Also removes all none values, they will have a new value attached in the respective function.
    results: dict = await scitech_handler(search_parameters)
    if type(results) != dict or bool(results) is False:
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")

    return results


