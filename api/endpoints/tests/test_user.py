"""
test_user.py
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
from api.meta.constants.errors import INVALID_USER_PASSWORD, USERNAME_TAKEN

from api.config import get_settings
from api.endpoints.user import users_db

settings = get_settings()
client = TestClient(app)


def test_user_creation():
    """
    This test ensures that the user gets created
    It also ensures no duplication of users.
    """

    params = {"username": "MONSEC", "password": "123"}
    response = client.post(
        "/user/create-account",
        json=params,
    )
    res_data = response.json()
    assert res_data is None
    assert len(users_db) == 1
    assert response.status_code == status.HTTP_201_CREATED
    assert any([user["username"] == "MONSEC" for user in users_db])

    # PART 2
    # Creation of the same user again, different password (trivial)
    params = {"username": "MONSEC", "password": "321"}
    response = client.post(
        "/user/create-account",
        json=params,
    )
    res_data = response.json()
    assert res_data is not None
    assert len(users_db) == 1
    assert res_data["detail"]["msg"] == USERNAME_TAKEN


def test_user_login():
    """
    This test ensures that once the user has been registered, it can access
    It also ensures that it matches passwords with given username
    """

    # PART 1
    # Create account
    params = {"username": "notadmin", "password": "supersecret"}
    response = client.post("/user/create-account", json=params)
    assert response.status_code == status.HTTP_201_CREATED

    # Login into account
    response = client.post("/user/login", json=params)
    res_data = response.json()
    assert res_data is not None
    token = AuthHandler().decode_token(res_data["token"])
    assert token["id"] == "notadmin"

    # Fail to login into account
    params = {"username": "notadmin", "password": "123"}
    response = client.post("/user/login", json=params)
    res_data = response.json()
    assert res_data is not None
    assert res_data["detail"]["msg"] == INVALID_USER_PASSWORD
