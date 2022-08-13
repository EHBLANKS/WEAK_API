# Package imports
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4


# Local imports
from api.config import get_settings

# ----------------------
settings = get_settings()
# ----------------------


# ----------------------
# User Schemas
# ----------------------


class AuthDetails(BaseModel):
    username: str = Field(
        title="Account username",
        example="1337Monsec",
    )
    password: str = Field(
        title="The password of the username",
        example="MONSEC{This_is_not_a_flag}",
    )
