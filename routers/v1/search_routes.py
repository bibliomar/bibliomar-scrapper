from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks
from functions.search_functions import fiction_handler, scitech_handler
from functions.search_index_functions import save_search_index
from models.query_models import FictionSearchQuery, ScitechSearchQuery, ValidTopics
from models.response_models import SearchResponse

router = APIRouter(
    prefix="/v1"
)


def format_item(item: dict):
    f_item = item
    f_item.update({"authors": item["author(s)"]})
    f_item.pop("author(s)")
    return f_item


def format_result(results: list[dict]) -> list:
    return list(map(format_item, results))


@router.get("/search/fiction", tags=["search"], response_model=SearchResponse)
async def fiction_search(response: Response, bg_tasks: BackgroundTasks,
                         search_parameters: FictionSearchQuery = Depends()):
    # Sends the search_parameters.
    results_handler: tuple = await fiction_handler(search_parameters)
    results: list = results_handler[0]
    f_results = format_result(results)
    cached = results_handler[1]

    if type(results) != list or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached

    bg_tasks.add_task(save_search_index, ValidTopics.fiction, f_results)
    return {"results": f_results}


@router.get("/search/sci-tech", tags=["search"], response_model=SearchResponse)
async def scitech_search(response: Response, bg_tasks: BackgroundTasks,
                         search_parameters: ScitechSearchQuery = Depends()):
    # Sends the search_parameters.
    results_handler: tuple = await scitech_handler(search_parameters)
    results: list = results_handler[0]
    f_results = format_result(results)
    cached = results_handler[1]

    if type(results) != list or bool(results) is False:
        # This check is here as a last resource, the handler should take care of error handling.
        raise HTTPException(500, "Something wrong happened. This may be an internal issue.")
    response.headers["Cached"] = cached

    bg_tasks.add_task(save_search_index, ValidTopics.scitech, f_results)
    return {"results": f_results}
