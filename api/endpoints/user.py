"""
user.py
Endpoints for creating, viewing, deleting and managing users.
"""

# System Imports
from uuid import UUID, uuid4

# Package Imports
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional
from api.utils.auth import AuthHandler
from api.meta.constants.schemas import AuthDetails


# Local imports
from api.config import get_settings
from api.meta.constants.errors import USERNAME_TAKEN, INVALID_USER_PASSWORD

####################
# Setup Router
####################

router = APIRouter()
settings = get_settings()
auth_handler = AuthHandler()

# we use this as db instead of a proper database for simplicity
users_db = []


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_account(user_details: AuthDetails) -> None:
    """
    This endpoint creates a user account given a username and a password
    in a json payload.

    Args:
        - username: str
        - password: str

    Returns: Response 201 Status Code (Created)

    """

    # avoids creating 2 accounts with the same username
    # this does not avoid entering " monsec" -> "monsec"
    if any([user["username"] == user_details.username for user in users_db]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USERNAME_TAKEN,
        )

    # hash the password and save it
    hashed_password = auth_handler.get_password_hash(user_details.password)
    users_db.append(
        {
            "username": user_details.username,
            "password": hashed_password,
            "notes": [],
        }
    )

    return


@router.post("/login")
def login(auth_details: AuthDetails) -> dict:
    """
    This endpoint logins the user given a username and a password
    in a json payload.
    Args:
        - username: str
        - password: str

    Returns:
        - JWT token if successful
    """
    user = None
    for _user in users_db:
        if _user["username"] == auth_details.username:
            user = _user
            break

    # if the username or the password are not valid
    # raise exception
    if user is None or not auth_handler.verify_password(
        auth_details.password, user["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_USER_PASSWORD,
        )

    # else: return token
    token = auth_handler.encode_token(user["username"])

    return {"token": token}


@router.post("/protected")
def protected(username=Depends(auth_handler.auth_wrapper)):
    return {"name": username}
