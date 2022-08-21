"""
test_user.py
Tests for the user endpoints
"""
from uuid import uuid4, UUID

# Package Imports
from fastapi.testclient import TestClient
from fastapi import status
from api.utils.auth import AuthHandler
from sqlalchemy.orm.session import Session

# Local Imports
from api.meta.constants.errors import INVALID_USER_PASSWORD, USERNAME_TAKEN
from api.meta.constants.messages import ACCOUNT_CREATED
import api.meta.database.model as mdl
import api.meta.database.factories as fac
from api.config import get_settings

settings = get_settings()


def login(user_id: UUID):
    return AuthHandler().encode_token(user_id)


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
    assert res_data is not None
    assert response.status_code == status.HTTP_201_CREATED
    assert res_data["msg"] == ACCOUNT_CREATED
    # check that the user has been created in the database properly
    query = test_db.query(mdl.User).filter(mdl.User.username == "MONSEC").one_or_none()
    assert query is not None


def test_user_creation_same_user(client: TestClient, test_db: Session):
    """This test avoids the creation of multiple users with the same name"""
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = uuid4()
    fac.User_factory.create(id=user_id, username="MONSEC")

    # try to create the same user
    params = {"username": "MONSEC", "password": "123"}
    response = client.post(
        "/user/signup",
        json=params,
    )
    res_data = response.json()

    # assert that we got an error
    assert res_data is not None
    assert res_data["detail"]["msg"] == USERNAME_TAKEN

    # check there is only one user with 'MONSEC' username
    query = (
        test_db.query(mdl.User)
        .filter(
            mdl.User.username == "MONSEC",
        )
        .count()
    )
    assert query == 1


def test_user_login(client: TestClient, test_db: Session):
    """
    This test ensures that once the user has been registered, it can access
    It also ensures that it matches passwords with given username
    """
    # Create account
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = str(uuid4())
    password = AuthHandler().get_password_hash("MONSEC")
    fac.User_factory.create(id=user_id, username="MONSEC", password=password)

    # Login into account
    params = {"username": "MONSEC", "password": "MONSEC"}
    response = client.post("/user/login", json=params)
    res_data = response.json()
    assert res_data is not None
    token = AuthHandler().decode_token(res_data["token"])
    assert token["id"] == user_id


def test_user_login_wrong_password(client: TestClient):
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


def test_attacker_gets_admin_privileges_during_signup(
    client: TestClient, test_db: Session
):
    """
    This test ensures that an attacker can get admin by saying is_admin = True
    when signing up.
    """

    payload = {
        "username": "attacker",
        "password": "1337",
        "is_admin": True,
    }
    response = client.post("/user/signup", json=payload)
    res_data = response.json()
    assert res_data["msg"] == ACCOUNT_CREATED
    assert response.status_code == status.HTTP_201_CREATED

    # check the db
    user = test_db.query(mdl.User).filter(mdl.User.username == "attacker").one_or_none()
    assert user is not None
    assert user.is_admin is True


def test_user_is_not_admin_by_default(client: TestClient, test_db: Session):
    """
    This test ensures that a normal signup will by default set is_admin as False
    without passing any parameter 'is_admin'.
    """
    payload = {
        "username": "user",
        "password": "1337",
    }
    response = client.post("/user/signup", json=payload)
    res_data = response.json()
    assert res_data["msg"] == ACCOUNT_CREATED
    assert response.status_code == status.HTTP_201_CREATED

    # check the db
    user = test_db.query(mdl.User).filter(mdl.User.username == "user").one_or_none()
    assert user is not None
    assert user.is_admin is False
