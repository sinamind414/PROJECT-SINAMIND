from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parents[3]

@dataclass
class OCRConfig:
    tesseract_cmd: str = "tesseract"
    tesseract_langs: str = "ara+fra"
    default_dpi: int = 140
    default_psm: int = 3
    default_oem: int = 1
    default_retries: int = 2
    default_timeout: int = 180
    data_dir: Path = BASE_DIR / "data"
    annales_pdf_dir: Path = data_dir / "ANNALES_SVT_BAC_ALGERIE"
    ocr_output_base: Path = data_dir / "annales_workspace" / "OCR_PROD"
    enable_preprocessing: bool = True
    bundle_suffix: str = ".ocr_prod_full.txt"

config = OCRConfig()

def get_config():
    return config
