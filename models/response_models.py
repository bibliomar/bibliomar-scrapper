from pydantic import BaseModel


class SearchResponse(BaseModel):
    pagination: dict
    data: list[dict]


class FilterResponse(BaseModel):
    filtered_data: dict

class MetadataResponse(BaseModel):
    download_links: dict
    description: str
