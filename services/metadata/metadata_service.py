from fastapi import Path

from models.query_models import ValidTopics


class MetadataService:

    def __init__(self, md5: str, topic: ValidTopics = Path()):
        self.md5 = md5
        self.topic = topic
        self.metadata_sql = self._sql_query_builder()

    def _sql_query_builder(self) -> str:
        if self.topic == ValidTopics.fiction:
            columns = ""
        else:
            columns = ""

        metadata_sql = f"""SELECT """
