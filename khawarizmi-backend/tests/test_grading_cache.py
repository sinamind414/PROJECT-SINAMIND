"""tests/test_grading_cache.py — Cache de correction exact (audit C2).

Tests d'acceptation C2 (plan réconcilié) :
- 2e envoi identique → hit cache, 0 appel LLM, source d'origine PRÉSERVÉE
  (grading_source_total fidèle) + from_cache=True
- Espaces de tête/traîne → hit (option 1 sûre : lstrip/rstrip, delta reprojeté)
  ; espaces INTERNES ou CRLF → miss documenté (zéro risque d'offset)
- Hashes élèves recalculés par copie (jamais lus du cache) — traçabilité RGPD
- Une note dégradée (local_fallback) n'est JAMAIS cachée (équité)
- Rejet sanity → jamais de lookup cache, jamais de store
- Bump de version de prompt → invalidation passive (clé différente)
- Single-flight : 10 corrections concurrentes identiques → 1 seul appel LLM
- Aucun llm_raw / student_answer / hash élève dans le payload caché
- TTL 7 jours (CORRECTION_CACHE_TTL)
"""

import asyncio
import json
import time
from unittest.mock import AsyncMock

import pytest

from app_state import state
from cache import get_cache
from grading import cache as grading_cache
from grading import cache_key as grading_cache_key
from grading.cache import (
    CACHE_PARSE_ALLOWED,
    evaluate_with_cache,
    is_cacheable,
    to_cache_payload,
)
from grading.cache_key import (
    CORRECTION_CACHE_TTL,
    build_correction_key,
    key_normalize,
)

# ── Fake Redis asynchrone (get/setex/set nx/ex/exists/eval) ──────────


class FakeRedis:
    """Implémentation minimale in-memory de l'API redis.asyncio utilisée."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._expiry: dict[str, float] = {}

    def _prune(self, key: str) -> None:
        if key in self._expiry and self._expiry[key] < time.monotonic():
            del self._data[key]
            del self._expiry[key]

    async def get(self, key: str) -> str | None:
        self._prune(key)
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self._data[key] = value
        self._expiry[key] = time.monotonic() + ttl

    async def set(self, key: str, value: str, nx: bool = False, ex: int | None = None):
        self._prune(key)
        if nx and key in self._data:
            return False
        self._data[key] = value
        if ex:
            self._expiry[key] = time.monotonic() + ex
        return True

    async def exists(self, key: str) -> int:
        self._prune(key)
        return 1 if key in self._data else 0

    async def delete(self, key: str) -> int:
        existed = key in self._data
        self._data.pop(key, None)
        self._expiry.pop(key, None)
        return 1 if existed else 0

    async def eval(self, _lua: str, _numkeys: int, key: str, token: str) -> int:
        """CAS : ne supprime le verrou que si le token est le nôtre."""
        if self._data.get(key) == token:
            await self.delete(key)
            return 1
        return 0


@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(state, "redis", fake)
    return fake


# ── Helpers ──────────────────────────────────────────────────────────

ANS = "نلاحظ من الوثيقة أن نسبة الغلوكوز تزداد من 0.8 إلى 1.4 غ/ل"
QID = 42
VERB = "analyse"
SMAX = 7


def _llm_result(score: int = 5, highlights=None, source: str = "llm") -> dict:
    return {
        "source": source,
        "score": score,
        "score_max": SMAX,
        "percentage": round((score / SMAX) * 100),
        "highlights": highlights or [
            {"start": 4, "end": 8, "type": "good_element", "message_ar": "عنصر صحيح"},
        ],
        "matched_criteria": ["تقديم الوثيقة"],
        "unmatched_criteria": [],
        "feedback_ar": "إجابة متوسطة",
        "advice_ar": "أضف التفاصيل",
        "confidence": 0.85,
        "sanity_code": "ok",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "finish_reason": "stop",
        "prompt_hash": "abc123",
        "student_answer_hash": "student-a",
        "llm_raw_hash": "raw-a",
        "parse_status": "ok" if source == "llm" else "recovered",
        "missing": [],
        "dominant_error_code": "partial_correct",
        "success": ["تقديم الوثيقة"],
        "errors": [],
        "remediation": {"advice_ar": "revise le cours"},
    }


def _make_evaluate_fn(return_result: dict | None = None, side_effect=None):
    """Mock asynchrone du correcteur : compte les appels, capture la copie
    reçue (doit être le texte canonique) et retourne une COPIE FRAÎCHE du
    résultat à chaque appel (le wrapper mute le dict retourné — un objet
    partagé fausserait les assertions)."""
    holder = {"result": return_result}
    mock = AsyncMock()

    async def _impl(**kwargs):
        if side_effect is not None:
            return await side_effect(**kwargs)
        return json.loads(json.dumps(holder["result"]))

    mock.side_effect = _impl
    mock.set_result = lambda r: holder.__setitem__("result", r)
    return mock


async def _call(evaluate_fn, answer: str, **overrides) -> dict:
    return await evaluate_with_cache(
        question_id=overrides.pop("question_id", QID),
        verb_slug=overrides.pop("verb_slug", VERB),
        score_max=overrides.pop("score_max", SMAX),
        student_answer=answer,
        model_id=overrides.pop("model_id", "gpt-4o-mini"),
        evaluate_fn=evaluate_fn,
        scenario_context="ctx",
        documents=None,
        question_prompt="حلل",
        question_skill="تحليل",
        model_answer="modèle",
        learning_focus=None,
        use_v2_prompt=True,
        **overrides,
    )


def _stats_snapshot() -> dict[str, int]:
    return dict(grading_cache.grading_cache_stats()["total"])


# ── Tests unitaires : clé et normalisation ───────────────────────────

class TestKeyNormalize:
    def test_lstrip_gives_delta(self):
        text, delta = key_normalize("  \nabc")
        assert text == "abc"
        assert delta == 3

    def test_trailing_whitespace_stripped_without_delta(self):
        text, delta = key_normalize("abc\n  ")
        assert text == "abc"
        assert delta == 0

    def test_crlf_not_converted(self):
        """CRLF n'est PAS normalisé : la copie réelle affichée au frontend
        garde ses \\r → la conversion casserait les offsets JS. Miss documenté."""
        text, delta = key_normalize("a\r\nb")
        assert text == "a\r\nb"
        assert delta == 0

    def test_internal_spaces_untouched(self):
        text, delta = key_normalize("a  b\tc")
        assert text == "a  b\tc"  # collapse interne INTERDIT (piège 1)
        assert delta == 0


class TestBuildCorrectionKey:
    def test_same_content_different_edge_whitespace_same_key(self):
        k1 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer="  " + ANS + "\n", model_id="m")
        k2 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer=ANS, model_id="m")
        assert k1 == k2

    def test_internal_space_difference_is_miss(self):
        """Option 1 minimale : pas de collapse → deux copies aux espaces
        internes différents ont des clés différentes (miss documenté)."""
        k1 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer="a  b", model_id="m")
        k2 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer="a b", model_id="m")
        assert k1 != k2

    def test_crlf_difference_is_miss(self):
        k1 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer="A\r\nB", model_id="m")
        k2 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                  answer="A\nB", model_id="m")
        assert k1 != k2

    def test_components_isolate(self):
        base = dict(question_id=QID, verb_slug=VERB, score_max=SMAX, answer=ANS, model_id="m")
        k = build_correction_key(**base)
        for field, value in [
            ("question_id", 43),
            ("verb_slug", "interpret"),
            ("score_max", 8),
            ("model_id", "other-model"),
            ("prompt_variant", "v1"),
        ]:
            other = build_correction_key(**{**base, field: value})
            assert other != k, f"{field} devrait isoler la clé"

    def test_answer_digest_never_contains_plaintext(self):
        key = build_correction_key(question_id=QID, verb_slug=VERB, score_max=SMAX,
                                   answer=ANS, model_id="m")
        assert ANS not in key  # HMAC-SHA256 pepperisé — pas de contenu en clair

    def test_score_max_in_key_invalidates_bareme_change(self):
        k1 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=7, answer=ANS, model_id="m")
        k2 = build_correction_key(question_id=QID, verb_slug=VERB, score_max=8, answer=ANS, model_id="m")
        assert k1 != k2


# ── Tests d'acceptation C2 ───────────────────────────────────────────

class TestCorrectionCache:
    async def test_second_identical_answer_hits_cache(self, fake_redis):
        """Acceptation C2 #1 : même réponse 2× → 2e correction from_cache=True,
        source d'origine PRÉSERVÉE (grading_source_total fidèle), 0 appel LLM."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        r1 = await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS)

        assert evaluate_fn.await_count == 1
        assert r2["from_cache"] is True
        assert r2["source"] == "llm"  # source d'origine préservée
        assert not r1.get("from_cache", False)
        assert r2["score"] == r1["score"] == 5
        assert r2["score_max"] == SMAX
        assert r2["attempts"] == 0
        assert r2["parse_status"] == "cached"
        assert r2["feedback_ar"] == r1["feedback_ar"]

    async def test_from_cache_preserves_v2_source(self, fake_redis):
        """Un hit d'une note produite en prompt v2 garde source='llm_v2'."""
        evaluate_fn = _make_evaluate_fn(
            return_result=_llm_result(score=5, source="llm_v2")
        )
        await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS)
        assert r2["from_cache"] is True
        assert r2["source"] == "llm_v2"

    async def test_trailing_newline_hits_and_offsets_shift(self, fake_redis):
        """Acceptation C2 #2 (option 1 sûre) : \\n\\n + réponse → hit,
        highlights reprojetés +2, le span pointe toujours le bon mot."""
        base_highlights = [{"start": 4, "end": 8, "type": "good_element", "message_ar": "x"}]
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5, highlights=base_highlights))

        await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, "\n\n" + ANS)

        assert evaluate_fn.await_count == 1
        assert r2["from_cache"] is True
        h = r2["highlights"][0]
        assert h["start"] == 4 + 2
        assert h["end"] == 8 + 2
        # Le span pointe le bon mot dans la copie réelle
        assert ("\n\n" + ANS)[h["start"]:h["end"]] == ANS[4:8]

    async def test_internal_spaces_are_miss(self, fake_redis):
        """Acceptation C2 #2 (option 2 documentée) : espaces INTERNES
        différents → miss (aucun collapse — zéro risque d'offset)."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, "a  b")
        r2 = await _call(evaluate_fn, "a b")
        assert r2["source"] == "llm"
        assert not r2.get("from_cache", False)
        assert evaluate_fn.await_count == 2

    async def test_crlf_is_miss(self, fake_redis):
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, "A\nB")
        r2 = await _call(evaluate_fn, "A\r\nB")
        assert r2["source"] == "llm"
        assert not r2.get("from_cache", False)

    async def test_one_char_difference_is_miss(self, fake_redis):
        """Acceptation C2 #3 : réponse différente d'1 caractère → miss."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS + "،")  # +1 caractère
        assert r2["source"] == "llm"
        assert not r2.get("from_cache", False)
        assert evaluate_fn.await_count == 2

    async def test_offsets_stored_in_canonical_space(self, fake_redis):
        """Piège 1 : le payload stocké est en espace canonique — une copie A
        avec préfixe puis une copie B sans préfixe restent cohérentes."""
        base_highlights = [{"start": 4, "end": 8, "type": "good_element", "message_ar": "x"}]
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5, highlights=base_highlights))

        # Copie A : 3 espaces de tête (delta=3) → highlights retournés décalés
        r1 = await _call(evaluate_fn, "   " + ANS)
        assert r1["highlights"][0]["start"] == 7  # espace élève (raw)
        # Copie B : sans préfixe → hit, highlights en position canonique
        r2 = await _call(evaluate_fn, ANS)
        assert r2["from_cache"] is True
        assert r2["highlights"][0]["start"] == 4  # espace élève (raw)
        assert evaluate_fn.await_count == 1

    async def test_hashes_are_per_student_not_cached(self, fake_redis):
        """Piège 2 : le hash RGPD est celui de la copie réelle, jamais relu
        du cache. Une réponse différente → miss → hash différent."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        r1 = await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS)
        # Hit : hash recalculé sur CETTE copie → identique pour la même copie
        assert r2["from_cache"] is True
        assert r2["student_answer_hash"] == r1["student_answer_hash"]

        # Réponse différente (miss volontaire) → hash différent, LLM rappelé
        r3 = await _call(evaluate_fn, ANS + "، وبالتالي يرتفع الغلوكوز")
        assert r3["source"] == "llm"
        assert not r3.get("from_cache", False)
        assert r3["student_answer_hash"] != r1["student_answer_hash"]

    async def test_hash_of_real_copy_on_whitespace_hit(self, fake_redis):
        """Même copie canonique mais copie réelle différente (espaces de tête) :
        le hash doit correspondre à la copie réelle, pas à la copie cachée."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        r1 = await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, "  " + ANS)  # hit (même canonique)
        assert r2["from_cache"] is True
        assert r2["student_answer_hash"] != r1["student_answer_hash"]  # copies réelles ≠

    async def test_degraded_result_is_not_cached(self, fake_redis):
        """Piège 3 : une note local_fallback n'est jamais cachée — quand le
        LLM revient, la même réponse est RE-corrigée par le LLM."""
        degraded = _llm_result(score=3)
        degraded["source"] = "local"
        degraded["parse_status"] = "local_fallback"
        degraded["model"] = "fallback_l2"

        evaluate_fn = _make_evaluate_fn(return_result=degraded)
        r1 = await _call(evaluate_fn, ANS)
        assert r1["source"] == "local"
        assert evaluate_fn.await_count == 1

        # LLM revenu : la même réponse doit RE-déclencher une correction LLM
        evaluate_fn.set_result(_llm_result(score=5))
        r2 = await _call(evaluate_fn, ANS)
        assert evaluate_fn.await_count == 2
        assert r2["source"] == "llm"

    async def test_sanity_rejection_never_cached_and_no_lookup(self, fake_redis):
        """Acceptation C2 #6 : un rejet sanity ne passe ni par le lookup ni
        par le store (déterministe, ~µs — le cache serait plus lent)."""
        before = _stats_snapshot()
        sanity = _llm_result(score=0)
        sanity["source"] = "sanity"
        sanity["parse_status"] = "not_called"
        sanity["dominant_error_code"] = "gibberish"
        evaluate_fn = _make_evaluate_fn(return_result=sanity)
        r1 = await _call(evaluate_fn, "ZZZZ")
        r2 = await _call(evaluate_fn, "ZZZZ")
        after = _stats_snapshot()

        assert r1["source"] == "sanity" and r2["source"] == "sanity"
        # Pas de lookup (miss/hit) ni de store — uniquement skip_uncacheable
        assert after.get("miss", 0) == before.get("miss", 0)
        assert after.get("hit", 0) == before.get("hit", 0)
        assert after.get("store", 0) == before.get("store", 0)
        assert after.get("skip_uncacheable", 0) == before.get("skip_uncacheable", 0) + 2

    async def test_llm_v2_is_cacheable(self, fake_redis):
        """Point factuel : en production (prompt v2), source='llm_v2' avec
        parse_status='recovered' (correction_v2.py:825) DOIT être cacheable —
        sinon le cache est mort en prod."""
        assert "recovered" in CACHE_PARSE_ALLOWED
        evaluate_fn = _make_evaluate_fn(
            return_result=_llm_result(score=5, source="llm_v2")
        )
        await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS)
        assert r2["from_cache"] is True

    async def test_prompt_version_bump_invalidates(self, fake_redis, monkeypatch):
        """Acceptation C2 #7 : bump de CORRECTION_PROMPT_VERSION → ancienne
        entrée ignorée (invalidation passive, clé différente)."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, ANS)
        monkeypatch.setattr(grading_cache_key, "CORRECTION_PROMPT_VERSION", "p2")
        r = await _call(evaluate_fn, ANS)
        assert r["source"] == "llm"  # miss — pas de résidu de l'ancienne version
        assert not r.get("from_cache", False)
        assert evaluate_fn.await_count == 2

    async def test_concurrent_identical_answers_single_llm_call(self, fake_redis):
        """Acceptation C2 #9 : single-flight — 10 corrections concurrentes
        identiques → 1 seul appel LLM."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))

        results = await asyncio.gather(*[_call(evaluate_fn, ANS) for _ in range(10)])

        assert evaluate_fn.await_count == 1
        assert all(r["score"] == 5 for r in results)
        assert sum(1 for r in results if r.get("from_cache")) == 9
        assert sum(1 for r in results if not r.get("from_cache")) == 1

    async def test_no_llm_raw_in_cached_payload(self, fake_redis):
        """Acceptation C2 #4 : payload caché = contrat Public — ni llm_raw,
        ni copie élève, ni hash élève (asserts runtime dans to_cache_payload)."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, ANS)

        key = build_correction_key(
            question_id=QID, verb_slug=VERB, score_max=SMAX, answer=ANS,
            model_id="gpt-4o-mini", prompt_variant="v2",
        )
        payload = await get_cache(key)
        assert payload is not None
        stored = json.loads(payload)
        assert "llm_raw" not in stored
        assert "llm_raw_hash" not in stored
        assert "student_answer" not in stored  # jamais la copie
        assert "student_answer_hash" not in stored  # hash de l'élève A jamais stocké
        assert "prompt_hash" not in stored
        assert "attempts" not in stored
        assert "source" in stored  # source d'origine préservée (observabilité)

    async def test_to_cache_payload_asserts(self):
        """Garde-fou runtime : to_cache_payload lève si le résultat contient
        llm_raw ou la copie élève dans les champs cachés."""
        r = _llm_result(score=5)
        r["llm_raw"] = "{}"
        r["student_answer"] = ANS
        payload = to_cache_payload(r)  # ces champs ne sont pas dans CACHEABLE_FIELDS
        assert "llm_raw" not in payload and "student_answer" not in payload

    async def test_correcteur_receives_canonical_text(self, fake_redis):
        """Invariant piège 1 : le LLM voit le texte canonique (offsets
        cohérents), jamais la copie brute avec espaces parasites."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        await _call(evaluate_fn, "   " + ANS + "\n")
        received = evaluate_fn.call_args.kwargs["student_answer"]
        assert received == ANS

    async def test_miss_returns_highlights_in_raw_space(self, fake_redis):
        """Au miss aussi, le retour API est en espace copie réelle (même
        convention qu'au hit — sinon le frontend désalignerait)."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        r = await _call(evaluate_fn, "   " + ANS)
        assert r["source"] == "llm"
        assert r["highlights"][0]["start"] == 7  # 4 + delta(3)

    async def test_cache_disabled_without_redis(self):
        """Acceptation C2 #8 : sans Redis (CI), le wrapper se comporte comme
        un simple appel — aucune erreur, calcul direct."""
        evaluate_fn = _make_evaluate_fn(return_result=_llm_result(score=5))
        r1 = await _call(evaluate_fn, ANS)
        r2 = await _call(evaluate_fn, ANS)
        assert evaluate_fn.await_count == 2
        assert r1["source"] == "llm" and r2["source"] == "llm"
        assert not r2.get("from_cache", False)

    async def test_ttl_is_7_days(self):
        assert CORRECTION_CACHE_TTL == 7 * 24 * 3600


# ── Tests unitaires : is_cacheable / to_cache_payload ────────────────

class TestIsCacheable:
    def test_llm_ok_cacheable(self):
        assert is_cacheable(_llm_result(score=5)) is True

    def test_llm_v2_recovered_cacheable(self):
        # Point factuel : en v2 (prod), parse_status est "recovered" — DOIT
        # rester cacheable, sinon le cache est mort.
        r = _llm_result(score=5, source="llm_v2")
        assert r["parse_status"] == "recovered"
        assert is_cacheable(r) is True

    def test_llm_retried_cacheable(self):
        r = _llm_result(score=5)
        r["source"] = "llm_retried"
        assert is_cacheable(r) is True

    def test_future_local_savoir_high_confidence_cacheable(self):
        """Contrat C2 : le futur étage savoir_corrector haute confiance est
        cacheable (0 token, déterministe)."""
        r = _llm_result(score=5, source="local_savoir")
        r["parse_status"] = "ok"
        assert is_cacheable(r) is True

    def test_local_fallback_not_cacheable(self):
        r = _llm_result(score=3)
        r["source"] = "local"
        r["parse_status"] = "local_fallback"
        assert is_cacheable(r) is False

    def test_llm_error_not_cacheable(self):
        r = _llm_result(score=0)
        r["source"] = "llm_error"
        r["parse_status"] = "failed"
        assert is_cacheable(r) is False

    def test_sanity_not_cacheable(self):
        r = _llm_result(score=0)
        r["source"] = "sanity"
        r["parse_status"] = "not_called"
        assert is_cacheable(r) is False

    def test_out_of_range_score_not_cacheable(self):
        r = _llm_result(score=99)  # > score_max
        assert is_cacheable(r) is False

    def test_parse_failed_not_cacheable(self):
        r = _llm_result(score=5)
        r["parse_status"] = "failed"
        assert is_cacheable(r) is False


class TestToCachePayload:
    def test_only_cacheable_fields(self):
        r = _llm_result(score=5)
        stored = to_cache_payload(r)
        assert stored["score"] == 5
        assert stored["source"] == "llm"
        assert stored["model"] == "gpt-4o-mini"
        assert stored["provider"] == "openai"
        assert "student_answer_hash" not in stored
        assert "attempts" not in stored
        assert "parse_status" not in stored
        assert "finish_reason" not in stored
        assert "llm_raw" not in stored
