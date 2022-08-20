"""
factories.py
Factories for easily creating test data in our tables
"""

# System Imports
import random

# import string
from uuid import uuid4, UUID
from sqlalchemy.orm import Session

import api.meta.database.model as mdl

# Package Imports
from factory import (
    alchemy,
    Faker,
    LazyAttribute,
    SubFactory,
    RelatedFactory,
    List as FakerList,
)


class User_factory(alchemy.SQLAlchemyModelFactory):

    username = Faker("lexify", text="faked-?????")
    password = Faker("lexify", text="faked-?????")

    class Meta:
        model = mdl.User


class Note_factory(alchemy.SQLAlchemyModelFactory):

    title = Faker("lexify", text="random note-????")
    description = Faker("lexify", text="Just another random description - ???")

    class Meta:
        model = mdl.Note
