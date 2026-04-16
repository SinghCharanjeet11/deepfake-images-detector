"""
Pytest fixtures shared across all tests.

Key design: SQLite :memory: databases are per-connection. To share tables
between the fixture and the route handlers, we must use a single connection
and bind all sessions to it.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from database.models import Base


@pytest.fixture(scope="function")
def client():
    """
    For each test:
      1. Open one SQLite in-memory connection
      2. Create all tables on that connection
      3. Override get_db() so every session in the app uses that same connection
      4. Yield the test client
      5. Drop all tables and close the connection
    """
    from main import app
    from database.connection import get_db

    # Single connection — all sessions must use this so they share the same DB
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    connection = engine.connect()
    Base.metadata.create_all(bind=connection)

    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=connection)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=connection)
    connection.close()
    engine.dispose()


@pytest.fixture(scope="function")
def db(client):
    """
    Yields a session on the same in-memory connection so tests can
    insert seed data that the route handlers will see.

    Depends on `client` to ensure the connection and tables exist first.
    """
    from database.connection import get_db
    from main import app

    # Grab a session from the same override that the app is using
    gen = app.dependency_overrides[get_db]()
    session = next(gen)
    try:
        yield session
    finally:
        session.commit()
        try:
            next(gen)
        except StopIteration:
            pass
