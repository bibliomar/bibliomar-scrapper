from fastapi import APIRouter
from methods.filter_functions import book_filtering
from models.response_models import FilterResponse

router = APIRouter(
    prefix="/v1"
)


@router.post("/filter", response_model=FilterResponse)
async def filtering(books: dict, filters: dict):
    print(books, filters)
    results = await book_filtering(books, filters)
    return results
