import json
from pathlib import Path
from typing import Dict, Any
import logging

from .config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class BundleManager:
    def __init__(self, pdf_path: Path):
        stem = pdf_path.stem
        self.bundle_dir = config.ocr_output_base / stem
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        self._pages_txt_dir = self.bundle_dir / "pages_txt"
        self._pages_txt_dir.mkdir(exist_ok=True)
        self._pages_meta_dir = self.bundle_dir / "pages_meta"
        self._pages_meta_dir.mkdir(exist_ok=True)

    def get_bundle_path(self) -> Path:
        return self.bundle_dir

    def write_page_text(self, page_no: int, text: str):
        path = self._pages_txt_dir / f"page_{page_no:06d}.txt"
        path.write_text(text, encoding="utf-8")

    def write_page_meta(self, page_result) -> None:
        path = self._pages_meta_dir / f"page_{page_result.page:06d}.json"
        path.write_text(
            json.dumps(page_result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def write_summary(self, summary) -> None:
        path = self.bundle_dir / "summary.json"
        path.write_text(
            json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
