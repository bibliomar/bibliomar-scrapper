import json

from grab_fork_from_libgen import AIOMetadata
from grab_fork_from_libgen.exceptions import MetadataError

from keys import redis_provider
from fastapi import HTTPException
import aioredis
import os


async def get_cover(md5: str):
    try:
        # This environment key is for Heroku Redis.
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()

    except aioredis.exceptions.RedisError:
        # If something goes wrong and we can't connect to redis.
        # It's quite broad, since all redis exceptions inherit from this class
        redis = None

    if redis:
        possible_cover = redis.get(f"cover:{md5}")
        if possible_cover:
            cached = "true"
            await redis.close()
            return possible_cover, cached

    # AIOMetadata has good error handling.
    try:
        # The topic doesn't matter for .get_cover()
        meta = AIOMetadata(md5, "sci-tech", timeout=20)
    except MetadataError as err:
        # There's little chance this error will actually be raised, since "sci-tech" is always valid.
        raise HTTPException(400, str(err))

    try:
        cover = await meta.get_cover()
        if redis:
            # Expires in 14 days
            await redis.set(f"cover:{md5}", cover, ex=1209600)
        cached = "false"
        return cover, cached
    except MetadataError as err:
        raise HTTPException(500, str(err))


async def get_metadata(topic: str, md5: str):
    # The cache implementation works like this:
    # For 72 hours, a book will be cached in redis, after this, it will be removed.

    try:
        # This environment key is for Heroku Redis.
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()

    except aioredis.exceptions.RedisError:
        # If something goes wrong and we can't connect to redis.
        # It's quite broad, since all redis exceptions inherit from this class
        redis = None

    if redis:
        possible_metadata = await redis.get(f"metadata:{md5}")
        # Note that this function only returns if there's actually a cached version.
        # So we can still use the same redis "client" for setting the cache below.
        if possible_metadata:
            possible_metadata = json.loads(possible_metadata)
            cached = "true"
            await redis.close()
            return possible_metadata, cached

    try:
        meta = AIOMetadata(md5, topic, timeout=30)
    except MetadataError as err:
        raise HTTPException(400, str(err))

    try:
        metadata = await meta.get_metadata()
        if redis:
            metadata_json = json.dumps(metadata)
            await redis.set(f"metadata:{md5}", metadata_json)
            await redis.close()

    except MetadataError as err:
        raise HTTPException(500, str(err))

    cached = "false"
    return metadata, cached
