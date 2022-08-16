"""
config.py
Stores settings that may change over time in project
Uses .env to store settings that change between environments, and for secrets.
"""
# System Imports
from datetime import timedelta
from functools import lru_cache
from json import loads
import os
from enum import Enum

# Package Imports
from pydantic import BaseSettings

# Local Imports

# --------------------------------------------------------------------------------

# We cannot import from anything else in config.py so sadly our environment types needs
# to be duplicated here. sorry.


@lru_cache()
def get_settings():
    return Settings()


def get_version():
    """We do this so that we can easily increment the version number in our version file"""

    script_dir = os.path.dirname(__file__)  # absolute dir this script is in
    rel_path = "version.json"
    abs_file_path = os.path.join(script_dir, rel_path)

    with open(abs_file_path, "r") as f:
        version = loads(f.read())
        return version


class Settings(BaseSettings):

    # Metadata
    APP_TITLE: str = "DVWA"
    APP_DESCRIPTION: str = "DAMN VULNERABLE WEB API"
    APP_VERSION: str = get_version()

    # Connection to Postgres database
    DATABASE_HOST: str = ""
    DATABASE_USER: str = ""
    DATABASE_PASSWORD: str = ""
    DATABASE_NAME: str = ""
    POSTGRES_PLUGINS = ["fuzzystrmatch"]

    SECRET = ""
    FLAG = "MONSEC{sup3r_s3cr3t_fl4g}"

    class Config:
        env_file = ".env"
