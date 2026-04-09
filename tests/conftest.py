from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dependencies.db import get_db
from app.main import app
from app.models import Base


def get_test_database_url() -> str:
    return os.getenv("TEST_DATABASE_URL", "sqlite+pysqlite:///:memory:")


@pytest.fixture(scope="session")
def db_engine():
    connect_args = {"check_same_thread": False} if get_test_database_url().startswith("sqlite") else {}
    engine = create_engine(get_test_database_url(), future=True, connect_args=connect_args)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
