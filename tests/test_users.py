from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from auth import create_access_token, hash_password
from database import get_db
from main import app
from models import User

client = TestClient(app)


def _make_user(name: str, email: str, password: str) -> User:
    return User(id=1, name=name, email=email, password=hash_password(password))


def _valid_token(email: str) -> str:
    return create_access_token({"sub": email})


def _mock_db(setup_fn=None) -> MagicMock:
    mock_db = MagicMock()
    if setup_fn:
        setup_fn(mock_db)
    app.dependency_overrides[get_db] = lambda: print("mock db ถูกเรียก") or mock_db
    return mock_db


def teardown_function():
    app.dependency_overrides.clear()


# --- POST /register ---


def test_register_success():
    mock_db = _mock_db(
        lambda db: db.query.return_value.filter.return_value.first.__setattr__(
            "return_value", None
        )
    )
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.refresh.side_effect = lambda obj: setattr(obj, "id", 1)

    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "password" not in data


def test_register_duplicate_email():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = _make_user(
        "Existing User", "test@example.com", "secret123"
    )
    app.dependency_overrides[get_db] = lambda: print("mock db ถูกเรียก") or mock_db

    response = client.post(
        "/register",
        json={
            "name": "Another User",
            "email": "test@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email นี้มีแล้ว"


# --- POST /login ---


def test_login_success():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = _make_user(
        "Test User", "test@example.com", "secret123"
    )
    app.dependency_overrides[get_db] = lambda: print("mock db ถูกเรียก") or mock_db

    response = client.post(
        "/login", json={"email": "test@example.com", "password": "secret123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = _make_user(
        "Test User", "test@example.com", "secret123"
    )
    app.dependency_overrides[get_db] = lambda: print("mock db ถูกเรียก") or mock_db

    response = client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email หรือ password ไม่ถูกต้อง"


# --- GET /users ---


def test_get_users_with_valid_token():
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [
        _make_user("User One", "one@example.com", "pass1"),
        _make_user("User Two", "two@example.com", "pass2"),
    ]
    app.dependency_overrides[get_db] = lambda: print("mock db ถูกเรียก") or mock_db

    token = _valid_token("test@example.com")
    response = client.get("/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_users_without_token():
    response = client.get("/users")
    assert response.status_code == 401
