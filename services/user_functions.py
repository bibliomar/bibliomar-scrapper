from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError

from config.mongodb_connection import mongodb_connect
from models.body_models import User
from services.security.hashing_functions import hash_create, hash_compare, jwt_encode, jwt_decode, email_to_md5
import re

# This regex makes sure the password is bigger than 6 and smaller than 16,
# has one uppercase character and one lowercase, and has at least one special symbol.
pass_reg = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,16}$")
# This regex ensures username has no whitespaces or special characters:
user_reg = re.compile("[\s@$!%*#?&]")
email_reg = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')


async def create_user(form_data: OAuth2PasswordRequestForm, email: str):
    # Sanitizes email
    email = email.strip().lower()
    # connection is an AsyncIOMotorCollection instance.
    connection = mongodb_connect()
    # Checks if username and password are valid:
    if re.match(user_reg, form_data.username):
        # If there's a whitespace or special character on the username string.
        raise HTTPException(400, "Username has whitespaces or special characters.")

    if not re.match(pass_reg, form_data.password):
        # If the password doesn't match the regex
        raise HTTPException(400, "Password is invalid.")

    if not re.match(email_reg, email):
        raise HTTPException(400, "Email is invalid.")


    # TODO: convert into single request (optional, motor already optimizes this.)
    # Checks if username or email_url already exists:
    user_check = await connection.find_one({"username": form_data.username})
    email_check = await connection.find_one({"email": email})
    if user_check or email_check:
        raise HTTPException(400, "Username or email already in use.")

    # If it doesn't:
    hashed_pwd = hash_create(form_data.password)
    gravatar_hash = email_to_md5(email)

    # This is the user's base schema.
    user_schema = {
        "username": form_data.username,
        "password": hashed_pwd,
        "email": email,
        "gravatar_hash": gravatar_hash,
        "reading": [],
        "to-read": [],
        "backlog": [],
        "followers": [],
        "following": [],
        "bio": None,
        "private_profile": False,
    }
    try:
        user_as_model = User(**user_schema)
    except ValidationError as e:
        print(e)

    await connection.insert_one(user_schema)
    token = jwt_encode(form_data.username, 3)
    return token


async def login_user(form_data: OAuth2PasswordRequestForm):
    # connection is an AsyncIOMotorCollection instance.
    connection = mongodb_connect()

    # Checks if username really exists...
    user_check: dict = await connection.find_one({"username": form_data.username})
    if user_check:
        # Then check if the password matches the hashed one.
        if hash_compare(user_check.get("password"), form_data.password):
            # If yes, encode the token and return it.
            token = jwt_encode(form_data.username, 3)
            return token

    # If username or password is incorrect.
    raise HTTPException(400, "Incorrect login credentials.")


async def recover_user(email: str):
    connection = mongodb_connect()
    user = await connection.find_one({"email": email})
    if not user:
        raise HTTPException(400, "Email doesn't correspond to an valid account.")

    return user


async def change_password(token: str, new_pass: str | None, new_email: str | None):
    connection = mongodb_connect()
    decoded_token: dict = jwt_decode(token)
    username = decoded_token.get("sub")
    if new_pass:
        if not re.match(pass_reg, new_pass):
            # If the password doesn't match the regex
            raise HTTPException(400, "New password is invalid.")

        hashed_pwd = hash_create(new_pass)
        try:
            await connection.update_one({"username": username}, {"$set": {"password": hashed_pwd}})
        except:
            raise HTTPException(500, "Couldn't change this user's password.")
    if new_email:
        if not re.match(email_reg, new_pass):
            # If the password doesn't match the regex
            raise HTTPException(400, "New password is invalid.")
        try:
            await connection.update_one({"username": username}, {"$set": {"email": new_email}})
        except:
            raise HTTPException(500, "Couldn't change this user's email.")

    return

