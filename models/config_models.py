from pydantic import BaseSettings, Field


class MySQLSettings(BaseSettings):
    host: str = Field(..., env="MYSQL_HOST")
    port: int = Field(..., env="MYSQL_PORT")
    user: str = Field(..., env="MYSQL_USER")
    password: str = Field(..., env="MYSQL_PASS")
    db: str = Field(..., env="MYSQL_SCHEMA")
