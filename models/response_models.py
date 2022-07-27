
from pydantic import BaseModel, Field


class SearchResponse(BaseModel):
    results: list[dict]


class MetadataResponse(BaseModel):
    download_links: dict
    description: str | None


class IndexesResponse(BaseModel):
    indexes: list[dict]


class LibraryGetResponse(BaseModel):
    reading: list
    to_read: list = Field(alias="to-read")
    backlog: list
