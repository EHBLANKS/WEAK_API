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
from sqlalchemy.orm.session import Session

# Local Imports
from api.main import app
from api.meta.constants.errors import INVALID_USER_PASSWORD, USERNAME_TAKEN
import api.meta.database.model as mdl

from api.config import get_settings
from pprint import pprint as pp

settings = get_settings()


def test_user_creation(client: TestClient, test_db: Session):
    """
    This test ensures that the user gets created
    It also ensures no duplication of users.
    """

    params = {"username": "MONSEC", "password": "123"}
    response = client.post(
        "/user/signup",
        json=params,
    )
    res_data = response.json()
    assert res_data is None
    assert response.status_code == status.HTTP_201_CREATED
    # check that the user has been created in the database properly
    query = test_db.query(mdl.User).filter(mdl.User.username == "MONSEC").one_or_none()
    assert query is not None


def test_user_creation_same_user(client: TestClient, test_db: Session):
    """This test avoids the creation of multiple users with the same name"""

    params = {"username": "MONSEC", "password": "123"}
    response = client.post(
        "/user/signup",
        json=params,
    )
    res_data = response.json()
    assert res_data is None

    # once created, check is in the database
    query = test_db.query(mdl.User).filter(mdl.User.username == "MONSEC").first()
    assert query is not None
    assert response.status_code == status.HTTP_201_CREATED

    # Creation of the same user again, different password (trivial)
    response = client.post(
        "/user/signup",
        json=params,
    )
    res_data = response.json()
    assert res_data is not None
    assert test_db.query(mdl.User).count() == 1
    assert res_data["detail"]["msg"] == USERNAME_TAKEN


def test_user_login(client: TestClient, test_db: Session):
    """
    This test ensures that once the user has been registered, it can access
    It also ensures that it matches passwords with given username
    """

    # PART 1
    # Create account
    params = {"username": "notadmin", "password": "supersecret"}
    response = client.post("/user/signup", json=params)
    assert response.status_code == status.HTTP_201_CREATED

    # Login into account
    response = client.post("/user/login", json=params)
    res_data = response.json()
    assert res_data is not None
    token = AuthHandler().decode_token(res_data["token"])
    assert token["id"] == "notadmin"


def test_user_login_wrong_password(client: TestClient, test_db: Session):
    """
    This test ensures that wrong passwords will return an error
    """
    # PART 1
    # Create account
    params = {"username": "notadmin", "password": "supersecret"}
    response = client.post("/user/signup", json=params)
    assert response.status_code == status.HTTP_201_CREATED

    # Fail to login into account
    params = {"username": "notadmin", "password": "123"}
    response = client.post("/user/login", json=params)
    res_data = response.json()
    assert res_data is not None
    assert res_data["detail"]["msg"] == INVALID_USER_PASSWORD
