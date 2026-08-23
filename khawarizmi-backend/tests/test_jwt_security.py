"""Régressions de sécurité JWT après migration python-jose → PyJWT."""
from datetime import UTC, datetime, timedelta
from importlib.util import find_spec
from pathlib import Path

import jwt
import pytest

from config import Settings


def test_requirements_use_pyjwt_without_vulnerable_ecdsa_dependency():
    requirements = (Path(__file__).parents[1] / "requirements.txt").read_text(encoding="utf-8")
    assert "PyJWT[crypto]==2.13.0" in requirements
    assert "python-jose" not in requirements
    assert find_spec("ecdsa") is None


def test_hs256_roundtrip_accepts_historical_integer_subject():
    secret = "s" * 32
    token = jwt.encode(
        {"sub": 42, "exp": datetime.now(UTC) + timedelta(minutes=5)},
        secret,
        algorithm="HS256",
    )
    payload = jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"verify_sub": False},
    )
    assert payload["sub"] == 42


def test_algorithm_confusion_is_rejected():
    secret = "s" * 32
    token = jwt.encode(
        {"sub": "42", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        secret,
        algorithm="HS256",
    )
    with pytest.raises(jwt.exceptions.InvalidAlgorithmError):
        jwt.decode(token, secret, algorithms=["RS256"])


def test_production_secret_requires_32_bytes(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    with pytest.raises(ValueError, match="Minimum 32 octets"):
        Settings(SECRET_KEY="too-short")
    settings = Settings(SECRET_KEY="x" * 32)
    assert len(settings.SECRET_KEY.encode("utf-8")) == 32
