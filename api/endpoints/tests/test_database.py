"""
test_database.py
Tests for the user endpoints
"""
from uuid import uuid4, UUID

# Package Imports
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pprint import pprint as pp

# Local Imports
from api.utils.auth import AuthHandler
import api.meta.database.factories as fac
import api.meta.database.model as mdl
from api.config import get_settings

# -------------------------
settings = get_settings()
# -------------------------


def test_create_user(test_db: Session):
    """
    This test ensures that a user can be
    created properly.
    """
    user_id = uuid4()
    new_user = mdl.User(
        id=user_id,
        username="test",
        password="random",
    )

    test_db.add(new_user)
    test_db.commit()

    assert (
        test_db.query(mdl.User)
        .filter(
            and_(
                mdl.User.username == "test",
                mdl.User.id == user_id,
            )
        )
        .one_or_none()
        is not None
    )


def test_delete_user(test_db: Session):
    """
    This test ensures that a user can be deleted
    from the database.
    """
    # setup (Create user)
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = uuid4()
    fac.User_factory.create(id=user_id, username="test")

    # assert that the user exists in the db
    user = test_db.query(mdl.User).filter(mdl.User.id == user_id).one_or_none()
    assert user is not None

    # delete the user
    test_db.delete(user)
    test_db.commit()
    user = test_db.query(mdl.User).filter(mdl.User.id == user_id).one_or_none()
    assert user is None


def test_create_note(test_db: Session):
    """
    This test ensures that a note has been created
    successfully under the specific user.
    """
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = uuid4()
    fac.User_factory.create(id=user_id)

    # create note for user
    note_id = uuid4()
    new_note = mdl.Note(
        id=note_id,
        title="note for testing",
        description="WOOOO, a nice test!",
        user_id=user_id,
    )

    # add new note to the database
    test_db.add(new_note)
    test_db.commit()

    # assert that the note was created and is in the db
    note = test_db.query(mdl.Note).filter(mdl.Note.id == note_id).one_or_none()
    assert note is not None


def test_add_note_no_user(test_db: Session):
    """
    This test ensures that a user must be added to the note,
    otherwise it fails.
    """
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = uuid4()

    # create note for user
    note_id = uuid4()
    new_note = mdl.Note(
        id=note_id,
        title="note for testing",
        description="WOOOO, a nice test!",
        user_id=user_id,  # unexistent user
    )

    try:
        # add new note to the database
        test_db.add(new_note)
        test_db.commit()
        # if it gets to this point, then it added it
        # which shouldn't happen
        assert False
    except Exception:
        test_db.rollback()
        assert True

    # assert that the note was not created due to key constraints and null fields
    note = test_db.query(mdl.Note).filter(mdl.Note.id == note_id).one_or_none()
    assert note is None


def test_delete_note(test_db: Session):
    """
    This test ensures that a note has been deleted
    without having any side effect on the user.
    """
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db

    user_id, note_id = uuid4(), uuid4()
    fac.User_factory.create(id=user_id, username="tester")
    fac.Note_factory.create(
        id=note_id,
        title="note",
        description="description of the note",
        user_id=user_id,
    )

    # check that the note has been created under the specified user
    note = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.id == note_id,
                mdl.Note.user_id == user_id,
            )
        )
        .one_or_none()
    )
    assert note is not None

    # delete the note
    test_db.delete(note)
    test_db.commit()

    # check that the user had no issue
    user = test_db.query(mdl.User).filter(mdl.User.id == user_id).one_or_none()
    assert user is not None


def test_update_note(test_db: Session):
    """
    This test ensures that a note has been updated
    successfully with database commands.
    """

    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db

    user_id, note_id = uuid4(), uuid4()
    fac.User_factory.create(id=user_id, username="tester")
    fac.Note_factory.create(
        id=note_id,
        title="note",
        description="description of the note",
        user_id=user_id,
    )

    # check that the note has been created under the specified user
    note = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.id == note_id,
                mdl.Note.user_id == user_id,
            )
        )
        .one_or_none()
    )
    assert note is not None

    # update the note title and description
    note.title = "New title!"
    note.description = "New description!"
    test_db.commit()

    note = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.id == note_id,
                mdl.Note.user_id == user_id,
            )
        )
        .one_or_none()
    )
    assert note is not None
    assert note.title == "New title!"
    assert note.description == "New description!"


def test_delete_user_and_notes_cascade(test_db: Session):
    """
    This test ensures that when a user is deleted also
    deletes his/her notes.
    """
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db

    user_id, note_id = uuid4(), uuid4()
    fac.User_factory.create(id=user_id, username="tester")
    fac.Note_factory.create(
        id=note_id,
        title="note",
        description="description of the note",
        user_id=user_id,
    )

    # check that the note has been created under the specified user
    note = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.id == note_id,
                mdl.Note.user_id == user_id,
            )
        )
        .one_or_none()
    )
    assert note is not None

    # delete user
    user = test_db.query(mdl.User).filter(mdl.User.id == user_id).one_or_none()
    test_db.delete(user)
    test_db.commit()

    # check that the note has been deleted
    note = test_db.query(mdl.Note).filter(mdl.Note.id == note_id).one_or_none()
    assert note is None
