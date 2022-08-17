"""
test_notes.py
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

settings = get_settings()


def test_note_has_been_created_successfully(client: TestClient, test_db: Session):
    """
    This test ensures that a note under the given
    user has been created properly.
    """
    # create user
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.User_factory.create()

    response = client.get("/notes/create")
    res_data = response.json()
    assert res_data is not None

    assert False


def test_note_has_been_deleted_successfully():
    """
    This test ensures that the note has been deleted successfully
    when requested.
    """
    assert False


def test_fetch_all_notes():
    """
    This ensures that all the notes of a given user are sent.
    (In general, should be just of the owner, but this is unsafe).

    """
    assert False
