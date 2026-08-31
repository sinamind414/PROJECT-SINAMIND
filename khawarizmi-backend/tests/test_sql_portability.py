"""Garde de portabilité du SQL brut — bug production mesuré le 2026-08-31.

`services/fsrs_unified.py` écrivait ses états FSRS avec `NOW()`. Cette fonction n'existe pas en
SQLite, or le dépôt **supporte SQLite** (`_sqlite_compat()` + `ensure_dialect_for_url()`, voir
`tests/test_dialect_guard.py`, et les docstrings « preview SQLite » du module). Conséquence mesurée :
sur SQLite, chaque `INSERT` levait, l'exception était avalée par un `except Exception: return False`,
et la mémoire de répétition de l'élève ne s'enregistrait **pas** — 22 tests rouges qui ne
racontaient pas cette histoire-là. Corrigé par `CURRENT_TIMESTAMP` (SQL standard, identique en
PostgreSQL : `timestamp with time zone`).

Ce fichier empêche deux rechutes :
1. une nouvelle écriture `NOW()` (ou consœur Postgres-only) dans un module **non exempté** ;
2. une exemption périmée, c'est-à-dire une dette déclarée réparée et qu'on traîne encore.

Les modules exemptés le sont parce que leur SQL contient de l'arithmétique de dates Postgres
(`EXTRACT(EPOCH FROM …)`, `INTERVAL '7 days'`, casts `::text`) : les convertir au doigt mouillé
casserait la production, qu'on ne peut pas exécuter ici. La dette est donc **inventoriée**, pas niée.
"""

from __future__ import annotations

import pathlib
import re

BACKEND = pathlib.Path(__file__).resolve().parent.parent

# Dettes déclarées — une par fichier, avec la raison exacte. `grep -n NOW() <fichier>` vérifie.
EXEMPT_POSTGRES_ONLY: dict[str, str] = {
    "services/interleaving.py": "EXTRACT(EPOCH FROM (NOW() - …)) : décroissance de sécurité, arithmétique PG-only",
    "services/kunz_tunnel_service.py": "NOW() dans des UPDATE de file Kunz/Tunnel, aucune couverture SQLite en test",
    "services/mindmap_service.py": "NOW() + ON CONFLICT sur la table de génération de cartes",
    "services/payment_service.py": "écriture facturation : à convertir avec une base PG en CI, pas à l'aveugle",
    "services/phase3_service.py": "NOW() - INTERVAL '30 minutes' : session active",
    "services/phase5_service.py": "NOW() - INTERVAL + casts ::text (amis, file de duel)",
    "services/phase6_service.py": "NOW() - INTERVAL '7 days' : glissement hebdomadaire",
    "services/remediation.py": "NOW() dans l'expiration de remédiation",
    "routes/auth.py": "NOW() dans les tokens/cookies : chemin critique, non testable en SQLite ici",
    "routes/bac_blanc.py": "NOW() sur les sessions d'examen (minuterie serveur)",
    "routes/lessons.py": "NOW() sur les leçons actives",
    "routes/lifespan.py": "NOW() à l'initialisation (entretien différé)",
    "routes/payment.py": "NOW() - INTERVAL '10 minutes' / '24 hours' : rapprochement de paiement",
    "routes/social.py": "NOW() sur invitations et fils sociaux",
}

PG_ONLY_MARKERS = {
    "NOW()": re.compile(r"\bNOW\(\)"),
    "ILIKE": re.compile(r"\bILIKE\b"),
    "::jsonb": re.compile(r"::jsonb"),
    "date_trunc": re.compile(r"\bdate_trunc\("),
}


def _sources() -> dict[str, str]:
    out: dict[str, str] = {}
    for folder in ("services", "routes"):
        for path in (BACKEND / folder).rglob("*.py"):
            if "__pycache__" in str(path):
                continue
            out[str(path.relative_to(BACKEND))] = path.read_text(encoding="utf-8")
    return out


def test_le_module_corrige_ne_redevient_pas_postgres_only():
    """`fsrs_unified` est le chemin d'écriture de la mémoire : aucune marque PG-only tolérée."""
    src = _sources()["services/fsrs_unified.py"]
    for marker, rx in PG_ONLY_MARKERS.items():
        assert not rx.search(src), f"régression : {marker} est réapparu dans services/fsrs_unified.py"


def test_toute_ecriture_postgres_only_est_declouee_ou_inventoriee():
    offenders: list[str] = []
    for rel, src in _sources().items():
        if rel in EXEMPT_POSTGRES_ONLY:
            continue
        # Un usage dans un commentaire n'est pas du SQL exécuté ; on ne juge que les chaînes.
        in_strings = "\n".join(re.findall(r"(?:\"\"\"|\')([\s\S]*?)(?:\"\"\"|\')", src))
        if re.search(r"\bNOW\(\)", in_strings):
            offenders.append(rel)
    assert not offenders, (
        "Nouveau SQL Postgres-only dans un module censé tenir sur SQLite : "
        f"{sorted(offenders)}. Utilise CURRENT_TIMESTAMP, ou ajoute le fichier à "
        "EXEMPT_POSTGRES_ONLY **avec la raison précise** (arithmétique de dates, cast, …)."
    )


def test_aucune_exemption_ne_traîne_inutilement():
    stale = [
        rel
        for rel in EXEMPT_POSTGRES_ONLY
        if not (BACKEND / rel).exists() or not re.search(r"\bNOW\(\)", (BACKEND / rel).read_text(encoding="utf-8"))
    ]
    assert not stale, f"exemptions périmées à retirer du registre : {stale}"
