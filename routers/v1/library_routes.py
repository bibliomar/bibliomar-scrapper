from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from models.body_models import AddBooks, RemoveBooks
from functions.hashing_functions import jwt_decode
from functions.library_functions import add_books, remove_books

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/login")

router = APIRouter(prefix="/v1")


@router.post("/library/add", tags=["library"])
async def library_add(token: str = Depends(oauth2_scheme), add_body: AddBooks = Depends(AddBooks)):
    """
    Use this endpoint to add new books to a user's library. <br>
    You can also use this to move books: <br>
    Just add new books and use a different category. <br>

    /add automatically deletes entries with the same md5 identifier in the user's library, so there's no need to manually
    use /remove before adding or moving.

    Be sure to send a list, even if you are only adding one entry.

    """
    payload = jwt_decode(token)
    sub = payload.get("sub")
    body_dict = add_body.dict()
    book_list = body_dict.get("books")
    category = add_body.category
    await add_books(sub, book_list, category)


@router.post("/library/remove", tags=["library"])
async def library_remove(token: str = Depends(oauth2_scheme), remove_body: RemoveBooks = Depends(RemoveBooks)):
    """
    Use this endpoint to remove books from a user's library. <br>
    Books are removed using its md5 identifier.

    Be sure to send a list, even if you are only removing one entry.

    """
    payload = jwt_decode(token)
    sub = payload.get("sub")
    remove_list = remove_body.md5_list
    await remove_books(sub, remove_list)

