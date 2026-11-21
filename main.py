from datetime import date
from html import escape
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="FridgeChef API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)

USERS = {
    "user-a-token": {"id": "user-a", "role": "user"},
    "user-b-token": {"id": "user-b", "role": "user"},
    "admin-token": {"id": "admin", "role": "admin"},
}

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


def current_user(request):
    header = request.headers.get("authorization", "")
    match = re.fullmatch(r"Bearer (\S+)", header)
    user = USERS.get(match.group(1)) if match else None
    if user is None:
        raise ApiError(401, "UNAUTHORIZED", "Missing or invalid authentication token.")
    return user


def find_ingredient(ingredient_id, user):
    item = next((item for item in ingredients if item["id"] == ingredient_id), None)
    if item is None:
        raise ApiError(404, "NOT_FOUND", "Ingredient not found.")
    if user["role"] != "admin" and item["ownerId"] != user["id"]:
        raise ApiError(403, "FORBIDDEN", "You cannot access another user's ingredient.")
    return item


async def validated_body(request):
    try:
        body = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise ApiError(400, "VALIDATION_ERROR", "Invalid JSON request body.", [{"field": "body", "message": "A valid JSON object is required."}])
    if not isinstance(body, dict):
        raise ApiError(400, "VALIDATION_ERROR", "Invalid ingredient data.", [{"field": "body", "message": "A JSON object is required."}])

    details = []
    for key in body:
        if key not in ("name", "quantity", "expiryDate"):
            details.append({"field": key, "message": "Unknown or non-editable field."})
    name = body.get("name")
    if not isinstance(name, str) or not 2 <= len(name.strip()) <= 80:
        details.append({"field": "name", "message": "Name must be a string of 2 to 80 characters."})
    if details:
        raise ApiError(400, "VALIDATION_ERROR", "Invalid ingredient data.", details)
    return body


@app.get("/api/v1/ingredients")
async def list_ingredients(request: Request):
    user = current_user(request)
    visible = [item for item in ingredients if user["role"] == "admin" or item["ownerId"] == user["id"]]
    return success("Ingredients retrieved successfully.", visible, meta={"total": len(visible), "page": 1, "perPage": max(1, len(visible))})


@app.get("/api/v1/ingredients/{ingredient_id}")
async def get_ingredient(ingredient_id: str, request: Request):
    user = current_user(request)
    return success("Ingredient retrieved successfully.", find_ingredient(ingredient_id, user))


@app.post("/api/v1/ingredients")
async def create_ingredient(request: Request):
    global next_id
    user = current_user(request)
    data = await request.json()
    item = {"id": f"ingredient_{next_id}", **data, "ownerId": user["id"]}
    next_id += 1
    ingredients.append(item)
    return success("Ingredient created successfully.", item, status=201)


@app.put("/api/v1/ingredients/{ingredient_id}")
async def update_ingredient(ingredient_id: str, request: Request):
    user = current_user(request)
    item = find_ingredient(ingredient_id, user)
    data = await request.json()
    item.update(data)
    return success("Ingredient updated successfully.", item)


@app.delete("/api/v1/ingredients/{ingredient_id}")
async def delete_ingredient(ingredient_id: str, request: Request):
    user = current_user(request)
    item = find_ingredient(ingredient_id, user)
    ingredients.remove(item)
    return success("Ingredient deleted successfully.", None)
