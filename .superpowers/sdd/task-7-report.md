# Task 7 Report: Create ChatMessage.tsx

## Status: DONE

## Changes Made
- Created `src/components/dashboard/chatbot/ChatMessage.tsx`
  - Functional component with "use client" directive
  - Imports `FeedbackButtons` from `./FeedbackButtons` and types from `./useChatbot`
  - Renders user messages right-aligned (`bg-mint/15 text-gray-100 mr-8`)
  - Renders assistant messages left-aligned (`bg-white/[0.04] text-gray-200 ml-8`)
  - Shows amber fallback warning when `message.fallback` is true
  - Renders clickable cards with gradient background and teal accent when `message.cartes` has items
  - Cards call `onCardClick(card.action)` only when action is non-empty and not `"#"`
  - Shows `FeedbackButtons` below assistant messages when `isLast` and `feedbackGiven` is undefined
  - Shows feedback indicator (emoji + label) when `feedbackGiven` is set
  - RTL layout via `dir="rtl"` on container
  - Rounded corners (`rounded-2xl`) matching existing ChatBubble.tsx patterns

## Verification
- TypeScript compiles: YES (only pre-existing error in SuggestionChips.tsx line 61, unrelated)
- Matches existing color scheme: YES (same classes as ChatBubble.tsx)
- Types aligned with useChatbot.ts: YES (DisplayMessage, FeedbackType)

## Concerns
- Pre-existing TS error in SuggestionChips.tsx:61 (`]` instead of `}` closing `CHAPTER_CHIPS`) — not introduced by this task
