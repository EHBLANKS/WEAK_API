"""
conftest.py
configures our pytest test runner and sets up the local database for testing
"""


# Package Imports
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from fastapi import HTTPException, status, Header

# Local Imports
from api.main import app
from api.config import get_settings

# --------------------------------------------------------------------------------

settings = get_settings()

# --------------------------------------------------------------------------------
