# Verrouille le garde-fou IAM des endpoints admin (correction n°1).
# Faux positif historique corrigé (2026-08-17) : les 3 endpoints analytics
# appellent _require_admin(x_admin_token) — vérifié en live :
#   JWT seul -> 404 · secret faux -> 404 · secret sans JWT -> 401 · secret+JWT -> 200.
import pytest
from fastapi import HTTPException

import routes.admin_analytics as admin_analytics


class _FakeSettings:
    def __init__(self, secret: str):
        self.ADMIN_SECRET = secret


def test_require_admin_refuse_quand_secret_absent(monkeypatch):
    monkeypatch.setattr(admin_analytics, "get_settings", lambda: _FakeSettings(""))
    with pytest.raises(HTTPException) as exc:
        admin_analytics._require_admin("n-importe-quoi")
    assert exc.value.status_code == 404  # fail-closed : jamais exposé par défaut


def test_require_admin_refuse_quand_token_vide(monkeypatch):
    monkeypatch.setattr(admin_analytics, "get_settings", lambda: _FakeSettings("secret"))
    with pytest.raises(HTTPException) as exc:
        admin_analytics._require_admin("")
    assert exc.value.status_code == 404


def test_require_admin_refuse_quand_token_faux(monkeypatch):
    monkeypatch.setattr(admin_analytics, "get_settings", lambda: _FakeSettings("secret"))
    with pytest.raises(HTTPException) as exc:
        admin_analytics._require_admin("mauvais-token")
    assert exc.value.status_code == 404


def test_require_admin_accepte_quand_token_egal_secret(monkeypatch):
    monkeypatch.setattr(admin_analytics, "get_settings", lambda: _FakeSettings("secret"))
    # Aucune exception attendue
    assert admin_analytics._require_admin("secret") is None
