import json
import re
import time
import google.generativeai as genai
from pathlib import Path


CONTEXT_BLOCK_TEMPLATE = """
[CONTEXTE] سياق الصفحة السابقة:
النص التالي هو نهاية التمرين في الصفحة السابقة الذي لم يكتمل:
---
{prev_page_ending}
---
إذا كانت بداية هذه الصفحة هي استمرار لذلك التمرين، ضع is_continuation = true للتمرين الأول.
"""

BASE_STRUCTURATION_PROMPT = """أنت مساعد متخصص في تحليل تمارين العلوم الطبيعية للبكالوريا الجزائرية.

سأعطيك نص تمرين مستخرج بواسطة OCR من كتاب حوليات. النص قد يحتوي على أخطاء OCR بسيطة أو يكون غير منظم.

مهمتك:
1. تصحيح أخطاء OCR الواضحة في النص العربي
2. تحديد المعلومات التالية وإرجاعها بصيغة JSON

{context_block}

أعد البيانات بهذا الشكل بالضبط (تأكد من أنه JSON صالح):
[
  {{
    "exercice_id": "رقم التمرين إن وجد",
    "is_continuation": false,
    "is_complete": true,
    "thematique": "الوحدة/المجال (مثال: التكتونية العامة، المناعة، إلخ)",
    "chapitre": "الفصل أو الدرس",
    "type_exercice": "تمرين | مسألة | سؤال نظري",
    "questions": [
      {{
        "numero": "1",
        "texte": "نص السؤال مصحح",
        "sous_questions": [
          {{
            "numero": "1-أ",
            "texte": "نص السؤال الفرعي"
          }}
        ]
      }}
    ],
    "reponses": [
      {{
        "numero_question": "1",
        "texte_reponse": "الإجابة أو الحل المقترح إن وجد في النص"
      }}
    ],
    "figures_referees": ["وصف أي إشارة لشكل أو جدول أو وثيقة في النص"],
    "mots_cles": ["كلمات مفتاحية علمية"]
  }}
]

النص المستخرج من الصفحة:
---
{text_content}
---

ملاحظات هامة جدا:
- إذا كان النص يحتوي على عدة تمارين في نفس الصفحة، أرجع مصفوفة (Array) تحتوي على عدة عناصر JSON، كل عنصر يمثل تمرينا.
- إذا أشار النص إلى "الوثيقة" أو "الشكل" أو "المنحنى" أو "الجدول"، سجّل ذلك في figures_referees.
- صحح الأخطاء الإملائية الواضحة الناتجة عن نظام التعرف على الحروف (OCR).
- is_continuation: true إذا كان التمرين يستمر من الصفحة السابقة (فقط للتمرين الأول في الصفحة).
- is_complete: false إذا كان النص ينقطع دون خاتمة (التمرين يكتمل في الصفحة التالية).
- أرجع JSON فقط بدون أي نص إضافي، وبدون علامات ```json أو ``` في البداية والنهاية. فقط JSON الصافي."""


def build_prompt(ocr_text: str, prev_page_ending: str = None) -> str:
    context_block = ""
    if prev_page_ending:
        context_block = CONTEXT_BLOCK_TEMPLATE.format(prev_page_ending=prev_page_ending)
    return BASE_STRUCTURATION_PROMPT.format(
        context_block=context_block,
        text_content=ocr_text
    )


class ExerciseStructurer:
    """
    Envoie le texte OCR brut à un LLM texte (pas vision !)
    pour le structurer en JSON d'exercices.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit(self):
        """Respecter les limites du free tier."""
        self.request_count += 1
        now = time.time()
        elapsed = now - self.last_request_time

        min_interval = 4.0  # ~15 requêtes par minute
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_request_time = time.time()

    def _call_gemini_with_retry(self, prompt: str, page_num: int,
                                 max_retries: int = 3) -> dict:
        """Appelle Gemini avec retry sur quota 429."""
        last_error = None
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )
                result_text = response.text
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json\n", "")
                    result_text = result_text.replace("```", "")
                if result_text.startswith("```"):
                    result_text = result_text.replace("```\n", "")
                    result_text = result_text.replace("```", "")

                return {"status": "success", "exercises": json.loads(result_text)}

            except Exception as e:
                last_error = e
                err_str = str(e)
                is_quota = "429" in err_str or "quota" in err_str.lower() or "RESOURCE_EXHAUSTED" in err_str

                if is_quota and attempt < max_retries - 1:
                    wait = 60 * (attempt + 1)
                    print(f"  [QUOTA] Page {page_num}, tentative {attempt+1}/{max_retries} - attente {wait}s...")
                    time.sleep(wait)
                else:
                    if is_quota:
                        print(f"  [QUOTA] Page {page_num}, quota epuise apres {max_retries} tentatives")
                    else:
                        print(f"  [ERREUR] Page {page_num} (tentative {attempt+1}): {e}")
                    break

        return {"status": "error", "error": str(last_error)}

    def structure_text(self, raw_text: str, page_num: int,
                       prev_page_ending: str = None) -> dict:
        if not raw_text or len(raw_text.strip()) < 20:
            return {"page": page_num, "status": "empty", "exercises": []}

        prompt = build_prompt(raw_text, prev_page_ending=prev_page_ending)
        result = self._call_gemini_with_retry(prompt, page_num)
        result["page"] = page_num
        return result


def is_exercise_incomplete(page_data: dict) -> bool:
    """
    Détecte si un exercice est coupé en fin de page.
    """
    if not page_data:
        return False
    exercises = page_data.get("exercises", [])
    if not exercises:
        return False
    last_ex = exercises[-1]
    last_text = last_ex.get("texte", "").strip()

    # Vérifier si Gemini a déjà marqué comme incomplet
    if not last_ex.get("is_complete", True):
        return True

    last_text_lower = last_text.lower()
    continuation_signals = [
        last_text.endswith((":", "،", ",", "…", "...")),
        bool(re.search(r'\d+[\.\-]\s*$', last_text)),
        bool(re.search(r'(suite|يتبع|التالية)', last_text_lower, re.IGNORECASE)),
        len(last_text) < 100 and not last_text.endswith(('.', '؟', '?', '!')),
    ]
    return any(continuation_signals)


def merge_cross_page_exercises(pages_data: list) -> list:
    """
    Fusionne les exercices qui s'étendent sur plusieurs pages.
    """
    merged = []
    pending_exercise = None

    for i, page in enumerate(pages_data):
        exercises = page.get("exercises", [])
        page_num = page.get("page_number", i)

        if not exercises:
            continue

        if pending_exercise is not None:
            first_ex = exercises[0]
            pending_exercise["texte"] += "\n" + first_ex.get("texte", "")

            existing_q = pending_exercise.get("questions", [])
            new_q = first_ex.get("questions", [])
            pending_exercise["questions"] = existing_q + new_q

            existing_f = pending_exercise.get("figures_referees", [])
            new_f = first_ex.get("figures_referees", [])
            pending_exercise["figures_referees"] = existing_f + new_f

            pages_src = pending_exercise.get("pages_source", [])
            if page_num not in pages_src:
                pages_src.append(page_num)
            pending_exercise["pages_source"] = pages_src

            merged.append(pending_exercise)
            pending_exercise = None
            remaining = exercises[1:]
        else:
            remaining = exercises

        for j, ex in enumerate(remaining):
            ex["pages_source"] = [page_num]
            if j == len(remaining) - 1 and is_exercise_incomplete({"exercises": [ex]}):
                print(f"  [INCOMPLET] Exercice incomplet page {page_num} -> attente page suivante")
                pending_exercise = ex
            else:
                merged.append(ex)

    if pending_exercise is not None:
        print(f"  [ATTENTE] Exercice en attente non complete (derniere page)")
        merged.append(pending_exercise)

    return merged


def structure_single_page(
    ocr_text: str,
    page_number: int,
    figures_dir: str,
    api_key: str,
    prev_page_ending: str = None
) -> dict:
    """
    Structure une seule page avec contexte de continuité.
    """
    structurer = ExerciseStructurer(api_key)
    result = structurer.structure_text(
        raw_text=ocr_text,
        page_num=page_number,
        prev_page_ending=prev_page_ending
    )
    result["page_number"] = page_number

    # Associer les figures de cette page
    figures_path = Path(figures_dir)
    page_figures = sorted(figures_path.glob(f"page{page_number:04d}_fig*.png"))
    if page_figures:
        result["figures_paths"] = [str(f) for f in page_figures]

    return result


def structure_all_pages(
    ocr_results: dict,
    figures_dir: str,
    api_key: str,
    output_file: str = "exercices_structures.json"
):
    """
    Pipeline original : prend les résultats OCR + les figures,
    structure tout page par page (sans continuité) et produit le JSON final.
    """
    structurer = ExerciseStructurer(api_key)
    figures_path = Path(figures_dir)
    all_exercises = []

    # Regrouper les zones texte par page
    pages = {}
    for filename, text in ocr_results.items():
        try:
            page_num_str = filename.split("_")[0].replace("page", "")
            page_num = int(page_num_str)
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(text)
        except ValueError:
            print(f"  [WARN] Impossible d'extraire la page de {filename}")

    total = len(pages)
    for i, (page_num, texts) in enumerate(sorted(pages.items())):
        print(f"Structuration page {page_num} ({i+1}/{total})...")

        full_text = "\n\n".join(texts)

        result = structurer.structure_text(full_text, page_num)

        # Associer les figures de cette page
        page_figures = sorted(figures_path.glob(f"page{page_num:04d}_fig*.png"))
        if page_figures:
            result["figures"] = [str(f) for f in page_figures]

        all_exercises.append(result)

    # Sauvegarder le résultat final
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_exercises, f, ensure_ascii=False, indent=2)

    print(f"\n[DONE] {len(all_exercises)} pages traitees -> {output_file}")
    return all_exercises
