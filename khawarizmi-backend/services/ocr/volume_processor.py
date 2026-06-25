import logging
from collections.abc import Callable
from pathlib import Path

from .bundle import BundleManager
from .config import get_config
from .models import PageResult, VolumeSummary, WordBox

logger = logging.getLogger(__name__)
config = get_config()


class VolumeProcessor:
    def __init__(
        self,
        dpi=None,
        psm=None,
        oem=None,
        retries=None,
        enable_hocr=True,
        use_parallel=False,
        max_workers=2,
        use_gpu=False,
    ):
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

    def process_volume(
        self,
        pdf_path: Path,
        use_parallel: bool = False,
        progress_callback: Callable | None = None,
        resume: bool = False,
    ) -> VolumeSummary:
        from .pdf_renderer import PDFRenderer
        from .preprocessor import ImagePreprocessor

        renderer = PDFRenderer(self.dpi)
        preprocessor = ImagePreprocessor()
        ocr = self._get_ocr_backend()
        bundle = BundleManager(pdf_path)

        total_pages = renderer.get_page_count(pdf_path)
        results: list[PageResult] = []
        errors = 0
        total_chars = 0
        confidences = []

        # Resume: collect already-processed pages
        if resume:
            done = set()
            for p in range(1, total_pages + 1):
                meta_path = bundle._pages_meta_dir / f"page_{p:06d}.json"
                txt_path = bundle._pages_txt_dir / f"page_{p:06d}.txt"
                if meta_path.exists() and txt_path.exists():
                    try:
                        import json

                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                        if meta.get("status") == "success":
                            pr = PageResult(
                                page=p,
                                text=meta.get("text", ""),
                                char_count=meta.get("char_count", 0),
                                confidence=meta.get("confidence", 0.0),
                                words=[WordBox(w["text"], w["conf"], w["bbox"]) for w in meta.get("words", [])],
                            )
                            results.append(pr)
                            total_chars += pr.char_count
                            confidences.append(pr.confidence)
                            done.add(p)
                    except Exception:
                        pass
            if done:
                logger.info("Resume: %d pages already done, skipping", len(done))

        for i in range(total_pages):
            page_num = i + 1
            if resume and page_num in done:
                continue

            try:
                img = renderer.render_page(pdf_path, i)
                if img is None:
                    continue

                pre = preprocessor.preprocess(img)
                text, conf, words = ocr.ocr_image(pre, return_hocr=self.enable_hocr)

                pr = PageResult(
                    page=page_num,
                    text=text,
                    char_count=len(text),
                    confidence=conf,
                    words=[WordBox(w["text"], w["conf"], w["bbox"]) for w in (words or [])],
                )
                results.append(pr)
                total_chars += len(text)
                confidences.append(conf)

                bundle.write_page_text(page_num, text)
                bundle.write_page_meta(pr)

                if progress_callback:
                    progress_callback({"page": page_num, "progress": round((page_num) / total_pages * 100, 1)})

                preprocessor.cleanup(img)
            except Exception as e:
                errors += 1
                logger.error("Page %d failed: %s", page_num, e)

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
            bundle_dir=str(bundle.get_bundle_path()),
        )
        bundle.write_summary(summary)
        renderer.cleanup_temp(pdf_path)
        return summary


def get_volume_processor(**kwargs):
    return VolumeProcessor(**kwargs)
