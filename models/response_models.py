from pydantic import BaseModel


class SearchResponse(BaseModel):
    results: list[dict]


class FilterResponse(BaseModel):
    filtered_data: dict


class MetadataResponse(BaseModel):
    download_links: dict
    description: str


class IndexesResponse(BaseModel):
    indexes: list[dict]


class LibraryGetResponse(BaseModel):
    reading: list
    to_read: list
    backlog: list
