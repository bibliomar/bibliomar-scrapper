from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from models.body_models import ValidEntry, IdentifiedComment, IdentifiedReply


class UserProfile(BaseModel):
    # This class shows two methods of settings default values to fields in Pydantic, lol.
    followers: list = Field(default=[])
    following: list = Field(default=[])
    bio: str = None
    profile_picture: Any = None
    private_profile: bool = None

    class Config:
        validate_assignment = True


class SearchResponse(BaseModel):
    results: list[dict]


class MetadataResponse(BaseModel):
    title: str | None
    authors: str | None
    series: str | None
    edition: str | None
    language: str | None
    year: str | None
    publisher: str | None
    isbn: str | None
    md5: str | None
    topic: str | None
    extension: str | None
    size: str | None
    description: str | None

    @validator("extension", pre=True, always=True)
    def extension_upper(cls, v):
        if v:
            return v.lower()
        else:
            return v


class IndexesResponse(BaseModel):
    indexes: list[dict]


class LibraryGetResponse(BaseModel):
    reading: list
    to_read: list = Field(alias="to-read")
    backlog: list


class BookGetResponse(BaseModel):
    result: ValidEntry


class DownloadLinksResponse(BaseModel):
    # If get is None it means something has gone wrong with the request.
    get: str = Field(..., alias="GET")
    Cloudflare: str | None
    ipfsio: str | None = Field(None, alias="IPFS.io")
    c4rex: str | None = Field(None, alias="c4rex.co")
    Crust: str | None
    Pinata: str | None


class CommentResponse(IdentifiedComment):
    id: str
    num_of_upvotes: int
    user_has_upvoted: bool

    @validator("id", pre=True, always=True)
    def str_to_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v


class ReplyResponse(IdentifiedReply):
    id: str
    num_of_upvotes: int
    user_has_upvoted: bool

    @validator("id", pre=True, always=True)
    def str_to_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        else:
            return v
