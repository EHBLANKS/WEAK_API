"""
notes.py
Endpoints for creating, viewing, deleting notes.
"""


from api.config import get_settings
from fastapi import APIRouter, HTTPException, status, Query, Depends
from api.utils.auth import AuthHandler

# ---------------
# Setup Router
# ---------------
router = APIRouter()
settings = get_settings()
auth_handler = AuthHandler()


@router.get("/notes")
def fetch_notes(user=Depends(auth_handler.auth_wrapper)):
    """
    This endpoint requires the user to be authenticated
    Args:
        - None
    Returns:
        - List with secrets of the user
    """

    pass


@router.post("/notes/create")
def create_note():
    """
    This creates a note in the given user
    Args:
        - title: str
        - note: str
    Returns:
        Status Code 201 (Created)
    """

    pass
