from fastapi import File
from pydantic import BaseModel, Field, validator

from models.body_models import ValidEntry


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

    @validator("extension", pre=True)
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
