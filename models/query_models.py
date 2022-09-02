from fastapi import Query
from pydantic import BaseModel
from enum import Enum


class ValidTopics(str, Enum):
    fiction = "fiction"
    scitech = "sci-tech"

class ValidCriteria(str, Enum):
    default = ""
    title = "title"
    authors = "authors"
    series = "series"


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


class ValidSortMode(str, Enum):
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
    results100 = 100


class FictionSearchQuery(BaseModel):
    # None values are excluded in search_functions.
    q: str = Query(..., min_length=3)
    criteria: ValidCriteria | None
    language: str | None
    format: str | None
    wildcard: ValidWildcardOrPhrase | None
    page: int = 1


class ScitechSearchQuery(BaseModel):
    # None values are excluded in search_functions.
    q: str = Query(..., min_length=3)
    sort: ValidSort | None
    sortmode: ValidSortMode | None
    column: ValidColumn | None
    phrase: ValidWildcardOrPhrase | None
    res: ValidRes | None
    page: int = 1
