import aiomysql
from aiomysql import Connection, Cursor, DictCursor

from keys import mysql_settings


async def mysql_connect() -> Connection:
    settings = mysql_settings
    conn = await aiomysql.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password,
        db=settings.db,
        echo=True,
        autocommit=True,
    )
    return conn


class MySQLConnect:
    """
    Use this class with the "async with" keywords for connecting to the mysql database (libgen dataset).
    """

    async def __aenter__(self) -> Cursor:
        self.connection = await mysql_connect()
        self.cursor: DictCursor = await self.connection.cursor(DictCursor)
        return self.cursor

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self.cursor.closed:
            await self.cursor.close()

        if not self.connection.closed:
            self.connection.close()
