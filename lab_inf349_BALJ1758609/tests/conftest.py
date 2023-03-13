import os
import tempfile

os.environ['DATABASE'] = ":memory:"

import pytest
from peewee import SqliteDatabase
from inf349.models import Product
from inf349 import create_app
from inf349.models import get_db_path, Product, Order

@pytest.fixture #configuration des tests et de la base de données 
def app():
    app = create_app({"TESTING": True})

    database = SqliteDatabase(get_db_path())
    database.create_tables([Product, Order])

    yield app

    database.drop_tables([Product, Order])

