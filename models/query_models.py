from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field, validator, ValidationError
from enum import Enum


class CommentSort(str, Enum):
    date = "date"
    upvotes = "upvotes"
    rating = "rating"


class ValidCriteria(str, Enum):
    any = "Any"
    title = "Title"
    authors = "Author"
    series = "Series"


class ValidTopics(str, Enum):
    fiction = "fiction"
    scitech = "sci-tech"


class SearchQuery(BaseModel):
    q: str = Query(..., min_length=3)
    criteria: ValidCriteria | None = Query(None)
    language: str | None = Query(None)
    format: str | None = Query(None)
    results_per_page: int = Query(25, ge=25, le=100)
    page: int = Query(default=1, ge=1)


class ValidWildcardOrPhrase(str, Enum):
    # Wildcard and Phrase are equivalent, but Libgen names them differently.
    # Pydantic converts these to str automatically.
    zero = 0
    one = 1


class ValidSort(str, Enum):
    default = "def"
    id = "id"
    title = "title"
    author = "author"
    publisher = "publisher"
    year = "year"


class SortMode(str, Enum):
    asc = "ASC"
    desc = "DESC"


class ValidColumn(str, Enum):
    # Equivalent to Criteria in Fiction Search, but it has more options.
    default = "def"
    title = "title"
    author = "author"
    publisher = "publisher"
    year = "year"
    series = "series"
    isbn = "ISBN"
    language = "Language"
    md5 = "md5"


class ValidRes(str, Enum):
    # Pydantic converts these to str automatically.
    results25 = 25
    results50 = 50
    results75 = 75
    results100 = 100


class CommentsQuery(BaseModel):
    sort: CommentSort | None = Query(None)
    mode: SortMode | None = Query(None)


class LegacyFictionSearchQuery(BaseModel):
    # None values are excluded in search_functions.
    q: str = Query(..., min_length=3)
    criteria: str | None
    language: str | None
    format: str | None
    wildcard: ValidWildcardOrPhrase | None
    page: int = 1


class LegacyScitechSearchQuery(BaseModel):
    # None values are excluded in search_functions.
    q: str = Query(..., min_length=3)
    sort: ValidSort | None
    sortmode: SortMode | None
    column: ValidColumn | None
    phrase: ValidWildcardOrPhrase | None
    res: ValidRes | None
    page: int = 1
