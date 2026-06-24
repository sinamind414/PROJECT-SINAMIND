# routes/openapi_config.py — Configuration OpenAPI/Swagger

description = """
**Plateforme educative IA pour lyceens algeriens (Bac Sciences Naturelles).**

### Fonctionnalites
- **Chat IA** — Tutorat SVT avec RAG + 4 piliers pedagogiques
- **Flashcards** — Repetition espacee (FSRS Graph)
- **Mind Maps** — Cartes mentales dynamiques JSON + Mermaid
- **Evaluation** — Corrections automatiques type Bac
- **Lexique** — 221+ termes SVT bilingue (FR/AR)
- **Dual Coding** — Schemas + texte

### Auth
- `POST /api/auth/register` puis `POST /api/auth/login`
- Inclure le token JWT dans le header `Authorization: Bearer <token>`

### Rate Limiting
- Gratuit : 20 req/h chat, 15 req/h evaluation
- Premium : 100 req/h chat, 80 req/h evaluation

### Langues
- Reponses en francais (defaut) ou arabe selon `Accept-Language`
"""

openapi_metadata = {
    "title": "Khawarizmi Pro API",
    "description": description,
    "version": "2.0.0",
    "contact": {
        "name": "Khawarizmi Team",
        "url": "https://github.com/anomalyco",
        "email": "contact@ia-khawarizmi.dz",
    },
    "license_info": {
        "name": "Proprietary — Usage educatif uniquement",
        "url": "https://ia-khawarizmi.dz/license",
    },
    "openapi_tags": [
        {"name": "Auth", "description": "Inscription, connexion, profil"},
        {"name": "Chat", "description": "Tutorat IA (RAG + 4 piliers)"},
        {"name": "Chatbot", "description": "Chatbot SVT autonome"},
        {"name": "Flashcards", "description": "FSRS spaced repetition"},
        {"name": "Mindmap", "description": "Cartes mentales dynamiques"},
        {"name": "Evaluation", "description": "Correction automatique Bac"},
        {"name": "Contenu", "description": "Cours, lexique, annales, exercices"},
        {"name": "Session", "description": "Sessions de revision"},
        {"name": "Progression", "description": "Suivi FSRS et stats"},
        {"name": "Paiement", "description": "Abonnements Chargily"},
        {"name": "Systeme", "description": "Sante, debugging, metriques"},
    ],
}
