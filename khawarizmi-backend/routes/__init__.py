# routes/__init__.py
# Registry centralisé de tous les routers API

from . import (
    action_verbs,
    admin_analytics,
    ai_chat,
    annales,
    aujourdhui,
    auth,
    avatar,
    bac_blanc,
    badges,
    chatbot,
    chatbot_engagement,
    cities,
    cours,
    dashboard,
    diagnostic,
    document_analysis,
    document_analysis_v2,
    dual_coding,
    duels,
    exercices,
    flashcards,
    gamification,
    gems,
    health,
    leaderboard,
    lessons,
    lexique,
    manhadjiya,
    methodology,
    methodology_flashcards,
    mindmap,
    mystery_box,
    observability,
    onboarding,
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
    videos,
)

ALL_ROUTERS = [
    # ── Core ──
    health.router,
    auth.router,
    chatbot.router,
    cours.router,
    exercices.router,
    flashcards.router,
    mindmap.router,
    session.router,
    payment.router,
    programme.router,
    progress.router,
    dashboard.router,
    observability.router,
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
    # ── Methodology Intelligence ──
    diagnostic.router,
    methodology.router,
    methodology_flashcards.router,
    # ── Tutor & Bac Blanc ──
    # ── Social Hub (Messenger + Blog + Fichiers) ──
    social.router,
    # ── Admin Analytics (Dashboard Professeur) ──
    admin_analytics.router,
    # ── Document Analysis (v1 : scenarios/progress/weak-spots + v2 : evaluate) ──
    document_analysis.router,
    document_analysis_v2.router,
    # ── Action Verbs ──
    action_verbs.router,
    # ── Gamification Sprint 1 ──
    streaks.router,
    badges.router,
    # ── Gamification Sprint 2 ──
    gems.router,
    duels.router,
    leaderboard.router,
    # ── Gamification Sprint 3 ──
    cities.router,
    onboarding.router,
    # ── Manhadjiya (LOT8 — Base de connaissance scientifique) ──
    manhadjiya.router,
    # ── Aujourd'hui (accueil) · Leçons actives · Bac Blanc v1 (immersif) ──
    aujourdhui.router,
    lessons.router,
    bac_blanc.router,
]

# ════════════════════════════════════════════════════════════════
# Gel d'endpoints orphelins — audit endpoints morts (2026-08-17)
# ════════════════════════════════════════════════════════════════
# Endpoints retirés du service SANS supprimer le code (réversible :
# retirer le chemin de cette liste). Chacun vérifié : 0 référence front,
# 0 test appelant. Différés (consommateurs de test) : /api/phase3/avatar,
# /api/mindmap/generate-methodological, /api/drill/session.
# Tier A (suppression physique) exige la confirmation par logs de prod.
FROZEN_ENDPOINTS: set[str] = {
    "/api/cities/{city_id}/unlock",
    "/api/cities/leaderboard",
    "/api/gems/transactions",
    "/api/gems/leaderboard",
    "/api/leaderboard/refresh",
    "/api/onboarding/welcome-gems",
    # "/api/social/upload",  # DÉGELÉ 2026-08-18 : sécurisé (whitelist + taille),
    #                         # le gel était un pis-aller pour l'endpoint non validé.
    "/api/phase6/events",
    "/api/phase6/session/start",
    "/api/phase6/funnels",
    "/api/streaks/me/activity",
    "/api/streaks/me/freeze",
    "/api/flashcards/methodology/",
    "/api/document-analysis/review",
    "/api/session/random",
}

for _router in ALL_ROUTERS:
    _router.routes = [r for r in _router.routes if r.path not in FROZEN_ENDPOINTS]
