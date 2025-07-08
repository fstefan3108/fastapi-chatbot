from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from app.api.deps import get_db, get_current_user
from app.db.base import Base
from app.main import app
from sqlalchemy import create_engine, StaticPool
import pytest

from app.models.website import Website

SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "stefan", "id": 23}

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def seeded_website():
    db = next(override_get_db())
    website = Website(
        id=47,
        title="Test Website",
        url="https://www.invt.tech/",
        chunks="Some Chunks",
        owner_id=19
    )
    db.add(website)
    db.commit()
    db.refresh(website)
    return website


@pytest.fixture(scope="function")
def test_client():
    with TestClient(app) as client:
        yield client