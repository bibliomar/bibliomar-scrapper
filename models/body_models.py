from fastapi import Form, Body
from pydantic import BaseModel, Field, NonNegativeInt
from enum import Enum

# This ensures that md5 is a valid 32 hexadecimal string.
md5_reg = "^[0-9a-fA-F]{32}$"


class ValidCategories(str, Enum):
    reading = "reading"
    to_read = "to-read"
    backlog = "backlog"


class ValidEntryConfig:
    validate_assignment = True
    allow_population_by_field_name = True


class ValidEntry(BaseModel):
    # Defines how a valid book entry should look like.
    class ValidTopics(str, Enum):
        fiction = "fiction"
        sci_tech = "sci-tech"

    authors: str = Field(..., alias="author(s)")
    series: str | None
    title: str
    topic: ValidTopics
    md5: str = Field(..., regex=md5_reg)
    extension: str | None
    size: str | None
    language: str | None
    # The user's set rating
    rating: int | None = Field(..., ge=0, le=5)

    # Only useful for keeping track of a user's progress in a book, with epubcifi.
    progress: str | None
    category: str | None

    class Config:
        allow_population_by_field_name = True


class RemoveBooks(BaseModel):
    # This model will receive a list of md5s, and remove all the matching entries.
    md5_list: list[str] = Body(..., regex=md5_reg)

