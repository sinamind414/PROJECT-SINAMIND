# Recall FE ↔ BE — P2.3 Gap

## Runtime STV

**FE** `localStorage["khawarizmi.recall_items.v1"]` — unique source de
vérité runtime.

**BE** `recall_items` table — **0 lignes en production** tant qu'aucun
mécanisme de création n'est branché.

## Architecture

```
FE (localStorage)                    BE (PostgreSQL)
┌──────────────────────────┐         ┌──────────────────────┐
│ recall_items.v1          │         │ tunnel_events        │
│  ← créé par              │ POST    │  ← append-only       │
│    openRecallGate*()     │ /event  │  ← ne crée PAS       │
│  ← jamais envoyé au BE   │────────►│    recall_items      │
│                          │         │                      │
│                          │         │ recall_items         │
│ (FE n'appelle jamais     │         │  ← 0 lignes          │
│  /recall/due ni          │◄/due────│  ← handlers prêts    │
│  /recall/{id}/result)    │   /result│    mais rien ne peuple│
└──────────────────────────┘         └──────────────────────┘
```

## Matrice d'ownership

| Action | FE | BE |
|--------|----|----|
| Schedule after evaluation | ✅ `localStorage` — `openRecallGateAndScheduleItem` | ❌ |
| Due list UI | ✅ lit localStorage | ❌ vide |
| Submit recall result (SI UI recall) | ✅ reducer recall local | ❌ sauf P2.3b |
| Audit tunnel | ❌ | ✅ `tunnel_events` (append-only) |
| Abort → recall | 0 recall créé | event only, 0 recall |

## Règles absolues

1. **`append_event`** ne doit JAMAIS créer de `recall_items` (cf. B3 P1.3).
2. **`openRecallGateAndScheduleItem`** = STV locale seulement ; pas de
   fetch réseau avant P2.3b.
3. **FE & BE** partagent la grille `RECALL_DELAY_DAYS = {0:1, 1:3, 2:7,
   3:14}` — dupliquée, pas synchro runtime.
4. **`abort`** → toujours 0 recall créé.
5. **Failed E0** → `success:false` dans le recall local ; si POST /result
   existe un jour, équivalent stage reset.

## Quand passer à P2.3b (Option B)

Besoin produit multi-appareil / dashboard tuteur / due list serveur /
analytics nécessitant les recall items côté BE.

P2.3b ajouterait :
- `POST /api/recall` — créer recall_item (idempotent par lesson_id)
- `openRecallGateAndScheduleItem` → 1. local (inchangé) 2.
  fire-and-forget POST /api/recall
- `GET /api/recall/due` — enfin non vide
- `POST /api/recall/{id}/result` — utilisable par une UI recall future

Interdit en P2.3b :
- Créer recall_items dans `append_event`
- 5ᵉ porte FE (toujours `openRecallGateAndScheduleItem`)
- Réimplémenter `canAdvance` / coach côté BE

## Historique

- 2026-07-22 : P2.3 Option A documentée — constat du gap
