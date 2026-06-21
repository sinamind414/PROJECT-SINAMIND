"""
=== OCR KHELIFA 1 & 2 - Version Google Colab (GPU) ===

Instructions:
1. Va sur https://colab.research.google.com/
2. Crée un nouveau notebook
3. Copie-colle TOUT ce fichier dans une cellule
4. Exécute (Runtime -> Run all)
5. Les fichiers JSON seront sauvegardés dans /content/ocr_output/
6. Télécharge-les via le panneau de gauche

Temps estimé sur GPU (T4) : ~2 secondes par page = ~30 min pour 30 volumes
"""

# ============================================================
# CELLULE 1 - Installation des dépendances
# ============================================================
import sys, os, subprocess, json, re, time, shutil, glob
from pathlib import Path

print("Installation des dépendances...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymupdf", "easyocr"], capture_output=True)
print("Dépendances installées.")

# ============================================================
# CELLULE 2 - Montage Google Drive & Upload des PDFs
# ============================================================
# from google.colab import drive, files  (local mode)
# drive.mount('/content/drive')  (local mode)

print("\n=== UPLOAD DES PDFs KHELIFA ===")
print("Crée un dossier 'khelifa_pdfs' dans ton Google Drive")
print("Dépose tous les PDFs KHELIFA dedans")
print()

PDF_SOURCE = "/content/drive/MyDrive/khelifa_pdfs"
OUTPUT_DIR = "/content/ocr_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PDF_SOURCE, exist_ok=True)

print(f"Dossier source : {PDF_SOURCE}")
print(f"Dossier sortie : {OUTPUT_DIR}")
print()

# Lister les PDFs trouvés
pdfs = sorted(glob.glob(os.path.join(PDF_SOURCE, "*.pdf")))
print(f"PDFs trouvés : {len(pdfs)}")
for p in pdfs:
    print(f"  - {os.path.basename(p)}")

# ============================================================
# CELLULE 3 - Moteur OCR
# ============================================================
import cv2
import numpy as np
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)
import pymupdf
import easyocr

print("Initialisation EasyOCR (GPU)...")
reader = easyocr.Reader(['ar', 'en'], gpu=True)
print("OK")


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


Q_PATTERN = re.compile(
    r'(التمرين|السؤال|سؤال|تمرين|question|exercice|exo?\s*\d+|'
    r'أذكر|بين|حدد|صف|فسر|استخرج|قارن|استنتج|وضح|علل|ارسم|'
    r'بماذا|كيف|لماذا|ما هو|ما هي|ماذا|انطلاقا|الجزء|الوثيقة|التعليمة)',
    re.IGNORECASE
)

MC_MAP = {
    "استنساخ":"mc_prot_01","نسخ":"mc_prot_01","transcription":"mc_prot_01",
    "ADN":"mc_prot_01","ARNm":"mc_prot_04","الرنا الرسول":"mc_prot_04",
    "ترجمة":"mc_prot_02","traduction":"mc_prot_02",
    "ARNt":"mc_prot_05","الرنا الناقل":"mc_prot_05","anticodon":"mc_prot_05",
    "ريبوزوم":"mc_prot_06","ribosome":"mc_prot_06",
    "كودون":"mc_prot_03","رامزة":"mc_prot_03","شفرة":"mc_prot_03",
    "بدء":"mc_prot_07","initiation":"mc_prot_07",
    "استطالة":"mc_prot_08","إطالة":"mc_prot_08","إنهاء":"mc_prot_08",
    "بنية أولية":"mc_struc_01","بنية اولية":"mc_struc_01",
    "بنية ثانوية":"mc_struc_02","بنية ثالثية":"mc_struc_03",
    "بنية رباعية":"mc_struc_04","بنية فراغية":"mc_struc_05",
    "إنزيم":"mc_enz_01","enzyme":"mc_enz_01","موقع فعال":"mc_enz_01",
    "نوعية إنزيمية":"mc_enz_02","تثبيط":"mc_enz_05","inhibition":"mc_enz_05",
    "لمفاويات B":"mc_imm_01","LB":"mc_imm_01",
    "لمفاويات T":"mc_imm_02","LT4":"mc_imm_02","LT8":"mc_imm_02",
    "مستضد":"mc_imm_03","antigene":"mc_imm_03",
    "جسم مضاد":"mc_imm_03","anticorps":"mc_imm_03",
    "مناعة خلطية":"mc_imm_04","humorale":"mc_imm_04",
    "مناعة خلوية":"mc_imm_05","cellulaire":"mc_imm_05","CTL":"mc_imm_05",
    "ذاكرة مناعية":"mc_imm_06","memoire":"mc_imm_06","vaccin":"mc_imm_06",
    "كلوروبلاست":"mc_photo_01","chloroplaste":"mc_photo_01",
    "طور ضوئي":"mc_photo_02","دورة كالفن":"mc_photo_03",
    "ميتوكندري":"mc_resp_01","mitochondrie":"mc_resp_01",
    "تحلل سكري":"mc_resp_02","glycolyse":"mc_resp_02",
    "كريس":"mc_resp_03","Krebs":"mc_resp_03",
    "سلسلة تنفسية":"mc_resp_04","تخمر":"mc_resp_05","fermentation":"mc_resp_05",
    "بنية الأرض":"mc_tec_01","sismique":"mc_tec_01",
    "صفائح":"mc_tec_02","plaques":"mc_tec_02",
    "تباعد":"mc_tec_03","تقارب":"mc_tec_03",
    "غوص":"mc_tec_04","subduction":"mc_tec_04",
    "زلزال":"mc_tec_05","بركان":"mc_tec_05","volcan":"mc_tec_05",
}

def ocr_page(pix, reader, use_preprocess=True):
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
    try:
        results = reader.readtext(tmp, paragraph=False, detail=1)
        blocks = []
        for r in results:
            if len(r) == 3:
                bbox, text, conf = r
            elif len(r) == 2:
                bbox, text = r
                conf = 0.5
            else:
                continue
            if conf > 0.3 and text.strip():
                blocks.append({
                    "text": text.strip(),
                    "confidence": round(float(conf), 2),
                    "bbox": [round(float(x), 1) for pt in bbox for x in pt]
                })
        return blocks
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

def extract_questions(blocks):
    questions = []
    cur = None
    for b in blocks:
        if Q_PATTERN.search(b['text']):
            if cur:
                questions.append(cur)
            cur = {"texte_brut": b['text'], "confidence": b['confidence'], "blocks": [b]}
        elif cur and len(cur['blocks']) < 10:
            cur['blocks'].append(b)
            cur['texte_brut'] += " " + b['text']
    if cur:
        questions.append(cur)
    return questions

def tag_concept(text):
    tl = text.lower()
    found = set()
    for kw, cid in MC_MAP.items():
        if kw.lower() in tl:
            found.add(cid)
    if not found:
        return "mc_xxx_xx", [], True
    spec = {"mc_prot_07":3,"mc_prot_08":3,"mc_prot_05":3,"mc_prot_06":3,
            "mc_enz_01":3,"mc_enz_02":3,"mc_imm_04":3,"mc_imm_05":3,"mc_imm_06":3,
            "mc_struc_01":2,"mc_struc_02":2,"mc_struc_03":2,"mc_struc_04":2,
            "mc_prot_01":2,"mc_prot_02":2,"mc_prot_03":2,"mc_prot_04":2,
            "mc_imm_01":2,"mc_imm_02":2,"mc_imm_03":2}
    sf = sorted(found, key=lambda x: spec.get(x, 0), reverse=True)
    return sf[0], sf[1:3], False

def clean_arabic(text):
    t = re.sub(r'\s+', ' ', text).strip()
    t = re.sub(r'[|¦•●]', '', t)
    t = t.replace('أ','ا').replace('إ','ا').replace('آ','ا')
    t = t.replace('ة','ه').replace('ى','ا')
    t = t.replace('٠','0').replace('١','1').replace('٢','2')
    t = t.replace('٣','3').replace('٤','4').replace('٥','5')
    t = t.replace('٦','6').replace('٧','7').replace('٨','8').replace('٩','9')
    return t

def process_volume(pdf_path, serie, vol_num, dpi=150, use_preprocess=True, resume=False):
    doc = pymupdf.open(pdf_path)
    total = len(doc)
    vol_data = {"source": f"KHELIFA {serie} - Volume {vol_num}",
                "fichier": os.path.basename(pdf_path),
                "total_pages": total, "processed_pages": 0, "pages": []}
    all_q = []
    processed_pages_set = set()
    existing_page_count = 0
    t_start = time.time()

    for pn in range(total):
        page_no = pn + 1
        if resume and page_no in processed_pages_set:
            log.info(f"  Page {page_no} deja traitee (skip)")
            continue

        pix = doc[pn].get_pixmap(dpi=dpi)
        blocks = ocr_page(pix, reader, use_preprocess=use_preprocess)
        qs = extract_questions(blocks)

        pd = {"page": pn+1, "blocks": len(blocks), "questions": []}
        for qi, q in enumerate(qs):
            cleaned = clean_arabic(q['texte_brut'])
            main, sec, av = tag_concept(cleaned)
            avg_conf = round(sum(b['confidence'] for b in q['blocks']) / len(q['blocks']), 2)
            qd = {
                "id": f"q_khelifa{serie}_v{vol_num:02d}_p{pn+1:02d}_{qi+1:02d}",
                "texte_brut": q['texte_brut'][:500],
                "texte_corrige": cleaned[:500],
                "micro_concept_id": main,
                "secondary_concepts": sec,
                "a_verifier": av,
                "confidence": avg_conf,
                "source": f"KHELIFA {serie} - Volume {vol_num} - Page {pn+1}",
                "type": "question", "difficulte": "moyenne",
                "bac_frequent": not av,
                "notes": "OCR auto + preprocessing", "source_page": page_no
            }
            pd["questions"].append(qd)
            all_q.append(qd)
        vol_data["pages"].append(pd)

        elapsed = time.time() - t_start
        eta = (elapsed / (pn+1)) * (total - pn - 1) / 60
        print(f"  [{pn+1}/{total}] {len(blocks)} blocs, {len(qs)} q | "
              f"{elapsed:.0f}s ecoulees, ETA {eta:.0f}min")

    doc.close()
    return vol_data, all_q

# ============================================================
# CELLULE 4 - LANCER LE TRAITEMENT
# ============================================================
print("\n=== DEBUT DU TRAITEMENT KHELIFA ===")
print()

total_questions = 0
for pdf_path in sorted(glob.glob(os.path.join(PDF_SOURCE, "*.pdf"))):
    fname = os.path.basename(pdf_path)

    # Extraire serie et volume du nom du fichier
    serie = None
    vol = None
    if "KHELIFA1" in fname.upper() or "KHELIFA 1" in fname.upper():
        serie = 1
    elif "KHELIFA2" in fname.upper() or "KHELIFA 2" in fname.upper():
        serie = 2
    else:
        print(f"Ignore (non-KHELIFA): {fname}")
        continue

    m = re.search(r'VOLUME[_\s]?(\d+)', fname, re.IGNORECASE)
    if m:
        vol = int(m.group(1))
    else:
        print(f"Volume non detecte: {fname}")
        continue

    print(f"\n{'='*60}")
    log.info(f"Traitement: KHELIFA {serie} Volume {vol} ({fname})")
    print(f"{'='*60}")

    vol_data, questions = process_volume(pdf_path, serie, vol, dpi=150, use_preprocess=USE_PREPROCESS, resume=RESUME_MODE)

    # Sauvegarder
    vn = f"khelifa{serie}_volume{vol:02d}"
    with open(os.path.join(OUTPUT_DIR, f"{vn}.json"), 'w', encoding='utf-8') as f:
        json.dump(vol_data, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_DIR, f"{vn}_questions.json"), 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    total_questions += len(questions)
    log.info(f"  -> {len(questions)} questions extraites")
    print()

# ============================================================
# CELLULE 5 - GENERER LE FICHIER CONSOLIDE
# ============================================================
print("\n=== GENERATION FICHIER CONSOLIDE ===")
all_consolidated = []
for qfile in sorted(glob.glob(os.path.join(OUTPUT_DIR, "*_questions.json"))):
    with open(qfile, 'r', encoding='utf-8') as f:
        all_consolidated.extend(json.load(f))

consolidated_path = os.path.join(OUTPUT_DIR, "khelifa_all_questions.json")
with open(consolidated_path, 'w', encoding='utf-8') as f:
    json.dump(all_consolidated, f, ensure_ascii=False, indent=2)

log.info(f"Total questions extraites : {len(all_consolidated)}")
print(f"Fichier consolide : {consolidated_path}")

# Stats
from collections import Counter
mc_counts = Counter(q.get('micro_concept_id', 'N/A') for q in all_consolidated)
print(f"\nDistribution des micro-concepts :")
for mc, count in mc_counts.most_common():
    print(f"  {mc}: {count}")

print(f"\n=== TERMINE ===")
print(f"Fichiers dans {OUTPUT_DIR}:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    size_mb = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / 1e6
    print(f"  {f} ({size_mb:.1f} MB)")
