import json
import logging
from pathlib import Path

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

    def export_combined_txt(self, suffix: str = ".ocr.txt") -> Path:
        pages = sorted(self._pages_txt_dir.glob("page_*.txt"))
        if not pages:
            logger.warning("No page text files to combine in %s", self._pages_txt_dir)
            return self.bundle_dir / ("empty" + suffix)
        out_path = self.bundle_dir / (self.bundle_dir.name + suffix)
        with out_path.open("w", encoding="utf-8") as f:
            for p in pages:
                page_num = p.stem.replace("page_", "")
                f.write(f"\n{'=' * 60}\n")
                f.write(f"PAGE {page_num}\n")
                f.write(f"{'=' * 60}\n")
                f.write(p.read_text(encoding="utf-8"))
                f.write("\n")
        logger.info("Exported combined text (%d pages) → %s", len(pages), out_path.name)
        return out_path
