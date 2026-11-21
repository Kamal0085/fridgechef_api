# FridgeChef API v1 Documentation

Base URL: `http://127.0.0.1:8000`

The main resource is the pantry **ingredient**. Data is stored in memory and resets when the server restarts.

## Authentication and access control

All ingredient endpoints require the `Authorization: Bearer <token>` header. The greeting page is public.

| Token | Identity | Authorization |
|---|---|---|
| `user-a-token` | user-a | Read and manage their own ingredients |
| `user-b-token` | user-b | Read and manage their own ingredients |
| `admin-token` | admin | Read, update and delete any ingredient |

List requests by regular users only return their own ingredients. If a regular user requests another user's ingredient, the API returns **403 Forbidden** instead of 404. We chose 403 so the client can tell an authorization failure apart from an ID that does not exist. The owner ID is set by the server and cannot be sent in the request body.

## JSON response format

Success responses contain `success`, `message`, and `data`. List responses additionally contain `meta` with `total`, `page`, and `perPage`. All items are returned on page 1.

```json
{"success":true,"message":"Ingredient retrieved successfully.","data":{"id":"ingredient_1","name":"Tomatoes","quantity":4,"expiryDate":"2026-12-01","ownerId":"user-a"}}
```

Errors contain `success:false` and an `error` with `code` and `message`. Only validation errors contain `details`.

```json
{"success":false,"error":{"code":"VALIDATION_ERROR","message":"Invalid ingredient data.","details":[{"field":"quantity","message":"Quantity must be a positive number no greater than 100000."}]}}
```

## Ingredient fields and validation

| Field | On POST / PUT | Validation |
|---|---|---|
| `name` | Required | String, trimmed, 2–80 characters |
| `quantity` | Required | Number greater than 0 and at most 100000 |
| `expiryDate` | Required | Existing calendar date in `YYYY-MM-DD` format |
| `id` | Response only | Set by the server |
| `ownerId` | Response only | Set by the server, cannot be changed |

Unknown fields are rejected with `400 VALIDATION_ERROR`. `PUT` requires all three fields.

## 1. List ingredients

**`GET /api/v1/ingredients`**

- Headers: `Authorization: Bearer <token>`; roles: user A, user B, admin.
- Path parameters: none. Query parameters: none. Body: none.
- Success: `200 OK`, list of visible ingredients, plus list metadata.
- Errors: `401 UNAUTHORIZED` for missing or invalid bearer token; `405 METHOD_NOT_ALLOWED` for unsupported methods on this path.

Example request:

```http
GET /api/v1/ingredients HTTP/1.1
Authorization: Bearer user-a-token
```

Example response (`200` for initial mock data):

```json
{"success":true,"message":"Ingredients retrieved successfully.","data":[{"id":"ingredient_1","name":"Tomatoes","quantity":4,"expiryDate":"2026-12-01","ownerId":"user-a"},{"id":"ingredient_2","name":"Eggs","quantity":6,"expiryDate":"2026-12-05","ownerId":"user-a"}],"meta":{"total":2,"page":1,"perPage":2}}
```

## 2. Get one ingredient

**`GET /api/v1/ingredients/{id}`**

- Headers: `Authorization: Bearer <token>`; roles: user A, user B, admin.
- Path: required string `id`, e.g. `ingredient_1`. Query/body: none.
- Success: `200 OK` with one ingredient.
- Errors: `401 UNAUTHORIZED`, `403 FORBIDDEN` (belongs to another user), `404 NOT_FOUND` (ID does not exist), `405 METHOD_NOT_ALLOWED`.

Example request:

```http
GET /api/v1/ingredients/ingredient_1 HTTP/1.1
Authorization: Bearer user-a-token
```

Example response (`200`):

```json
{"success":true,"message":"Ingredient retrieved successfully.","data":{"id":"ingredient_1","name":"Tomatoes","quantity":4,"expiryDate":"2026-12-01","ownerId":"user-a"}}
```

## 3. Create ingredient

**`POST /api/v1/ingredients`**

- Headers: `Authorization: Bearer <token>` and `Content-Type: application/json`; roles: user A, user B, admin.
- Path/query parameters: none. Body: required `name`, `quantity`, `expiryDate`.
- Success: `201 Created` with the new ingredient.
- Errors: `400 VALIDATION_ERROR` (missing, wrong or unknown fields, invalid JSON, invalid date), `401 UNAUTHORIZED`, `405 METHOD_NOT_ALLOWED`.

Example request:

```http
POST /api/v1/ingredients HTTP/1.1
Authorization: Bearer user-a-token
Content-Type: application/json

{"name":"Potatoes","quantity":5,"expiryDate":"2026-12-15"}
```

Example response (`201`):

```json
{"success":true,"message":"Ingredient created successfully.","data":{"id":"ingredient_5","name":"Potatoes","quantity":5,"expiryDate":"2026-12-15","ownerId":"user-a"}}
```

## 4. Update ingredient

**`PUT /api/v1/ingredients/{id}`**

- Headers: `Authorization: Bearer <token>` and `Content-Type: application/json`; roles: owner or admin.
- Path: required string `id`. Query: none. Body: all of `name`, `quantity`, `expiryDate`.
- Success: `200 OK` with updated ingredient.
- Errors: `400 VALIDATION_ERROR`, `401 UNAUTHORIZED`, `403 FORBIDDEN`, `404 NOT_FOUND`, `405 METHOD_NOT_ALLOWED`.

Example request:

```http
PUT /api/v1/ingredients/ingredient_1 HTTP/1.1
Authorization: Bearer user-a-token
Content-Type: application/json

{"name":"Tomatoes","quantity":7,"expiryDate":"2026-12-12"}
```

Example response (`200`):

```json
{"success":true,"message":"Ingredient updated successfully.","data":{"id":"ingredient_1","name":"Tomatoes","quantity":7,"expiryDate":"2026-12-12","ownerId":"user-a"}}
```

## 5. Delete ingredient

**`DELETE /api/v1/ingredients/{id}`**

- Headers: `Authorization: Bearer <token>`; roles: owner or admin.
- Path: required string `id`. Query/body: none.
- Success: `204 No Content`.
- Errors: `401 UNAUTHORIZED`, `403 FORBIDDEN`, `404 NOT_FOUND`, `405 METHOD_NOT_ALLOWED`.

Example request:

```http
DELETE /api/v1/ingredients/ingredient_2 HTTP/1.1
Authorization: Bearer user-a-token
```

Example response (`200`):

```json
{"success":true,"message":"Ingredient deleted successfully.","data":null}
```

## 6. HTML greeting

**`GET /api/v1/greeting`**

- Headers: none; public route. Path/query/body: none.
- Success: `200 OK`, `Content-Type: text/html; charset=utf-8`.
- Returns an HTML page with the project description, team members, the list of endpoints and the API status.
- Errors: `405 METHOD_NOT_ALLOWED` for unsupported methods.

Example request:

```http
GET /api/v1/greeting HTTP/1.1
```

Example response (abbreviated HTML):

```html
<!doctype html><html lang="en"><head><title>FridgeChef API</title></head><body><main><h1>FridgeChef API</h1><p>FridgeChef helps students, young professionals, and families...</p></main></body></html>
```

## HTTP errors and response codes

| HTTP | Fixed error code | Meaning |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Missing or invalid fields, wrong types or invalid JSON |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | User tries to access another user's ingredient |
| 404 | `NOT_FOUND` | Ingredient ID or endpoint does not exist |
| 405 | `METHOD_NOT_ALLOWED` | Unsupported HTTP method for a path |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

Only validation errors include `error.details`.

Error examples:

```http
GET /api/v1/ingredients/ingredient_3
Authorization: Bearer user-a-token
```

```json
{"success":false,"error":{"code":"FORBIDDEN","message":"You cannot access another user's ingredient."}}
```

```http
GET /api/v1/ingredients/ingredient_999
Authorization: Bearer admin-token
```

```json
{"success":false,"error":{"code":"NOT_FOUND","message":"Ingredient not found."}}
```
