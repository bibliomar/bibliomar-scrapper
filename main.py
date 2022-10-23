from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers.v1 import search_routes, metadata_routes, user_routes, library_routes, download_routes, profile_routes, comments_routes
from keys import preview_url
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["3/2 seconds"])

if preview_url is None:
    preview_url = "http://localhost:3002"

origins = [
    "http://localhost:3000",
    "http://localhost:3001"
    "https://bibliomar.netlify.app",
    "http://bibliomar.netlify.app"
    "https://bibliomar.site",
    "http://bibliomar.site",
    "https://www.bibliomar.site",
    "http://www.bibliomar.site",
    preview_url
]

tags_metadata = [
    {
        "name": "search",
        "description": "Searches LibraryGenesis for the given query and returns the books that match."
    },
    {
        "name": "filter",
        "description": "Deprecated."
    },
    {
        "name": "metadata",
        "description": "Returns either a cover link, metadata or download links for "
                       "the given md5 and topic."
    },
    {
        "name": "temp",
        "description": "Temporarily downloads a book and returns a FileResponse to the user. Using it here in preview "
                       "will make the docs bug out. Should be used in a frontend that wants to download a file, "
                       "but doesn't want to save it."
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

app.include_router(metadata_routes.router)
app.include_router(user_routes.router)
app.include_router(library_routes.router)
app.include_router(download_routes.router)
app.include_router(profile_routes.router)
app.include_router(comments_routes.router)


@app.get("/")
async def root(request: Request):
    return "See /v1/docs for usage."


@app.head("/")
async def root_head(request: Request):
    return 200
