from fastapi import APIRouter, Depends, Body
from models.body_models import ValidEntry, ValidCategories, md5_reg
from models.response_models import LibraryGetResponse
from functions.hashing_functions import jwt_decode
from functions.library_functions import add_books, remove_books, get_books
from routers.v1.user_routes import oauth2_scheme

router = APIRouter(prefix="/v1")


@router.get("/library/get", tags=["library"], response_model=LibraryGetResponse)
async def library_get(token: str = Depends(oauth2_scheme)):
    """
    Returns the populated library of a valid user. Needs to be logged in.
    """
    payload = jwt_decode(token)
    sub = payload.get("sub")
    library = await get_books(sub)
    return library


@router.post("/library/add/{category}", tags=["library"])
async def library_add(books: list[ValidEntry], category: ValidCategories, token: str = Depends(oauth2_scheme)):
    """
    Use this endpoint to add new books to a user's library. <br>
    You can also use this to move books: <br>
    Add new books and use a different category. <br>
    Or update existing ones: <br>
    Add new books in the same category.

    /add automatically deletes entries with the same md5 identifier in the user's library, so there's no need to manually
    use /remove before adding or moving.

    Be sure to send a list, even if you are only adding one entry.

    """
    payload = jwt_decode(token)
    sub = payload.get("sub")

    await add_books(sub, books, category)


@router.post("/library/remove", tags=["library"])
async def library_remove(token: str = Depends(oauth2_scheme), md5_list: list[str] = Body(..., regex=md5_reg)):
    """
    Use this endpoint to remove books from a user's library. <br>
    Books are removed using its md5 identifier.

    Be sure to send a list, even if you are only removing one entry.

    """
    payload = jwt_decode(token)
    sub = payload.get("sub")
    await remove_books(sub, md5_list)
    return 200
