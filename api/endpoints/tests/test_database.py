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
    assert False


def test_delete_user(test_db: Session):
    """
    This test ensures that a user can be deleted
    from the database.
    """
    assert False


def test_create_note(test_db: Session):
    """
    This test ensures that a note has been created
    successfully under the specific user.
    """
    assert False


def test_delete_note(test_db: Session):
    """
    This test ensures that a note has been deleted
    without having any side effect on the user.
    """
    assert False


def test_update_note(test_db: Session):
    """
    This test ensures that a note has been updated
    successfully with database commands.
    """
    assert False


def test_delete_user_and_notes_cascade(test_db: Session):
    """
    This test ensures that when a user is deleted also
    deletes his/her notes.
    """
    assert False
