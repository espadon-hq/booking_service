import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from booking_service import database as db_models  # noqa: F401
from booking_service.database import Base, get_db
from booking_service.main import app
from booking_service.models import Hotel, Room, Booking

# ── API тести (SQLite in-memory) ──────────────────────────────────────────────

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=TEST_ENGINE)

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
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ── Unit тести (dataclass моделі) ─────────────────────────────────────────────

@pytest.fixture
def sample_hotel():
    return Hotel(id=1, name="Test Hotel", city="Київ", address="вул. Тестова, 1", stars=4)


@pytest.fixture
def sample_room():
    return Room(id=1, hotel_id=1, number="101", room_type="double", price_per_night=1000.0)


@pytest.fixture
def future_dates():
    today = date.today()
    return today + timedelta(days=1), today + timedelta(days=4)
