# AGENTS.md — IA Khawarizmi Pro
# Version : 2.1.0
# Emplacement : Racine du projet
# Rôle : System Prompt permanent pour tout agent IA
#         intervenant sur ce projet

##############################################################
# SECTION 0 — IDENTITÉ DU PROJET
##############################################################

Tu travailles sur **IA Khawarizmi Pro**.

C'est une plateforme éducative IA destinée aux lycéens
algériens préparant le Bac Sciences Naturelles.

Stack technique officiel :
- Backend  : FastAPI + Python 3.12
- Base     : PostgreSQL 16 + pgvector
- Cache    : Redis 7
- IA       : Gemini 2.5 Flash (principal)
             OpenAI GPT (fallback 1)
             Pattern matching local (fallback 2)
             JSON de sécurité (fallback 3)
- Auth     : JWT uniquement (python-jose + bcrypt)
- Répétion : Algorithme FSRS Graph
- Deploy   : Railway (Docker)
- Frontend : Next.js 16 + React 19 + TailwindCSS 4
- Mobile   : React Native + Expo 56

##############################################################
# SECTION 1 — RÈGLES ABSOLUES (NE JAMAIS VIOLER)
##############################################################

## 1.1 Sécurité

- JAMAIS de clé API, token ou mot de passe dans le code
- JAMAIS de valeur par défaut pour SECRET_KEY en production
- JAMAIS de fichier .env commité dans Git
- TOUJOURS lever une ValueError si SECRET_KEY absent :

  ```python
  secret_key = os.environ.get("SECRET_KEY")
  if not secret_key:
      raise ValueError(
          "SECRET_KEY non défini. Arrêt du serveur."
      )
  ```

- TOUJOURS utiliser **JWT uniquement** pour l'auth
- JAMAIS de double système auth (pas de Supabase Auth,
  pas de localStorage token, pas de demo_local_token)

## 1.2 Architecture Code

- main.py : **maximum 100 lignes** (imports + init + lifespan)
- Un fichier = Une responsabilité unique
- Migrations : **Alembic uniquement** (jamais SQL inline)
- Dépendances : **versions épinglées** dans requirements.txt

Structure obligatoire du backend :

```
khawarizmi-backend/
├── main.py              (max 100 lignes)
├── config.py            (Settings Pydantic)
├── auth.py              (JWT uniquement)
├── database.py          (connexion DB)
├── cache.py             (Redis uniquement)
├── schemas/
│   ├── user.py
│   ├── session.py
│   ├── flashcard.py
│   ├── mindmap.py
│   └── lexique.py
├── models/
│   ├── user.py
│   ├── concept.py
│   ├── session.py
│   ├── payment.py
│   ├── reference.py
│   └── lexique.py
├── routes/
│   ├── auth.py
│   ├── chat.py
│   ├── evaluate.py
│   ├── flashcards.py
│   ├── mindmap.py
│   ├── sessions.py
│   ├── health.py
│   ├── programme.py
│   ├── lexique.py
│   └── payment.py
├── services/
│   ├── rag_service.py
│   ├── ai_service.py
│   ├── fsrs_service.py
│   ├── mindmap_service.py
│   ├── payment_service.py
│   └── khawarizmi_engine.py
├── migrations/
│   ├── env.py
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_programme_officiel.py
│       ├── 003_mindmaps_and_nodes.py
│       ├── 004_rag_chunks.py
│       └── 005_lexique_termes.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_chat.py
│   ├── test_mindmap.py
│   └── test_fsrs.py
├── scripts/
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 1.3 Ports et Déploiement

- TOUJOURS utiliser `$PORT` dynamique (Railway l'injecte)
- JAMAIS de port hardcodé dans railway.toml
- Configuration correcte obligatoire :

  ```dockerfile
  # Dockerfile
  CMD ["sh", "-c",
       "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
  ```

  ```toml
  # railway.toml
  [deploy]
  startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
  ```

## 1.4 Rate Limiting

- TOUJOURS appliquer slowapi sur /api/chat et /api/evaluate
- Quotas obligatoires :
  - Gratuit  : 20 req/heure chat — 15 req/heure evaluate
  - Premium  : 100 req/heure chat — 80 req/heure evaluate

## 1.5 SQL et Base de Données

- JAMAIS de concaténation de chaînes dans les requêtes SQL
- JAMAIS de `IN :param` avec tuple (bug asyncpg)
- TOUJOURS utiliser `ANY(:array)` pour les listes :

  ```python
  # Correct
  await db.execute(
      text("SELECT * FROM t WHERE id = ANY(:ids)"),
      {"ids": list(my_ids)}
  )
  ```

##############################################################
# SECTION 2 — LES 4 PILIERS PÉDAGOGIQUES
##############################################################

Toute réponse de l'IA au tuteur doit respecter ces 4 piliers.
Ne jamais générer de code qui les contourne.

## Pilier 1 — Simplification (Feynman)
- Explication simple avant technique
- Analogie concrète obligatoire
- Méthode Socratique intégrée (guider, pas donner)

## Pilier 2 — Rappel Actif (Active Recall)
- Questions L1 (restitution) → L2 (application)
         → L3 (type Bac)
- Jamais donner la réponse dans la même réponse

## Pilier 3 — Répétition Espacée (FSRS)
- Flashcards : Recto (max 15 mots) / Verso (max 30 mots)
- Intégration obligatoire avec l'algorithme FSRS Graph
- Plan : J+0 / J+1 / J+3 / J+7 / J+14 / J+30

## Pilier 4 — Mind Map Dynamique (JSON)
- Schéma JSON obligatoire (voir Section 4)
- Connexion automatique avec FSRS
- 3 niveaux de rendu :
  A) Textuel (toujours)
  B) Mermaid.js (si supporté)
  C) JSON Dynamique (interface avancée)

##############################################################
# SECTION 3 — POLITIQUE RAG STRICTE
##############################################################

- L'IA répond UNIQUEMENT à partir du contexte RAG fourni
- Si contexte vide → répondre :
  "Je n'ai pas trouvé cette information dans la base.
   Consulte ton manuel officiel."
- JAMAIS inventer une définition, formule, corrigé,
  barème ou référence ONEC

Exception de Navigation :
  Si l'élève demande la liste des chapitres ou
  le programme officiel → autoriser les connaissances
  générales avec mention obligatoire de la source.

##############################################################
# SECTION 4 — SCHÉMA JSON MIND MAP (RÉFÉRENCE)
##############################################################

```json
{
  "id": "string-unique",
  "titre": "NOM DU CHAPITRE",
  "matiere": "SVT | Maths | Physique...",
  "filiere": "Sciences Naturelles...",
  "racine": {
    "id": "string",
    "label": "string — max 5 mots",
    "type": "concept|definition|formule|processus|exception",
    "niveau": 0,
    "importance": "critique|haute|moyenne",
    "bac_frequent": true,
    "flashcard_auto": true,
    "maitrise_eleve": 0,
    "couleur": "#E74C3C",
    "enfants": [],
    "liens": []
  },
  "liens_transversaux": [
    {
      "source": "id_noeud",
      "target": "id_noeud",
      "relation": "string",
      "type": "causal|dependance|opposition|inclusion"
    }
  ],
  "metadata": {
    "genere_le": "ISO date",
    "version": "1.0",
    "source_rag": "nom du chunk"
  }
}
```

Règles Mind Map :
- Maximum 3 niveaux de profondeur
- Maximum 7 enfants par nœud
- Maximum 5 mots par label
- flashcard_auto = true si importance critique ou haute
- Couleurs : critique=#E74C3C haute=#F39C12 moyenne=#3498DB

Endpoints obligatoires :
- POST /api/mindmap/generate      (générer)
- GET  /api/mindmap/{id}          (récupérer)
- PATCH /api/mindmap/{node}/maitrise (mettre à jour)
- GET  /api/mindmap/{id}/weak     (nœuds faibles)

##############################################################
# SECTION 5 — GITIGNORE OBLIGATOIRE
##############################################################

Le .gitignore racine doit contenir exactement :

```gitignore
# Environnement — CRITIQUE
**/.env
**/.env.*
!**/.env.example

# Secrets
*.pem
*.key
*.p12
secrets/

# Backups et données lourdes
*.backup_*
*.backup_inject_*
*.bak

# Python
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/

# Node
node_modules/
.next/
dist/
.expo/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Modèles IA lourds
models/
*.zip
*.tar.gz
*.gguf

# Logs
*.log
logs/
```

Encodage : UTF-8 obligatoire (jamais UTF-16)

##############################################################
# SECTION 6 — TESTS OBLIGATOIRES
##############################################################

- conftest.py obligatoire dans tests/
- pytest-asyncio obligatoire
- Couverture minimum : 50% (en vigueur) — objectif 70%
- CI/CD GitHub Actions obligatoire (configuré)

tests/conftest.py (en place) :

```python
import pytest
import asyncio
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        yield ac
```

Tests obligatoires par module (13 fichiers en place) :
- test_auth.py             : register, login, token invalide
- test_chat.py             : RAG valide, RAG vide, rate limit
- test_mindmap.py          : génération, structure JSON,
                             flashcard auto, FSRS sync
- test_fsrs.py             : création carte, schedule, weak nodes
- test_config_critical.py  : détection régression case_sensitive
- test_payment.py          : flux paiement
- test_ch1_integration.py  : intégration chapitre 1
- test_evaluate_full.py    : pipeline évaluation complet
- test_ia_appel.py         : appel IA
- test_sciences.py         : tests spécifiques SVT
- test_simulateur.py       : tests simulateur

##############################################################
# SECTION 7 — MONITORING
##############################################################

- Sentry obligatoire en production
- Health check endpoint /health obligatoire :

  ```json
  {
    "status": "healthy",
    "version": "2.0.0",
    "database": "connected",
    "redis": "connected",
    "ai_model": "gemini-2.5-flash",
    "fallback_active": false,
    "timestamp": "ISO date"
  }
  ```

- Alertes obligatoires :
  Erreur 500 → alerte immédiate
  Rate limit massif → alerte
  Clé API invalide → alerte
  Fallback IA activé → log

##############################################################
# SECTION 8 — COMPORTEMENT DE L'AGENT
##############################################################

## Avant de générer du code, toujours vérifier :

  [ ] Aucune clé API dans le code
  [ ] `case_sensitive=False` dans SettingsConfigDict
  [ ] `get_settings().X` au lieu de `os.getenv("X")`
  [ ] `CAST(:emb AS vector)` au lieu de `:emb::vector`
  [ ] SECRET_KEY lève ValueError si absent
  [ ] main.py reste sous 100 lignes
  [ ] Un fichier = Une responsabilité
  [ ] Migrations via Alembic
  [ ] Dépendances épinglées
  [ ] Rate limiting présent si endpoint IA
  [ ] JWT vérifié sur chaque endpoint protégé
  [ ] ANY(:array) au lieu de IN :tuple
  [ ] $PORT dynamique (jamais hardcodé)

## Si une règle est violée dans la demande :

  → Signaler AVANT de générer le code :
    "⚠️ Cette demande viole la règle [X].
     Voici la version corrigée conforme
     au prompt développeur Khawarizmi Pro."

## Format de réponse code :

  1. Fichier concerné (chemin complet)
  2. Code complet (jamais de "..." ou "[reste du code]")
  3. Commandes d'installation si nouvelles dépendances
  4. Test correspondant si applicable

## Langue :

  - Commentaires dans le code : Français
  - Variables et fonctions : Anglais (snake_case)
  - Noms de fichiers : Anglais (snake_case)

##############################################################
# SECTION 9 — PRIORITÉS ACTUELLES DU PROJET
##############################################################

État au moment de la rédaction de ce fichier :

CRITIQUE — À faire immédiatement :
  [x] Régénérer toutes les clés API exposées
  [x] Réécrire .gitignore en UTF-8 propre
  [x] Corriger les ports ($PORT partout)
  [x] Unifier l'auth sur JWT uniquement
  [x] Ajouter rate limiting sur /api/chat
      et /api/evaluate

IMPORTANT — À faire ce mois :
  [x] Refactorer main.py (1296 lignes → 96 lignes)
  [x] Épingler les dépendances requirements.txt
  [x] Configurer Alembic pour les migrations (5 versions)
  [x] Créer conftest.py et activer les tests (13 fichiers)
  [x] Configurer GitHub Actions CI/CD

STRATÉGIQUE — À faire ce trimestre :
  [x] Implémenter Mind Map JSON dynamique (4 endpoints)
  [x] Ajouter Sentry monitoring
  [x] Implémenter /health endpoint
  [x] Implémenter Lexique SVT bilingue (221 termes, 4 endpoints API, RAG)
  [x] Connecter Next.js frontend au backend (en cours)
  [x] Connecter Mind Map ↔ FSRS

##############################################################
# SECTION 11 — BUGS CRITIQUES CONNUS & RÉSOLUS
##############################################################

## Bug 1 : case_sensitive dans SettingsConfigDict

RÈGLE : Toujours utiliser `case_sensitive=False` dans SettingsConfigDict.
RAISON : Les variables .env en UPPER_CASE doivent matcher les champs
         snake_case Python. Avec `True`, les clés API sont ignorées
         silencieusement sans aucune erreur.
FICHIER : config.py → model_config → case_sensitive
DÉTECTION : Config loader
IMPACT : Critique — toutes les clés API deviennent inopérantes,
         le serveur utilise les valeurs par défaut sans alerte.

## Bug 2 : Cast vector dans SQL

RÈGLE : Utiliser `CAST(:emb AS vector)` au lieu de `:emb::vector`.
RAISON : Compatibilité asyncpg garantie sur toutes les versions.
         `::vector` fonctionne en local mais peut casser selon
         la version de asyncpg/PostgreSQL en production.
FICHIER : mindmap_service.py → requête RAG
IMPACT : Élevé — la recherche vectorielle RAG peut échouer

## Bug 3 : os.getenv au lieu de get_settings()

RÈGLE : TOUJOURS utiliser `get_settings().X`.
INTERDIT : `os.getenv("X")` (sauf pour bootstrap pré-config).
RAISON : os.getenv lit l'environnement SYSTÈME, pas le fichier .env.
         get_settings() lit via Pydantic → source de vérité unique.
FICHIERS : mindmap_service.py, llm.py (et tout nouveau service)
IMPACT : Élevé — configuration incohérente entre machines

## Bug 4 : Alembic stamp échoue silencieusement avec asyncpg

RÈGLE : Utiliser SQL direct au lieu de `alembic stamp` pour forcer
        la version de migration en base.
RAISON : `alembic stamp 005` ne produit pas d'erreur mais n'écrit
         PAS la ligne dans `alembic_version`. Le problème vient
         de l'interaction entre asyncpg et le driver Alembic.
WORKAROUND : `psql -c "UPDATE alembic_version SET version_num = '005'"`
             ou via SQLAlchemy raw_connection.
FICHIER : migrations/env.py (driver asyncpg)
IMPACT : Moyen — retarde les déploiements si non documenté

## Bug 5 : postcss vulnérable dans Next.js (moderate, accepté)

SÉCURITÉ : `npm audit --omit=dev` rapporte 2 moderate.
CAUSE : `postcss <8.5.10` embarqué par Next.js dans sa chaîne de build.
        CVE : GHSA-qx2v-qp2m-jg93 (XSS via `</style>` non échappé).
FIX DIRECT : Aucun — `npm audit fix --force` downgrade Next 16 → 9 (breaking).
SURFACE : Build-time uniquement, nécessite input CSS utilisateur contrôlé.
          Non exploitable dans l'état actuel de l'application.
STATUT : Accepté temporairement. Résolu upstream quand Next 16.3+ bundle
         postcss ≥8.5.10, ou en retirant le lock postcss du bundle.
FICHIER : khawarizmi-frontend/package.json (dépendance transitive next)
IMPACT : Faible — modéré, build-time, pas de risque runtime.

## Bug 6 (RÉSOLU) : next-pwa vulnérable retiré

SÉCURITÉ : `serialize-javascript ≤7.0.2` (high) via la chaîne
           next-pwa → workbox-webpack-plugin → serialize-javascript.
CAUSE : next-pwa n'était pas configuré (aucun import, aucune config).
FIX : `npm uninstall next-pwa` — package mort, 0 impact fonctionnel.
IMPACT : Résolu — 5 high supprimés du rapport npm audit.

##############################################################
# SECTION 12 — TESTS DE RÉGRESSION OBLIGATOIRES
##############################################################

En plus des tests de la Section 6, ces tests spécifiques sont
obligatoires pour détecter des régressions silencieuses :

- test_config_critical.py : Détecte le retour du bug case_sensitive
  (vérifie que les variables UPPER_CASE du .env sont lues)

##############################################################
# FIN — AGENTS.md v2.1.0 — IA KHAWARIZMI PRO
# Ce fichier est la source de vérité du projet.
# Toute décision de développement s'y réfère.
##############################################################
