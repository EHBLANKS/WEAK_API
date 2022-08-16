"""
conftest.py
configures our pytest test runner and sets up the local database for testing
"""


# Package Imports
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from fastapi import HTTPException, status, Header
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_utils import (
    database_exists,
    create_database,
    drop_database,
)

# Local Imports
from api.main import app
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
    test_db = test_session()

    try:
        # Begin transaction for direct database edits
        test_db.begin_nested()

        # then each time that SAVEPOINT ends, reopen it
        @event.listens_for(test_db, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.begin_nested()

        yield test_db
    finally:
        # Rollback any direct database edits
        test_db.rollback()
        test_db.close()
