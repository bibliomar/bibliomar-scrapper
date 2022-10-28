from fastapi import APIRouter, Query, Depends

from models.body_models import md5_reg, CommentUpvoteRequest, ReplyUpvoteRequest
from routers.v1.user_routes import oauth2_scheme
from services.security.hashing_functions import jwt_decode
from services.social.upvotes_service import UpvotesService

router = APIRouter(prefix="/v1")


@router.post("/upvotes/{md5}", tags=["upvotes"])
async def add_comment_upvote(upvote_request: CommentUpvoteRequest,
                             md5: str = Query(..., regex=md5_reg),
                             handler: UpvotesService = Depends(),
                             token: str = Depends(oauth2_scheme)):
    payload = jwt_decode(token)



@router.delete("/upvotes/{md5}", tags=["upvotes"])
async def remove_comment_upvote(upvote_request: CommentUpvoteRequest,
                                md5: str = Query(..., regex=md5_reg),
                                handler: UpvotesService = Depends(),
                                token: str = Depends(oauth2_scheme)):
    pass


@router.post("/upvotes/{md5}", tags=["upvotes"])
async def add_reply_upvote(upvote_request: ReplyUpvoteRequest,
                           md5: str = Query(..., regex=md5_reg),
                           handler: UpvotesService = Depends(),
                           token: str = Depends(oauth2_scheme)):
    pass
