"""
database.py
Connection to the pg database
"""
# Package imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local imports
from api.config import get_settings


# -------------------------
settings = get_settings()
# ------------------------


def get_db():
    """
    Get the db session
    """
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://%s:%s@%s/%s" % (
        settings.DATABASE_USER,
        settings.DATABASE_PASSWORD,
        settings.DATABASE_HOST,
        settings.DATABASE_NAME,
    )

    db_config = {
        # Maximum number of permanent connections to keep.
        "pool_size": 5,
        # Temporarily exceeds the set pool size if no connections are available
        "max_overflow": 2,
        "pool_timeout": 30,  # 30 seconds
        # maximum number of seconds a connection can persist
        "pool_recycle": 1800,  # 30 minutes
    }

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"connection_timeout": 15},
        **db_config,
    )

    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
