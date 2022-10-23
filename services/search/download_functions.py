from fastapi import HTTPException
from grab_fork_from_libgen.search_config import get_request_headers
from requests import exceptions
from requests_html import AsyncHTMLSession
from services.search.metadata_functions import get_dlinks

import aiofiles
from aiofiles import os as aioos

temp_download_folder = "temp"


async def remove_temp_download(filename: str):
    await aioos.remove(filename)


async def _create_temp_file(content: bytes, md5: str):
    filename = f"{temp_download_folder}/{md5}.epub"
    async with aiofiles.open(filename, "wb+") as fo:
        await fo.write(content)
        await fo.close()

    return filename


async def _download_handler(d_link: str):
    session = AsyncHTMLSession()
    req = await session.get(d_link, timeout=60, headers=get_request_headers())
    return req.content


async def make_temp_download(md5: str, topic: str):
    # We make use of a possible d_links cache by using the same function we use in /metadata.
    d_links_handler = await get_dlinks(md5, topic)
    d_links = d_links_handler[0]
    downloaded_file = None
    last_err = None
    for index, link in enumerate(d_links.values()):
        print(link)
        try:
            tried_download = await _download_handler(link)
            temp_file = await _create_temp_file(tried_download, md5)
            print(f"from {link}")
            if temp_file is not None:
                downloaded_file = temp_file
                break
            else:
                continue

        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError) as err:
            print(err)
            last_err = err
            continue

    if downloaded_file is None:
        if last_err is not None:
            raise HTTPException(500, str(last_err))
        raise HTTPException(500, "Couldn't download this book in any of the mirrors.")

    return downloaded_file
