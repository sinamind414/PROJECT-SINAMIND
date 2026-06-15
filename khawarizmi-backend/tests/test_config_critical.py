# tests/test_config_critical.py
# Tests de régression pour bugs critiques de configuration
# Détecte les retours silencieux des bugs connus

import os
import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestCaseSensitiveRegression:
    """Détecte si case_sensitive=True est réintroduit dans SettingsConfigDict.

    Si ce test échoue → bug case_sensitive est revenu.
    Toutes les clés API du .env sont ignorées silencieusement.
    """

    def test_upper_case_env_var_read_as_snake_case(self):
        os.environ["KHAWARIZMI_TEST_UPPER"] = "validation_ok"

        class TestSettings(BaseSettings):
            khawarizmi_test_upper: str = "default"
            model_config = SettingsConfigDict(case_sensitive=False)

        ts = TestSettings()
        assert ts.khawarizmi_test_upper == "validation_ok", (
            "case_sensitive=False ne fonctionne pas — "
            "les variables UPPER_CASE du .env sont ignorées"
        )

    def test_case_sensitive_true_casse_tout(self):
        """Preuve que case_sensitive=True IGNORE les UPPER_CASE."""
        os.environ["KHAWARIZMI_TEST_FAIL"] = "should_be_ignored"

        class BrokenSettings(BaseSettings):
            khawarizmi_test_fail: str = "default_value"
            model_config = SettingsConfigDict(case_sensitive=True)

        bs = BrokenSettings()
        assert bs.khawarizmi_test_fail == "default_value", (
            "case_sensitive=True devrait IGNORER les UPPER_CASE"
        )
        assert bs.khawarizmi_test_fail != "should_be_ignored"


class TestVectorCastRegression:
    """Vérifie que :emb::vector n'est pas utilisé (instable avec asyncpg)."""

    def test_mindmap_service_uses_cast_syntax(self):
        path = os.path.join(
            os.path.dirname(__file__),
            "..", "services", "mindmap_service.py"
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "CAST(:emb AS vector)" in content, (
            "mindmap_service.py doit utiliser CAST(:emb AS vector), "
            "pas :emb::vector (instable avec asyncpg)"
        )
        assert ":emb::vector" not in content, (
            "Syntaxe :emb::vector détectée — utiliser CAST(:emb AS vector)"
        )


class TestOsGetenvRegression:
    """Détecte les retours de os.getenv au lieu de get_settings()."""

    def _check_file_no_os_getenv(self, filepath: str, filename: str):
        path = os.path.join(os.path.dirname(__file__), "..", filepath)
        if not os.path.exists(path):
            pytest.skip(f"Fichier introuvable: {path}")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        bad_lines = [
            (i+1, line.rstrip()) for i, line in enumerate(lines)
            if "os.getenv" in line and "OPENAI" in line.upper()
        ]
        assert not bad_lines, (
            f"{filename} utilise os.getenv au lieu de get_settings():\n"
            + "\n".join(f"  Ligne {n}: {l}" for n, l in bad_lines)
        )

    def test_mindmap_service_no_os_getenv(self):
        self._check_file_no_os_getenv(
            "services/mindmap_service.py", "mindmap_service.py"
        )

    def test_llm_no_os_getenv(self):
        self._check_file_no_os_getenv(
            "services/llm.py", "llm.py"
        )
