"""
Locust — test de charge sur les trajets métier (audit 100k §5.3 / grille G0-4, §A)

Profil « un élève » : inscription une seule fois, puis alternance de
  - navigation légère (GET manhadjiya : verbs, verb/{slug})
  - remédiation contextuelle (POST /api/manhadjiya/contextual-remediation,
    endpoint pur-mémoire — Reçu R6 : 42 ms)
  - soumission + correction (POST /api/document-analysis/evaluate-v2)
    = le TRAJET CRITIQUE (le vrai endpoint d'évaluation — R15)

Usage (headless, rapport HTML+JSON) :
    cd khawarizmi-backend
    LT_PLAN=pro LT_SECRET=<SECRET_KEY du serveur> \
    .venv/bin/locust -f loadtest/locustfile.py --headless \
        --host http://127.0.0.1:8100 -u 10 -r 1 -t 90s \
        --only-summary --json /tmp/locust.json --html /tmp/locust.html

Variables d'environnement :
    LT_PLAN      free (défaut) | pro — free = plafonné 15 éval/h (le rate
                 limit fait alors partie de la mesure) ; pro = 80/h.
    LT_SECRET    secret du serveur, requis si LT_PLAN=pro (permet de forger
                 un JWT pro pour l'utilisateur créé à l'inscription).
    LT_SCENARIO  slug du scénario seeded (défaut : gene-expression-protein-disorder-v1)
    LT_EVAL_WEIGHT  poids du trajet critique dans le mix (défaut 1, sur 7)

⚠️ Interprétation : avec des clés LLM de test, l'évaluation passe par la voie
LOCALE (sanity + fallback) — la latence Gemini réelle, variable dominante
(R11), n'est PAS incluse. Re-run avec clés réelles sur une instance contrôlée
pour chiffrer le pic LLM (c'est l'objet du §B du modèle de coût).
"""

import itertools
import os
import random
import uuid

from locust import HttpUser, between, task

USER_COUNTER = itertools.count(1)

SCENARIO_ID = os.environ.get("LT_SCENARIO_ID", "gene-expression-protein-disorder-v1")
VERBS = ["analyse", "interpret", "deduce", "hypothesis", "scientific-text"]
ANSWERS = [
    "La protéine est codée par le gène grâce à la transcription puis la traduction.",
    "Un gène porte l'information qui permet de fabriquer une protéine fonctionnelle.",
    "L'ARN messager transporte l'information du gène vers les ribosomes.",
    "La structure de la protéine détermine sa fonction dans la cellule.",
]
HEAVY_WEIGHT = int(os.environ.get("LT_EVAL_WEIGHT", "1"))


class EleveUser(HttpUser):
    """Un élève : s'inscrit une fois, puis navigue/corrige à son rythme."""

    wait_time = between(2, 6)

    def on_start(self) -> None:
        self.uid = next(USER_COUNTER)
        email = f"loadtest-{self.uid}-{uuid.uuid4().hex[:6]}@bac.dz"
        r = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "LoadTest#2026",
                "prenom": "Locust",
                "wilaya": "Tlemcen",
                "filiere": "sciences",
            },
            catch_response=True,
            name="POST /api/auth/register (1×/utilisateur)",
        )
        if r.status_code != 200:
            r.failure(f"register {r.status_code}")
            raise RuntimeError(f"register {r.status_code} — serveur injoignable ?")
        self.token = r.json()["access_token"]
        if os.environ.get("LT_PLAN") == "pro":
            from jose import jwt

            secret = os.environ.get("LT_SECRET")
            if not secret:
                raise RuntimeError("LT_PLAN=pro exige LT_SECRET")
            user_id = r.json()["user"]["id"]
            self.token = jwt.encode(
                {"sub": user_id, "plan": "pro"}, secret, algorithm="HS256"
            )
        self.auth = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def navigation_manhadjiya(self) -> None:
        with self.client.get("/api/manhadjiya/verbs", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"verbs {r.status_code}")
        slug = random.choice(VERBS)
        with self.client.get(
            f"/api/manhadjiya/verb/{slug}", catch_response=True
        ) as r:
            if r.status_code != 200:
                r.failure(f"verb/{slug} {r.status_code}")

    @task(3)
    def remediation_contextuelle(self) -> None:
        body = {"verb_slug": random.choice(VERBS), "context": "unité: التعبير المورثي"}
        with self.client.post(
            "/api/manhadjiya/contextual-remediation",
            json=body,
            catch_response=True,
        ) as r:
            if r.status_code != 200:
                r.failure(f"remediation {r.status_code}")

    @task(HEAVY_WEIGHT)
    def soumission_correction(self) -> None:
        """Trajet critique : soumission + correction (evaluate-v2)."""
        body = {
            "scenario_id": SCENARIO_ID,
            "answers": [
                {
                    "verb_slug": random.choice(VERBS),
                    "answer": random.choice(ANSWERS),
                    "question_id": "q1",
                }
            ],
        }
        with self.client.post(
            "/api/document-analysis/evaluate-v2",
            json=body,
            headers=self.auth,
            catch_response=True,
        ) as r:
            # 429 = le rate limit fait son travail (free 15/h) — pas un échec.
            if r.status_code not in (200, 429):
                r.failure(f"evaluate-v2 {r.status_code}: {r.text[:200]}")
