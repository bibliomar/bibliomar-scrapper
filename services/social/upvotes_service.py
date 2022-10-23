from fastapi import HTTPException
from pydantic import ValidationError

from config.mongodb_connection import mongodb_comments_connect
from models.body_models import IdentifiedComment


class UpvoteService:
    def __init__(self):
        self.db_connection = mongodb_comments_connect()
