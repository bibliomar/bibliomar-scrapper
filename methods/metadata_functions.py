from grab_fork_from_libgen import AIOMetadata
from grab_fork_from_libgen.exceptions import MetadataError

# from keys import redis_keys
from fastapi import HTTPException
import aioredis
import os


async def get_cover(topic: str, md5: str):
    try:
        redis = aioredis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
    except KeyError:
        # If something goes wrong and we can't connect to redis.
        redis = None

    if redis:
        possible_cover = await redis.get(md5)
        if possible_cover:
            print("cover is logged: ", possible_cover)
            await redis.close()
            return possible_cover

    # AIOMetadata as good error handling.
    try:
        meta = AIOMetadata(md5, topic)
    except MetadataError as err:
        # If the topic is not "fiction" or "sci-tech"
        raise HTTPException(400, str(err))

    try:
        cover = await meta.get_cover()
        if redis:
            await redis.set(md5, cover)

        return cover
    except MetadataError as err:
        raise HTTPException(500, str(err))


async def get_metadata(topic: str, md5: str):
    pass
