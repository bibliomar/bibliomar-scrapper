from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from models.body_models import AddBooks, MoveBooks, RemoveBooks
from functions.hashing_functions import jwt_decode

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/login")

router = APIRouter(prefix="/v1")


@router.post("/library/add", tags=["library"])
async def library_add(token: str = Depends(oauth2_scheme), add_body: AddBooks = Depends(AddBooks)):
    payload = jwt_decode(token)
    pass


@router.post("/library/move", tags=["library"])
async def library_move(token: str = Depends(oauth2_scheme), move_body: MoveBooks = Depends(MoveBooks)):
    payload = jwt_decode(token)
    pass


@router.post("/library/remove", tags=["library"])
async def library_remove(token: str = Depends(oauth2_scheme), remove_body: RemoveBooks = Depends(RemoveBooks)):
    payload = jwt_decode(token)
    pass
