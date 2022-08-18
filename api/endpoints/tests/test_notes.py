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
from sqlalchemy import and_
from pprint import pprint as pp

# Local Imports
from api.utils.auth import AuthHandler
import api.meta.database.factories as fac
import api.meta.database.model as mdl
from api.config import get_settings

settings = get_settings()


def login(user_id: str):
    return AuthHandler().encode_token(user_id)


def test_note_has_been_created_successfully(client: TestClient, test_db: Session):
    """
    This test ensures that a note under the given
    user has been created properly.
    """
    # create user
    fac.User_factory._meta.sqlalchemy_session = test_db
    user_id = str(uuid4())
    fac.User_factory.create(id=user_id, username="monsec", password="password")

    # login token
    token = login(user_id)

    headers = {"Authorization": f"Bearer {token}"}
    params = {"title": "My new note", "description": "This note is amazing"}
    response = client.post("/notes/create", json=params, headers=headers)
    res_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED

    # check database
    query = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.user_id == user_id,
                mdl.Note.description == params["description"],
                mdl.Note.title == params["title"],
            ),
        )
        .one_or_none()
    )
    assert query is not None


def test_note_has_been_deleted_successfully(client: TestClient, test_db: Session):
    """
    This test ensures that the note has been deleted successfully
    when requested.
    """
    # create user
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    user_id, note_id = str(uuid4()), str(uuid4())
    fac.User_factory.create(id=user_id, username="monsec", password="password")
    fac.Note_factory.create(id=note_id, user_id=user_id)
    # login token
    token = login(user_id)

    headers = {"Authorization": f"Bearer {token}"}
    params = {"id": note_id}
    response = client.delete("/notes/delete", json=params, headers=headers)
    assert response.status_code == status.HTTP_200_OK

    # check database
    query = (
        test_db.query(mdl.Note)
        .filter(
            and_(
                mdl.Note.user_id == user_id,
                mdl.Note.id == note_id,
            ),
        )
        .one_or_none()
    )
    assert query is None


def test_fetch_all_notes(client: TestClient, test_db: Session):
    """
    This ensures that all the notes of a given user are sent.
    (In general, should be just of the owner, but this is unsafe).

    """
    # create user
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    user_id = str(uuid4())
    fac.User_factory.create(id=user_id, username="monsec", password="password")

    # create 5 random notes
    for _ in range(5):
        fac.Note_factory.create(user_id=user_id)

    # login token
    token = login(user_id)

    # request
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes", headers=headers)
    res_data = response.json()

    assert res_data is not None
    assert response.status_code == status.HTTP_200_OK
    notes = test_db.query(mdl.Note).filter(mdl.Note.user_id == user_id).count()
    assert notes == 5


def test_fetch_all_notes_attacker_user(client: TestClient, test_db: Session):
    """
    This ensures that all the notes of a given user are sent.
    (In general, should be just of the owner, but this is unsafe).

    """
    # create user
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    user_id, attacker_id = str(uuid4()), str(uuid4())
    fac.User_factory.create(id=user_id, username="monsec", password="password")
    fac.User_factory.create(id=attacker_id, username="attacker", password="password")

    # create 5 random notes
    for _ in range(5):
        fac.Note_factory.create(user_id=user_id)

    # login token
    token = login(attacker_id)

    # request
    headers = {"Authorization": f"Bearer {token}"}
    params = {"user-id": user_id}
    response = client.get("/notes", headers=headers, params=params)
    res_data = response.json()
    assert response.status_code == status.HTTP_200_OK

    # assert that 5 items were grabbed from the user monsec
    assert len(res_data) == 5


def test_attacker_attemps_to_delete_other_user_note(
    client: TestClient, test_db: Session
):
    assert False


def test_attacker_attemps_to_post_as_other_user(client: TestClient, test_db: Session):
    assert False
