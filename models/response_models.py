from pydantic import BaseModel, Field, validator

from models.body_models import IdentifiedComment, IdentifiedReply, SearchEntry, LibraryEntry


class UserProfile(BaseModel):
    followers: list = Field(default=[])
    following: list = Field(default=[])
    avatar_url: str = Field(default=None)
    gravatar_profile_info: dict = Field(default=None)
    private_profile: bool = Field(default=False)


class SearchPaginationInfo(BaseModel):
    current_page: int
    has_next_page: bool
    total_pages: int


class SearchResponse(BaseModel):
    pagination: SearchPaginationInfo | None
    results: list[SearchEntry]


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
    def extension_lower(cls, v):
        if v:
            return v.lower()
        else:
            return v


class IndexesResponse(BaseModel):
    indexes: list[dict]


class UserLibraryResponse(BaseModel):
    reading: list
    to_read: list = Field(alias="to-read")
    backlog: list


class BookGetResponse(BaseModel):
    result: LibraryEntry


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


class ReplyResponse(IdentifiedReply):
    id: str
    num_of_upvotes: int
    user_has_upvoted: bool
