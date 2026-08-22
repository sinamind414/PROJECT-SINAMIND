# tests/test_rate_limit.py
# G0-5 (grille go-no-go-100k) : PREMIERS TESTS des rate limits slowapi.
# L'audit 100k v2 (reçu R7) constatait : « 6 fichiers de routes plafonnés,
# 0 test ». Ce fichier comble ce vide — et corrige un contresens du grep.
#
# ⚠️ CONSTAT (découvert en écrivant ces tests, 2026-08-21) :
#   Le grep R7 comptait les DÉCORATEURS dans le code : 7, sur 6 fichiers.
#   Mais depuis le GEL d'endpoints orphelins (2026-08-17, routes/__init__.py),
#   `routes/evaluate.py` et `routes/ai_evaluate.py` ne sont PLUS importés du
#   registre → leurs @limiter.limit sont de la MORT : le plafond « 15/h »
#   annoncé pour POST /api/evaluate n'existe pas (la route renvoie le 404
#   catch-all). Les 5 plafonds VIVANTS au runtime :
#     - routes/ai_chat.py            ai_chat_unified        (chat 20/100 h)
#     - routes/chatbot.py            ask_chatbot            (chat 20/100 h)
#     - routes/chatbot.py            ask_chatbot_stream     (chat 20/100 h)
#     - routes/document_analysis_v2.py evaluer_reponses_v2  (eval 15/80 h)
#     - routes/dual_coding.py        evaluate_schema        (eval 15/80 h)
#   Le VRAI endpoint d'évaluation LLM = POST /api/document-analysis/evaluate-v2.
#
# Ce que les tests prouvent (reçus) :
#   T1 — un compte FREE est plafonné à 15/h sur evaluate-v2 : 15 appels
#        passent (404 « scénario introuvable » = handler atteint), le 16e → 429.
#   T2 — le tier PRO (claim plan=pro du JWT signé) passe à 80/h :
#        80 appels passent, le 81e → 429.
#   T3 — les seuils contractés (chat 20/100, evaluate 15/80) sont figés.
#   T4 — garde de régression : le vrai endpoint est monté ET plafonné ;
#        les routes mortes du gel ne sont PAS montées.
#   T5 — garde de régression (BUG CORRIGÉ 2026-08-21) : les compteurs sont
#        par UTILISATEUR, pas par IP. Avant le fix, _get_user_plan échouait
#        sur tous les tokens réels (sub int → JWTClaimsError « Subject must
#        be a string ») → tout le trafic était compté par IP au tier free :
#        élèves derrière la même IP/NAT partageant un seul 15/h, tier pro
#        (80/h) jamais appliqué. Fix : options={"verify_sub": False}
#        (pattern déjà documenté dans deps.get_current_user).
#
# Isolation : subs uniques (424242 / 424243) → clés de limiter dédiées
# (user:424242:free, user:424243:pro), aucun impact sur les autres tests
# qui partagent la clé user:1:free (fixture auth_headers).

from auth import create_access_token
from rate_limit import chat_limit, evaluate_limit


# ─── T3 — Unit : les seuils contractés ─────────────────────────────────────


class TestLimitThresholds:
    def test_evaluate_free_is_15_per_hour(self):
        assert evaluate_limit("user:424242:free") == "15/hour"

    def test_evaluate_pro_is_80_per_hour(self):
        assert evaluate_limit("user:424242:pro") == "80/hour"

    def test_evaluate_ip_key_falls_back_to_free(self):
        # Sans JWT valide, la clé est l'adresse IP → tier free.
        assert evaluate_limit("10.0.0.7") == "15/hour"

    def test_chat_free_is_20_per_hour(self):
        assert chat_limit("user:1:free") == "20/hour"

    def test_chat_pro_is_100_per_hour(self):
        assert chat_limit("user:1:pro") == "100/hour"


# ─── T1/T2 — Intégration : le plafond est réellement appliqué ──────────────
#
# Méthode : scenario_id inexistante → le handler est ATTEINT (404) après le
# passage par le limiter (qui compte l'appel), sans lancer le pipeline LLM.
# 15×404 puis 429 = preuve que le compteur passe bien de 15 → blocage.

EVAL_V2_URL = "/api/document-analysis/evaluate-v2"
EVAL_V2_BODY = {
    "scenario_id": "scenario_rl_inexistant",
    "answers": [{"verb_slug": "verbe_rl", "answer": "réponse test"}],
}


async def _hit_eval_v2(client, token: str):
    return await client.post(
        EVAL_V2_URL,
        json=EVAL_V2_BODY,
        headers={"Authorization": f"Bearer {token}"},
    )


async def test_evaluate_free_user_blocked_on_16th_request(client):
    """Compte free : 15 appels passent, le 16e est bloqué (429)."""
    token = create_access_token(
        {"sub": 424242, "email": "rl-free@bac.dz", "plan": "free"}
    )
    for i in range(15):
        r = await _hit_eval_v2(client, token)
        assert r.status_code == 404, (
            f"appel {i + 1}/15 : attendu 404 (handler atteint), obtenu {r.status_code}"
        )
    r = await _hit_eval_v2(client, token)
    assert r.status_code == 429, (
        f"16e appel : attendu 429 (rate limit), obtenu {r.status_code}"
    )


async def test_evaluate_pro_user_allows_80_per_hour(client):
    """Compte pro (claim plan=pro) : 80 appels passent, le 81e est bloqué."""
    token = create_access_token(
        {"sub": 424243, "email": "rl-pro@bac.dz", "plan": "pro"}
    )
    for i in range(80):
        r = await _hit_eval_v2(client, token)
        assert r.status_code == 404, (
            f"appel {i + 1}/80 : attendu 404 (handler atteint), obtenu {r.status_code}"
        )
    r = await _hit_eval_v2(client, token)
    assert r.status_code == 429, (
        f"81e appel : attendu 429 (rate limit), obtenu {r.status_code}"
    )


async def test_rate_limits_are_per_user_not_per_ip(client):
    """T5 — garde de régression du bug de partage par IP (corrigé 2026-08-21) :
    deux comptes free distincts ont chacun leur compteur 15/h, même depuis la
    même « IP » (tous les tests partagent 127.0.0.1 en ASGI)."""
    tok_a = create_access_token({"sub": 424244, "email": "rl-a@bac.dz", "plan": "free"})
    tok_b = create_access_token({"sub": 424245, "email": "rl-b@bac.dz", "plan": "free"})
    for i in range(15):
        r = await _hit_eval_v2(client, tok_a)
        assert r.status_code == 404, (
            f"appel {i + 1}/15 user A : attendu 404, obtenu {r.status_code}"
        )
    r = await _hit_eval_v2(client, tok_a)
    assert r.status_code == 429, (
        f"user A : attendu 429, obtenu {r.status_code}"
    )
    # User B, même IP : son compteur est intact.
    r = await _hit_eval_v2(client, tok_b)
    assert r.status_code == 404, (
        f"user B : attendu 404 (compteur indépendant), obtenu {r.status_code}"
    )


# ─── T4 — Garde de régression : routes mortes du gel 2026-08-17 ────────────


def test_live_evaluate_route_is_mounted_and_limited():
    """Le VRAI endpoint d'évaluation est monté ET plafonné ; les routes mortes
    du gel (routes/evaluate.py, routes/ai_evaluate.py) ne sont PAS montées.
    Garde contre le contresens du grep R7 de l'audit 100k (7 décorateurs dans
    le code, dont 2 sur des modules jamais importés → plafonds fictifs)."""
    from main import app
    from rate_limit import limiter

    paths = {getattr(r, "path", None) for r in app.routes}
    assert EVAL_V2_URL in paths, "endpoint vivant evaluate-v2 dé-monté ?!"

    marked = set(limiter._Limiter__marked_for_limiting.keys())
    assert "routes.document_analysis_v2.evaluer_reponses_v2" in marked

    # Routes mortes : décorateurs @limiter.limit présents dans le code,
    # modules jamais importés du registre → ne doivent PAS être montées.
    assert "/api/evaluate" not in paths
    assert "/api/ai/evaluate" not in paths
