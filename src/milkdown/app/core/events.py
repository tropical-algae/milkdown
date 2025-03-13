import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import pytz
from fastapi import FastAPI
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from milkdown.app.util import download_nltk_resources
from milkdown.common.config import settings


def resp_success(response_body: Any) -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": status.HTTP_200_OK,
            "message": "success",
            "timestamp": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "data": response_body,
        },
    )


def resp_error(response_body: dict) -> Response:
    return JSONResponse(
        status_code=response_body["status"],
        content={
            "status": response_body["status"],
            "message": response_body["message"],
            "timestamp": str(datetime.now(tz=pytz.timezone("Asia/Shanghai"))),
            "data": response_body["data"],
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI, logger: logging.Logger):
    logger.info("Starting service...")
    logger.info("Loading event extraction model...")
    download_nltk_resources()


    yield
    logger.info("Shut down and clear cache...")


def add_middleware(app: FastAPI):
    async def log_response(request: Request, call_next):
        response = await call_next(request)
        # return directly if not an api endpoint
        is_not_api: bool = not request.url.path.startswith(settings.API_PREFIX)
        is_access: bool = request.url.path.endswith("access-token")
        if is_access or is_not_api:
            return response

        # return exception
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        response_body = json.loads(response_body[0].decode())
        if isinstance(response_body, dict) and response_body.get("is_exception", False):
            return resp_error(response_body)

        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))
        response_body = json.loads(response_body[0].decode())

        return resp_success(response_body)

    app.add_middleware(BaseHTTPMiddleware, dispatch=log_response)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.TRUSTED_DOMAINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
