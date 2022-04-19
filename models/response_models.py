from pydantic import BaseModel
from typing import OrderedDict


class SearchResponse(BaseModel):
    pagination: dict
    data: OrderedDict


class FilterResponse(BaseModel):
    filtered_data: dict
