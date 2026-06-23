# Chatbot V2 React — Implementation Plan

**Goal:** Rebuild chatbot with 5 V1 interactive pillars: Suggestion Chips, Feedback Buttons, Tutor Mode, Confetti, Achievements.

**Architecture:** Component decomposition + useChatbot hook. 7 new files, 1 npm dependency.

**Tech Stack:** React 19, Next.js 16, TypeScript, canvas-confetti, TailwindCSS 4.

---

## File Structure

```
src/components/dashboard/chatbot/  (CREER)
  useChatbot.ts          hook central
  ChatbotWidget.tsx      conteneur principal
  ChatMessage.tsx        bulle message
  SuggestionChips.tsx    chips adaptatives
  FeedbackButtons.tsx    5 boutons feedback
  TutorToggle.tsx        bouton 🎓
  AchievementPopup.tsx   popup badge 🏆

src/components/dashboard/
  ChatBubble.tsx         SUPPRIMER

src/components/layout/
  AppShell.tsx           MODIFIER
```

---

### Task 1: Installer canvas-confetti
- [ ] npm install canvas-confetti && npm install -D @types/canvas-confetti
- [ ] Commit: "feat(chatbot): add canvas-confetti dependency"

### Task 2: Creer useChatbot.ts
- [ ] Creer src/components/dashboard/chatbot/useChatbot.ts
- [ ] Types: FeedbackType, DisplayMessage, UserAchievements, UseChatbotReturn
- [ ] Logique: sendMessage, handleFeedback, toggleTutorMode, detectTopic, checkBadges, achievements localStorage
- [ ] Commit: "feat(chatbot): add useChatbot hook"

### Task 3: Creer SuggestionChips.tsx
- [ ] Props: { onSelect }
- [ ] 8 chips defaut + adaptatif par chapitre (pathname)
- [ ] Commit: "feat(chatbot): add SuggestionChips"

### Task 4: Creer FeedbackButtons.tsx
- [ ] Props: { onFeedback }
- [ ] 5 boutons: fhemt/nawzan/lam afham/mithal akhar/ikhtabirni
- [ ] Affiche sous dernier message assistant uniquement
- [ ] Commit: "feat(chatbot): add FeedbackButtons"

### Task 5: Creer TutorToggle.tsx
- [ ] Props: { isTutorMode, onToggle }
- [ ] Bouton 🎓, change header couleur si actif
- [ ] Commit: "feat(chatbot): add TutorToggle"

### Task 6: Creer AchievementPopup.tsx
- [ ] Props: { newBadge, onDismiss }
- [ ] Popup fade-in + canvas-confetti burst
- [ ] 4 badges: debutant/apprenti/scientifique/maitre
- [ ] Commit: "feat(chatbot): add AchievementPopup"

### Task 7: Creer ChatMessage.tsx
- [ ] Props: { message: DisplayMessage }
- [ ] Bulle user/assistant, cartes cliquables, fallback warning
- [ ] Commit: "feat(chatbot): add ChatMessage"

### Task 8: Creer ChatbotWidget.tsx
- [ ] Conteneur principal utilisant useChatbot()
- [ ] FAB button + Panel header/messages/input
- [ ] Integre tous les sous-composants
- [ ] Commit: "feat(chatbot): add ChatbotWidget"

### Task 9: Integrer dans AppShell.tsx
- [ ] Remplacer ChatBubble par ChatbotWidget
- [ ] Supprimer ancien ChatBubble.tsx
- [ ] Commit: "feat(chatbot): integrate in AppShell"

### Task 10: Build et Verification
- [ ] npm run build (0 erreurs)
- [ ] Tester: suggestions, feedback, tutor mode, achievements
- [ ] Commit: "feat(chatbot): Chatbot V2 complete"
