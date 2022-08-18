# Package imports
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4, UUID
from sqlalchemy.orm import relationship

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


# ----------------------
# Note Schemas
# ----------------------


class NotePayload(BaseModel):
    title: str = Field(
        title="The note title",
        example="My super secret",
    )
    description: str = Field(
        title="description of the note or the note itself",
        example="You may not know, but you can get others notes",
    )


class NoteDeletePayload(BaseModel):
    id: UUID = Field(
        title="The uuid of the note to delete",
        example=uuid4(),
    )
