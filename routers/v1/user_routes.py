from fastapi import APIRouter, Depends, requests, responses
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from functions.user_functions import create_user, login_user
from functions.hashing_functions import jwt_validate
from functions.database_functions import mongodb_connect

router = APIRouter(
    prefix="/v1"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/login")


# We use OAuth2 Password flow for better integration with the OpenAPI Schema

@router.get("/user/validate", tags=["user"])
async def user_validate(token: str = Depends(oauth2_scheme)):
    new_user_token = jwt_validate(token, 3)
    return {"access_token": new_user_token, "token_type": "bearer"}


@router.post("/user/signup", tags=["user"])
async def user_signup(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    """
    **WARNING:** <br>
    PLEASE make sure to not use passwords used elsewhere here. <br>
    Biblioterra is not proprietary software and the security functions used are not hidden. <br>
    All passwords are hashed with
    [pbkdf2 - sha256](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.pbkdf2_digest.html#passlib.hash.pbkdf2_sha256) <br>
    Only username and password are required.
    """
    user_token = await create_user(form_data)
    return {"access_token": user_token, "token_type": "bearer"}


@router.post("/user/login", tags=["user"])
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    """
    Use this endpoint to authenticate users. <br>
    After authenticating, use the /library routes to populate the user's library. <br>
    Only username and password are needed.
    """
    user_token = await login_user(form_data)
    return {"access_token": user_token, "token_type": "bearer"}
