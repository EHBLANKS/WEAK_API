"""
test_notes.py
Tests for the user endpoints
"""
from uuid import uuid4

# Package Imports
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Local Imports
from api.utils.auth import AuthHandler
import api.meta.database.factories as fac
import api.meta.database.model as mdl
from api.config import get_settings
from api.meta.constants.errors import NOTE_DOES_NOT_EXIST, USER_NOT_AUTHORIZED

# -------------------------
settings = get_settings()
# -------------------------


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
    response = client.post("/notes", json=params, headers=headers)
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
    response = client.delete("/notes", json=params, headers=headers)
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
    """
    This test ensures that an 'attacker' cannot delete other's notes.
    """
    # setup
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db

    # create user and note
    user_id, attacker_id, note_id = str(uuid4()), str(uuid4()), str(uuid4())
    fac.User_factory.create(id=user_id)
    fac.User_factory.create(id=attacker_id)

    # create note as normal user
    fac.Note_factory.create(id=note_id, user_id=user_id)

    # login token as attacker
    token = login(attacker_id)

    payload = {"id": note_id}
    headers = {"Authorization": f"Bearer {token}"}

    # attacker sends the note_id of another user, while authorized
    response = client.delete("/notes", headers=headers, json=payload)
    res_data = response.json()
    assert res_data is not None
    assert res_data["detail"]["msg"] == NOTE_DOES_NOT_EXIST


def test_attacker_attempts_to_get_another_user_note(
    client: TestClient, test_db: Session
):
    """
    This test ensures that an attacker can see any user's note
    requirement: have a valid session and send the note UUID.
    """
    # setup
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    user_id, note_id, attacker_id = str(uuid4()), str(uuid4()), str(uuid4())

    # create note,user and attacker
    fac.User_factory.create(id=user_id, username="MONSEC")
    fac.User_factory.create(id=attacker_id, username="ATTACKER")
    fac.Note_factory.create(
        id=note_id,
        user_id=user_id,
        title="my secure note",
    )

    # login
    token = login(attacker_id)

    # request by attacker to get the user note
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/notes/{note_id}", headers=headers)
    res_data = response.json()
    print(res_data)
    assert res_data is not None
    assert response.status_code == status.HTTP_200_OK


def test_an_unprivileged_attacker_attempts_to_get_an_admin_secrets(
    client: TestClient, test_db: Session
):
    """
    This test ensures that an attacker without admin privileges
    cannot see any admin's notes.
    """
    # setup
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    admin_id, note_id, attacker_id = str(uuid4()), str(uuid4()), str(uuid4())

    # create note,user and attacker
    fac.User_factory.create(id=admin_id, username="ADMIN", is_admin=True)
    fac.User_factory.create(id=attacker_id, username="ATTACKER")
    fac.Note_factory.create(
        id=note_id,
        user_id=admin_id,
        title="DO NOT READ",
        description="I AM THE ADMIN, I HAVE POWER!",
    )

    # login
    token = login(attacker_id)

    # request by attacker to get the user note
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/notes/{note_id}", headers=headers)
    res_data = response.json()
    print(res_data)
    assert res_data is not None
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert res_data["detail"]["msg"] == USER_NOT_AUTHORIZED


def test_a_privileged_attacker_attempts_to_get_an_admin_notes(
    client: TestClient, test_db: Session
):
    """
    This test ensures that an attacker with privileges can obtain
    any admins notes by passing the UUID.
    """
    # setup
    fac.User_factory._meta.sqlalchemy_session = test_db
    fac.Note_factory._meta.sqlalchemy_session = test_db
    admin_id, note_id, attacker_id = str(uuid4()), str(uuid4()), str(uuid4())

    # create note,user and attacker
    fac.User_factory.create(id=admin_id, username="ADMIN", is_admin=True)
    fac.User_factory.create(id=attacker_id, username="ATTACKER", is_admin=True)
    fac.Note_factory.create(
        id=note_id,
        user_id=admin_id,
        title="DO NOT READ",
        description="I AM THE ADMIN, I HAVE POWER!",
    )

    # login
    token = login(attacker_id)

    # request by attacker to get the user note
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/notes/{note_id}", headers=headers)
    res_data = response.json()
    print(res_data)
    assert res_data is not None
    assert response.status_code == status.HTTP_200_OK
    assert "DO NOT READ" in res_data["title"]
    assert "I AM THE ADMIN, I HAVE POWER!" in res_data["description"]
