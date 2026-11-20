from datetime import date
from html import escape
import re

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="FridgeChef API", version="1.0.0", docs_url=None, redoc_url=None, openapi_url=None)
