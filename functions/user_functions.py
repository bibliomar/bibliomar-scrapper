from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from functions.database_functions import mongodb_connect
from functions.hashing_functions import hash_create, hash_compare, jwt_encode
import re

# This regex makes sure the password is bigger than 6 and smaller than 16,
# has one uppercase character and one lowercase, and has at least one special symbol.
pass_reg = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,16}$")
# This regex ensures username has no whitespaces and is bigger than 5 and smaller than 16:
user_reg = re.compile("[\s@$!%*#?&]")


async def create_user(form_data: OAuth2PasswordRequestForm):
    # connection is an AsyncIOMotorCollection instance.
    connection = mongodb_connect()
    # Checks if username and password are valid:
    if re.search(user_reg, form_data.username):
        # If there's a whitespace on the username string.
        raise HTTPException(400, "Username has whitespaces or special characters.")

    if not re.search(pass_reg, form_data.password):
        # If the password doesn't match the regex
        raise HTTPException(400, "Password is invalid or too insecure.")

    # Checks if username already exists:
    user_check = await connection.find_one({"username": form_data.username})
    if user_check:
        raise HTTPException(400, "Username already exists.")

    # If it doesn't:
    hashed_pwd = hash_create(form_data.password)

    # This is the user's base schema.
    user_schema = {
        "username": form_data.username,
        "password": hashed_pwd,
        "reading": [],
        "to_read": [],
        "backlog": []
    }

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
