from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from auth import create_access_token, hash_password, verify_password, verify_token
from database import get_db
from main import app
from models import User

client = TestClient(app)


# --- auth.py unit tests ---


def test_hash_password_returns_string():
    hashed = hash_password("mypassword")
    assert isinstance(hashed, str)


def test_hash_password_is_not_plaintext():
    hashed = hash_password("mypassword")
    assert hashed != "mypassword"


def test_verify_password_correct():
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("mypassword")
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)


def test_verify_token_valid():
    token = create_access_token({"sub": "test@example.com"})
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"


def test_verify_token_invalid():
    payload = verify_token("notavalidtoken")
    assert payload is None


# --- POST /login endpoint tests ---


def _make_user(email: str, password: str) -> User:
    return User(id=1, name="Test User", email=email, password=hash_password(password))


def teardown_function():
    app.dependency_overrides.clear()


def test_login_success():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = _make_user(
        "test@example.com", "secret"
    )
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/login", json={"email": "test@example.com", "password": "secret"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = _make_user(
        "test@example.com", "secret"
    )
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/login", json={"email": "test@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email หรือ password ไม่ถูกต้อง"


def test_login_user_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.post(
        "/login", json={"email": "nobody@example.com", "password": "secret"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email หรือ password ไม่ถูกต้อง"


def test_login_missing_fields():
    response = client.post("/login", json={"email": "test@example.com"})
    assert response.status_code == 422
