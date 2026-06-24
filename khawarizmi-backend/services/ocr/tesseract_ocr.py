import csv
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

from .config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class TesseractOCR:
    def __init__(self, psm: int | None = None, oem: int | None = None):
        self.psm = psm or config.default_psm
        self.oem = oem or config.default_oem
        self.langs = config.tesseract_langs
        self.cmd = config.tesseract_cmd

    def ocr_image(self, image: np.ndarray, return_hocr: bool = False) -> tuple[str, float, list[dict]]:
        with tempfile.TemporaryDirectory() as tmp_dir:
            img_path = Path(tmp_dir) / "page.png"
            if not cv2.imwrite(str(img_path), image):
                raise RuntimeError("Failed to write temp image for Tesseract")

            text = self._run_tesseract_text(img_path)
            words = []
            conf = 0.0
            if return_hocr:
                words, conf = self._run_tesseract_tsv(img_path)
            return text, conf, words

    def _run_tesseract_text(self, img_path: Path) -> str:
        command = [
            self.cmd,
            str(img_path),
            "stdout",
            "-l",
            self.langs,
            "--psm",
            str(self.psm),
            "--oem",
            str(self.oem),
            "-c",
            "preserve_interword_spaces=1",
        ]
        result = self._run(command)
        if result.returncode != 0:
            err = result.stderr.strip()[:500] if result.stderr else "unknown error"
            logger.warning("Tesseract text extraction failed: %s", err)
            return ""
        return result.stdout.strip()

    def _run_tesseract_tsv(self, img_path: Path) -> tuple[list[dict], float]:
        command = [
            self.cmd,
            str(img_path),
            "stdout",
            "-l",
            self.langs,
            "--psm",
            str(self.psm),
            "--oem",
            str(self.oem),
            "tsv",
        ]
        result = self._run(command)
        if result.returncode != 0:
            return [], 0.0
        return self._parse_tsv(result.stdout)

    def _parse_tsv(self, tsv_text: str) -> tuple[list[dict], float]:
        words = []
        confidences = []
        lines = [line for line in tsv_text.splitlines() if line.strip()]
        if len(lines) <= 1:
            return [], 0.0
        reader = csv.DictReader(lines, delimiter="\t")
        for row in reader:
            text = (row.get("text") or "").strip()
            conf_raw = (row.get("conf") or "").strip()
            if not text:
                continue
            try:
                left = int(row.get("left", 0))
                top = int(row.get("top", 0))
                width = int(row.get("width", 0))
                height = int(row.get("height", 0))
            except (ValueError, TypeError):
                left = top = width = height = 0
            bbox = (left, top, left + width, top + height)
            conf = 0.0
            if conf_raw and conf_raw not in {"-1", "nan"}:
                try:
                    conf = float(conf_raw)
                except ValueError:
                    conf = 0.0
            words.append(
                {
                    "text": text,
                    "conf": conf,
                    "bbox": bbox,
                }
            )
            if conf > 0:
                confidences.append(conf)
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        return words, avg_conf

    def _run(self, command: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.setdefault("OMP_THREAD_LIMIT", "1")
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            env=env,
        )
