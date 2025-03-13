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

# from milkdown.app.db.crud.select import select_all_user
from milkdown.app.db.models import User
from milkdown.app.models.model_user import Token, UserBase
from milkdown.common.config import settings

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate_user(db, full_name=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail=CONSTANT.TOKEN_NOT_MATCH)
    scopes = json.loads(str(user.scopes))
    form_data.scopes = scopes
    return {
        "access_token": security.create_access_token(
            data={
                "userid": user.id,
                "username": user.full_name,
                "scopes": scopes,
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        "token_type": "bearer",
        "user_id": user.id,
        "scopes": scopes,
        "status": 200,
        "message": CONSTANT.RESP_200,
        "timestamp": pytz.timezone("Asia/Shanghai").localize(datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
    }


@router.post("/test-token", response_model=UserBase)
async def token_test(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token
    """
    del current_user.password
    return current_user
