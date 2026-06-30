# Audit technique ciblé — moteur RAG

## Fichiers audités
- `khawarizmi-backend/services/rag_service.py`
- `khawarizmi-backend/services/reranker.py`
- `khawarizmi-backend/services/embedder.py`

## Objectif
Optimiser le moteur RAG sans casser l'API existante ni les consommateurs actuels (chatbot, mindmap, tutorat).

---

# 1. Diagnostic franc

Le moteur RAG est **fonctionnel**, mais **coûte plus que nécessaire** et ramène parfois plus de contexte que de signal.

## Ce qu'il fait bien
- combine vector search et keyword search ;
- fusionne les chunks ;
- rerank réel ;
- format de sortie simple et exploitable.

## Ce qu'il fait mal
- limite trop haute côté récupération primaire ;
- exécute vector + keyword même quand le message est faible ;
- `ILIKE ANY` peu performant ;
- reranker recalcule inutilement certains scores ;
- pas de compression pédagogique explicite du contexte ;
- le contexte formatté garde des extraits un peu trop longs.

---

# 2. Problèmes techniques ciblés

## Problème A — récupération primaire trop large
### Actuel
- `vector_rag_search(..., limit=20)`
- `keyword_rag_search(..., limit=20)`

### Risque
- plus de travail SQL ;
- plus de candidats à reranker ;
- plus de bruit ;
- coût CPU accru.

### Décision
Réduire les limites primaires et les rendre explicites.

---

## Problème B — mot-clé naïf
### Actuel
- split simple sur espaces
- jusqu'à 5 mots
- pas de vrai filtrage sémantique léger

### Risque
- mots faibles ou redondants ;
- recherche mot-clé peu discriminante.

### Décision
Ajouter extraction légère de mots-clés utiles.

---

## Problème C — pas de compression pédagogique du contexte
### Actuel
Le contexte envoyé au moteur aval est un collage d'extraits.

### Risque
- plus de tokens ;
- moins de lisibilité ;
- moins de focalisation pour le moteur pédagogique.

### Décision
Ajouter un formateur de contexte plus compact et plus orienté BAC.

---

## Problème D — reranker inefficace
### Actuel
`max_bm25` est recalculé dans la boucle pour chaque chunk.

### Risque
- coût inutile O(n²) ;
- perte de performance pure.

### Décision
Pré-calculer les scores BM25 une fois.

---

# 3. Changements sûrs à faire

## Changement 1 — ajouter extraction légère des mots-clés
Créer une fonction dédiée.

## Changement 2 — réduire les limites primaires
Exemple :
- vector = 8
- keyword = 8
- sortie finale = 3 ou 5 selon usage

## Changement 3 — limiter plus proprement la taille des extraits
Réduire certains extraits à 360–420 chars pour le retrieval primaire.

## Changement 4 — ajouter un contexte compact orienté BAC
Format plus lisible :
- source
- chapitre
- idée utile

## Changement 5 — optimiser le reranker sans changer son contrat
Pré-calcul des scores BM25.

---

# 4. Ce qu'on ne touche pas

- signature publique de `rag_search()` ;
- structure des chunks retournés ;
- existence du reranker ;
- embedder ONNX ;
- routes consommatrices.

---

# 5. Résultat attendu

## Technique
- moins de coût SQL ;
- moins de coût CPU ;
- rerank plus propre ;
- moins de tokens envoyés aux moteurs aval.

## Produit
- contexte plus précis ;
- réponses plus rapides ;
- sensation de meilleure pertinence pour l'élève.

---

# 6. Décision

Le moteur RAG doit être optimisé par **resserrement**, pas par refonte brutale :
- récupérer moins ;
- sélectionner mieux ;
- formater plus intelligemment.
