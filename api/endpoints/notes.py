"""
notes.py
Endpoints for creating, viewing, deleting notes.
"""


# Package imports
from uuid import UUID
from jinja2 import Environment, FileSystemLoader
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from api.config import get_settings

# Local imports
from api.utils.auth import AuthHandler, require_user_account
from api.utils.database import get_db
from api.meta.constants.schemas import NotePayload, NoteDeletePayload, NoteObject
from api.meta.database.model import User, Note
from api.meta.constants.errors import (
    SOMETHING_WENT_WRONG,
    NOTE_DOES_NOT_EXIST,
)
from api.meta.constants.messages import NOTE_DELETED, NOTE_CREATED

# ---------------
# Setup Router
# ---------------
router = APIRouter()
settings = get_settings()
auth_handler = AuthHandler()

get_db = Depends(get_db)
require_user_account = Depends(require_user_account)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=NoteObject | list,
)
def fetch_notes(
    user_id: UUID = Query(None, alias="user-id"),
    user: User = require_user_account,
    db: Session = get_db,
):
    """
    This endpoint requires the user to be authenticated

    NOTE: This endpoint is meant to be vulnerable, this won't
    check for the correct user, only for a valid session.

    Args:
        - user_id:UUID the user_id passed will retrieve the user notes
    Returns:
        - List with secrets of the user
    """
    # If there is no user id input, then use the one from the db
    # NOTE: Vuln here, we should not trust user data
    if user_id is None:
        user_id = user.id

    notes = db.query(Note).filter(Note.user_id == user_id).all()
    return [
        NoteObject(id=note.id, title=note.title, description=note.description)
        for note in notes
    ]


@router.get("/{note_id}", status_code=status.HTTP_200_OK)
def view_note(
    note_id: UUID,
    user=require_user_account,
    db: Session = get_db,
):
    """
    This endpoint returns the note given the UUID

    NOTE: This is meant to be vulnerable, this won't
    check for correct user, only for a valid session.

    Args:
        - note_id: UUID, the UUID of the note to display

    Returns:
        - Jinja2 template rendered (Vulnerability)
    """

    # get note from db
    note = db.query(Note).filter(Note.id == note_id).first()

    template_loader = FileSystemLoader(searchpath=settings.JINJA_FILE_PATH)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(settings.NOTE_TEMPLATE)
    output_text = template.render(note=note)
    print(output_text)
    return output_text


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
)
def create_note(
    note: NotePayload,
    user: User = require_user_account,
    db: Session = get_db,
):
    """
    This creates a note in the given user
    Args:
        - title: str
        - note: str
    Returns:
        Status Code 201 (Created)
    """

    # if correct: create new note
    new_note = Note(
        user_id=user.id,
        title=note.title,
        description=note.description,
    )

    # try to add to the database
    try:
        db.add(new_note)
        db.commit()

    # catch any error
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=SOMETHING_WENT_WRONG,
        )
    return {"msg": NOTE_CREATED}


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
)
def delete_note(
    note: NoteDeletePayload,
    db: Session = get_db,
    user: User = require_user_account,
):

    # retrieve note from db
    note = (
        db.query(Note)
        .filter(
            and_(
                Note.user_id == user.id,
                Note.id == note.id,
            ),
        )
        .one_or_none()
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOTE_DOES_NOT_EXIST,
        )

    # delete note
    try:
        db.delete(note)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=SOMETHING_WENT_WRONG,
        )

    return {"msg": NOTE_DELETED}
