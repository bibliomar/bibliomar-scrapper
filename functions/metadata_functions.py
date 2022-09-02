import json

from grab_fork_from_libgen import AIOMetadata
from grab_fork_from_libgen.exceptions import MetadataError
from models.response_models import MetadataResponse
from pydantic import ValidationError
from keys import redis_provider
from fastapi import HTTPException
import aioredis


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
        possible_cover = await redis.get(f"cover:{md5}")
        if possible_cover:
            cached = "true"
            await redis.close()
            return possible_cover, cached

    # AIOMetadata has good error handling.
    try:
        meta = AIOMetadata(timeout=20)
    except MetadataError as err:
        # There's little chance this error will actually be raised, since "sci-tech" is always valid.
        raise HTTPException(400, str(err))

    try:
        cover = await meta.get_cover(md5)
        if redis:
            # Expires in 14 days
            await redis.set(f"cover:{md5}", cover, ex=14 * 86400)
            await redis.close()
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
            try:
                possible_metadata = MetadataResponse(**possible_metadata)
                return possible_metadata, cached
            except (ValidationError, TypeError):
                pass

    try:
        meta = AIOMetadata(timeout=30)
    except MetadataError as err:
        raise HTTPException(400, str(err))

    try:
        metadata = await meta.get_metadata(md5, topic)

        if redis:
            metadata_json = json.dumps(metadata)
            await redis.set(f"metadata:{md5}", metadata_json, ex=14 * 86400)
            await redis.close()

    except MetadataError as err:
        raise HTTPException(500, str(err))

    cached = "false"
    try:
        response = MetadataResponse(**metadata)
        return response, cached
    except ValidationError:
        raise HTTPException(500, "Error validating metadata.")


async def get_dlinks(md5: str, topic: str) -> [dict, str]:
    try:
        # This environment key is for Heroku Redis.
        redis = aioredis.from_url(redis_provider, decode_responses=True)
        await redis.ping()

    except aioredis.exceptions.RedisError:
        # If something goes wrong and we can't connect to redis.
        # It's quite broad, since all redis exceptions inherit from this class
        redis = None

    if redis:
        possible_dlinks = await redis.get(f"dlinks-{md5}")
        if possible_dlinks:
            possible_dlinks_dict: dict = json.loads(possible_dlinks)
            cached = "true"
            return possible_dlinks_dict, cached

    meta = AIOMetadata(timeout=30)
    dlinks = await meta.get_download_links(md5, topic)
    if redis:
        await redis.set(f"dlinks-{md5}", json.dumps(dlinks), ex=5 * 86400)
    cached = "false"
    return dlinks, cached
