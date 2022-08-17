"""
conftest.py
configures our pytest test runner and sets up the local database for testing
"""

#System imports
from re import compile as re_compile

# Package Imports
import pytest
from requests_mock import Mocker
from typing import Generator
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine,event
from sqlalchemy_utils import (
    database_exists,
    create_database,
    drop_database,
)

# Local Imports
from api.main import app
from api.utils.database import get_db
from api.config import get_settings
from api.meta.database.model import Base

# --------------------------------------------------------------------------------

settings = get_settings()

# --------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def test_session(worker_id):

    print("\ninitialising database connection...")

    # Normal Use
    # This will create a new database called "TESTMONSEC" for testing
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://%s:%s@%s/%s" % (
        settings.DATABASE_USER,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_HOST,
        f"TESTMONSEC{worker_id}",
    )

    engine = create_engine(SQLALCHEMY_DATABASE_URL)

    if not database_exists(engine.url):
        print("Creating testdb database...")
        create_database(engine.url)

    else:
        print("Dropping testdb database...")
        drop_database(engine.url)
        print("Creating testdb database...")
        create_database(engine.url)

    # Create the tables from our model definitions
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    print("Initialising test data factory...")

    # Create our database sessionmaker
    SessionLocal = sessionmaker(bind=engine)

    print("Installing PostgreSQL plugins...")
    setup_session = SessionLocal()
    for plugin in settings.POSTGRES_PLUGINS:
        installSQL = f"""CREATE EXTENSION IF NOT EXISTS {plugin};"""
        setup_session.execute(installSQL)
    setup_session.commit()

    return SessionLocal


@pytest.fixture(scope="function")
def test_db(test_session) -> Session:
    """Get the test db session"""

    # Start a new test database connection session
    testDb = test_session()

    try:
        # Begin transaction for direct database edits
        testDb.begin_nested()

        # then each time that SAVEPOINT ends, reopen it
        @event.listens_for(testDb, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

        yield testDb
    finally:
        # Rollback any direct database edits
        testDb.rollback()
        testDb.close()


# Test client for tests to use
@pytest.fixture(scope="function")
def client(test_db) -> Generator:
    def override_db():
        return test_db

    # def override_firebase(Authorization: str = Header(...)):
    #     return firebase_override(Authorization)

    with TestClient(app) as tClient:
        # Begin the transaction for database changes from endpoints
        test_db.begin_nested()

        # Force all endpoints to use our test db session.
        app.dependency_overrides[get_db] = override_db

        # Force all endpoints to use our firebase auth override
        # app.dependency_overrides[require_firebase_auth] = override_firebase

        with Mocker() as adapter:
            matcher = re_compile("http://testserver/")
            adapter.register_uri("GET", matcher, real_http=True)
            adapter.register_uri("POST", matcher, real_http=True)
            adapter.register_uri("PATCH", matcher, real_http=True)
            adapter.register_uri("PUT", matcher, real_http=True)
            adapter.register_uri("DELETE", matcher, real_http=True)
            yield tClient

        # Rollback any changes made to the database from endpoints
        test_db.rollback()