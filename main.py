from fastapi import FastAPI
from routers.v1 import search_routers, filter_routes, metadata_routes
app = FastAPI(
    title="Biblioterra",
    version="1.0.0",
    openapi_url="/v1/openapi.json",
    docs_url="/v1/docs",
    redoc_url="/v1/redocs",
)


app.include_router(search_routers.router)
app.include_router(filter_routes.router)
app.include_router(metadata_routes.router)


@app.get("/")
async def root():
    return "See /v1/docs for usage."
