import json

from fastapi import HTTPException
from requests import Response
from requests_html import AsyncHTMLSession

from models.body_models import User
from models.response_models import UserProfile
from config.mongodb_connection import mongodb_connect
from services.security.hashing_functions import email_to_md5


class ProfileService:
    def __init__(self):
        self._db_connection = mongodb_connect()
        self._session = AsyncHTMLSession()
        self._gravatar_url = "https://www.gravatar.com"
        self._gravatar_hash = None

    @staticmethod
    def _make_gravatar_ready(user: User):
        if user.gravatar_hash is None:
            return email_to_md5(user.email)
        return user.gravatar_hash

    async def _get_gravatar_avatar(self):
        gravatar_url = f"{self._gravatar_url}/avatar/{self._gravatar_hash}"
        possible_picture: Response = await self._session.get(f"{gravatar_url}?d=404")
        if possible_picture.status_code == 404:
            return None
        return gravatar_url

    async def _get_gravatar_profile(self):
        gravatar_profile_url = f"{self._gravatar_url}/{self._gravatar_hash}"
        possible_profile: Response = await self._session.get(f"{gravatar_profile_url}.json")
        if possible_profile.status_code == 404:
            return None
        possible_profile_dict = json.loads(possible_profile.content)
        return possible_profile_dict

    async def get_user_profile(self, username: str):
        connection = self._db_connection
        possible_user = await connection.find_one({"username": username})
        if not possible_user:
            raise HTTPException(400, "User doesn't exist")
        user_schema = User(**possible_user)
        if user_schema.private_profile:
            raise HTTPException(400, "User profile is private.")
        user_schema.gravatar_hash = self._make_gravatar_ready(user_schema)
        profile = UserProfile(**possible_user)
        self._gravatar_hash = user_schema.gravatar_hash
        profile.avatar_url = await self._get_gravatar_avatar()
        profile.gravatar_profile_info = await self._get_gravatar_profile()
        return profile
