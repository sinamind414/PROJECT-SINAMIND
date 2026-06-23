# Task 2 Report: Create useChatbot.ts
## Status: DONE
## Changes Made
- Created `src/components/dashboard/chatbot/useChatbot.ts` (414 lines)
- Exports: `useChatbot` (default), `FeedbackType`, `DisplayMessage`, `UserAchievements`, `UseChatbotReturn`
- Includes all required logic:
  - `sendMessage` with context (page_source, history last 6 messages, chapitre from pathname)
  - `handleFeedback` mapping 5 FeedbackType values to Arabic messages
  - `toggleTutorMode` with `__activate_tutor__` message and exit message
  - `detectTopic` extracting topic from `/cours/[slug]` pathname
  - `checkBadges` with 4 thresholds (débutant/apprenti/scientifique/maître)
  - Achievements persistence via localStorage key `khawarizmi-achievements`
  - `updateConsecutiveDays` for streak tracking
  - Auto-scroll via `scrollRef` + `useEffect` on messages
- Added `scrollRef` to `UseChatbotReturn` interface (required for component to attach to DOM)
## Verification
- TypeScript compiles: YES (no errors in useChatbot.ts; pre-existing error in SuggestionChips.tsx is unrelated)
## Concerns
- `SuggestionChips.tsx` has a pre-existing TS1136 error (property assignment expected at line 61) — not related to this task
