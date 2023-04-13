import datetime
import uuid
from typing import Any, Generator

import jwt
import psycopg2
import pytest
from faker import Factory as FakerFactory
from flask import Flask
from flask.testing import FlaskClient
from psycopg2 import Error
from pytest import FixtureRequest

# FACTORYBOY Integration
from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session

from database import db
from src.app import create_app
from src.config import Config

from .factories import ArticleFactory, SavedArticleFactory, UserInfoFactory

faker = FakerFactory.create()


register(UserInfoFactory)
register(ArticleFactory)
register(SavedArticleFactory)


@pytest.fixture(scope="session", autouse=True)
def create_db():
    con = psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
    )
    con.autocommit = True
    cursor = con.cursor()

    # Create and drop database statement
    create_db_q = f"CREATE DATABASE {Config.POSTGRES_DATABASE};"
    drop_db_q = f"DROP DATABASE IF EXISTS {Config.POSTGRES_DATABASE};"

    try:
        cursor.execute(create_db_q)
    except Error:
        print("DB is already there recreating it.")
    finally:
        cursor.execute(drop_db_q)
        cursor.execute(create_db_q)

    yield

    # Close the connection
    cursor.close()
    # con.close()
    print("PostgreSQL connection closed.")


@pytest.fixture(scope="function")
def engine():
    return create_engine(Config.SQLALCHEMY_DATABASE_URI)


@pytest.fixture(scope="function")
def db_session(engine: Engine) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)

    yield session  # use the session in tests.

    session.close()
    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    transaction.rollback()
    # return connection to the Engine
    connection.close()
    engine.dispose()


@pytest.fixture(scope="function")
def persistent_db_session(engine: Engine) -> Generator[Session, Any, None]:
    """
    Creates a fresh sqlalchemy session for each test that operates in a
    transaction. The transaction is rolled back at the end of each test ensuring
    a clean state.
    """

    # connect to the database
    connection = engine.connect()
    # bind an individual Session to the connection
    session = Session(bind=connection)

    yield session  # use the session in tests.

    session.close()
    # return connection to the Engine
    connection.close()
    engine.dispose()


@pytest.fixture(scope="function")
def app(engine: Engine) -> Generator[Flask, Any, None]:
    """
    Create a fresh database on each test case.
    """
    db.Model.metadata.create_all(bind=engine)  # Create the tables.

    _app = create_app()

    _app.config.update(
        {
            "TESTING": True,
        }
    )

    @_app.teardown_request
    def teardown_request(exception):
        db.session.rollback()
        db.session.remove()

    yield _app

    db.Model.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def client(app: Flask) -> Generator[FlaskClient, Any, None]:
    """
    Create a new Flask TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    yield app.test_client()


# Fixture for Seeding the data to database
def persist_object(db: Session, object):
    db.add(object)
    db.commit()
    return object


pytest.persist_object = persist_object


@pytest.fixture
def seed(request: FixtureRequest, persistent_db_session: Session):
    marker = request.node.get_closest_marker("seed_data")
    if not (marker and marker.args and isinstance(marker.args, tuple)):
        print("_______________________________________________________")
        print("    There is no seed data or not a valid seed data.    ")
        print("-------------------------------------------------------")
        assert False

    for dataset in marker.args:
        entity_name, overridden_attributes = dataset

        factory = request.getfixturevalue(entity_name + "_factory")
        # Attributes can either be passed as a:
        #   * `dict` if there is only one entity record to be seeded
        #   * `list` if there are multiple entity recores to be seeded
        if isinstance(overridden_attributes, dict):
            pytest.persist_object(
                persistent_db_session, factory(**overridden_attributes)
            )
        elif isinstance(overridden_attributes, list):
            for attribute_set in overridden_attributes:
                pytest.persist_object(persistent_db_session, factory(**attribute_set))


IDENTIFIERS = {}


def id_for(key):
    if key not in IDENTIFIERS:
        IDENTIFIERS[key] = str(uuid.uuid4())
    return IDENTIFIERS[key]


def token_for(user_id, exp=3600):
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=exp)
    return jwt.encode(
        {"user_id": user_id, "exp": exp}, Config.JWT_SECRET_KEY, algorithm="HS256"
    )


pytest.id_for = id_for
pytest.token_for = token_for
