import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


class PDFRenderer:
    def __init__(self, dpi: int = 140):
        self.dpi = dpi
        self._doc_cache: dict = {}

    def _get_doc(self, pdf_path: Path):
        key = str(pdf_path.resolve())
        if key not in self._doc_cache:
            import fitz

            self._doc_cache[key] = fitz.open(key)
        return self._doc_cache[key]

    def get_page_count(self, pdf_path: Path) -> int:
        doc = self._get_doc(pdf_path)
        return doc.page_count

    def render_page(self, pdf_path: Path, page_index: int) -> np.ndarray | None:
        import fitz

        doc = self._get_doc(pdf_path)
        page = doc[page_index]
        zoom = self.dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n).copy()
        if pix.n == 1:
            return np.stack([arr] * 3, axis=-1)
        if pix.n == 4:
            import cv2

            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        if pix.n == 3:
            import cv2

            return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return arr

    def cleanup_temp(self, pdf_path: Path):
        key = str(pdf_path.resolve())
        if key in self._doc_cache:
            try:
                self._doc_cache[key].close()
            except Exception:
                pass
            del self._doc_cache[key]
