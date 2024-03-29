from bson import ObjectId
from fastapi import Form, Body
from pydantic import BaseModel, Field, NonNegativeInt, validator, ValidationError, root_validator
from .query_models import ValidTopics
from enum import Enum

# This ensures that md5 is a valid 32 hexadecimal string.
md5_reg = "^[0-9a-fA-F]{32}$"
match_anywhere_md5_reg = "[0-9a-fA-F]{32}$"
# Date format that should be used. It's mainly made to work with Javascript Date().
date_format = "%Y-%m-%dT%H:%M:%SZ"


class CommentOrReply(str, Enum):
    comment = "comment"
    reply = "reply"


class ValidCategories(str, Enum):
    reading = "reading"
    to_read = "to-read"
    backlog = "backlog"


class SearchEntry(BaseModel):
    authors: str
    title: str
    md5: str = Field(..., regex=md5_reg)
    topic: str
    extension: str
    size: str
    language: str | None
    cover_url: str | None
    relevance: int | None = Field(None)  # Relevance of a entry based on the search.


class LibraryEntry(BaseModel):
    # Defines how a valid book entry in library should look like.
    authors: str = Field(..., alias="author(s)")
    series: str | None
    title: str
    topic: ValidTopics
    md5: str = Field(..., regex=md5_reg)
    extension: str | None
    size: str | None
    language: str | None
    # Only useful for keeping track of a user's progress in a book, with epubcifi.
    progress: str | None
    category: ValidCategories | None

    class Config:
        allow_population_by_field_name = True


class Metadata(BaseModel):
    md5: str = Field(..., alias="MD5")
    title: str = Field(..., alias="Title")
    authors: str = Field(..., alias="Author")
    topic: str
    series: str | None = Field(None, alias="Series")
    edition: str | None = Field(None, alias="Edition")
    language: str | None = Field(None, alias="Language")
    year: str | None = Field(None, alias="Year")
    publisher: str | None = Field(None, alias="Publisher")
    city: str | None = Field(None, alias="City")
    pages: int | None = Field(None, alias="Pages")
    volume: str | None = Field(None, alias="VolumeInfo")
    isbn: str | None = Field(None)
    asin: str | None = Field(None, alias="ASIN")
    googlebooks_id: str | None = Field(None, alias="GooglebookID")
    extension: str | None = Field(None, alias="Extension")
    size: str | None = Field(None)
    cover_url: str | None = Field(None)
    description: str | None = Field(None, alias="Descr")
    added_at: str | None = Field(None)


class RemoveBooks(BaseModel):
    # This model will receive a list of md5s, and remove all the matching entries.
    md5_list: list[str] = Body(..., regex=md5_reg)


class User(BaseModel):
    username: str
    password: str
    email: str
    gravatar_hash: str | None = Field(default=None)
    reading: list[dict]
    to_read: list[dict] = Field(..., alias="to-read")
    backlog: list[dict]
    followers: list[str] = Field(default=[])
    following: list[str] = Field(default=[])
    bio: str | None = Field(default=None)
    private_profile: bool | None = Field(default=False)

    class Config:
        allow_population_by_field_name = True


class Comment(BaseModel):
    """
    Represents a new comment:
    A comment that is yet to be identified in the database (has no ID, or responses or upvotes attached)
    """
    username: str
    rating: int | None = Field(default=None, le=5, ge=0)
    content: str


class CommentUpdateRequest(BaseModel):
    username: str
    id: str
    updated_rating: int | None = Field(default=None, le=5, ge=0)
    updated_content: str | None = Field(default=None)


class CommentUpvoteRequest(BaseModel):
    username: str
    id: str


class Reply(BaseModel):
    username: str
    content: str
    parent_id: str


class ReplyUpdateRequest(BaseModel):
    username: str
    id: str
    parent_id: str
    updated_content: str


class ReplyUpvoteRequest(BaseModel):
    username: str
    id: str
    parent_id: str


class IdentifiedComment(Comment):
    id: str
    attached_responses: list[dict] = Field(default=[])
    upvotes: list[str] = Field(default=[])
    created_at: str | None = Field(default=None)
    modified_at: str | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @validator("id", pre=True, always=True)
    def objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v


class IdentifiedReply(Reply):
    id: str
    upvotes: list[str] = Field(default=[])
    created_at: str | None = Field(default=None)
    modified_at: str | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    @validator("id", pre=True, always=True)
    def objectid_to_string(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v
