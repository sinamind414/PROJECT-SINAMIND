"""
tests/golden/audit_correcteur_golden.py — Jeu doré SYNTHÉTIQUE d'audit du correcteur.

Objectif : mesurer, sur les moteurs LOCAUX (savoir déterministe + L2 fallback),
la tenue du barème et les faux positifs / faux négatifs sur un éventail de copies :
  - exacte (reprise de la réponse modèle)
  - partielle (certains concepts, d'autres non)
  - correcte mais reformulée (même sens, mots différents)
  - hors sujet (texte arabe sans rapport)
  - contradictoire / erreur conceptuelle grave (règle du lexique : 32 ATP, ADN hors
    noyau, traduction dans le noyau, photosynthèse produisant du CO2...)
  - erreur classique du Bac (mélange respiration/traduction, etc.)

NB : Savoir est appelé via deterministic_correct_v2 (chemin prod réel, concepts
déduits de la réponse modèle). L2 via evaluate_l2 avec redistribution des poids
quand l'embedder ONNX est en fallback (CI), même logique que scoring.py.
"""
from __future__ import annotations

import asyncio
import json
import os
import statistics
from dataclasses import dataclass, field

from services.fallback_v2 import evaluate_l2
from services.savoir_corrector import deterministic_correct_v2
from services.embedder import get_embedder
from grading.l2 import _extract_concepts  # chemin de prod (run_l2) pour concepts_requis

# ─────────────────────────────────────────────────────────────────────────────
# Jeu doré : questions sur les 3 domaines, réponse modèle, barème.
# Chaque copie est taguée par la catégorie attendue (oracle).
# ─────────────────────────────────────────────────────────────────────────────
QUESTIONS = [
    {
        "qid": "synth_1",
        "domaine": "D1-U1",
        "question": "تتم عملية استنساخ المعلومات الوراثية على مستوى ADN. حدد مقر هذه الظاهرة ودور إنزيم ARN بوليميراز.",
        "reponse_attendue": "تتم عملية الاستنساخ داخل النواة بتدخل إنزيم ARN بوليميراز الذي يفتح سلسلتي الADN ويكسر الروابط الهيدروجينية ثم يقرأ السلسلة المستنسخة 3' إلى 5' ليربط النكليوتيدات الريبية الحرة وفق مبدأ التكامل A مع U و C مع G فتتشكل جزيئة ARNm.",
        "bareme": 4,
    },
    {
        "qid": "enz_1",
        "domaine": "D1-U3",
        "question": "دراسة تأثير درجة الحرارة على النشاط الإنزيمي. لماذا يسترجع الإنزيم نشاطه بعد التبريد ولا يسترجعه بعد الغليان؟",
        "reponse_attendue": "التبريد يخفض سرعة التفاعل دون تخريب البنية الفراغية للإنزيم فيسترجع نشاطه عند العودة للحرارة المثلى، بينما الغليان يسبب تمسخ البنية الفراغية للموقع الفعال فيفقد الإنزيم وظيفته نهائيا.",
        "bareme": 4,
    },
    {
        "qid": "imm_1",
        "domaine": "D1-U4",
        "question": "وضح آلية القضاء على الخلية المصابة بالفيروس من طرف اللمفاويات LTc.",
        "reponse_attendue": "تتعرف الخلية LTc على الخلية المصابة بتطابق مستقبل TCR مع المستضد ومؤشر CD8 مع CMH-I، فتفرز البرفورين الذي يتبلمر في غشاء الخلية المصابة مكونا ثقوبا تسمح بدخول الماء والشوارد والغرانزيم فتحدث صدمة حلولية وموت الخلية.",
        "bareme": 4,
    },
    {
        "qid": "nerf_1",
        "domaine": "D1-U5",
        "question": "علل لماذا يسمى كمون الراحة بكمون الراحة ولماذا يثبت عند -70 mV؟",
        "reponse_attendue": "لأن الغشاء مستقطب: داخل الليف سالب وخارجه موجب بسبب التوزع غير المتكافئ لشوارد الصوديوم والبوتاسيوم، وتحمي مضخة Na+/K+ ATPase هذا التدرج باستهلاك ATP فيبقى الكمون ثابتا قرب -70 mV.",
        "bareme": 4,
    },
    {
        "qid": "photo_1",
        "domaine": "D2-U1",
        "question": "من أين يأتي الأكسجين المنطلق أثناء التركيب الضوئي؟"
        " (تجربة الأكسجين المشع)",
        "reponse_attendue": "الأكسجين المنطلق يأتي من التحلل الضوئي لجزيء الماء H2O وليس من CO2، حيث يتفكك الماء على مستوى النظام الضوئي PSII ويحرر البروتونات والإلكترونات والأكسجين.",
        "bareme": 4,
    },
    {
        "qid": "resp_1",
        "domaine": "D2-U2",
        "question": "احسب الحصيلة الطاقوية الكاملة للتنفس الهوائي لجزيء غلوكوز واحد.",
        "reponse_attendue": "الحصيلة الكاملة للتنفس الهوائي هي 38 جزيء ATP (التحلل السكري 2 + حلقة كريبس 2 + الفسفرة التأكسدية 34).",
        "bareme": 4,
    },
    {
        "qid": "tec_1",
        "domaine": "D3-U1",
        "question": "ما هي الشواهد الجيوفيزيائية على غوص الصفيحة المحيطية تحت الصفيحة القارية؟",
        "reponse_attendue": "من الشواهد: مستوى بنيوف للزلازل العميقة، الخندق المحيطي، الشذوذ الحراري المزدوج، وتشكل الأنديزيت والغرانودوريت نتاج انصهار البيريدوتيت المماه تحت الصفيحة الطافية.",
        "bareme": 4,
    },
    {
        "qid": "struct_1",
        "domaine": "D3-U2",
        "question": "ما هو الدليل العلمي الذي استنتجه العلماء من توقف الموجات الزلزالية S عند عمق 2900 كم؟",
        "reponse_attendue": "توقف الموجات S (لا تخترق السوائل) عند انقطاع غوتنبرغ يثبت أن النواة الخارجية سائلة، لأن الموجات S تنعدم في الأوساط السائلة.",
        "bareme": 4,
    },
]

# ── Copies par question (taguées par catégorie) ──────────────────────────────
TYPE_ORDER = ["exacte", "partielle", "reformulee", "reformulee_b", "hors_sujet", "contradictoire", "erreur_bac"]

COPIES = {
    "synth_1": [
        ("exacte", QUESTIONS[0]["reponse_attendue"]),
        ("partielle", "تتم عملية الاستنساخ داخل النواة بتدخل إنزيم ARN بوليميراز."),
        ("reformulee",
         "يتم نسخ المعلومة الوراثية في النواة حيث يعمل إنزيم بوليميراز على فك التفاف الحلزون المزدوج وقراءة الشريط القالب 3 إلى 5 لتجميع النكليوتيدات الريبية بالتكامل فتنتج رنا رسولا."),
        ("reformulee_b",
         "بداخل النواة يقوم انزيم البوليميراز على فصل سلسلي الدنا وقراءة الخيط المنسوخ لربط النكليوتيدات الحرة بشكل متكامل فيظهر رنا رسول يحمل معلومة المورثة."),
        ("hors_sujet", "المناعة هي وسيلة دفاع الجسم ضد الجراثيم وتوجد خلايا لمفاوية تقضي على الفيروسات."),
        ("contradictoire", "يتم الاستنساخ داخل الهيولى حيث يخرج الADN من النواة ويتجه نحو الريبوزوم ليركب البروتين."),
        ("erreur_bac", "تتم الترجمة داخل النواة على مستوى الADN مباشرة."),
    ],
    "enz_1": [
        ("exacte", QUESTIONS[1]["reponse_attendue"]),
        ("partielle", "الغليان يسبب تمسخ الإنزيم فيفقد وظيفته."),
        ("reformulee",
         "عند التبريد تنخفض سرعة التفاعل لكن البروتين يحتفظ بشكله الفراغي، لذا يعود نشاطه بارتفاع الحرارة. أما التسخين العالي فيغير البنية الفراغية للموقع الفعال ولا يمكن استرجاعها."),
        ("reformulee_b",
         "البرودة لا تدمر الموقع الفعال ففقط تبطئ التفاعل ويعود الانزيم للعمل عند الحرارة المثالية، بينما الحرارة المرتفعة تشوه البنية الفراغية للانزيم فلا يعود نشاطه."),
        ("hors_sujet", "البروتينات هي جزيئات حيوية تتكون من أحماض أمينية مرتبطة بروابط ببتيدية."),
        ("contradictoire", "التبريد يسبب تمسخ الإنزيم بينما الغليان يحمي الموقع الفعال ويحسن النشاط."),
        ("erreur_bac", "درجة الحرارة المثلى للنشاط الإنزيمي عند الإنسان هي 80 درجة مئوية."),
    ],
    "imm_1": [
        ("exacte", QUESTIONS[2]["reponse_attendue"]),
        ("partielle", "تفرز الخلية LTc البرفورين الذي يثقب غشاء الخلية المصابة."),
        ("reformulee",
         "تكبر الخلية القاتلة LTc معرفيا بالخلية المصابة بفضل تطابق مستقبل الTCR والمؤشر CD8 مع معقد التوافق النسيجي من النمط الأول، ثم تفرز مادة تثقب الغشاء وتدخل إنزيمات محللة تقضي على الخلية."),
        ("reformulee_b",
         "تقوم الخلايا التائية السامة بالتعرف على الخلية المريضة بواسطة مؤشر CD8 والنمط الأول من مجمع التوافق النسيجي، ثم تحقن مادة تفتح ثقوبا في الغشاء لتدخل إنزيمات القتل فتحدث انحلالا خلوي."),
        ("hors_sujet", "تتميز الأجسام المضادة بخصوصيتها تجاه المستضدات المختلفة."),
        ("contradictoire", "الأجسام المضادة تدخل داخل الخلية المصابة لتقضي على الفيروس مباشرة دون تدخل الخلايا القاتلة."),
        ("erreur_bac", "المناعة الخلطية هي التي تقضي على الخلايا المصابة بالفيروسات."),
    ],
    "nerf_1": [
        ("exacte", QUESTIONS[3]["reponse_attendue"]),
        ("partielle", "داخل الليف سالب وخارجه موجب بسبب التوزع غير المتكافئ للشوارد."),
        ("reformulee",
         "يقال كمون راحة لأن الغشاء يكون متقطبا: الشحنة الداخلية سالبة والخارجية موجبة نتيجة اختلاف تركيز الصوديوم والبوتاسيوم على جانبي الغشاء، ويحافظ عليه بالعمل النشط للمضخة."),
        ("reformulee_b",
         "سمي هذا الكمون بكمون الراحة لأن الخلية في وضع السكون يكون جهد الغشاء مستقرا عند 70 ملي فولت بالاشارة السالبة من الداخل، وهذا بفضل مضخة الايونات التي توزع الشوارد بشكل غير متساو بين الداخل والخارج."),
        ("hors_sujet", "الإنزيمات سرعات التفاعلات الحيوية داخل الخلية."),
        ("contradictoire", "داخل الليف موجب وخارجه سالب أثناء الراحة بسبب دخول الصوديوم."),
        ("erreur_bac", "كمون الراحة يساوي +30 مللي فولط وتكون الشحنة الداخلية موجبة دائما."),
    ],
    "photo_1": [
        ("exacte", QUESTIONS[4]["reponse_attendue"]),
        ("partielle", "الأكسجين يأتي من الماء H2O وليس من CO2."),
        ("reformulee",
         "باستعمال الأكسجين المشع تبيّن أن غاز الأكسجين المنطلق خلال التركيب الضوئي ناتج عن تفكك جزيء الماء عند نظام PSII، ولا يأتي من ثنائي أكسيد الكربون."),
        ("reformulee_b",
         "الاكسجين المتحرر في الظاهرة الضوئية تركيبه ينبع من شطر جزيئين الماء على مستوى النظام الضوئي الثاني، فليس مصدره غاز الكربون."),
        ("hors_sujet", "يتم التنفس الخلوي في الميتوكندري حيث يستهلك الأكسجين."),
        ("contradictoire", "التركيب الضوئي يستهلك الأكسجين وينتج ثنائي أكسيد الكربون."),
        ("erreur_bac", "الأكسجين المنطلق في التركيب الضوئي يأتي من تفكيك ثنائي أكسيد الكربون CO2."),
    ],
    "resp_1": [
        ("exacte", QUESTIONS[5]["reponse_attendue"]),
        ("partielle", "الحصيلة الكاملة للتنفس الهوائي هي ATP."),
        ("reformulee",
         "يستمر التنفس الهوائي بانتاج 38 وحدة طاقة أتب من التحلل السكري ودورة كريبس والفوسفرة المؤكسدة."),
        ("reformulee_b",
         "بعد تفكيك الغلوكوز في الهيولى ودورة الحمض الستريك وسلسلة النقل الالكتروني يبلغ مجموع جزيئات الطاقة ثلاثي الفوسفات 38 أثناء التنفس الهوائي."),
        ("hors_sujet", "يتم التركيب الضوئي في الصانعة الخضراء بعيدا عن الأكسجين."),
        ("contradictoire", "التنفس الهوائي ينتج 2 ATP فقط والتخمر ينتج 38 ATP."),
        ("erreur_bac", "الحصيلة الطاقوية للتنفس الهوائي هي 32 جزيء ATP."),
    ],
    "tec_1": [
        ("exacte", QUESTIONS[6]["reponse_attendue"]),
        ("partielle", "من الشواهد وجود الخندق المحيطي ومستوى بنيوف للزلازل العميقة."),
        ("reformulee",
         "تتميز مناطق الغوص بوجود خندق بحري عميق وتوزع البؤر الزلزالية على مستوى مائل يسمى مستوى بنيوف، إلى جانب شذوذ حراري مزدوج وبركانية أنديزيتية ناتجة عن انصهار البيريدوتيت المماه."),
        ("reformulee_b",
         "دليل الغوص هو تركيز الزلازل على مستوى مائل عميق يشكل مستوى بنيوف مع وجود خندق محيطي وتدفق حراري غريب في هذه المنطقة."),
        ("hors_sujet", "تتكون صخور الغرانيت والبازلت في المحيطات والجبال."),
        ("contradictoire", "في مناطق الغوص ترتفع الصفيحة المحيطية فوق القارية ولا يوجد خندق."),
        ("erreur_bac", "الظهرات المحيطية هي مناطق غوص تستهلك القشرة المحيطية."),
    ],
    "struct_1": [
        ("exacte", QUESTIONS[7]["reponse_attendue"]),
        ("partielle", "توقف الموجات S يدل على أن النواة الخارجية سائلة."),
        ("reformulee",
         "بما أن الموجات الثانوية S لا تنتشر في السوائل، فإن اختفاءها عند عمق 2900 كم يعني أن نواة الأرض الخارجية في حالة سائلة."),
        ("reformulee_b",
         "عند العمق الكبير الذي يسمى انقطاع غوتنبرغ تختفي الموجات الزلزالية الثانوية S، والسبب في ذلك أن النواة الخارجية سائلة فتمنع مرور هذه الموجات التي لا تعبر المواد السائلة."),
        ("hors_sujet", "الموجات الأولية P تخترق جميع الأغلفة لأنها سريعة."),
        ("contradictoire", "توقف الموجات S يثبت أن النواة الخارجية صلبة تماما."),
        ("erreur_bac", "الموجات S تنتشر في الأوساط السائلة ولذلك تتوقف عند الانقطاع الموهروروفيتش."),
    ],
}


def _l2_score(item: dict, reponse_eleve: str) -> tuple[float, int, str]:
    item["_cat"] = item.get("_cat", "")
    # Chemin prod (run_l2) : concepts_requis extraits de la réponse modèle.
    concepts = _extract_concepts("", item["reponse_attendue"])
    question_data = {
        "reponse_attendue": item["reponse_attendue"],
        "concepts_requis": concepts,
        "points_cles": [item["reponse_attendue"]],
        "question_id": None,
    }
    res = asyncio.get_event_loop().run_until_complete(
        evaluate_l2(reponse_eleve=reponse_eleve, question_data=question_data, db=None)
    )
    if os.environ.get("AUDIT_L2_DEBUG"):
        print(f"  DEBUG l2 qid={item.get('qid')} cat={item['_cat']} "
              f"sf={res.score_final} sem={res.semantic_score} "
              f"struct={res.structural_score} cov={res.coverage_score}")
    final = res.score_final
    try:
        if bool(getattr(get_embedder(), "is_fallback", False)):
            w_t, w_r = 0.25, 0.35
            final = (w_t * res.coverage_score + w_r * res.structural_score) / (w_t + w_r)
            final = max(0.0, min(1.0, final))
    except Exception:
        pass
    score = round(final * item["bareme"])
    code = "all_correct" if score >= item["bareme"] else ("partial_correct" if score > 0 else "insufficient")
    return final, score, code


def _savoir_score(item: dict, reponse_eleve: str) -> dict:
    return deterministic_correct_v2(
        question=item["question"],
        student_answer=reponse_eleve,
        score_max=item["bareme"],
        language="ar",
        model_answer=item["reponse_attendue"],
    )


# ── Oracle de frontières (ce que le correcteur DEVRAIT faire) ────────────────
# retourne la bande de score attendue (sur bareme) pour une catégorie.
def oracle(cat: str, bareme: int) -> tuple[float, float]:
    if cat == "exacte":
        return 0.8 * bareme, bareme  # ~ note pleine
    if cat == "partielle":
        return 0.25 * bareme, 0.85 * bareme  # bande large : partiel
    if cat in ("reformulee", "reformulee_b"):
        return 0.7 * bareme, bareme  # correcte → haut
    if cat == "hors_sujet":
        return 0.0, 0.4 * bareme  # proche de zéro
    if cat == "contradictoire":
        return 0.0, 0.5 * bareme  # pénalisé
    if cat == "erreur_bac":
        return 0.0, 0.5 * bareme  # pénalisé
    return 0.0, bareme


def run() -> dict:
    rows = []
    metrics = {"savoir": [], "l2": []}
    for q in QUESTIONS:
        q["_cat"] = ""
        for cat, copie in COPIES.get(q["qid"], []):
            s = _savoir_score(q, copie)
            qc = dict(q); qc["_cat"] = cat
            fl2, sl2, code_l2 = _l2_score(qc, copie)
            rows.append({
                "qid": q["qid"], "domaine": q.get("domaine", ""),
                "cat": cat, "bareme": q["bareme"],
                "savoir_score": s["score"], "savoir_%": s["percentage"],
                "savoir_can_handle": s.get("_savoir_can_handle"),
                "savoir_n": s.get("_savoir_n_concepts"),
                "savoir_dominant": s.get("dominant_error_code"),
                "l2_score": sl2, "l2_%": round(fl2 * 100), "l2_raw": round(fl2, 3),
                "l2_code": code_l2,
            })
    return {"rows": rows}


def summarize(rows: list[dict]) -> dict:
    from collections import Counter, defaultdict

    # Faux positifs = copie correcte (exacte/reformulee) notée < 0.6 barème
    # Faux négatifs = copie fautive (hors_sujet/contradictoire/erreur_bac) notée ≥ 0.6 barème
    summary = defaultdict(lambda: {"n": 0, "savoir": [], "l2": []})
    for r in rows:
        cat = r["cat"]
        summary[cat]["n"] += 1
        summary[cat]["savoir"].append(r["savoir_%"])
        summary[cat]["l2"].append(r["l2_%"])

    def mean(x): return round(statistics.mean(x), 1) if x else 0.0

    out = {}
    for cat in TYPE_ORDER:
        d = summary.get(cat, {})
        out[cat] = {
            "n": d.get("n", 0),
            "savoir_%_moy": mean(d.get("savoir", [])),
            "l2_%_moy": mean(d.get("l2", [])),
        }

    # Détection faux pos/nég
    fp = {"savoir": [], "l2": []}
    fn = {"savoir": [], "l2": []}
    corrects = {"exacte", "reformulee", "reformulee_b"}
    faults = {"hors_sujet", "contradictoire", "erreur_bac"}
    for r in rows:
        if r["cat"] in corrects:
            if r["savoir_%"] < 60:
                fp["savoir"].append((r["qid"], r["cat"], r["savoir_%"]))
            if r["l2_%"] < 60:
                fp["l2"].append((r["qid"], r["cat"], r["l2_%"]))
        if r["cat"] in faults:
            if r["savoir_%"] >= 60:
                fn["savoir"].append((r["qid"], r["cat"], r["savoir_%"]))
            if r["l2_%"] >= 60:
                fn["l2"].append((r["qid"], r["cat"], r["l2_%"]))

    # Stabilité : variance des scores entre DEUX paraphrases de la même vérité
    # (reformulee et reformulee_b), même question, même barème attendu.
    st = {"savoir": [], "l2": []}
    for q in QUESTIONS:
        refs = [r["savoir_%"] for r in rows if r["qid"] == q["qid"] and r["cat"] in ("reformulee", "reformulee_b")]
        refl = [r["l2_%"] for r in rows if r["qid"] == q["qid"] and r["cat"] in ("reformulee", "reformulee_b")]
        if len(refs) > 1:
            st["savoir"].append(statistics.pstdev(refs))
        if len(refl) > 1:
            st["l2"].append(statistics.pstdev(refl))

    # Conformité au barème : pour chaque catégorie, la %-note attendue (bande
    # oracle) vs la note réellement attribuée. On compte les copies DANS la bande.
    conf = defaultdict(lambda: {"savoir": [0, 0], "l2": [0, 0]})  # [dans_bande, total]
    for r in rows:
        lo, hi = oracle(r["cat"], r["bareme"])
        lo_pct = round(lo / r["bareme"] * 100)
        hi_pct = round(hi / r["bareme"] * 100)
        conf[r["cat"]]["savoir"][1] += 1
        conf[r["cat"]]["l2"][1] += 1
        if lo_pct <= r["savoir_%"] <= hi_pct:
            conf[r["cat"]]["savoir"][0] += 1
        if lo_pct <= r["l2_%"] <= hi_pct:
            conf[r["cat"]]["l2"][0] += 1

    out["_conformite_bareme"] = {
        cat: {
            "attend": [round(oracle(cat, 1)[0] * 100, 1), round(oracle(cat, 1)[1] * 100, 1)],
            "savoir": f"{d['savoir'][0]}/{d['savoir'][1]}",
            "l2": f"{d['l2'][0]}/{d['l2'][1]}",
        }
        for cat, d in conf.items()
    }

    out["_faux_positifs"] = {
        "savoir": fp["savoir"], "l2": fp["l2"],
        "count": {"savoir": len(fp["savoir"]), "l2": len(fp["l2"])},
    }
    out["_faux_negatifs"] = {
        "savoir": fn["savoir"], "l2": fn["l2"],
        "count": {"savoir": len(fn["savoir"]), "l2": len(fn["l2"])},
    }
    out["_stabilite_reformulees"] = {
        "n_questions": len(st["savoir"]),
        "savoir_pstdev_moyen": round(statistics.mean(st["savoir"]), 1) if st["savoir"] else 0,
        "savoir_pstdev_max": round(max(st["savoir"]), 1) if st["savoir"] else 0,
        "l2_pstdev_moyen": round(statistics.mean(st["l2"]), 1) if st["l2"] else 0,
        "l2_pstdev_max": round(max(st["l2"]), 1) if st["l2"] else 0,
    }
    return out


if __name__ == "__main__":
    import sys
    data = run()
    rows = data["rows"]
    print(f"ÉCHANTILLON : {len(rows)} copies (8 questions × {len(TYPE_ORDER)} catégories)\n")
    print(f"{'qid':9s} {'cat':15s} {'b':1s} {'sav':>4s} {'sav%':>4s} {'can':>3s} {'n':>2s} | {'l2':>4s} {'l2%':>4s}")
    print("-" * 78)
    for r in rows:
        print(f"{r['qid']:9s} {r['cat']:15s} {r['bareme']:1.0f} {int(r['savoir_score']):4d} "
              f"{str(r['savoir_%']):>4s} {str(bool(r['savoir_can_handle'])):>3s} "
              f"{str(r['savoir_n']):>2s} | {int(round(r['l2_score'])):4d} {str(r['l2_%']):>4s} r={r.get('l2_raw')}")

    print("\n=== RÉSUMÉ PAR CATÉGORIE (% moyen) ===")
    s = summarize(rows)
    for cat in TYPE_ORDER:
        d = s[cat]
        print(f"  {cat:15s} n={d['n']:2d}  savoir={d['savoir_%_moy']:5.1f}%  l2={d['l2_%_moy']:5.1f}%")

    print("\n=== FAUX POSITIFS (copie correcte notée < 60 %) ===")
    print(f"  savoir: {s['_faux_positifs']['count']['savoir']} -> {s['_faux_positifs']['savoir']}")
    print(f"  l2    : {s['_faux_positifs']['count']['l2']} -> {s['_faux_positifs']['l2']}")

    print("\n=== FAUX NÉGATIFS (copie fautive notée ≥ 60 %) ===")
    print(f"  savoir: {s['_faux_negatifs']['count']['savoir']} -> {s['_faux_negatifs']['savoir']}")
    print(f"  l2    : {s['_faux_negatifs']['count']['l2']} -> {s['_faux_negatifs']['l2']}")

    print("\n=== STABILITÉ (écart-type des % sur copies reformulées d'une même question) ===")
    print(f"  {s['_stabilite_reformulees']}")

    print("\n=== CONFORMITÉ AU BARÈME (nb copies dans la bande attendue) ===")
    for cat, d in s["_conformite_bareme"].items():
        print(f"  {cat:15s} attendu {d['attend'][0]}-{d['attend'][1]}%  savoir={d['savoir']}  l2={d['l2']}")
