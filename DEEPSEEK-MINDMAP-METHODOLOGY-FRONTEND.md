# Frontend — Mind Map Méthodologique

**Projet :** Khawarizmi Pro  
**Statut :** 100% implémenté

---

## 1. Composant

**Fichier :** `components/mindmap/MethodologicalMindMap.tsx`

- Vue arborescente interactive (expand/collapse)
- Badge par nœud : verbe d'action détecté
- Conseil méthodologique en dessous
- Props : `mindmap`, `onNodeClick`

---

## 2. Page

**Fichier :** `app/mindmap/page.tsx`

- Bouton "Générer" → `POST /api/mindmap/generate-methodological` via `apiClient`
- Loading spinner pendant génération
- État vide si pas encore généré
- Affichage des points méthodologiques gagnés

---

## 3. Corrections appliquées

| Spec original | Implémentation |
|---|---|
| `fetch("/api/mindmap/methodology/generate")` | `apiClient.request("/api/mindmap/generate-methodological")` |
| Pas de token JWT | JWT automatique via apiClient |
