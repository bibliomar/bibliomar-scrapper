from fastapi import APIRouter, Request, Query, BackgroundTasks
from fastapi.responses import FileResponse
from services.search.download_functions import make_temp_download, remove_temp_download
from models.body_models import md5_reg
from models.query_models import ValidTopics

router = APIRouter(prefix="/v1")


@router.get("/temp-download/{topic}/{md5}", tags=["temp"])
async def temp_download_book(bg: BackgroundTasks, request: Request, topic: ValidTopics,
                             md5: str = Query(..., regex=md5_reg)):

    downloaded_file = await make_temp_download(md5, topic)
    bg.add_task(remove_temp_download, downloaded_file)
    return FileResponse(downloaded_file, media_type="application/epub+zip")
