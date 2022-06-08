from pydantic import BaseModel


class SearchResponse(BaseModel):
    pagination: dict
    data: list[dict]


class FilterResponse(BaseModel):
    filtered_data: dict


class MetadataResponse(BaseModel):
    download_links: dict
    description: str


class IndexesResponse(BaseModel):
    indexes: list[str]


class LibraryGetResponse(BaseModel):
    reading: list
    to_read: list
    backlog: list
