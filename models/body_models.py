from fastapi import Form, Body
from pydantic import BaseModel, ValidationError, validator
from enum import Enum

# This regex makes sure the password is bigger than 6 and smaller than 16, has one uppercase character and one lowercase,
# And has at least one special symbol.
pass_reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,16}$"
# This ensures that md5 is a 32 hexadecimal string.
md5_reg = "^[\w]{32}$"


class ValidCategories(str, Enum):
    reading = "reading"
    to_read = "to-read"
    backlog = "backlog"


class AddBooks(BaseModel):
    # This validates the method to add a number of books to a user's document.
    books: list[dict] = Body(...)
    category: ValidCategories


class MoveBooks(BaseModel):
    # This will receive a list of md5s, and the category to move them to.
    books_md5: list[str] = Body(...)
    new_category: ValidCategories


class RemoveBooks(BaseModel):
    # This model will receive a list of md5s, and remove all the matching entries.
    books_md5: list[str] = Body(...)
