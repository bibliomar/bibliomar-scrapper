from fastapi import APIRouter
from services.social.profile_service import ProfileService

router = APIRouter(prefix="/v1")


@router.get("/profile/{username}")
async def get_profile(username: str):
    handler = ProfileService()
    profile = handler.get_user_profile(username)
    return {"result": profile}
