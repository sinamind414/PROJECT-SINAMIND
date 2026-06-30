# routes/__init__.py
# Registry centralisé de tous les routers API

from . import (
    ai_chat,
    ai_evaluate,
    annales,
    auth,
    avatar,
    chapitres,
    chatbot,
    chatbot_engagement,
    cours,
    dashboard,
    diagnostic,
    dual_coding,
    exercices,
    flashcards,
    gamification,
    health,
    lexique,
    methodology,
    methodology_flashcards,
    mindmap,
    mindmap_methodology,
    mystery_box,
    orientation,
    payment,
    phase1,
    phase3,
    phase5,
    phase6,
    programme,
    progress,
    session,
    videos,
)

ALL_ROUTERS = [
    # ── Core ──
    health.router,
    auth.router,
    chapitres.router,
    # chat.router,          # DEPRECATED — migré vers /api/ai/chat
    chatbot.router,
    cours.router,
    exercices.router,
    flashcards.router,
    mindmap.router,
    # evaluate.router,      # DEPRECATED — migré vers /api/ai/evaluate
    session.router,
    payment.router,
    programme.router,
    progress.router,
    dashboard.router,
    orientation.router,
    lexique.router,
    videos.router,
    annales.router,
    dual_coding.router,
    # ── Gamification ──
    gamification.router,
    mystery_box.router,
    avatar.router,
    # ── Phase 1-6 (phase2, phase4, badges retirés : doublons ou non utilisés) ──
    phase1.router,
    phase3.router,
    phase5.router,
    phase6.router,
    chatbot_engagement.router,
    # ── AI Orchestrator ──
    ai_chat.router,
    ai_evaluate.router,
    # ── Methodology Intelligence ──
    diagnostic.router,
    methodology.router,
    methodology_flashcards.router,
    mindmap_methodology.router,
]
