# AGENTS.md — IA Khawarizmi Pro
# PATCH FABLE 5 PERMANENT – 2026-07-03
# - Mode Fable 5 + Rigor Pack activé en permanence
#   (plan-gate, scope-fence, live-state-truth, adversarial-verify,
#    ruthless-editor, memory-hygiene, visuel, preuve réelle)
# - skills fable 5, fabuleux et fabuleux-v3 supprimés
# - LOT 8 : routes/manhadjiya.py, 9 endpoints REST,
#   VERB_UNIT_MAP, PRACTICAL_EXAMPLES, get_full_remediation(), 99 tests
#

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
# SECTION 0b — MODE FABLE 5 + RIGOR PACK (ACTIF EN PERMANENCE)
##############################################################

Le protocole Fable 5 renforcé par Rigor Pack est **actif en permanence**
sur chaque session, sans besoin d'invocation `/skill`.

## Actes obligatoires

Sauf tâche triviale (1 ligne, pas d'effet de bord) ou impossibilité
réelle à signaler :

1. **Classer** la tâche : ARTEFACT/AGENTIQUE, PROSE, ANALYSE/CONSEIL ou MÉMOIRE.
2. **Définir le succès** : 2-4 critères concrets.
3. **Plan-gate** si multi-étapes : plan court avant la première modification.
4. **Scope-fence** si modification d'existant : exactement ce qui est demandé,
   signaler le reste sans le corriger.
5. **Live-state-truth** avant toute affirmation système : vérifier l'état réel.
6. **Produire un premier jet fini** : livrable utilisable, pas une intention.
7. **Observer** le résultat réel : exécuter, tester, lire, capturer.
8. **Corriger** après observation.
9. **Adversarial-verify** avant livraison : attaquer son propre travail.
10. **Livrer sobrement** : produit, preuves, limites.

## Règles Rigor Pack intégrées

- **Plan-gate** : GOAL + UNKNOWNS + SUCCESS CRITERIA + STEPS + OUT OF SCOPE
- **Scope-fence** : ne modifier que ce qui est demandé ; flagger le adjacent non touché
- **Live-state-truth** : le système est la source de vérité, pas sa documentation
- **Adversarial-verify** : verdict SURVIVED / REFUTED / UNTESTABLE HERE
- **Ruthless-editor** : viser 20-30% plus court sans perte d'information
- **Memory-hygiene** : dater, vérifier, ne pas persister de secrets

## Route par type de tâche

- **ARTEFACT/AGENTIQUE** : produire → observer (capture, test, rendu)
  → corriger → vérifier → livrer avec preuve
- **PROSE** : draft → ruthless-editor → relire → livrer le texte final
- **ANALYSE/CONSEIL** : faits ≠ hypothèses ≠ jugement → vérifier faits décisifs
  → adversarial-verify → dire la vérité utile
- **MÉMOIRE** : memory-hygiene → l'état réel gagne toujours sur la mémoire

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
│   ├── auth.py              # JWT
│   ├── chat.py              # /api/chat (rate limit)
│   ├── evaluate.py          # /api/evaluate (rate limit)
│   ├── flashcards.py        # FSRS drill
│   ├── mindmap.py           # mind map JSON
│   ├── session.py           # sessions
│   ├── health.py
│   ├── programme.py
│   ├── lexique.py
│   ├── payment.py
│   # --- extensions validées ---
│   ├── cours.py
│   ├── exercices.py
│   ├── lessons.py
│   ├── action_verbs.py
│   ├── document_analysis.py
│   ├── bac_blanc.py
│   ├── annales.py
│   ├── videos.py
│   ├── progress.py
│   ├── chatbot.py
│   ├── tuteur.py
│   ├── dual_coding.py
│   └── orientation.py
├── services/
│   # piliers
│   ├── llm.py                 # ai_service
│   ├── chat_service.py
│   ├── fsrs_graph.py          # fsrs_service
│   ├── mindmap_service.py
│   ├── payment_service.py
│   ├── khawarizmi_engine.py
│   # extensions
│   ├── scheduler.py
│   ├── questions.py
│   ├── correction_service.py
│   ├── document_analysis_service.py
│   ├── action_verbs_service.py
│   ├── orientation_service.py
│   ├── (... 29 fichiers au total)
│   # voir: services/__init__.py
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
  [x] LOT 5 : Base connaissance scientifique (5 unités, 189 termes, 83 faits, 54 erreurs)
  [x] LOT 6 : Alignement V1↔V2 (25 verbes), sécurité next-pwa supprimé, fix lint
  [x] LOT 7 : 6 PDFs BAC, 37 erreurs, 72 verbes Bloom, 2 verbes nouveaux (27 total)
  [x] LOT 8 : routes/manhadjiya.py (9 endpoints), VERB_UNIT_MAP (27 verbes),
      PRACTICAL_EXAMPLES (11 exemples), get_full_remediation(), 99 tests
  [x] Mode Fable 5 + Rigor Pack actif permanent

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

##############################################################
# SECTION 12 — TESTS DE RÉGRESSION OBLIGATOIRES
##############################################################

En plus des tests de la Section 6, ces tests spécifiques sont
obligatoires pour détecter des régressions silencieuses :

- test_config_critical.py : Détecte le retour du bug case_sensitive
  (vérifie que les variables UPPER_CASE du .env sont lues)

##############################################################
# SECTION 13 — VARIABLES RAILWAY OBLIGATOIRES
##############################################################

Variables à configurer dans Railway Dashboard (PROJECT-SINAMIND → Variables) :

## Groq (remplace Gemini comme IA principale)
- OPENAI_API_KEY       = gsk_...    (clé Groq, auto-détectée par préfixe gsk_)
- OPENAI_BASE_URL      = https://api.groq.com/openai/v1
- OPENAI_MODEL         = llama-3.3-70b-versatile
- AI_MODEL_PRIMARY     = llama-3.3-70b-versatile

## Base de données
- DATABASE_URL  = postgresql+asyncpg://...(injecté par Railway Postgres)
- REDIS_URL     = redis://...(injecté par Railway Redis)

## Sécurité
- SECRET_KEY    = <min 32 caractères, généré aléatoirement>
- ENVIRONMENT   = production

## Version (ne PAS définir sauf override explicite)
- VERSION       = 2.0.0-rc.1  (optionnel — sinon lu depuis config.py)

## Monitoring
- SENTRY_DSN    = <Sentry DSN> (optionnel)

##############################################################
##############################################################
# SECTION 14 — ANCRAGE DE SESSION
##############################################################
# DERNIÈRE SESSION : 2026-07-04 — Gamification Sprint 3 (final)
#
# État : Build clean, 549/549 tests pass, Vercel deployé
# Commit : 0ff011c
# URL : https://khawarizmi-ia-two.vercel.app
#
# Gamification complète (3 sprints, 12 tâches) :
#
# Sprint 1 (Streak + Boss + Badges) :
#   ✅ Quick Win 1: 40 citations motivantes en darija
#   ✅ Quick Win 2: HardestVerbPoll (mini-sondage footer)
#   ✅ Quick Win 3: StreakBanner (localStorage + backend sync)
#   ✅ Streak backend (migration 027, service, routes)
#   ✅ 12 Badges backend + frontend (achievements page)
#   ⏳ Boss Final (en attente — 2-3j)
#
# Sprint 2 (Social + Économie) :
#   ✅ Duel 1v1 (create, share token, accept, submit, leaderboard)
#   ✅ Leaderboard national/wilaya/school (weighted scoring)
#   ✅ Gemmes system + shop (6 items, balance, spend, transactions)
#   ✅ Migration 028: duels, gems, user_stats
#
# Sprint 3 (Carte + Onboarding + Polish) :
#   ✅ Carte des Verbes d'Algérie (24 villes = 24 verbes, SVG map)
#   ✅ Onboarding 3 étapes (nouveaux utilisateurs guidés)
#   ✅ Polish: useSound hook, manifest.json PWA
#   ✅ Migration 029: verb_cities, city_progress, user_onboarding
#
# Fichiers ajoutés (total) :
#   Frontend (17) : achievements, map, shop, duel(x2), leaderboard,
#     StreakBanner, HardestVerbPoll, MotivationalQuote, GemsCounter,
#     OnboardingOverlay, useLocalStreak, useSound, motivational-quotes
#   Backend (14) : streaks, badges, gems, duels, leaderboard, cities,
#     onboarding routers + services + shop_service
#   Migrations : 027 (streaks/badges/boss), 028 (gems/duels/stats),
#     029 (cities/onboarding)
#
# Routes API : 36 endpoints opérationnels
#   /api/streaks/... (3), /api/badges/... (1), /api/gems/... (4),
#   /api/duels/... (5), /api/leaderboard/... (3), /api/cities/... (5),
#   /api/onboarding/... (3)
#
# Session 2026-07-04 — VerbLessonFlow Phase B+ (Highlight + Voice)
#
# ✅ Tâche D: Page verbe "analyse" interactive (VerbLessonFlow.tsx 6 étapes)
# ✅ Tâche E: Rollout 24 verbes data-driven via buildLesson() + INTERACTIVE_LESSON_VERBS[]
# ✅ Phase B+: computeLiveSegments() (vert requis, rouge interdits)
# ✅ Phase B+: SpeechRecognition API (Mic/MicOff bouton)
# ✅ Phase B+: renderVisualFeedback() chips succès/erreur/oubli
# ✅ Phase B+: Audio play/pause
# ✅ Déploiement: Vercel (khawarizmi-ia-two.vercel.app) + Railway (healthy)
# ✅ Commit: 61fd54b — Build 37 routes, 0 erreurs
#
# Fichiers modifiés (1) :
#   khawarizmi-frontend/src/components/methodology/VerbLessonFlow.tsx
#     (248 insertions, 21 deletions, 23.9 KB final)
#
# Prochaine étape : Boss Final si souhaité
#   → seed_boss_questions.py (24+12 questions Bac)
#   → boss_service.py + routes/boss.py
#   → app/action-verbs/boss/page.tsx
##############################################################

# FIN — AGENTS.md v2.1.1 — IA KHAWARIZMI PRO
# Ce fichier est la source de vérité du projet.
# Toute décision de développement s'y réfère.
##############################################################
