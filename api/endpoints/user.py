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
from sqlalchemy.orm import Session

# Local imports
from api.utils.auth import AuthHandler
from api.meta.constants.schemas import AuthDetails
from api.utils.database import get_db
from api.config import get_settings
from api.meta.constants.errors import (
    USERNAME_TAKEN,
    INVALID_USER_PASSWORD,
    SOMETHING_WENT_WRONG,
)
from api.meta.database.model import User
from api.meta.constants.messages import ACCOUNT_CREATED

####################
# Setup Router
####################

router = APIRouter()
settings = get_settings()
auth_handler = AuthHandler()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_account(
    user_details: AuthDetails,
    db: Session = Depends(get_db),
) -> None:
    """
    This endpoint creates a user account given a username and a password
    in a json payload.

    Args:
        - username: str
        - password: str

    Returns: Response 201 Status Code (Created)

    """

    # avoids creating 2 accounts with the same username
    # this might not avoid entering " monsec" -> "monsec"
    # check that the user is not in the db
    user_details.username = user_details.username.lower()
    user_exists = (
        db.query(User)
        .filter(
            User.username == user_details.username,
        )
        .one_or_none()
    )
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=USERNAME_TAKEN,
        )

    # hash the password and save it
    hashed_password = auth_handler.get_password_hash(user_details.password)

    # create user
    # VULN: shouldn't pass is_admin here (param injection)
    new_user = User(
        username=user_details.username,
        password=hashed_password,
        is_admin=user_details.is_admin,  # This should be patched
    )

    # add user to the db
    try:
        db.add(new_user)
        db.commit()

    # if somethingwent wrong raise exception
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=SOMETHING_WENT_WRONG,
        )

    return {"msg": ACCOUNT_CREATED}


@router.post("/login")
def login(auth_details: AuthDetails, db: Session = Depends(get_db)) -> dict:
    """
    This endpoint logins the user given a username and a password
    in a json payload.
    Args:
        - username: str
        - password: str

    Returns:
        - JWT token if successful
    """

    # get user
    user = (
        db.query(User)
        .filter(
            User.username == auth_details.username.lower(),
        )
        .one_or_none()
    )

    # if the username or the password are not valid
    # raise exception
    if user is None or not auth_handler.verify_password(
        auth_details.password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_USER_PASSWORD,
        )

    # else: return token
    token = auth_handler.encode_token(str(user.id))

    return {"token": token}
