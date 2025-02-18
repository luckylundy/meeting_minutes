# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.core.config import get_settings, Settings

def get_test_settings():
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        DATABASE_URL="sqlite:///./test.db"
    )

# テスト用の設定をオーバーライド
app.dependency_overrides[get_settings] = get_test_settings

# テスト用のデータベースエンジンを作成
test_engine = create_engine(
    get_test_settings().DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()