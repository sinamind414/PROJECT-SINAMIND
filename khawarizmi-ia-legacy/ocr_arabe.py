import numpy as np
from pathlib import Path


class ArabicOCR:
    """
    Wrapper unifié pour l'OCR arabe local.
    """

    def __init__(self, backend: str = "easyocr"):
        self.backend = backend
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        if self.backend == "easyocr":
            self._init_easyocr()
        else:
            raise ValueError(f"Backend inconnu: {self.backend}")

    def _init_easyocr(self):
        """
        EasyOCR — https://github.com/JaidedAI/EasyOCR
        """
        try:
            import easyocr
            print("Chargement du modèle EasyOCR arabe (première fois = téléchargement)...")
            # gpu=False par défaut pour compatibilité maximale
            self._engine = easyocr.Reader(
                ['ar'],  # Langues : arabe
                gpu=False,
                verbose=False
            )
            print("EasyOCR prêt.")
        except ImportError:
            raise ImportError(
                "EasyOCR non installé. Exécutez: pip install easyocr"
            )

    def extract_text(self, image: np.ndarray) -> str:
        """
        Extrait le texte arabe d'une image numpy (BGR ou grayscale).
        Retourne le texte brut en UTF-8.
        """
        if self.backend == "easyocr":
            return self._extract_easyocr(image)

    def _extract_easyocr(self, image: np.ndarray) -> str:
        results = self._engine.readtext(image, detail=0, paragraph=True)
        return "\n".join(results)


def ocr_all_text_zones(text_zones_dir: str, backend: str = "easyocr") -> dict:
    """
    Applique l'OCR sur toutes les zones texte extraites par l'étape 1.
    Retourne un dictionnaire {nom_fichier: texte_extrait}.
    """
    import cv2

    ocr = ArabicOCR(backend=backend)
    results = {}
    text_dir = Path(text_zones_dir)

    files = sorted(text_dir.glob("*.png"))
    for i, filepath in enumerate(files):
        print(f"OCR {i+1}/{len(files)}: {filepath.name}")
        img = cv2.imread(str(filepath))
        if img is None:
            print(f"  ⚠ Impossible de lire {filepath.name}")
            continue
        text = ocr.extract_text(img)
        results[filepath.name] = text

    return results
