import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        gray = self._to_gray(image)
        angle = self._estimate_skew(gray)
        if abs(angle) > 0.3:
            gray = self._rotate(gray, angle)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        normalized = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(normalized, h=7, templateWindowSize=7, searchWindowSize=21)
        return denoised

    def binarize_adaptive(self, image: np.ndarray) -> np.ndarray:
        gray = self._to_gray(image)
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)

    def binarize_otsu(self, image: np.ndarray) -> np.ndarray:
        gray = self._to_gray(image)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def cleanup(self, image: np.ndarray):
        pass

    def _to_gray(self, image: np.ndarray) -> np.ndarray:
        if image.ndim == 2:
            return image.copy()
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def _estimate_skew(self, gray: np.ndarray) -> float:
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(thresh > 0))
        if coords.shape[0] < 200:
            return 0.0
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        if abs(angle) < 0.2 or abs(angle) > 15:
            return 0.0
        return float(angle)

    def _rotate(self, image: np.ndarray, angle: float) -> np.ndarray:
        h, w = image.shape[:2]
        matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
        border_value = 255 if image.ndim == 2 else (255, 255, 255)
        return cv2.warpAffine(
            image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=border_value
        )
