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


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request, exc):
    details = []
    for entry in exc.errors():
        field = ".".join(str(item) for item in entry["loc"] if item != "body") or "body"
        details.append({"field": field, "message": entry["msg"]})
    return failure(400, "VALIDATION_ERROR", "Invalid request parameters.", details)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request, exc):
    codes = {404: ("NOT_FOUND", "Endpoint not found."), 405: ("METHOD_NOT_ALLOWED", "Method not allowed.")}
    code, message = codes.get(exc.status_code, ("HTTP_ERROR", "Request failed."))
    return failure(exc.status_code, code, message)
