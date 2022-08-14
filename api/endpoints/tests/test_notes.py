"""
test_notes.py
Tests for the user endpoints
"""
from uuid import uuid4, UUID

# Package Imports
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from api.utils.auth import AuthHandler

# Local Imports
from pprint import pprint as pp
from api.main import app

from api.config import get_settings
from api.endpoints.user import users_db

settings = get_settings()
client = TestClient(app)


def test_note_has_been_created_successfully():
    """
    This test ensures that a note under the given
    user has been created
    """

    assert False


def test_note_has_been_deleted_successfully():
    assert False


def test_fetch_all_notes():
    assert False
