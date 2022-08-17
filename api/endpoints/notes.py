"""
notes.py
Endpoints for creating, viewing, deleting notes.
"""


# Package imports
from uuid import uuid4, UUID
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from api.config import get_settings
from api.utils.auth import AuthHandler
from api.utils.database import get_db

# Local imports
from api.meta.constants.schemas import NotePayload, AuthDetails

# ---------------
# Setup Router
# ---------------
router = APIRouter()
settings = get_settings()
auth_handler = AuthHandler()


@router.get("")
def fetch_notes(
    user=Depends(auth_handler.auth_wrapper),
    db: Session = Depends(get_db),
):
    """
    This endpoint requires the user to be authenticated
    Args:
        - None
    Returns:
        - List with secrets of the user
    """

    pass


@router.post(
    "/notes/create",
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    note: NotePayload,
    user=Depends(auth_handler.auth_wrapper),
):
    """
    This creates a note in the given user
    Args:
        - title: str
        - note: str
    Returns:
        Status Code 201 (Created)
    """

    # TODO:
    # Verify token
    # Check that the note gets posted under the username in the token

    pass


@router.delete(
    "/notes/delete",
    status_code=status.HTTP_202_ACCEPTED,
)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(auth_handler.auth_wrapper),
):
    pass
