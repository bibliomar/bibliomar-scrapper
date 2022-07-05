from pydantic import BaseModel


class SearchResponse(BaseModel):
    results: list[dict]


class FilterResponse(BaseModel):
    filtered_data: list[dict]


class MetadataResponse(BaseModel):
    download_links: dict
    description: str | None


class IndexesResponse(BaseModel):
    indexes: list[dict]


class LibraryGetResponse(BaseModel):
    reading: list | None
    to_read: list | None
    backlog: list | None
