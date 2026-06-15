# Rapport pour Claude — IA Khawarizmi Pro

## État d'avancement du projet Lexique SVT Terminale

---

## Ce qui a été fait

### 1. Analyse du programme (4 fichiers sources)
- **`programme_sciences_3as.backup_20260608_181234.json`** — Structure squelette : 6 chapitres (`ch1_proteines`, `ch_structure`, `ch2_enzymes`, `ch3_immunite`, `ch_nerveux`, `ch_minhajiya`) avec concepts clés en arabe
- **`programme_sciences_3as.json`** — Base de questions BAC réelles, chaque question taggée avec `micro_concept_id` et `diagnostic_erreur_cible`
- **`methodologie_sciences_3as.json`** — Règles méthodologiques, progression officielle, erreurs fréquentes
- **`eddirasa_minhajiya_links.json`** — 31 URLs eddirasa.com avec résumés par chapitre

### 2. Validation du schéma
- **`lexique_svt_terminale_sample.json`** — Extrait de validation avec 34 termes couvrant les 3 domaines et 11 catégories, liens transversaux inclus

### 3. Infrastructure backend (code prêt)
- **`models/lexique.py`** — Modèle SQLAlchemy `LexiqueTerme` avec 26 colonnes (ARRAY pour synonymes/tags/exemples, JSONB pour données brutes)
- **`schemas/lexique.py`** — Pydantic `LexiqueTermeResponse` + `LexiqueSearchResponse`
- **`migrations/versions/005_lexique_termes.py`** — Migration Alembic avec 6 index (dont composite importance+chapitre+type)
- **`routes/lexique.py`** — 4 endpoints REST :
  - `GET /api/lexique/search?q=...&chapitre=...&domaine=...&importance=...`
  - `GET /api/lexique/{id}`
  - `GET /api/lexique/by-chapter/{chapitre}`
  - `GET /api/lexique/by-domaine/{domaine_id}`
- **`models/__init__.py`** et **`main.py`** — Modèle et route enregistrés

### 4. Prompt de génération
- **`data/prompt_claude_lexique.md`** — Prompt détaillé pour générer le JSON complet du lexique (schéma, règles, structure des 3 domaines, types valides)

---

## Ce qui reste à faire

### 1. Générer le lexique complet
- Utiliser `prompt_claude_lexique.md` comme instruction
- Générer un fichier `lexique_svt_terminale_complet.json` avec **300+ termes**
- Couvrir les 3 domaines et 11 chapitres
- Valider la structure JSON avant import

### 2. Importer le lexique en base de données
- Créer un script d'import : lire le JSON → insérer dans `lexique_termes`
- Utiliser `INSERT ... ON CONFLICT (id) DO UPDATE` pour l'upsert

### 3. Intégration RAG
- Enrichir le contexte du tutor (`rag_service.py`) avec les définitions du lexique
- Quand une question contient un terme du lexique, injecter sa définition dans le prompt

### 4. Intégration Mind Maps
- Lier les nœuds de mind map aux IDs du lexique
- Afficher les définitions en tooltip (français/arabe)
- Connecter `flashcard_auto` du lexique avec la génération FSRS

---

## Architecture technique

```
Backend (FastAPI)
├── models/lexique.py          ← Modèle DB
├── schemas/lexique.py         ← Pydantic
├── routes/lexique.py          ← Endpoints
└── migrations/versions/       ← Migration 005

Données
├── data/programme_sciences_3as.json          ← Questions BAC
├── data/programme_sciences_3as.backup_*.json ← Structure chapitres
├── data/methodologie_sciences_3as.json       ← Méthodologie
├── data/eddirasa_minhajiya_links.json        ← URLs eddirasa
├── data/prompt_claude_lexique.md             ← Prompt génération
├── data/lexique_svt_terminale_sample.json    ← Extrait validation
└── data/lexique_svt_terminale_complet.json   ← À générer (300+ termes)
```

---

## Règles absolues à respecter

1. **Encoding** : UTF-8, caractères arabes préservés
2. **Indentation** : 2 espaces dans le JSON
3. **IDs** : `term-XXX` (3 digits, ex: term-001, term-042, term-301)
4. **Types valides** : molecule, enzyme, concept, processus, cellule, organite, structure, mecanisme
5. **Importance** : critique → haute → moyenne
6. **micro_concept_id** : doit matcher les IDs du programme (`ch1_proteines`, `ch_structure`, `ch2_enzymes`, `ch3_immunite`, `ch_nerveux`)
7. **Liens transversaux** : minimum 15-20 liens entre termes de différents domaines
8. **Pas de commentaires** dans le JSON

---

*Généré le 2026-06-15 — Projet IA Khawarizmi Pro v2.0.0*
