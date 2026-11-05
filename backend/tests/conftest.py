import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, engine, Base


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

