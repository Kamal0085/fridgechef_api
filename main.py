from datetime import date
from html import escape
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="FridgeChef API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

ingredients = [
    {"id": "ingredient_1", "name": "Tomatoes", "quantity": 4, "expiryDate": "2026-12-01", "ownerId": "user-a"},
    {"id": "ingredient_2", "name": "Eggs", "quantity": 6, "expiryDate": "2026-12-05", "ownerId": "user-a"},
    {"id": "ingredient_3", "name": "Milk", "quantity": 1, "expiryDate": "2026-11-28", "ownerId": "user-b"},
    {"id": "ingredient_4", "name": "Carrots", "quantity": 3, "expiryDate": "2026-12-03", "ownerId": "user-b"},
]
next_id = 5


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


@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    return failure(500, "INTERNAL_ERROR", "An unexpected server error occurred.")


def find_ingredient(ingredient_id):
    item = next((item for item in ingredients if item["id"] == ingredient_id), None)
    if item is None:
        raise ApiError(404, "NOT_FOUND", "Ingredient not found.")
    return item


@app.get("/api/v1/ingredients")
async def list_ingredients(request: Request):
    return success("Ingredients retrieved successfully.", ingredients, meta={"total": len(ingredients), "page": 1, "perPage": max(1, len(ingredients))})


@app.get("/api/v1/ingredients/{ingredient_id}")
async def get_ingredient(ingredient_id: str, request: Request):
    return success("Ingredient retrieved successfully.", find_ingredient(ingredient_id))


@app.post("/api/v1/ingredients")
async def create_ingredient(request: Request):
    global next_id
    data = await request.json()
    item = {"id": f"ingredient_{next_id}", **data}
    next_id += 1
    ingredients.append(item)
    return success("Ingredient created successfully.", item)
