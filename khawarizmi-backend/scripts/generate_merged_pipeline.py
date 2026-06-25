#!/usr/bin/env python3
"""Generate the merged OCR pipeline: EasyOCR GPU + OpenCV preprocessing."""
import os

src = r'C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-backend\scripts\run_khelifa_ocr_colab.py'
dst = r'C:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-backend\scripts\ocr_khelifa_pipeline.py'

# Read the Colab script as base
with open(src, encoding='utf-8') as f:
    content = f.read()

# Add OpenCV preprocessing imports after the imports section
old_imports = 'import pymupdf\nimport easyocr'
new_imports = '''import cv2
import numpy as np
import pymupdf
import easyocr'''

content = content.replace(old_imports, new_imports)

# Add preprocessing functions before Q_PATTERN
old_qpattern = "Q_PATTERN = re.compile("
preprocessing_code = '''
# ---------------------------------------------------------------------------
# Preprocessing OpenCV (deskew, denoising, binarization)
# ---------------------------------------------------------------------------
def _deskew(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                             minLineLength=100, maxLineGap=10)
    if lines is None:
        return image
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 != x1:
            angles.append(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
    if not angles:
        return image
    median_angle = np.median(angles)
    if abs(median_angle) < 0.5:
        return image
    h, w = image.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), median_angle, 1.0)
    return cv2.warpAffine(image, M, (w, h),
                          flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def preprocess_for_ocr(img_array: np.ndarray) -> np.ndarray:
    img = _deskew(img_array)
    if img.ndim == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    denoised = cv2.fastNlMeansDenoising(gray, h=10,
                                          templateWindowSize=7,
                                          searchWindowSize=21)
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, blockSize=31, C=10,
    )
    return binary


'''

content = content.replace(old_qpattern, preprocessing_code + old_qpattern)

# Modify ocr_page to use preprocessing
old_ocr_page = '''def ocr_page(pix, reader):
    tmp = f"/tmp/ocr_{os.urandom(4).hex()}.png"
    pix.save(tmp)
    try:'''

new_ocr_page = '''def ocr_page(pix, reader, use_preprocess=True):
    tmp = f"/tmp/ocr_{os.urandom(4).hex()}.png"
    if use_preprocess:
        import numpy as np
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width, pix.n
        )
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif pix.n == 1:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif pix.n == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        processed = preprocess_for_ocr(img_array)
        cv2.imwrite(tmp, processed)
    else:
        pix.save(tmp)
    try:'''

content = content.replace(old_ocr_page, new_ocr_page)

# Add resume mode and preprocess flag to process_volume
old_proc_vol = '''def process_volume(pdf_path, serie, vol_num, dpi=150):'''

new_proc_vol = '''def process_volume(pdf_path, serie, vol_num, dpi=150, use_preprocess=True, resume=False):'''

content = content.replace(old_proc_vol, new_proc_vol)

# Add resume logic after opening the doc
old_after_open = '''    vol_data = {"source": f"KHELIFA {serie} - Volume {vol_num}",
                "fichier": os.path.basename(pdf_path),
                "total_pages": total, "processed_pages": total, "pages": []}
    all_q = []
    t_start = time.time()'''

new_after_open = '''    vol_data = {"source": f"KHELIFA {serie} - Volume {vol_num}",
                "fichier": os.path.basename(pdf_path),
                "total_pages": total, "processed_pages": 0, "pages": []}
    all_q = []
    processed_pages_set = set()
    existing_page_count = 0
    t_start = time.time()'''

content = content.replace(old_after_open, new_after_open)

# Add resume check and page skipping
old_loop_start = '''    for pn in range(total):
        pix = doc[pn].get_pixmap(dpi=dpi)
        blocks = ocr_page(pix, reader)'''

new_loop_start = '''    for pn in range(total):
        page_no = pn + 1
        if resume and page_no in processed_pages_set:
            log.info(f"  Page {page_no} deja traitee (skip)")
            continue

        pix = doc[pn].get_pixmap(dpi=dpi)
        blocks = ocr_page(pix, reader, use_preprocess=use_preprocess)'''

content = content.replace(old_loop_start, new_loop_start)

# Add page_no to question IDs and data
old_id_gen = '''                    "id": f"q_khelifa{serie}_v{vol_num:02d}_p{pn+1:02d}_{qi+1:02d}","'''
new_id_gen = '''                    "id": f"q_khelifa{serie}_v{vol_num:02d}_p{page_no:02d}_{qi+1:02d}","'''

content = content.replace(old_id_gen, new_id_gen)

old_source = '''                    "source": f"KHELIFA {serie} - Volume {vol_num} - Page {pn+1}","'''
new_source = '''                    "source": f"KHELIFA {serie} - Volume {vol_num} - Page {page_no}","'''

content = content.replace(old_source, new_source)

# Update notes
content = content.replace('"notes": "OCR auto"', '"notes": "OCR auto + preprocessing"')

# Add source_page field
content = content.replace('"notes": "OCR auto + preprocessing"', '"notes": "OCR auto + preprocessing", "source_page": page_no')

# Add logging import
content = content.replace('import pymupdf', 'import logging\nlogging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")\nlog = logging.getLogger(__name__)\nimport pymupdf')

# Update print statements to use log
content = content.replace('print(f"Traitement: KHELIFA {serie} Volume {vol}', 'log.info(f"Traitement: KHELIFA {serie} Volume {vol}')
content = content.replace('print(f"  -> {len(questions)} questions extraites")', 'log.info(f"  -> {len(questions)} questions extraites")')
content = content.replace('print(f"Total questions extraites : {len(all_consolidated)}")', 'log.info(f"Total questions extraites : {len(all_consolidated)}")')

# Add resume argument to CLI
old_cli = '''    print(f"Fichier consolide : {consolidated_path}")'''

content = content.replace(old_cli, '''    log.info(f"Fichier consolide : {consolidated_path}")''')

# Add --resume and --preprocess flags to argument parsing
old_argparse = '    if not pdfs:'
content = content.replace(old_argparse, '''
if len(sys.argv) > 1 and '--resume' in sys.argv:
    RESUME_MODE = True
    sys.argv.remove('--resume')
    print("Mode REPRISE active")
else:
    RESUME_MODE = False

USE_PREPROCESS = True
if '--no-preprocess' in sys.argv:
    USE_PREPROCESS = False
    sys.argv.remove('--no-preprocess')
    print("Preprocessing desactive")

''' + old_argparse)

# Update process_volume calls to pass resume and preprocess flags
old_pv_call = '    vol_data, questions = process_volume(pdf_path, serie, vol)'
new_pv_call = '    vol_data, questions = process_volume(pdf_path, serie, vol, dpi=150, use_preprocess=USE_PREPROCESS, resume=RESUME_MODE)'
content = content.replace(old_pv_call, new_pv_call)

# Update processed_pages count
content = content.replace('"processed_pages": total', '"processed_pages": len(processed_pages_set)')

# Write output
with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Merged pipeline written to {dst}')
print(f'Size: {os.path.getsize(dst)} bytes')
