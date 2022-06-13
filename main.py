from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.v1 import search_routes, filter_routes, metadata_routes, user_routes, library_routes
from keys import redis_provider
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["1/2seconds"])

origins = [
    "http://localhost"
    "http://localhost:3000"
]

tags_metadata = [
    {
        "name": "search",
        "description": "Searches LibraryGenesis for the given query and returns the books that match."
    },
    {
        "name": "filter",
        "description": "Filters the given books using the given parameters"
    },
    {
        "name": "metadata",
        "description": "Returns either a cover link, or metadata (which includes download links and description) for "
                       "the given md5 and topic."
    },
    {
        "name": "user",
        "description": "Defines routes for authenticating the user. The tokens are then used by library endpoints."
    },
    {
        "name": "library",
        "description": "Endpoints for populating a user's library. Needs auth token from /users. "
                       "All books are unique, e.g. you can't have a book both in reading and in backlog"
                       "at the same time. Biblioterra will try to automatically move your entries when you add "
                       "something."
    }
]

app = FastAPI(
    title="Biblioterra",
    version="1.0.0",
    openapi_url="/v1/openapi.json",
    docs_url="/v1/docs",
    redoc_url="/v1/redocs",
    openapi_tags=tags_metadata
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(search_routes.router)
app.include_router(filter_routes.router)
app.include_router(metadata_routes.router)
app.include_router(user_routes.router)
app.include_router(library_routes.router)


@app.get("/")
async def root(request: Request):
    return "See /v1/docs for usage."
