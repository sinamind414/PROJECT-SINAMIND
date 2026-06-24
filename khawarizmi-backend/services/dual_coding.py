"""
services/dual_coding.py — Moteur Dual Coding Khawarizmi v2.0
Évaluation de schémas manuscrits par Vision IA.
Méthode : Allan Paivio — Dual Coding Theory (1971)
Effet mesuré : +75% rétention vs texte seul.
"""

import base64
import logging
from typing import Any

from openai import AsyncOpenAI

from config import get_settings

logger = logging.getLogger("khawarizmi.dual_coding")

# ═══ CONSTANTES ═════════════════════════════════════════════════
MAX_IMAGE_SIZE_MB = 5
MIN_IMAGE_SIZE_B = 1000  # < 1Ko = image corrompue
VISION_TEMPERATURE = 0.25  # Légèrement plus souple pour la vision
VISION_MAX_TOKENS = 400
VISION_DETAIL = "low"  # 'low' = 85 tokens fixes = 3x moins cher


# ═══ CORPUS SCHÉMAS — PROGRAMME ALGÉRIEN ════════════════════════

SCHEMAS_SVT = {
    # ── IMMUNOLOGIE ──────────────────────────────────────────────
    "SVT-IMMU-01-MC-01": {
        "nom": "Réponse immunitaire non spécifique",
        "chapitre": "SVT-IMMU-01",
        "schema_ascii": """
PATHOGÈNE ENTRE
      ↓
  [PHAGOCYTE]
  (Neutrophile / Macrophage)
      ↓ Phagocytose
  [DIGESTION INTRACELLULAIRE]
      ↓
DESTRUCTION DU PATHOGÈNE
      ↓
  [PRÉSENTATION ANTIGÈNE]
  → Déclenche réponse spécifique
        """,
        "points_critiques": [
            "Phagocyte = neutrophile OU macrophage",
            "Phagocytose AVANT digestion intracellulaire",
            "La présentation antigénique déclenche la réponse spécifique",
        ],
    },
    "SVT-IMMU-01-MC-02": {
        "nom": "Réponse immunitaire humorale",
        "chapitre": "SVT-IMMU-01",
        "schema_ascii": """
ANTIGÈNE ENTRE
      ↓
  [MACROPHAGE]
      ↓ Présentation CMH II
  [LYMPHOCYTE B]
      ↓ Activation + Multiplication
   ┌──┴──────────────┐
   ↓                 ↓
[PLASMOCYTES]   [LB MÉMOIRE]
   ↓
[ANTICORPS]
   ↓
[COMPLEXE Ag-Ac]
   ↓
NEUTRALISATION / ÉLIMINATION
        """,
        "points_critiques": [
            "Macrophage doit présenter via CMH II",
            "LB → 2 voies : Plasmocytes ET LB Mémoire",
            "Complexe Ag-Ac AVANT neutralisation",
        ],
    },
    "SVT-IMMU-01-MC-03": {
        "nom": "Réponse immunitaire cellulaire",
        "chapitre": "SVT-IMMU-01",
        "schema_ascii": """
ANTIGÈNE ENTRE
      ↓
  [MACROPHAGE]
      ↓ Présentation CMH I
  [LYMPHOCYTE T CD8+]
      ↓ Activation + Multiplication
   ┌──┴──────────────┐
   ↓                 ↓
[LT CYTOTOXIQUES]  [LT MÉMOIRE]
   ↓
[DESTRUCTION CELLULE CIBLE]
(Perforine / Apoptose)
        """,
        "points_critiques": [
            "CMH I pour LT CD8+ (≠ CMH II pour LB)",
            "LT → 2 voies : Cytotoxiques ET Mémoire",
            "Destruction par perforine ou apoptose",
        ],
    },
    # ── GÉNÉTIQUE ────────────────────────────────────────────────
    "SVT-GEN-01-MC-03": {
        "nom": "Transcription → Traduction",
        "chapitre": "SVT-GEN-01",
        "schema_ascii": """
[ADN]
  ↓ Transcription (noyau)
  ↓ ARN polymérase
[ARNm]
  ↓ Sortie vers cytoplasme
  ↓ Traduction (ribosome)
[ARNt] portant acides aminés
  ↓
[PROTÉINE]
        """,
        "points_critiques": [
            "La transcription a lieu dans le noyau",
            "ARN polymérase est nécessaire pour la transcription",
            "L'ARNm sort dans le cytoplasme",
            "La traduction a lieu au niveau du ribosome",
            "L'ARNt transporte les acides aminés",
        ],
    },
    "SVT-GEN-01-MC-04": {
        "nom": "Réplication de l'ADN",
        "chapitre": "SVT-GEN-01",
        "schema_ascii": """
[ADN DOUBLE BRIN]
      ↓ Hélicase
[2 BRINS SÉPARÉS]
   ↓          ↓
[Brin matrice 1]  [Brin matrice 2]
   ↓ ADN polymérase
[NOUVEAU BRIN 1]  [NOUVEAU BRIN 2]
      ↓
[2 ADN IDENTIQUES]
(Semi-conservatrice)
        """,
        "points_critiques": [
            "L'hélicase sépare les 2 brins",
            "L'ADN polymérase synthétise les nouveaux brins",
            "Réplication semi-conservatrice : 1 brin ancien + 1 nouveau",
        ],
    },
    # ── NEUROPHYSIOLOGIE ─────────────────────────────────────────
    "SVT-NEURO-01-MC-01": {
        "nom": "Transmission synaptique",
        "chapitre": "SVT-NEURO-01",
        "schema_ascii": """
[NEURONE PRÉ-SYNAPTIQUE]
      ↓ Influx nerveux
[VÉSICULES SYNAPTIQUES]
      ↓ Exocytose
[NEUROTRANSMETTEUR]
  (dans fente synaptique)
      ↓
[RÉCEPTEURS POST-SYNAPTIQUES]
      ↓
[NEURONE POST-SYNAPTIQUE]
  → Nouveau potentiel d'action
        """,
        "points_critiques": [
            "Vésicules synaptiques libèrent le neurotransmetteur",
            "Exocytose vers la fente synaptique",
            "Récepteurs spécifiques sur le neurone post-synaptique",
        ],
    },
}

# Alias pour compatibilité avec l'ancien code
SCHEMAS_SVT_PROGRAMME_ALGERIEN = SCHEMAS_SVT


# ═══ SERVICE DUAL CODING ════════════════════════════════════════


class DualCodingService:
    """
    Évalue les schémas manuscrits des élèves par Vision IA.
    Dual Coding Theory : texte + visuel = +75% rétention.
    """

    def __init__(self, openai_client: AsyncOpenAI = None):
        cfg = get_settings()
        self.schemas = SCHEMAS_SVT

        if cfg.VISION_API_KEY:
            self.client = AsyncOpenAI(
                api_key=cfg.VISION_API_KEY,
                base_url=cfg.vision_base_url,
            )
            self.model = cfg.vision_model
            self.vision_available = True
        elif openai_client is not None:
            self.client = openai_client
            self.model = cfg.vision_model
            self.vision_available = True
        else:
            self.client = None
            self.model = None
            self.vision_available = False
            logger.warning(
                "Vision IA désactivée — VISION_API_KEY non configurée. "
                "Le dual coding retournera un message d'erreur gracieux."
            )

    # ═══ MÉTHODE PRINCIPALE ════════════════════════════════════

    async def evaluer_schema_photo(
        self,
        image_base64: str,
        schema_id: str,
    ) -> dict[str, Any]:
        """
        Évalue la photo d'un schéma manuscrit.

        Args:
            image_base64 : Image encodée en base64 (JPEG/PNG)
            schema_id    : Identifiant du schéma (ex: 'SVT-IMMU-01-MC-02')

        Returns:
            Dict avec score, feedback socratique et éléments manquants
        """
        # ── Guard : vision IA disponible ? ────────────────────────
        if not self.vision_available:
            return {
                "erreur": "La vision IA n'est pas configurée sur ce serveur.",
                "score": 0,
                "feedback": "L'évaluation de schémas par photo nécessite une clé API Vision. "
                "Demande à ton enseignant de l'activer.",
            }

        # ── Validation ──────────────────────────────────────────
        validation = self._valider_image(image_base64)
        if not validation["valide"]:
            return {"erreur": validation["message"], "score": 0}

        schema_ref = self.schemas.get(schema_id)
        if not schema_ref:
            disponibles = list(self.schemas.keys())[:5]
            logger.warning(f"Schema '{schema_id}' introuvable")
            return {
                "erreur": f"Schéma '{schema_id}' introuvable.",
                "disponibles": disponibles,
                "score": 0,
            }

        # ── Construction prompt ────────────────────────────────
        prompt = self._build_vision_prompt(schema_ref)

        # ── Appel Vision IA ────────────────────────────────────
        logger.info(f"Vision IA : schema={schema_id} taille={len(image_base64) // 1024}Ko")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": VISION_DETAIL,  # 'low' = 3x moins cher
                                },
                            },
                        ],
                    }
                ],
                temperature=VISION_TEMPERATURE,
                max_tokens=VISION_MAX_TOKENS,
                response_format={"type": "json_object"},
            )

            result = response.choices[0].message.content

            logger.info(f"Vision OK : schema={schema_id} tokens={response.usage.total_tokens}")

            return result

        except Exception as e:
            logger.error(f"Erreur Vision IA : {e}")
            return {
                "erreur": f"Erreur IA : {e!s}",
                "score": 0,
                "feedback": "Une erreur technique est survenue. Réessaie.",
            }

    # ═══ HELPERS ═══════════════════════════════════════════════

    def _valider_image(self, image_base64: str) -> dict[str, Any]:
        """Valide l'image avant d'appeler l'API."""
        if not image_base64:
            return {"valide": False, "message": "Image vide ou manquante."}

        # Nettoyer l'en-tête base64 (Data URI) si présent (ex: data:image/jpeg;base64,...)
        if "," in image_base64:
            image_base64 = image_base64.split(",")[-1]

        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            return {"valide": False, "message": "Image base64 invalide."}

        taille_bytes = len(image_bytes)
        taille_mb = taille_bytes / (1024 * 1024)

        if taille_bytes < MIN_IMAGE_SIZE_B:
            return {"valide": False, "message": "Image trop petite (< 1Ko)."}

        if taille_mb > MAX_IMAGE_SIZE_MB:
            return {
                "valide": False,
                "message": f"Image trop lourde ({taille_mb:.1f}Mo > {MAX_IMAGE_SIZE_MB}Mo). "
                f"Compresse la photo avant envoi.",
            }

        return {"valide": True, "taille_mb": round(taille_mb, 2)}

    def _build_vision_prompt(self, schema_ref: dict) -> str:
        """Construit le prompt Vision pour l'évaluation."""
        points = "\n".join(f"→ {p}" for p in schema_ref["points_critiques"])

        return f"""
Tu es KHAWARIZMI, expert du BAC algérien en Sciences Naturelles.

L'élève devait reproduire CE schéma de mémoire :
{schema_ref["schema_ascii"]}

Points critiques à vérifier ABSOLUMENT :
{points}

ÉVALUE la photo du schéma de l'élève.

FORMAT JSON STRICT :
{{
    "score":               <0-10>,
    "fleches_correctes":   true/false,
    "vocabulaire_exact":   true/false,
    "ordre_correct":       true/false,
    "elements_manquants":  ["<element>", ...],
    "feedback":            "<commence par ce qui est BIEN>",
    "question_socratique": "<une seule question pour approfondir>"
}}

RÈGLES :
- Commence TOUJOURS par ce qui est correct
- Sois bienveillant mais précis
- Plasmocyte ≠ "cellule qui fabrique anticorps"
- Une flèche approximative mais dans le bon sens = acceptée
""".strip()

    # ═══ UTILITAIRES PÉDAGOGIQUES ═══════════════════════════════

    def get_schema(self, schema_id: str) -> dict | None:
        """Retourne le schéma de référence pour l'affichage."""
        return self.schemas.get(schema_id)

    def lister_schemas_chapitre(self, chapitre_id: str) -> list:
        """Retourne tous les schémas d'un chapitre."""
        return [{"id": sid, "nom": s["nom"]} for sid, s in self.schemas.items() if s.get("chapitre") == chapitre_id]

    def get_instruction_eleve(self, schema_id: str) -> str:
        """Message d'instruction standardisé pour l'élève."""
        schema = self.schemas.get(schema_id, {})
        nom = schema.get("nom", "ce schéma")
        return (
            f"📝 MODE SCHÉMA — {nom}\n\n"
            "1. Regarde ce schéma 30 secondes\n"
            "2. Ferme l'app\n"
            "3. Reproduis-le sur ton cahier\n"
            "4. Photographie ta reproduction\n\n"
            "L'IA va vérifier :\n"
            "→ Les flèches dans le bon sens\n"
            "→ Les termes scientifiques exacts\n"
            "→ L'ordre des étapes\n"
            "→ Les éléments manquants"
        )
