from datetime import date
from html import escape
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="FridgeChef API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        self.status = status
        self.code = code
        self.message = message
        self.details = details


def success(message, data, status=200, meta=None):
    body = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return JSONResponse(body, status_code=status)


def failure(status, code, message, details=None):
    error = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return JSONResponse({"success": False, "error": error}, status_code=status)


@app.exception_handler(ApiError)
async def api_error_handler(request, exc):
    return failure(exc.status, exc.code, exc.message, exc.details)
