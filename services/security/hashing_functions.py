from fastapi import HTTPException
from passlib.hash import pbkdf2_sha256
from hashlib import md5
from datetime import datetime, timedelta
from jose import jwt, JWTError
from keys import jwt_secret, jwt_algorithm


def hash_create(password):
    hashed_pwd = pbkdf2_sha256.hash(password)
    return hashed_pwd


def hash_compare(hashed_pwd, password):
    verify: bool = pbkdf2_sha256.verify(password, hashed_pwd)
    return verify


def jwt_encode(username: str, expire: int):
    expire_at = datetime.utcnow() + timedelta(days=expire)
    payload = {
        "sub": username,
        "exp": expire_at,
    }
    jwt_token = jwt.encode(payload, jwt_secret, jwt_algorithm)
    return jwt_token


def jwt_decode(jwt_token: str):
    try:
        decoded_jwt = jwt.decode(jwt_token, jwt_secret, jwt_algorithm)
        return decoded_jwt
    except JWTError:
        HTTPException(401, "Login token is invalid or has expired. Please log in again.",
                      headers={"WWW-Authenticate": "Bearer"})


def jwt_validate(jwt_token: str, expire: int):
    # Takes a valid token and revalidates it.
    # This is just a shorthand.

    decoded_jwt = jwt_decode(jwt_token)
    try:
        new_jwt = jwt_encode(decoded_jwt.get("sub"), expire)
    except AttributeError:
        raise HTTPException(401, "Invalid JWT token.", headers={"WWW-Authenticate": "Bearer"})
    return new_jwt


def email_to_md5(email: str):
    email = email.strip().lower().encode("utf-8")

    return md5(email).hexdigest()
