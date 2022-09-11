from pydantic import BaseModel
from enum import Enum


class ValidIndexesTopic(str, Enum):
    any = "any"
    fiction = "fiction"
    scitech = "sci-tech"
