import os

os.environ["JWT_SECRET"] = "test-secret-with-at-least-32-characters"

from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.core.security import ALGORITHM
from jose import jwt
from backend.app.core.config import settings


def test_password_hashing_and_length_limit():
    password = "CorrectHorseBattery12"
    password_hash = hash_password(password)
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)
    assert not verify_password("x" * 73, password_hash)


def test_access_token_contains_identity_and_role():
    token = create_access_token("operator", "OPERATOR")
    claims = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    assert claims["sub"] == "operator"
    assert claims["role"] == "OPERATOR"
