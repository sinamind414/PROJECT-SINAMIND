#!/usr/bin/env python3
"""Audit des SURFACES de correction du site — chemin réel élève, pas seulement le moteur.

Ce que ça prouve, en exécution (aucun LLM, aucune DB, aucun réseau) :

  S1   le câblage frontend : les 13 gradeQuestionId des pages == les 13 grilles git
  S2   les 13 grilles corrigent via HTTP : copie modèle -> 100 % / all_correct
  S3   id inconnu -> 422 ungraded (jamais une note de 0 présentée comme officielle)
  S4   copie vide -> message arabe + bannière, jamais un 0 muet
  S5   les DEUX axes arrivent jusqu'à l'UI : méthode vs global (cap « 36 ATP », cap stuffing)
  S6   le fix F1 (enclitique لأنها) est visible SUR LE SITE (HTTP), pas seulement au moteur
  S7   2e soumission identique -> from_cache, quota non re-consommé
  S8   aucune fuite de secret de grille (variants / model_answer / keypoints)
  S9   quota dépassé -> 429 lisible par l'UI (message arabe + Retry-After), jamais un 500
  S10  sentier F12 : le 429 survit à un limiter désactivé/court-circuité (le cas qui crashait)

Chemin testé = celui du navigateur :
  pages /document-analysis + /diagnostic/chapters -> ScenarioRunner
    -> apiClient.grade() -> POST /api/grade -> grade()

Note : chaque section consomme son propre budget de quota (clé JWT dédiée) pour ne
pas se marcher dessus — 15 corrections/h free sinon fausserait S2..S8.

Usage :  python scripts/probe_audit_surfaces_site.py
Sortie : 0 si tout passe, 1 sinon.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
_FRONTEND = _BACKEND.parent / "khawarizmi-frontend"
sys.path.insert(0, str(_BACKEND))

os.environ.setdefault("SECRET_KEY", "probe-secret-key-khawarizmi-2026")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://probe:probe@localhost/probe_absent")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("ENABLE_EXTERNAL_LLM", "false")

logging.getLogger("httpx").setLevel(logging.WARNING)

from httpx import ASGITransport, AsyncClient

FAILURES: list[str] = []
PASSES: list[str] = []


def ok(label: str, detail: str = "") -> None:
    PASSES.append(label)
    print(f"  \033[32m✓\033[0m {label}" + (f"  \033[2m{detail}\033[0m" if detail else ""))


def bad(label: str, detail: str = "") -> None:
    FAILURES.append(f"{label} — {detail}")
    print(f"  \033[31m✗\033[0m {label}\n      \033[31m{detail}\033[0m")


def check(cond: bool, label: str, detail: str = "") -> bool:
    (ok if cond else bad)(label, detail)
    return bool(cond)


def section(title: str) -> None:
    print(f"\n\033[1m── {title}\033[0m")


# ── Câblage frontend (source de vérité : le fichier que le navigateur charge) ──

_GRADE_ID_RE = re.compile(r'gradeQuestionId:\s*"([^"]+)"')
_API_CLIENT_GRADE_RE = re.compile(r"fetch\(`\$\{API_BASE_URL\}/api/grade`")
_BOURRAGE = " ".join(["الغلوكوز غلوكوز الخميرة خميرة تنفس تخمر طاقة مادة أيض نمو تكاثر"] * 3)


def frontend_grade_ids() -> list[str]:
    """Les ids câblés dans les données de scénarios des pages du site."""
    src = (_FRONTEND / "src" / "lib" / "methodology-documents.ts").read_text(encoding="utf-8")
    seen: list[str] = []
    for m in _GRADE_ID_RE.finditer(src):
        if m.group(1) not in seen:
            seen.append(m.group(1))
    return seen


def frontend_pages_mounting(name: str) -> list[str]:
    out: list[str] = []
    for p in sorted((_FRONTEND / "src" / "app").rglob("*.tsx")):
        if name in p.read_text(encoding="utf-8"):
            out.append(str(p.relative_to(_FRONTEND / "src" / "app")).replace("/page.tsx", ""))
    return out


def frontend_callers_of(method: str) -> list[str]:
    """Appels d'une méthode de l'api-client hors de l'api-client lui-même = surface vivante."""
    out: list[str] = []
    for root in (_FRONTEND / "src", _FRONTEND / "lib"):
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.suffix not in {".ts", ".tsx"} or p.name == "api-client.ts":
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if re.search(rf"apiClient\.{method}\s*\(", text):
                out.append(str(p.relative_to(_FRONTEND)))
    return out


def api_client_method_source(method: str) -> str:
    src = (_FRONTEND / "src" / "lib" / "api-client.ts").read_text(encoding="utf-8")
    start = src.index(f"async {method}(")
    depth, i = 0, src.index("{", start)
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start : i + 1]
        i += 1
    return src[start:]


async def _run() -> None:
    from auth import create_access_token
    from deps import get_current_user
    from main import app
    from rate_limit import limiter
    from services.rubric_store import data_dir, list_question_ids, load

    fe_ids = frontend_grade_ids()
    be_ids = sorted(list_question_ids())

    # Un sub JWT différent par section => budget de quota indépendant (15/h par clé).
    def headers_for(tag: int) -> dict[str, str]:
        sub = 991000 + tag
        return {"Authorization": f"Bearer {create_access_token({'sub': sub, 'plan': 'free'})}"}

    app.dependency_overrides[get_current_user] = lambda: {"id": 991000, "plan": "free", "email": "probe@bac.dz"}
    transport = ASGITransport(app=app)  # type: ignore[arg-type]

    async with AsyncClient(transport=transport, base_url="http://site") as ac:

        async def grade(tag: int, question_id: str, answer: str, surface: str = "da"):
            r = await ac.post(
                "/api/grade",
                json={"question_id": question_id, "answer": answer, "surface": surface},
                headers=headers_for(tag),
            )
            try:
                body = r.json()
            except Exception:
                body = {"_raw": r.text[:400]}
            return r.status_code, body, r.headers

        # ── S1 — câblage ──────────────────────────────────────────────────
        section("S1 — câblage : les pages du site ↔ les 13 grilles git")
        check(len(fe_ids) == 13, "frontend expose 13 gradeQuestionId", f"{len(fe_ids)} trouvés")
        check(
            sorted(fe_ids) == be_ids,
            "les 13 ids du frontend == les grilles git (aucune orpheline)",
            f"frontend-only={sorted(set(fe_ids) - set(be_ids))} backend-only={sorted(set(be_ids) - set(fe_ids))}",
        )
        pages = frontend_pages_mounting("ScenarioRunner")
        check(len(pages) >= 2, "ScenarioRunner monté sur les pages corrigibles", ", ".join(pages))
        check(
            bool(_API_CLIENT_GRADE_RE.search((_FRONTEND / "src" / "lib" / "api-client.ts").read_text(encoding="utf-8"))),
            "ScenarioRunner -> apiClient.grade -> POST /api/grade (point d'entrée unique)",
        )
        wall_pages = frontend_pages_mounting("NoLocalGradeWall")
        check(len(wall_pages) >= 2, "les pages sans grille affichent le mur honnête", ", ".join(wall_pages))

        # ── S2 — 13/13 via HTTP ───────────────────────────────────────────
        section("S2 — les 13 grilles corrigent via HTTP : copie modèle -> 100 %")
        scored: list[str] = []
        for i, qid in enumerate(fe_ids):
            packed = load(qid)
            if packed is None:
                bad(f"{qid}: grille absente du store")
                continue
            status, body, _ = await grade(2, qid, packed.rubric.model_answer)
            good = (
                status == 200
                and body.get("ungraded") is False
                and body.get("method_percent") == 100
                and body.get("overall_training_percent") == 100
                and body.get("criteria")
                and all(c["status"] == "full" for c in body["criteria"])
            )
            if good:
                scored.append(qid)
            else:
                bad(
                    f"{qid}: copie modèle non validée à 100 %",
                    f"http={status} method={body.get('method_percent')} overall={body.get('overall_training_percent')} "
                    f"critères={[c.get('status') for c in body.get('criteria', [])]}",
                )
        check(len(scored) == len(fe_ids), f"{len(scored)}/{len(fe_ids)} grilles -> 100 % en copie modèle (via HTTP)")

        # ── S3 — id inconnu ───────────────────────────────────────────────
        section("S3 — id inconnu (exercice sans grille) -> 422 ungraded, jamais 0")
        status, body, _ = await grade(3, "exercice-base-sans-grille", "إجابة التلميذ في الوثيقة")
        check(status == 422, "id inconnu -> HTTP 422", f"reçu {status}")
        check(
            body.get("code") == "ungraded" or body.get("erreur") == "ungraded",
            "payload porte code=ungraded (l'UI affiche le mur, pas une note)",
            json.dumps(body, ensure_ascii=False)[:120],
        )
        check(
            "score" not in body and "method_percent" not in body and "percentage" not in body,
            "aucun score fabriqué pour un id inconnu",
        )

        # ── S4 — copie vide ───────────────────────────────────────────────
        section("S4 — copie vide -> message arabe, pas un 0 muet")
        status, body, _ = await grade(4, fe_ids[0], "")
        blob_ar = " ".join(str(body.get(k, "")) for k in ("banner_ar", "phrase_ar", "next_step_ar"))
        check(status == 200, "copie vide -> 200 + bannière pédagogique", f"reçu {status}")
        check("ليست علامة بكالوريا رسمية" in blob_ar, "le message arabe remonte jusqu'à l'UI", blob_ar[:80])
        check(
            body.get("ungraded") is False,
            "copie vide = note entraînée (ungraded False), pas un rejet technique",
            f"ungraded={body.get('ungraded')}",
        )

        # ── S5 — deux axes ────────────────────────────────────────────────
        section("S5 — les DEUX axes (méthode / global) arrivent jusqu'à l'UI")
        qid5 = "enzyme-temp-analyse"
        packed5 = load(qid5)
        assert packed5 is not None
        raw5 = json.loads((data_dir() / packed5.rubric_path).read_text(encoding="utf-8"))
        atp = next((c for c in raw5.get("counter_examples") or [] if c.get("id") == "atp36"), None)
        if atp:
            status, body, _ = await grade(5, qid5, packed5.rubric.model_answer + " ينتج 36 ATP.")
            if status == 200:
                check(body.get("method_percent") == 100, "« 36 ATP » : axe méthode intact", f"method={body.get('method_percent')}")
                check(
                    body.get("overall_training_percent") <= atp.get("max_percent", 40),
                    "« 36 ATP » : axe global capé (vote science)",
                    f"overall={body.get('overall_training_percent')} caps={body.get('caps_applied')}",
                )
                check(
                    body.get("science_status") == "error" or body.get("science_capped") is True,
                    "le drapeau science est exposé à l'UI",
                    f"status={body.get('science_status')} capped={body.get('science_capped')}",
                )
            else:
                bad("« 36 ATP » : HTTP inattendu", f"status={status} {json.dumps(body, ensure_ascii=False)[:160]}")
        else:
            bad("counter_example atp36 absent de la grille", qid5)

        qid5b = "yeast-glucose-interpret"
        status, body, _ = await grade(5, qid5b, _BOURRAGE + " العدد يصل 18 ")
        if status == 200:
            check(body.get("stuffing_suspected") is True, "bourrage lexical -> stuffing_suspected (site)", f"stuffing={body.get('stuffing_suspected')}")
            check(
                body.get("overall_training_percent") <= 50,
                "bourrage -> cap global ≤ 50 %",
                f"overall={body.get('overall_training_percent')} caps={body.get('caps_applied')}",
            )
            diag = body.get("diagnosis") or {}
            check(diag.get("code") == "stuffing", "le diagnostic nommé remonte à l'UI", f"diagnosis={diag}")
            check(body.get("method_percent") < 100, "le bourrage n'obtient pas la méthode pleine", f"method={body.get('method_percent')}")
        else:
            bad("stuffing : HTTP inattendu", f"status={status} {json.dumps(body, ensure_ascii=False)[:160]}")

        # ── S6 — F1 sur le site ───────────────────────────────────────────
        section("S6 — fix F1 (enclitique لأنها) visible SUR LE SITE")
        target = next((q for q in fe_ids if "لأن" in ((load(q).rubric.model_answer if load(q) else "") or "")), None)
        if target:
            packed6 = load(target)
            assert packed6 is not None
            glued = packed6.rubric.model_answer.replace("لأن", "لأنها", 1)
            check(glued != packed6.rubric.model_answer, "sonde construite : لأن -> لأنها collé")
            status, body, _ = await grade(6, target, glued)
            if status == 200:
                check(
                    body.get("method_percent") == 100,
                    f"{target} : « parce-qu'elle » reconnu -> 100 % (et non 75 %)",
                    f"method={body.get('method_percent')} overall={body.get('overall_training_percent')}",
                )
            else:
                bad("F1 : HTTP inattendu", f"status={status}")
        else:
            bad("aucune grille du site avec لأن dans la copie modèle", "S6 non démontrable")

        # ── S7 — cache ────────────────────────────────────────────────────
        section("S7 — cache : 2e soumission = from_cache, quota non re-consommé")
        qid7 = fe_ids[1]
        packed7 = load(qid7)
        assert packed7 is not None
        ans7 = packed7.rubric.model_answer + " ملاحظة أولى للطالب."
        st1, b1, _ = await grade(7, qid7, ans7)
        st2, b2, _ = await grade(7, qid7, ans7)
        check(st1 == 200 and st2 == 200, "deux soumissions identiques -> 200/200", f"{st1}/{st2}")
        check(
            b1.get("from_cache") is False and b2.get("from_cache") is True,
            "2e réponse servie depuis le cache",
            f"1st={b1.get('from_cache')} 2nd={b2.get('from_cache')}",
        )
        check(b1.get("method_percent") == b2.get("method_percent") and b1.get("criteria") == b2.get("criteria"),
              "la note ne dérive pas entre copie fraîche et cache")

        # ── S8 — fuites ───────────────────────────────────────────────────
        section("S8 — aucune fuite de secret de grille dans la réponse à l'élève")
        st, body, _ = await grade(8, fe_ids[2], "نلاحظ في الوثيقة أن النشاط يتغير مع الزمن.")
        blob = json.dumps(body, ensure_ascii=False)
        leaked = [k for k in ("model_answer", "variants", "keypoints", "counter_examples", "advice_by_gap") if k in blob]
        check(st == 200, "copie d'élève corrigée normalement", f"http={st}")
        check(not leaked, "ni model_answer, ni variants, ni keypoints, ni contre-exemples", f"fuites={leaked}")
        r_rub = await ac.get(f"/api/grade/rubric/{fe_ids[2]}", headers=headers_for(8))
        blob_r = json.dumps(r_rub.json(), ensure_ascii=False)
        check(
            r_rub.status_code == 200 and not any(k in blob_r for k in ("model_answer", "variants", "keypoints")),
            "/api/grade/rubric/{id} n'expose que labels + étapes de méthode",
            f"http={r_rub.status_code}",
        )

        # ── S9 — quota vu par l'élève ─────────────────────────────────────
        section("S9 — élève à 15 corrections/h : 429 lisible, jamais un 500")
        qid9 = fe_ids[3]
        packed9 = load(qid9)
        assert packed9 is not None
        statuses: list[int] = []
        bodies: list[dict] = []
        headers_last = None
        for i in range(18):
            st, body, hd = await grade(9, qid9, packed9.rubric.model_answer + f" ملاحظة رقم {i}.")
            statuses.append(st)
            bodies.append(body)
            headers_last = hd
        check(statuses[:15] == [200] * 15, "15 premières corrections -> 200", f"{statuses[:15]}")
        check(500 not in statuses, "AUCUN 500 pour un élève en surquota", f"statuts={statuses}")
        refused = [(i, s) for i, s in enumerate(statuses) if s != 200]
        check(bool(refused) and refused[0][1] == 429, "le dépassement renvoie 429", f"refus={refused[:3]}")
        if refused:
            ref = bodies[refused[0][0]]
            blob = json.dumps(ref, ensure_ascii=False)
            check(ref.get("code") == "quota_exceeded", "429 avec code machine `quota_exceeded` (UI) ", blob[:120])
            check("ليست علامة بكالوريا رسمية" in blob, "429 avec le message arabe élève", blob[:120])
            check("erreur" in ref, "429 conforme au contrat d'erreur de l'app (clé `erreur`)", blob[:80])
            check(bool(headers_last and headers_last.get("retry-after")), "429 porte Retry-After",
                  f"retry-after={headers_last.get('retry-after') if headers_last else None}")

        # ── S10 — sentier F12 (crash d'origine) ───────────────────────────
        section("S10 — F12 : plus aucun 429 ne dépend de request.state.view_rate_limit")
        main_src = (_BACKEND / "main.py").read_text(encoding="utf-8")
        check(
            "add_exception_handler(429," not in main_src and "add_exception_handler(RateLimitExceeded" in main_src,
            "main.py branche le handler sur la CLASSE, plus sur le statut 429",
        )
        rate_src = (_BACKEND / "rate_limit.py").read_text(encoding="utf-8")
        check("raise HTTPException" not in rate_src, "enforce_evaluate_quota ne lève plus : il répond")
        # le cas qui crashait : limiter court-circuité (middleware ne pose pas l'état)
        limiter.enabled = False
        try:
            st_off, body_off, _ = await grade(10, qid9, packed9.rubric.model_answer + " حالة limiter معطل.")
            check(st_off == 200, "limiter.enabled=False -> correction normale, pas de 500", f"http={st_off}")
        except Exception as e:  # une levée ici = le crash d'origine
            bad("limiter.enabled=False -> exception (le sentier F12)", repr(e))
        finally:
            limiter.enabled = True
        # et le 429 manuel d'un AUTRE routeur ne peut plus atterrir chez slowapi
        st_429, body_429, _ = await grade(11, "id-inexistant-pour-422", "نص")
        check(st_429 == 422, "un autre code d'erreur n'est pas happé par le handler 429", f"http={st_429}")

        # ── S11 — surfaces de correction mortes ───────────────────────────
        section("S11 — surfaces backend branchées mais jamais appelées par le site (F13)")
        dead = {
            "submitDrillAnswer": "/api/drill/submit",
            "correctExercise": "/api/exercices/",
            "evaluateDaAnswersV2": "/api/document-analysis/evaluate-v2",
        }
        for method, path in dead.items():
            callers = frontend_callers_of(method)
            src = api_client_method_source(method)
            check(
                not callers and path in src + (_FRONTEND / "src" / "lib" / "api-client.ts").read_text(encoding="utf-8"),
                f"{method} : appelée par 0 page (méthode vivante de l'api-client vers {path})",
                f"callers={callers}",
            )
        routes_src = (_BACKEND / "routes" / "flashcards.py").read_text(encoding="utf-8")
        check("/submit" in routes_src, "la route /api/drill/submit existe toujours côté backend (dette à solder)")
        ex_src = (_BACKEND / "routes" / "exercices.py").read_text(encoding="utf-8")
        check("/correct" in ex_src, "la route /api/exercices/{id}/correct existe toujours côté backend")

        # ── S13 — bac blanc : 2e surface de correction (serveur), pont d'ids ──
        section("S13 — bac blanc : même moteur, autre route — et le pont d'ids (F15)")
        from services.grade_adapter import UNGRADED_AR, grade_or_none, resolve_question_id

        seed = json.loads((_BACKEND / "scripts" / "bac_blanc_seed.json").read_text(encoding="utf-8"))
        ids = [e["exercise_id"] for s in seed for e in s["exercises"]]
        annale = seed[0]["annale_slug"]
        resolved = [resolve_question_id(e.get("grade_question_id"), ex_id, f"bac:{annale}:{ex_id}")
                    for s in seed for ex_id, e in ((e["exercise_id"], e) for e in s["exercises"])]
        check(
            all(r is None for r in resolved),
            f"fait mesuré : les {len(ids)} exercices du sujet seed ({annale}) ne résolvent AUCUNE grille",
            f"ids={ids[:4]}…",
        )
        check(
            grade_or_none(resolve_question_id("s1-e2", f"bac:{annale}:s1-e2"), "إجابة التلميذ") is None,
            "copie de bac blanc -> ungraded (mur), jamais une note inventée",
        )
        check("تعذر التصحيح" in UNGRADED_AR, "le texte serveur dit « non noté » (لا شبكة), pas « 0 »")
        bac_src = (_BACKEND / "routes" / "bac_blanc.py").read_text(encoding="utf-8")
        schema_src = (_BACKEND / "schemas" / "bac_blanc.py").read_text(encoding="utf-8")
        check('ex.get("grade_question_id")' in bac_src and "grade_question_id" in schema_src,
              "pont ajouté (S39) : le sujet peut déclarer son rubric_id -> correction locale immédiate")
        corr_page = (_FRONTEND / "src" / "app" / "annales" / "[slug]" / "exam" / "correction" / "page.tsx").read_text(
            encoding="utf-8"
        )
        check(corr_page.count("formatTrainingPercent") >= 2,
              "UI : la ligne par exercice n'affiche plus « 0 % » sur un non-noté (— comme l'en-tête)")
        check(
            "enforce_evaluate_quota" not in bac_src,
            "constat : /api/bac-blanc/submit corrige hors quota (budget de correction non partagé)",
        )

        # ── S12 — qui paie le quota ? (F14) ───────────────────────────────
        section("S12 — le quota est bien par élève (et le plan pro respecté)")
        from rate_limit import evaluate_limit, get_user_key

        class _FakeReq:
            def __init__(self, hdrs):
                from starlette.datastructures import Headers

                self.headers = Headers(hdrs)

        key_free = get_user_key(_FakeReq(headers_for(12)))
        key_pro_real = get_user_key(
            _FakeReq({"Authorization": f"Bearer {create_access_token({'sub': 991013, 'plan': 'pro'})}"})
        )
        check(key_free.startswith("user:991012"), "l'élève authentifié a une clé par compte (pas par IP)", f"clé={key_free}")
        check(evaluate_limit(key_free) == "15/hour", "plan free -> 15 corrections/h", evaluate_limit(key_free))
        check(evaluate_limit(key_pro_real) == "80/hour", "plan pro -> 80 corrections/h (budget payant respecté)",
              evaluate_limit(key_pro_real))

        # A consomme tout son budget ; B (autre compte, même IP de test) doit rester libre
        qid12 = fe_ids[4]
        packed12 = load(qid12)
        assert packed12 is not None
        statuses_a = [
            (await grade(12, qid12, packed12.rubric.model_answer + f" أ {i}."))[0] for i in range(16)
        ]
        st_b, body_b, _ = await grade(13, qid12, packed12.rubric.model_answer + " ب.")
        check(statuses_a.count(200) == 15 and statuses_a[-1] == 429,
              "compte A : 15 corrections puis refus", f"A={statuses_a[:16]}")
        check(st_b == 200, "compte B (même IP) n'est PAS pénalisé par le quota de A",
              f"http={st_b} {json.dumps(body_b, ensure_ascii=False)[:80]}")

    app.dependency_overrides.clear()


def main() -> int:
    print("\033[1mProbe — surfaces de correction du site\033[0m (chemin élève réel, 0 LLM, 0 DB)")
    asyncio.run(_run())
    print(f"\n\033[1mRésultat :\033[0m {len(PASSES)} OK · {len(FAILURES)} échec(s)")
    for f in FAILURES:
        print(f"  \033[31m✗\033[0m {f}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
