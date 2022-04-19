from pydantic import BaseModel
from enum import Enum


class ValidTopics(str, Enum):
    fiction = "fiction"
    scitech = "sci-tech"

