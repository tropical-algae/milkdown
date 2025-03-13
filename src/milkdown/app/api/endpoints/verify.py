import json
from datetime import datetime, timedelta
from typing import Any

import pytz
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from milkdown.app.api.deps import get_current_user, get_db
from milkdown.app.core import security
from milkdown.app.core.constant import CONSTANT
from milkdown.app.db import crud

from milkdown.app.db.models import User
from milkdown.app.models.model_user import Token, UserBase
from milkdown.app.models.model_verify import VerifyRequest, VerifyResponse
from milkdown.app.services.services_verify import verify_client_info
from milkdown.common.config import settings

router = APIRouter()

@router.post("/version")
async def verify_version(
    data: VerifyRequest
) -> VerifyResponse:
    result = verify_client_info(data=data)
    if result is None:
        raise HTTPException(status_code=500, detail=CONSTANT.CLIENT_VERIFY_ERROR)
    return VerifyResponse(
        status=result,
        message=CONSTANT.RESP_200 if result else CONSTANT.CLIENT_VERIFY_FAIL
    )
