import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# デバッグ情報
print("Current working directory:", os.getcwd())
print("Initial sys.path:", sys.path)

# Pythonパスを明示的に設定
app_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if app_root not in sys.path:
    sys.path.insert(0, app_root)

print("Modified sys.path:", sys.path)
print("App directory exists:", os.path.exists(os.path.join(app_root, 'app')))
print("App directory contents:", os.listdir(os.path.join(app_root, 'app')))

from app.main import app
from app.database import get_db, Base

# テスト用のSQLiteデータベースを使用
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

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
