from fastapi import HTTPException
from models.response_models import UserProfile
from config.mongodb_connection import mongodb_connect


class ProfileService:
    def __init__(self):
        self.db_connection = mongodb_connect()

    async def get_user_profile(self, username: str):
        connection = self.db_connection
        possible_user = await connection.find_one({"username": username})
        if not possible_user:
            raise HTTPException(400, "User doesn't exist")

        profile = UserProfile(**possible_user)
        return profile
