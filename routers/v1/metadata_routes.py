from fastapi import APIRouter
from methods.metadata_functions import get_cover, get_metadata

router = APIRouter(
    prefix="/v1"
)


@router.get("/cover")
async def get_cover_by_md5(topic: str, md5: str):
    results = await get_cover(topic, md5)
    return results


@router.get("/metadata")
async def get_metadata_by_md5(topic: str, md5: str):
    pass
