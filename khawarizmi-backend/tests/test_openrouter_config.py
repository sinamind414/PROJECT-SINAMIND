# tests/test_openrouter_config.py
# Tests de régression pour la configuration OpenRouter

import os


class TestOpenRouterConfig:
    """Vérifie l'intégration OpenRouter comme provider IA principal."""

    def test_lifespan_contains_openrouter_detection(self):
        """Vérifie que lifespan.py contient la logique de détection OpenRouter."""
        path = os.path.join(os.path.dirname(__file__), "..", "routes", "lifespan.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert 'api_key.startswith("sk-or-v1")' in content, (
            "lifespan.py doit détecter les clés OpenRouter (sk-or-v1*)"
        )

    def test_openrouter_base_url(self):
        """Vérifie que la base URL OpenRouter est correctement définie."""
        path = os.path.join(os.path.dirname(__file__), "..", "routes", "lifespan.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert 'base_url = "https://openrouter.ai/v1"' in content, (
            "OpenRouter utilise base_url https://openrouter.ai/v1"
        )

    def test_openrouter_default_model(self):
        """Vérifie que le modèle par défaut OpenRouter est google/gemini-2.5-flash."""
        path = os.path.join(os.path.dirname(__file__), "..", "routes", "lifespan.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert 'model = "google/gemini-2.5-flash"' in content, (
            "OpenRouter utilise modèle google/gemini-2.5-flash (avec préfixe vendor)"
        )

    def test_openrouter_detection_order(self):
        """Vérifie que OpenRouter est après Gemini dans la chaîne elif."""
        path = os.path.join(os.path.dirname(__file__), "..", "routes", "lifespan.py")
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        groq_line = None
        gemini_line = None
        openrouter_line = None
        for i, line in enumerate(lines):
            if 'api_key.startswith("gsk_")' in line:
                groq_line = i
            if 'api_key.startswith("AIza")' in line:
                gemini_line = i
            if 'api_key.startswith("sk-or-v1")' in line:
                openrouter_line = i
        assert groq_line is not None, "Détection Groq non trouvée"
        assert gemini_line is not None, "Détection Gemini non trouvée"
        assert openrouter_line is not None, "Détection OpenRouter non trouvée"
        assert groq_line < gemini_line < openrouter_line, (
            "L'ordre de détection doit être: Groq → Gemini → OpenRouter"
        )

    def test_openrouter_model_fallback_logic(self):
        """Vérifie la logique de fallback du modèle pour OpenRouter."""
        path = os.path.join(os.path.dirname(__file__), "..", "routes", "lifespan.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert 'if not model or "gpt" in model:' in content, (
            "OpenRouter doit fallback sur gemini si modèle non défini ou contient 'gpt'"
        )