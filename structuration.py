import json
import time
import google.generativeai as genai
from pathlib import Path


STRUCTURATION_PROMPT = """أنت مساعد متخصص في تحليل تمارين العلوم الطبيعية للبكالوريا الجزائرية.

سأعطيك نص تمرين مستخرج بواسطة OCR من كتاب حوليات. النص قد يحتوي على أخطاء OCR بسيطة أو يكون غير منظم.

مهمتك:
1. تصحيح أخطاء OCR الواضحة في النص العربي
2. تحديد المعلومات التالية وإرجاعها بصيغة JSON

أعد البيانات بهذا الشكل بالضبط (تأكد من أنه JSON صالح):
[
  {
    "exercice_id": "رقم التمرين إن وجد",
    "thematique": "الوحدة/المجال (مثال: التكتونية العامة، المناعة، إلخ)",
    "chapitre": "الفصل أو الدرس",
    "type_exercice": "تمرين | مسألة | سؤال نظري",
    "questions": [
      {
        "numero": "1",
        "texte": "نص السؤال مصحح",
        "sous_questions": [
          {
            "numero": "1-أ",
            "texte": "نص السؤال الفرعي"
          }
        ]
      }
    ],
    "reponses": [
      {
        "numero_question": "1",
        "texte_reponse": "الإجابة أو الحل المقترح إن وجد في النص"
      }
    ],
    "figures_referees": ["وصف أي إشارة لشكل أو جدول أو وثيقة في النص"],
    "mots_cles": ["كلمات مفتاحية علمية"]
  }
]

النص المستخرج من الصفحة:
---
{text_content}
---

ملاحظات هامة جدا:
- إذا كان النص يحتوي على عدة تمارين في نفس الصفحة، أرجع مصفوفة (Array) تحتوي على عدة عناصر JSON، كل عنصر يمثل تمرينا.
- إذا أشار النص إلى "الوثيقة" أو "الشكل" أو "المنحنى" أو "الجدول"، سجّل ذلك في figures_referees.
- صحح الأخطاء الإملائية الواضحة الناتجة عن نظام التعرف على الحروف (OCR).
- أرجع JSON فقط بدون أي نص إضافي، وبدون علامات ```json أو ``` في البداية والنهاية. فقط JSON الصافي."""


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

    def structure_text(self, raw_text: str, page_num: int) -> dict:
        if not raw_text or len(raw_text.strip()) < 20:
            return {"page": page_num, "status": "empty", "exercises": []}

        self._rate_limit()

        prompt = STRUCTURATION_PROMPT.replace("{text_content}", raw_text)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                )
            )

            result_text = response.text
            # Nettoyer si le modèle renvoie du markdown
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json\n", "")
                result_text = result_text.replace("```", "")
            if result_text.startswith("```"):
                result_text = result_text.replace("```\n", "")
                result_text = result_text.replace("```", "")
                
            result = json.loads(result_text)
            return {"page": page_num, "status": "success", "exercises": result}

        except Exception as e:
            print(f"  ⚠ Erreur page {page_num}: {e}")
            return {"page": page_num, "status": "error", "error": str(e)}


def structure_all_pages(
    ocr_results: dict,
    figures_dir: str,
    api_key: str,
    output_file: str = "exercices_structures.json"
):
    """
    Pipeline complet : prend les résultats OCR + les figures,
    structure tout et produit le JSON final.
    """
    structurer = ExerciseStructurer(api_key)
    figures_path = Path(figures_dir)
    all_exercises = []

    # Regrouper les zones texte par page
    pages = {}
    for filename, text in ocr_results.items():
        # Extraire le numéro de page du nom de fichier (page0042_text01.png)
        # Format attendu : pageXXXX_textYY.png
        try:
            page_num_str = filename.split("_")[0].replace("page", "")
            page_num = int(page_num_str)
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(text)
        except ValueError:
            print(f"  ⚠ Impossible d'extraire la page de {filename}")

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

    print(f"\n✅ {len(all_exercises)} pages traitées → {output_file}")
    return all_exercises
