# routes/__init__.py
# Registry centralisé de tous les routers API

from . import (
    action_verbs,
    admin_analytics,
    ai_chat,
    ai_evaluate,
    annales,
    auth,
    avatar,
    badges,
    bac_blanc_intelligent,
    chapitres,
    chatbot,
    chatbot_engagement,
    cours,
    dashboard,
    diagnostic,
    document_analysis_v2,
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
    social,
    streaks,
    tutor,
    videos,
)
from . import (
    document_analysis as document_analysis,
)
from . import manhadjiya

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
    # ── Tutor & Bac Blanc ──
    tutor.router,
    bac_blanc_intelligent.router,
    # ── Social Hub (Messenger + Blog + Fichiers) ──
    social.router,
    # ── Admin Analytics (Dashboard Professeur) ──
    admin_analytics.router,
    # ── Document Analysis (v2 uniquement — v1 désactivée) ──
    # document_analysis.router,  # DÉSACTIVÉ : v1 utilisait evaluate_answer (regex) qui notait 75% le charabia
    document_analysis_v2.router,
    # ── Action Verbs ──
    action_verbs.router,
    # ── Gamification Sprint 1 ──
    streaks.router,
    badges.router,
    # ── Manhadjiya (LOT8 — Base de connaissance scientifique) ──
    manhadjiya.router,
]
