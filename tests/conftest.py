"""Спільні фікстури для всіх тестів."""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from booking_service import repository as repo
from booking_service.database import Base, get_db
from booking_service.main import app
from booking_service.models import Hotel, Room

# ── Спільний engine для API тестів ────────────────────────────────────────────

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)


# ── Фікстури ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """TestClient з SQLite замість PostgreSQL."""
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


@pytest.fixture
def db():
    """Окрема SQLite БД для репозиторійних тестів."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def hotel(db):
    """Тестовий готель в БД."""
    return repo.create_hotel(db, "Test Hotel", "Київ", "вул. 1", 4)


@pytest.fixture
def user(db):
    """Тестовий користувач в БД."""
    return repo.create_user(db, "Test User", "test@test.com")


@pytest.fixture
def sample_hotel():
    """Dataclass готель для unit тестів."""
    return Hotel(id=1, name="Test Hotel", city="Київ", address="вул. Тестова, 1", stars=4)


@pytest.fixture
def sample_room():
    """Dataclass кімната для unit тестів."""
    return Room(id=1, hotel_id=1, number="101", room_type="double", price_per_night=1000.0)


@pytest.fixture
def future_dates():
    """Майбутні дати: завтра → через 4 дні."""
    today = date.today()
    return today + timedelta(days=1), today + timedelta(days=4)
