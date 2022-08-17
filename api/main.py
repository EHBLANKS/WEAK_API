# Package Imports
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field


# Local Imports
from api.endpoints import user, notes
from api.config import get_settings
from api.meta.constants.errors import BAD_REQUEST

# ------------------------------
settings = get_settings()
# ------------------------------

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)


class WeakApiError(BaseModel):
    user_msg: str = Field(
        "Invalid request to server",
        title="An error message to display for the user",
        example="Invalid request to server",
    )
    msg: int = Field(
        None,
        title="An error message that may contain techincal jargon and be messy",
        example="Either an auto-generated error or a custom verbose error",
    )


class WeakApiErrorResponse(BaseModel):
    detail: WeakApiError


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Override default exception handler to return better exceptions for frontend"""

    if exc.detail == "weak api exception":
        errorDetail = {
            "detail": {
                "user_msg": exc.user_msg,
                "msg": exc.msg,
            }
        }
    else:
        errorDetail = {
            "detail": {
                "user_msg": "Invalid request to server",
                "msg": str(exc.detail),
            }
        }

    response = JSONResponse(content=errorDetail, status_code=exc.status_code)

    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Override default validation handler to return better exceptions for frontend"""

    errorDetail = {
        "detail": {
            "user_msg": "Invalid request to server",
            "msg": str(exc),
        }
    }
    response = JSONResponse(content=errorDetail, status_code=400)

    return response


# --------------------------------------------------------------------------------

DEFAULT_RESPONSE_CODES = {
    422: {},
    400: {"description": BAD_REQUEST, "model": WeakApiErrorResponse},
}


origins = ["http://localhost:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disallow slashes at the end of the endpoint
app.router.redirect_slashes = False


@app.get("/")
async def root():
    return {"msg": "Welcome"}


app.include_router(
    user.router,
    prefix="/user",
    tags=["User"],
    responses=DEFAULT_RESPONSE_CODES,
)

app.include_router(
    notes.router,
    prefix="/notes",
    tags=["Notes"],
    responses=DEFAULT_RESPONSE_CODES,
)
