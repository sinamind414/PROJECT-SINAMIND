import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_reader_instance = None


def _get_reader():
    global _reader_instance
    if _reader_instance is None:
        import easyocr
        logger.info("Initializing EasyOCR reader (GPU) with ara+fra...")
        _reader_instance = easyocr.Reader(
            ["ar", "en"],
            gpu=True,
            verbose=False,
        )
        logger.info("EasyOCR GPU reader ready")
    return _reader_instance


class GpuOCR:
    def ocr_image(
        self, image: np.ndarray, return_hocr: bool = False
    ) -> Tuple[str, float, List[dict]]:
        reader = _get_reader()
        results = reader.readtext(image, paragraph=False, width_ths=0.7)

        words = []
        confidences = []
        text_parts = []

        for bbox, text, conf in results:
            text = text.strip()
            if not text:
                continue
            x_coords = [p[0] for p in bbox]
            y_coords = [p[1] for p in bbox]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))
            bbox_xyxy = (x_min, y_min, x_max, y_max)

            words.append({
                "text": text,
                "conf": round(float(conf), 2),
                "bbox": bbox_xyxy,
            })
            confidences.append(float(conf))
            text_parts.append(text)

        full_text = " ".join(text_parts)
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        return full_text, avg_conf, words
