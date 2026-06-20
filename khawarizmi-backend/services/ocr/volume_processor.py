from pathlib import Path
from typing import Optional, Callable, List
import time
import logging

from .config import get_config
from .models import PageResult, VolumeSummary, WordBox
from .bundle import BundleManager

logger = logging.getLogger(__name__)
config = get_config()


class VolumeProcessor:
    def __init__(self, dpi=None, psm=None, oem=None, retries=None,
                 enable_hocr=True, use_parallel=False, max_workers=2,
                 use_gpu=False):
        self.dpi = dpi or config.default_dpi
        self.psm = psm or config.default_psm
        self.oem = oem or config.default_oem
        self.retries = retries or config.default_retries
        self.enable_hocr = enable_hocr
        self.use_parallel = use_parallel
        self.max_workers = max_workers
        self.use_gpu = use_gpu

    def _get_ocr_backend(self):
        if self.use_gpu:
            from .gpu_ocr import GpuOCR
            return GpuOCR()
        from .tesseract_ocr import TesseractOCR
        return TesseractOCR(self.psm, self.oem)

    def process_volume(self, pdf_path: Path,
                       use_parallel: bool = False,
                       progress_callback: Optional[Callable] = None) -> VolumeSummary:
        from .pdf_renderer import PDFRenderer
        from .preprocessor import ImagePreprocessor

        renderer = PDFRenderer(self.dpi)
        preprocessor = ImagePreprocessor()
        ocr = self._get_ocr_backend()
        bundle = BundleManager(pdf_path)

        total_pages = renderer.get_page_count(pdf_path)
        results: List[PageResult] = []
        errors = 0
        total_chars = 0
        confidences = []

        for i in range(total_pages):
            try:
                img = renderer.render_page(pdf_path, i)
                if img is None:
                    continue

                pre = preprocessor.preprocess(img)
                text, conf, words = ocr.ocr_image(pre, return_hocr=self.enable_hocr)

                pr = PageResult(
                    page=i + 1,
                    text=text,
                    char_count=len(text),
                    confidence=conf,
                    words=[WordBox(w["text"], w["conf"], w["bbox"]) for w in (words or [])]
                )
                results.append(pr)
                total_chars += len(text)
                confidences.append(conf)

                bundle.write_page_text(i + 1, text)
                bundle.write_page_meta(pr)

                if progress_callback:
                    progress_callback({"page": i + 1, "progress": round((i + 1) / total_pages * 100, 1)})

                preprocessor.cleanup(img)
            except Exception as e:
                errors += 1
                logger.error("Page %d failed: %s", i + 1, e)

        avg = sum(confidences) / len(confidences) if confidences else 0
        summary = VolumeSummary(
            volume=pdf_path.stem,
            pdf=str(pdf_path),
            total_pages=total_pages,
            pages_processed=len(results),
            errors=errors,
            total_characters=total_chars,
            avg_confidence=round(avg, 2),
            quality_warning="None" if errors == 0 else "Check sequences",
            bundle_dir=str(bundle.get_bundle_path())
        )
        bundle.write_summary(summary)
        renderer.cleanup_temp(pdf_path)
        return summary


def get_volume_processor(**kwargs):
    return VolumeProcessor(**kwargs)
