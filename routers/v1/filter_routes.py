from fastapi import APIRouter
from functions.filter_functions import book_filtering
from models.response_models import FilterResponse

router = APIRouter(
    prefix="/v1"
)


@router.post("/filter", tags=["filter"], response_model=FilterResponse)
async def filtering(books: list[dict], filters):
    print(books, filters)
    results = await book_filtering(books, filters)
    return results
