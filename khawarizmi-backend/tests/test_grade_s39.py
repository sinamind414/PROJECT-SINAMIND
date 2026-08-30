"""S39 — la clé de quota est le COMPTE, pas l'IP (audit surfaces 2026-08-30, F14).

`rate_limit._get_user_plan` décodait le JWT sans `options={"verify_sub": False}`.
Les tokens de l'app portent `sub` en int (cf. deps.get_current_user, qui passe
l'option) → python-jose leve `JWTClaimsError: Subject must be a string.` → l'except
avalait l'erreur → clé retombée sur `get_remote_address(request)`.

Effets sur le chemin élève réel :
  1. quota de correction 15/h partagé par IP. Or uvicorn tourne sans
     `--proxy-headers` derrière le proxy (Dockerfile / railway.toml) : request.client
     est l'IP du proxy → TOUS les élèves du site partagent un seul seau.
  2. le plan `pro` n'étant jamais lu, un élève payant restait borné à 15/h
     (corrections) et 20/h (chat) au lieu de 80/h et 100/h.
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "s39-test-secret-key-0123456789")

from starlette.datastructures import Headers

from auth import create_access_token
from rate_limit import chat_limit, evaluate_limit, get_user_key

RATE_SRC = (Path(__file__).resolve().parent.parent / "rate_limit.py").read_text(encoding="utf-8")


class _Req:
    def __init__(self, authorization: str | None):
        hdrs = {"Authorization": authorization} if authorization else {}
        self.headers = Headers(hdrs)
        self.client = type("C", (), {"host": "203.0.113.9"})()
        self.state = type("S", (), {})()


def _req(sub, plan: str = "free") -> _Req:
    return _Req(f"Bearer {create_access_token({'sub': sub, 'plan': plan})}")


def test_int_sub_token_is_understood():
    """Racine du bug : sub int (format réel des tokens de l'app)."""
    key = get_user_key(_req(4242, "free"))
    assert key == "user:4242:free", f"l'élève authentifié doit être clé par compte, reçu {key}"
    assert key != "203.0.113.9"


def test_str_sub_token_still_understood():
    assert get_user_key(_req("4242", "pro")) == "user:4242:pro"


def test_two_students_do_not_share_the_bucket():
    a, b = get_user_key(_req(111)), get_user_key(_req(222))
    assert a != b


def test_pro_plan_gets_pro_budget():
    assert evaluate_limit(get_user_key(_req(7, "pro"))) == "80/hour"
    assert chat_limit(get_user_key(_req(7, "pro"))) == "100/hour"
    assert evaluate_limit(get_user_key(_req(8, "free"))) == "15/hour"
    assert chat_limit(get_user_key(_req(8, "free"))) == "20/hour"


def test_missing_plan_claim_defaults_free():
    """JWT valide sans claim plan -> free (pas de 500, pas de trou de budget)."""
    req = _Req(f"Bearer {create_access_token({'sub': 99})}")
    assert get_user_key(req) == "user:99:free"
    assert evaluate_limit(get_user_key(req)) == "15/hour"


def test_anonymous_and_garbage_fall_back_to_ip():
    assert get_user_key(_Req(None)) == "203.0.113.9"
    assert get_user_key(_Req("Bearer pas-un-jwt")) == "203.0.113.9"


def test_no_sub_is_rejected_to_ip_not_none_sub():
    """sub absent -> repli IP (jamais 'user:None:free', qui mutualiserait les exclus)."""
    req = _Req(f"Bearer {create_access_token({'plan': 'free'})}")
    assert get_user_key(req) == "203.0.113.9"


def test_verify_sub_option_is_present():
    assert '"verify_sub": False' in RATE_SRC, "sans cette option, tout le monde retombe sur l'IP"


# ── F15 — le bac blanc ne pouvait matcher AUCUNE grille git ─────────────────


def test_bac_blanc_ids_do_not_reach_a_rubric_on_their_own():
    """Preuve du trou : tels qu'ils sont écrits dans le sujet seed, aucun id ne résout."""
    from services.grade_adapter import resolve_question_id

    assert resolve_question_id("s1-e2", "bac:bac-svt-2025:s1-e2") is None


def test_bac_blanc_bridge_resolves_the_git_rubric():
    """Le pont `grade_question_id` (S39) est le premier candidat -> note locale."""
    from services.grade_adapter import resolve_question_id

    assert resolve_question_id("bac2023-s1-ex2-analyse-traduction", "s1-e2") == "bac2023-s1-ex2-analyse-traduction"


def test_bac_blanc_route_passes_the_bridge_first():
    src = (Path(__file__).resolve().parent.parent / "routes" / "bac_blanc.py").read_text(encoding="utf-8")
    i_bridge = src.index('ex.get("grade_question_id")')
    i_ids = src.index("resolve_question_id(")
    assert i_bridge > i_ids, "grade_question_id doit être un candidat de resolve_question_id"
    model = (Path(__file__).resolve().parent.parent / "schemas" / "bac_blanc.py").read_text(encoding="utf-8")
    assert "grade_question_id" in model, "le sujet doit pouvoir porter l'id de grille"


def test_bac_blanc_without_bridge_stays_ungraded_never_zero():
    """Pas de grille -> ungraded (feedback UNGRADED_AR), jamais une note inventée."""
    from services.grade_adapter import UNGRADED_AR, grade_or_none, resolve_question_id

    qid = resolve_question_id("s1-e2", "bac:bac-svt-2025:s1-e2")
    assert grade_or_none(qid, "إجابة التلميذ") is None
    assert "تعذر التصحيح" in UNGRADED_AR and "لا شبكة" in UNGRADED_AR
