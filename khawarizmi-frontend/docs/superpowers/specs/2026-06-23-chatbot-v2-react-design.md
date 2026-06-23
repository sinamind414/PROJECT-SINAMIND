# Chatbot V2 React — Design Spec

**Date** : 2026-06-23
**Auteur** : OpenCode (brainstorming)
**Statut** : En attente review

---

## 1. Objectif

Reconstruire le widget chatbot (`ChatBubble.tsx`) en replicant les 5 piliers d'interactivité de la VERSION 1 (chatbot.js vanilla) dans l'architecture React/Next.js actuelle, tout en conservant les gains de la V2 (JWT, /api/tuteur, cartes cliquables, RTL arabe).

---

## 2. Fonctionnalités à implémenter

### 2.1 Suggestion Chips adaptatives (au démarrage)

**Composant** : `SuggestionChips.tsx`

- Affiché uniquement quand `messages.length === 0`
- 8 chips de questions prédéfinies en arabe
- **Adaptatives** : les chips changent selon le chapitre détecté via `window.location.pathname`
  - Page `/cours/...` → questions SVT du chapitre
  - Page `/annales/...` → questions annales BAC
  - Page `/action-verbs/...` → questions méthodologiques
  - Défaut → 8 questions générales SVT
- Clique sur chip → appelle `sendMessage(chipText)` directement
- Style : pillules RTL, scroll horizontal si débordement

**Chips par défaut (fallback)** :
```
🤔 ما هو ADN؟ اشرح بطريقة بسيطة
🌱 لماذا الأوراق خضراء؟
🛡️ كيف يدافع جسمي عن نفسه؟
⚡ كيف يفكر الدماغ؟
🔋 كيف تحصل خلاياي على الطاقة؟
🧬 ما الفرق بين ADN و ARN؟
🤷 لم أفهم درس المناعة ساعدني
📚 اشرح لي التركيب الضوئي بمثال
```

**Chaps adaptatifs** (mapping `slug → questions`) :
- `communication_hormonale` → hormones, neurotransmetteurs, synapse
- `genetique` → ADN, transcription, traduction, mutation
- `immunologie` → anticorps, antigènes, vaccination, SIDA
- ` enzymologie` → enzyme, site actif, inhibition, cinétique

### 2.2 Feedback Buttons (après chaque message bot)

**Composant** : `FeedbackButtons.tsx`

- Affiché sous le **dernier** message assistant uniquement
- 5 boutons :
  - ✅ `فهمت!` (Compris) → envoie "فهمت شكرا!" + animation confettis CSS
  - 🤔 `نوعاً ما` (Moyen) → envoie "هل يمكنك تبسيط الشرح أكثر مع مثال من الحياة اليومية؟"
  - ❌ `لم أفهم` (Pas compris) → envoie "لم أفهم! اشرح بطريقة مختلفة تماماً كأنني طفل صغير 😅"
  - 💡 `مثال آخر` (Exemple) → envoie "أعطني مثالاً آخر مختلفاً من الحياة اليومية"
  - 🧪 `اختبرني` (Teste-moi) → envoie "اختبرني على هذا المفهوم"
- Après envoi : les boutons disparaissent, le message pré-formaté est envoyé à `/api/tuteur`
- Style : grille 3+2, boutons avec emoji + texte, RTL

### 2.3 Tutor Mode Toggle 🎓

**Composant** : `TutorToggle.tsx`

- Bouton dans le header (à côté de ✕)
- Toggle ON/OFF
- **ON** :
  - Appelle `POST /api/tuteur/activate` avec contexte (page_source, chapitre)
  - Le backend retourne un message d'orientation + questions suggérées
  - Le header change de couleur (teal → or `#F59E0B`)
  - Le bouton passe à opacity 1
- **OFF** :
  - Reset au mode normal
  - Envoie "خرجت من وضع المدرس الشخصي"
  - Le header revient à teal
- Style : bouton rond, icône 🎓, animation pulse quand actif

### 2.4 Succès Animation (Confettis)

**Outil** : CSS animation par défaut + `canvas-confetti` (npm) pour milestones

- **Feedback "Compris"** : animation CSS scale-up + glow vert sur la bulle
- **Achievement majeur** : `canvas-confetti` (burst de confettis dorés)
- Le package `canvas-confetti` (~3KB gzipped) sera ajouté à `package.json`

### 2.5 Achievements System 🏆

**Composant** : `AchievementPopup.tsx`

**Stockage** :
- localStorage : `khawarizmi-achievements` (affichage immédiat)
- Backend : `GET /api/achievements` pour sync cross-device (futur)

**Structure localStorage** :
```json
{
  "totalMessages": 12,
  "topicsExplored": ["adn", "mitose", "enzyme"],
  "badges": ["debutant", "apprenti"],
  "consecutiveDays": 3,
  "lastVisit": "2026-06-23"
}
```

**Badges** :
| Badge | Condition | Emoji |
|---|---|---|
| Débutant | 5 messages envoyés | 🌟 |
| Apprenti | 10 messages + 3 topics | 🎓 |
| Scientifique | 25 messages + 5 topics | 🧠 |
| Maître | 50 messages + 10 topics + 7 jours consécutifs | 🏆 |

**Affichage** :
- Popup centrale avec animation fade-in
- Canvas-confetti burst
- Disparaît après 3 secondes ou au clic

---

## 3. Architecture

### 3.1 Arborescence des fichiers

```
src/components/dashboard/chatbot/
├── ChatbotWidget.tsx        ← conteneur principal (remplace ChatBubble.tsx)
├── ChatMessage.tsx           ← bulle message (user/assistant)
├── SuggestionChips.tsx       ← chips adaptatives au démarrage
├── FeedbackButtons.tsx       ← 5 boutons de feedback
├── TutorToggle.tsx           ← bouton 🎓 toggle
├── AchievementPopup.tsx      ← popup badge 🏆
└── useChatbot.ts             ← hook: state + API + logique
```

### 3.2 Hook `useChatbot.ts`

```typescript
// Interface publique
interface UseChatbotReturn {
  // State
  messages: DisplayMessage[]
  input: string
  loading: boolean
  badge: number
  isOpen: boolean
  isTutorMode: boolean
  achievements: UserAchievements

  // Actions
  setInput: (v: string) => void
  sendMessage: (text?: string) => Promise<void>
  openChat: () => void
  closeChat: () => void
  handleFeedback: (type: FeedbackType) => void
  toggleTutorMode: () => void
  handleSuggestion: (text: string) => void
}

type FeedbackType = "understood" | "partial" | "confused" | "example" | "quiz"
```

### 3.3 Intégration

- `AppShell.tsx` : `<ChatBubble />` → `<ChatbotWidget />`
- Les anciens fichiers `features/ChatBubble.tsx` (stub) et `dashboard/ChatBubble.tsx` sont supprimés
- Pas de changement dans le routing

---

## 4. Backend — Nouvel endpoint

```
POST /api/tuteur/activate
Headers: Authorization: Bearer <token>
Body: {
  context?: {
    chapitre?: string
    page_source?: string
  }
}
Response: {
  message: string,
  type: "orientation",
  questions_suggerees: string[],
  cartes: ChatCard[],
  fallback_active: boolean
}
```

Le backend envoie le greeting du tuteur avec des questions de révision FSRS adaptées au chapitre.

---

## 5. Dépendances

| Package | Taille | Usage |
|---|---|---|
| `canvas-confetti` | ~3KB gzipped | Confettis sur milestones |
| `@types/canvas-confetti` | — | Types TypeScript |

---

## 6. Migration

1. Créer le dossier `src/components/dashboard/chatbot/`
2. Implémenter `useChatbot.ts` (hook)
3. Implémenter chaque sous-composant
4. Créer `ChatbotWidget.tsx` (conteneur)
5. Modifier `AppShell.tsx` : remplacer `<ChatBubble />` par `<ChatbotWidget />`
6. Supprimer l'ancien `ChatBubble.tsx`
7. Créer `POST /api/tuteur/activate` côté backend
8. Tester : suggestions, feedback, tutor mode, achievements, confettis

---

## 7. Critères de succès

- [ ] 8 suggestions adaptatives s'affichent au démarrage
- [ ] 5 feedback buttons apparaissent après chaque message bot
- [ ] Tutor Mode 🎓 appelle `/api/tuteur/activate` et change le header
- [ ] Confettis CSS sur "Compris", canvas-confetti sur achievements
- [ ] 4 badges débloqués progressivement avec popup
- [ ] Tout fonctionne en RTL arabe
- [ ] Aucune régression sur les features existantes (cartes, auth, JWT)
- [ ] Build Next.js passe sans erreur
