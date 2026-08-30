"""services/local_grader.py — SEUL moteur de note (0 LLM, déterministe).

Pipeline : sanity → normalize → structure → document → method →
science veto → stuffing → diagnosis.

N'importe ni n'appelle aucun client génératif.
"""

from __future__ import annotations

import re
from functools import lru_cache

from schemas.document_model import DocumentModel
from schemas.rubric import (
    Criterion,
    CriterionHit,
    Diagnosis,
    GradeResult,
    Rubric,
)
from services.answer_sanity import check_answer_sanity
from services.arabic import normalize_arabic

GRADER_VERSION = "1.1.9"
SCIENCE_CAP_DEFAULT = 40
TRAINING_BANNER_AR = "ملاحظة تدريبية — منهج + محتوى. ليست علامة بكالوريا رسمية."

_NUM_RE = re.compile(r"\d+(?:[.,]\d+)?")
_CHEM_TOKEN_RE = re.compile(
    r"(?:atp|adp|nadh|fadh2?|co2|o2|h2o|p/o|ph|ca2\+?|na\+|k\+|°|→|->)",
    re.IGNORECASE,
)
_USEFUL_RE = re.compile(
    r"[\u0600-\u06FF0-9A-Za-z°+\-→/]|ATP|CO2|O2",
    re.IGNORECASE,
)

# N8 chiffres orientaux — filet science seulement (S27). Pas une fusion normalize.
_INDIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
_HAS_38_ATP = re.compile(r"38\s+atp", re.IGNORECASE)

_ATP_38_WINDOW = 90  # ~ _near(savoir) ; «ليس 36 بل 38» est adjacent (S31)


def _has_38_near(sav: str, pos: int) -> bool:
    """Vrai si un «38 atp» est à ≤ _ATP_38_WINDOW chars du 36/32 (S31).

    Loin du 36, le 38 ne lave plus la faute : «36 affirmé + 38 ailleurs»
    redevient une erreur grave (cap 40).
    """
    return any(
        abs(m.start() - pos) <= _ATP_38_WINDOW for m in _HAS_38_ATP.finditer(sav)
    )


_CAUSE_MARKERS = ("لان", "بسبب", "يفسر", "تفسير", "هذا يدل", "راجع")
_ANALYSE_SLIP = ("لان", "بسبب", "يفسر", "تفسير", "هذا يدل")
_KULLAMA = "كلما"

# S32 — marqueurs de structure pour l'exemption stuffing ancrée. Liste fermée,
# même philosophie que _CAUSE_MARKERS / _ANALYSE_SLip : pas de parsing.
_STRUCTURE_MARKERS = (
    "لان",
    "بسبب",
    "لذلك",
    "نستنتج",
    "نلاحظ",
    "كلما",
    "يرجع",
    "راجع",
    "مما",
    "بالتالي",
)

# Graves photosynthèse (faux positifs hors ce thème) — messages Savoir.
_PS_GRAVE_HINTS = ("التركيب الضوئي", "صانعات", "chloroplaste")
_PS_CONTEXT = (
    "تركيب ضوي",
    "التركيب الضوي",
    "photosynth",
    "chloroplaste",
    "يخضور",
    "كلوروفيل",
    "صانعه",
    "صانعات",
)


class UngradedError(Exception):
    """Pas de Rubric pour cette question — honnête, pas de fallback."""

    def __init__(self, question_id: str) -> None:
        self.question_id = question_id
        super().__init__(f"ungraded:{question_id}")


def _round_pts(x: float) -> float:
    return round(x + 1e-12, 4)


def _extract_numbers(text: str) -> list[tuple[float, int]]:
    """[(valeur, index)] — virgule ou point décimal."""
    out: list[tuple[float, int]] = []
    for m in _NUM_RE.finditer(text):
        raw = m.group().replace(",", ".")
        try:
            out.append((float(raw), m.start()))
        except ValueError:
            continue
    return out


def _expand_variants(variants: list[str]) -> list[str]:
    """$lex:id → lexique git (S5) puis Savoir ; sinon littéral. Puis normalize."""
    from services.lexicon import synonyms as lex_synonyms

    raw: list[str] = []
    for v in variants:
        if v.startswith("$lex:"):
            key = v[5:].strip()
            raw.extend(lex_synonyms(key))
        else:
            raw.append(v)
    seen: set[str] = set()
    out: list[str] = []
    for item in raw:
        n = normalize_arabic(item)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


_WORD_BOUND = r"[a-z0-9\u0600-\u06ff]"
# Liste FERMÉE — pas de stemming. تقبل «فكلما» / «النمو» / «كالخميرة».
# كال = ك+ال (comme فال/بال/وال). Sans ça, خميرة ⊄ كالخميرة (ك already, ال already, pas le composé).
_PROCLITICS = ("وال", "فال", "بال", "لل", "كال", "ال", "و", "ف", "ب", "ك", "ل")
# S30 — enclitiques suffixaux COLLÉS (pronoms) : لأنها = لأن + ها،
# ولاننا = و + لأن + نا. Symétrique de _PROCLITICS : liste fermée, testée.
# Pas «ات» (pluriel ≠ pronom), pas de stemming.
_ENCLITICS = ("ها", "هم", "هن", "هما", "كم", "نا", "ه", "ك", "ي")


@lru_cache(maxsize=1024)
def _needle_res(needle: str) -> tuple[re.Pattern[str], ...]:
    """1–2 regex du needle : proclitique optionnel + base + enclitique optionnel.

    Même sémantique que l'ancienne énumération de formes (frontières de mot,
    proclitiques fermés, radical sans ال en 2ᵉ pattern) — et les combos
    proclitique×enclitique (ولأنها) matchent sans énumérer le produit cartésien.
    Enclitiques refusés sur needle < 3 chars (garde anti-collision).
    """
    pro = "(?:" + "|".join(re.escape(p) for p in _PROCLITICS) + ")?"
    enc = (
        "(?:" + "|".join(re.escape(e) for e in _ENCLITICS) + ")?"
        if len(needle) >= 3
        else ""
    )
    head = rf"(?<!{_WORD_BOUND})"
    tail = rf"(?!{_WORD_BOUND})"
    pats = [re.compile(head + pro + re.escape(needle) + enc + tail)]
    if needle.startswith("ال") and len(needle) > 3:
        # radical sans ال : frontières + enclitiques, sans proclitique
        pats.append(re.compile(head + re.escape(needle[2:]) + enc + tail))
    return tuple(pats)


def _hit_pos(text: str, needle: str) -> int | None:
    """Position du 1er match.

    Unigramme → frontières de mot (évite لان ⊂ الانزيم / لانطلاق)
    + proclitiques/enclitiques fermés (فكلما، النمو، كالخميرة، لأنها).
    Locution (espace) → sous-chaîne.
    """
    if not needle:
        return None
    if " " in needle.strip():
        idx = text.find(needle)
        return idx if idx >= 0 else None
    best: int | None = None
    for pat in _needle_res(needle):
        m = pat.search(text)
        if m is None:
            continue
        if best is None or m.start() < best:
            best = m.start()
    return best


def _first_pos(text: str, variants_norm: list[str]) -> int | None:
    best: int | None = None
    for v in variants_norm:
        p = _hit_pos(text, v)
        if p is None:
            continue
        if best is None or p < best:
            best = p
    return best


def _count_hits(text: str, variants_norm: list[str]) -> int:
    n = 0
    for v in variants_norm:
        if _hit_pos(text, v) is not None:
            n += 1
    return n


def _occurrence_count(text: str, variants_norm: list[str]) -> int:
    """Compte les occurrences avec les MÊMES règles que _hit_pos (frontières + proclitiques)."""
    total = 0
    for v in variants_norm:
        if not v:
            continue
        if " " in v.strip():
            start = 0
            while True:
                i = text.find(v, start)
                if i < 0:
                    break
                total += 1
                start = i + max(1, len(v))
            continue
        best = 0
        for pat in _needle_res(v):
            best = max(best, len(pat.findall(text)))
        total += best
    return total


def _chemistry_signal_count(text: str) -> int:
    """Tokens chimie FERMÉS. Digits seuls ≠ chimie (sinon dump numérique → defer)."""
    return len(_CHEM_TOKEN_RE.findall(text))


def _useful_len(text: str) -> int:
    return len(_USEFUL_RE.findall(text.replace(" ", "")))


def _sanity_fork(answer: str, verb_slug: str) -> tuple[str, bool]:
    """Retourne (sanity_code, stop).

    stop=True → method=0. defer → on continue (pas de cache).
    """
    if not answer or not answer.strip():
        return "empty", True

    valid, code, _ = check_answer_sanity(answer)
    if valid:
        return "ok", False

    if code == "empty":
        return code, True

    if code == "too_short":
        if verb_slug in ("cite", "define") and _useful_len(answer) >= 3:
            return "ok", False
        return "too_short", True

    if code in ("not_arabic", "gibberish"):
        if _chemistry_signal_count(answer) >= 2:
            return "defer", False
        return code, True

    if code == "repeated_chars":
        return code, True

    return code, True


def _keypoint_hits(
    text: str, document: DocumentModel | None
) -> tuple[bool, int | None]:
    if document is None or not document.keypoints:
        return False, None
    nums = _extract_numbers(text)
    best_pos: int | None = None
    found = False
    for val, pos in nums:
        for kp in document.keypoints:
            if abs(val - kp.value) <= kp.tolerance + 1e-9:
                found = True
                if best_pos is None or pos < best_pos:
                    best_pos = pos
                break
    return found, best_pos


def _object_hits(
    text: str, document: DocumentModel | None
) -> tuple[bool, int | None]:
    if document is None:
        return False, None
    variants = _expand_variants(document.objects)
    pos = _first_pos(text, variants)
    return pos is not None, pos


def _trend_hits(
    text: str, document: DocumentModel | None
) -> tuple[bool, int | None]:
    if document is None:
        return False, None
    variants = _expand_variants(document.trend_variants)
    pos = _first_pos(text, variants)
    return pos is not None, pos


def _tokens(text: str) -> list[str]:
    return [t for t in re.split(r"\s+", text) if t]


def _cooccurrence(text: str, variants_norm: list[str], window: int | None) -> bool:
    if not variants_norm:
        return False
    toks = _tokens(text)
    if not toks:
        return False
    win = window if window is not None else max(8, len(toks))
    positions: list[list[int]] = []
    for v in variants_norm:
        found = [i for i, tok in enumerate(toks) if v in tok or tok in v]
        if not found:
            # fallback : le variant peut être multi-mots
            pos = _hit_pos(text, v)
            if pos is None:
                return False
            # approx token index
            found = [max(0, text[:pos].count(" "))]
        positions.append(found)
    # existe-t-il un intervalle de `win` tokens couvrant ≥1 pos par variant ?
    for i, tok in enumerate(toks):
        j = min(len(toks) - 1, i + win)
        ok = True
        for plist in positions:
            if not any(i <= p <= j for p in plist):
                ok = False
                break
        if ok:
            return True
    return False


def _eval_criterion(
    crit: Criterion,
    text: str,
    document: DocumentModel | None,
) -> CriterionHit:
    variants = _expand_variants(crit.variants)
    status = "absent"
    earned = 0.0

    if crit.check == "any_of":
        if _first_pos(text, variants) is not None:
            status = "full"
            earned = crit.points
    elif crit.check == "all_of":
        n = _count_hits(text, variants)
        if variants and n == len(variants):
            status = "full"
            earned = crit.points
        elif n >= 1:
            status = "partial"
            earned = _round_pts(crit.points * n / len(variants))
    elif crit.check == "forbidden_abs":
        if _first_pos(text, variants) is None:
            status = "full"
            earned = crit.points
        else:
            status = "absent"
            earned = 0.0
    elif crit.check == "cites_keypoint":
        ok, _ = _keypoint_hits(text, document)
        if ok:
            status = "full"
            earned = crit.points
    elif crit.check == "cites_object":
        ok, _ = _object_hits(text, document)
        if ok:
            status = "full"
            earned = crit.points
    elif crit.check == "cites_trend":
        ok, _ = _trend_hits(text, document)
        if ok:
            status = "full"
            earned = crit.points
    elif crit.check == "number_present":
        if _extract_numbers(text):
            status = "full"
            earned = crit.points
    elif crit.check == "min_length":
        need = crit.min_chars or 0
        if len(text.replace(" ", "")) >= need:
            status = "full"
            earned = crit.points
    elif crit.check == "section_markers":
        if _first_pos(text, variants) is not None:
            status = "full"
            earned = crit.points
    elif crit.check == "cooccurrence":
        if _cooccurrence(text, variants, crit.window_tokens):
            status = "full"
            earned = crit.points

    return CriterionHit(
        id=crit.id,
        status=status,  # type: ignore[arg-type]
        points_earned=_round_pts(earned),
        points_max=crit.points,
        label_ar=crit.label_ar,
    )


def _criterion_pos(
    crit: Criterion, text: str, document: DocumentModel | None
) -> int | None:
    variants = _expand_variants(crit.variants)
    if crit.check == "cites_keypoint":
        _, pos = _keypoint_hits(text, document)
        return pos
    if crit.check == "cites_object":
        _, pos = _object_hits(text, document)
        return pos
    if crit.check == "cites_trend":
        _, pos = _trend_hits(text, document)
        return pos
    if crit.check == "forbidden_abs":
        return None
    return _first_pos(text, variants)


def _order_ok(
    rubric: Rubric, hits: list[CriterionHit], text: str, document: DocumentModel | None
) -> bool | None:
    graph = rubric.method_graph
    if graph is None or not graph.require_order:
        return None
    by_id = {c.id: c for c in rubric.criteria}
    hit_map = {h.id: h for h in hits}
    # Désordre seulement si TOUTES les steps sont présentes (full).
    if any(hit_map.get(sid) is None or hit_map[sid].status != "full" for sid in graph.steps):
        return True
    positions: list[int] = []
    for sid in graph.steps:
        pos = _criterion_pos(by_id[sid], text, document)
        if pos is None:
            return True
        positions.append(pos)
    return all(positions[i] <= positions[i + 1] for i in range(len(positions) - 1))


def _label_ar(
    percent: int,
    order_ok: bool | None,
    required_missing: bool,
    stuffing: bool = False,
) -> str:
    if percent <= 39:
        base = "غير كاف"
    elif percent <= 69:
        base = "جزئي"
    elif percent <= 84:
        base = "مقبول"
    else:
        base = "متقن"
    if base == "متقن" and (order_ok is False or required_missing or stuffing):
        return "مقبول"
    return base


def _science_veto(
    student_raw: str,
    text_norm: str,
    rubric: Rubric,
) -> tuple[str, list[str], int]:
    """science_status, flags, cap. Ignore le score lexique Savoir.

    Errata manuel (10⁶ ARNr/ARNt) → flags jaunes, status reste ok, pas de cap.
    """
    from services.savoir_corrector import (
        _GRAVE_ERRORS,
        _NUMERIC_RULES,
        _normalize,
        detect_textbook_errata,
    )

    hard: list[str] = []
    warn: list[str] = []
    cap = SCIENCE_CAP_DEFAULT
    sav = _normalize((student_raw or "").translate(_INDIC_DIGITS))

    # Hors-sujet
    theme = _expand_variants(rubric.theme_variants)
    theme_hits = _count_hits(text_norm, theme)
    if rubric.theme_min_hits > 0 and theme_hits < rubric.theme_min_hits:
        hard.append("خارج الموضوع")
        return "error", hard, cap

    ps_ctx = any(_hit_pos(sav, normalize_arabic(p)) is not None or p in sav for p in _PS_CONTEXT)

    for pattern, msg_ar, _pen in _GRAVE_ERRORS:
        if any(h in msg_ar for h in _PS_GRAVE_HINTS) and not ps_ctx:
            continue
        m = re.search(pattern, sav, re.IGNORECASE)
        if m is None:
            continue
        # 38 ATP À CÔTÉ du 36/32 → l'élève a corrigé (ليس 36 بل 38).
        # Pas un parseur de نفي, mais fenêtre fermée (S31) : loin du 36,
        # le 38 n'annule plus la faute.
        if re.search(r"36\\s|32\\s", pattern) and _has_38_near(sav, m.start()):
            continue
        hard.append(msg_ar)
        break

    for grave in rubric.grave:
        if grave.context_any:
            ctx = _expand_variants(grave.context_any)
            if _first_pos(text_norm, ctx) is None and _first_pos(sav, ctx) is None:
                continue
        if grave.pattern and re.search(grave.pattern, sav, re.IGNORECASE):
            hard.append(grave.message_ar or grave.id or "خطأ علمي")
            cap = min(cap, grave.cap_science)

    for rule_id, rule in _NUMERIC_RULES.items():
        if not any(re.search(p, sav, re.IGNORECASE) for p in rule["patterns"]):
            continue
        expected = rule["expected"]
        for pat in rule["patterns"]:
            m = re.search(rf"({pat}).{{0,30}}?(\d+)", sav, re.IGNORECASE)
            if not m:
                continue
            try:
                val = int(m.group(2))
            except ValueError:
                break
            if val != expected:
                hard.append(
                    f"قيمة {rule_id} الصحيحة هي {expected} وليس {val}"
                )
            break

    warn.extend(detect_textbook_errata(student_raw))
    flags = hard + warn
    if hard:
        return "error", flags, cap
    return "ok", flags, cap


def _stuffing(
    text: str,
    rubric: Rubric,
    hits: list[CriterionHit],
    document: DocumentModel | None,
) -> bool:
    toks = _tokens(text)
    if len(toks) < 20:
        return False

    distractor_vars: list[str] = []
    for d in rubric.distractors:
        distractor_vars.extend(_expand_variants(d.variants))
    if distractor_vars and _first_pos(text, distractor_vars) is not None:
        return True

    theme = _expand_variants(rubric.theme_variants)
    crit_vars: list[str] = []
    for c in rubric.criteria:
        if c.check == "forbidden_abs":
            continue
        crit_vars.extend(_expand_variants(c.variants))
    occ = _occurrence_count(text, theme) + _occurrence_count(text, crit_vars)
    ratio = occ / max(1, len(toks))
    kp_full = any(
        h.status == "full"
        for h, c in zip(hits, rubric.criteria)
        if c.check == "cites_keypoint"
    )
    obj_full = any(
        h.status == "full"
        for h, c in zip(hits, rubric.criteria)
        if c.check == "cites_object"
    )
    if kp_full or obj_full:
        # S32 — l'ancre (chiffre/objet du doc) n'exempte plus aveuglément :
        # il faut AUSSI un marqueur de structure (liste fermée). Un bourrage
        # + le chiffre magique du doc reste détecté ; une vraie copie courte
        # (enzyme-temp-interpret : ratio 1.0 mais «لأن») reste exempte.
        if any(_hit_pos(text, m) is not None for m in _STRUCTURE_MARKERS):
            return False
        # sans marqueur → on retombe sur le ratio (pas d'exemption)
    return ratio > 0.60


def _verb_slip(verb: str, text: str) -> str | None:
    if verb == "analyse":
        if any(_hit_pos(text, m) is not None for m in _ANALYSE_SLIP):
            return "verb_slip.interpret"
    if verb == "interpret":
        has_k = _hit_pos(text, _KULLAMA) is not None
        has_cause = any(_hit_pos(text, m) is not None for m in _CAUSE_MARKERS)
        if has_k and not has_cause:
            return "verb_slip.analyse"
    return None


def _diagnosis(
    *,
    sanity_code: str,
    science_status: str,
    science_flags: list[str],
    slip: str | None,
    stuffing: bool,
    hits: list[CriterionHit],
    rubric: Rubric,
    unanchored: bool,
) -> Diagnosis:
    if sanity_code not in ("ok", "defer"):
        return Diagnosis(code=f"sanity.{sanity_code}", label_ar="إجابة غير صالحة")
    if science_status == "error" and any("خارج" in f for f in science_flags):
        return Diagnosis(code="off_topic", label_ar="الإجابة خارج الموضوع")
    if science_status == "error":
        return Diagnosis(code="science.grave", label_ar="خطأ علمي")
    if slip:
        label = (
            "حلّلت لكن فسّرت مبكراً (لأن)"
            if slip.endswith("interpret")
            else "فسّرت بأسلوب حلّل (كلما دون سبب)"
        )
        return Diagnosis(code=slip, label_ar=label)
    if unanchored:
        return Diagnosis(code="unanchored", label_ar="لا رقم من الوثيقة")
    if stuffing:
        return Diagnosis(code="stuffing", label_ar="حشو معجمي")
    for h, c in zip(hits, rubric.criteria):
        if c.required and h.status != "full":
            return Diagnosis(code=f"first_required_gap.{c.id}", label_ar=c.label_ar)
    if any("تصويب الدليل" in f for f in science_flags):
        return Diagnosis(
            code="science.erratum",
            label_ar="غلطة الكتاب (10⁶) — الدليل: 10⁴",
        )
    return Diagnosis(code="all_correct", label_ar="إجابة مكتملة")


def _stopped_result(
    rubric: Rubric, sanity_code: str, message: str
) -> GradeResult:
    hits = [
        CriterionHit(
            id=c.id,
            status="absent",
            points_earned=0.0,
            points_max=c.points,
            label_ar=c.label_ar,
        )
        for c in rubric.criteria
    ]
    diag = Diagnosis(code=f"sanity.{sanity_code}", label_ar=message)
    return GradeResult(
        grader_version=GRADER_VERSION,
        rubric_id=rubric.rubric_id,
        rubric_version=rubric.version,
        verb_slug=rubric.verb_slug,
        method_points=0.0,
        method_points_max=rubric.total_points,
        method_percent=0,
        method_label_ar="غير كاف",
        order_ok=None,
        science_status="not_applicable",
        science_flags=[],
        science_capped=False,
        sanity_code=sanity_code,
        stuffing_suspected=False,
        diagnosis=diag,
        praise_ar="",
        next_step_ar=message,
        phrase_ar=message,
        criteria=hits,
        overall_training_percent=0,
        cacheable=False,
        caps_applied=[],
    )


def grade(
    *,
    student_answer: str,
    rubric: Rubric,
    document: DocumentModel | None = None,
) -> GradeResult:
    """Pur, sync, 0 I/O, 0 LLM. Testable sans FastAPI."""
    raw = student_answer if isinstance(student_answer, str) else ""

    if rubric.verb_slug == "schematiser":
        msg = "لا يمكن تصحيح الرسم آلياً. قارن مع النموذج."
        r = _stopped_result(rubric, "ok", msg)
        r.science_status = "not_applicable"
        r.diagnosis = Diagnosis(code="schematiser_manual", label_ar=msg)
        r.cacheable = False
        return r

    sanity_code, stop = _sanity_fork(raw, rubric.verb_slug)
    if stop:
        msg = {
            "empty": "الإجابة فارغة. اكتب إجابتك ثم أرسلها.",
            "too_short": "إجابتك قصيرة جداً. حاول كتابة جملة كاملة على الأقل.",
            "not_arabic": "يجب أن تكتب إجابتك باللغة العربية.",
            "gibberish": "إجابتك غير مفهومة. أعد كتابة إجابتك بشكل واضح ومنظم.",
            "repeated_chars": "إجابتك تحتوي على أحرف مكررة بشكل غير طبيعي.",
        }.get(sanity_code, "إجابة غير صالحة.")
        return _stopped_result(rubric, sanity_code, msg)

    text = normalize_arabic(raw)

    hits = [_eval_criterion(c, text, document) for c in rubric.criteria]
    method_points = _round_pts(sum(h.points_earned for h in hits))
    max_pts = rubric.total_points or 1.0
    method_percent = int(round(100.0 * method_points / max_pts))
    method_percent = max(0, min(100, method_percent))

    order = _order_ok(rubric, hits, text, document)
    required_missing = any(
        c.required and h.status != "full" for c, h in zip(rubric.criteria, hits)
    )

    science_status, science_flags, cap = _science_veto(raw, text, rubric)

    stuffing = _stuffing(text, rubric, hits, document)
    caps_applied: list[str] = []
    overall = method_percent
    if stuffing:
        overall = min(overall, 50)
        caps_applied.append("stuffing")
    if science_status == "error":
        overall = min(overall, cap)
        caps_applied.append("science")
        capped = True
    else:
        capped = False

    label = _label_ar(method_percent, order, required_missing, stuffing)

    slip = _verb_slip(rubric.verb_slug, text)
    unanchored = False
    if rubric.document_id:
        kp_crits = [
            (h, c)
            for h, c in zip(hits, rubric.criteria)
            if c.check == "cites_keypoint"
        ]
        if kp_crits and all(h.status != "full" for h, _ in kp_crits):
            unanchored = True

    diag = _diagnosis(
        sanity_code=sanity_code,
        science_status=science_status,
        science_flags=science_flags,
        slip=slip,
        stuffing=stuffing,
        hits=hits,
        rubric=rubric,
        unanchored=unanchored,
    )

    praise_bits: list[str] = []
    for h in hits:
        if h.status == "full" and h.id in rubric.advice_praise:
            praise_bits.append(rubric.advice_praise[h.id])
    praise_ar = " ".join(praise_bits[:2])

    next_step = rubric.advice_by_gap.get(diag.code) or rubric.advice_by_gap.get(
        diag.code.split(".", 1)[-1], ""
    )
    if not next_step and diag.code.startswith("first_required_gap."):
        cid = diag.code.split(".", 1)[-1]
        next_step = rubric.advice_by_gap.get(cid, "")
    if science_flags and diag.code == "science.grave":
        next_step = science_flags[0] + ((" " + next_step) if next_step else "")
    if diag.code == "off_topic" and not next_step:
        next_step = "الإجابة خارج الموضوع"
    if diag.code == "science.erratum" and science_flags:
        next_step = science_flags[0]
    elif any("تصويب الدليل" in f for f in science_flags):
        # ne pas masquer le jaune 10⁴ derrière un autre diagnostic
        extra = next((f for f in science_flags if "تصويب الدليل" in f), "")
        if extra and extra not in next_step:
            next_step = (next_step + " " + extra).strip()

    phrase_parts = [p for p in (praise_ar, next_step) if p]
    phrase_ar = " ".join(phrase_parts[:2])

    cacheable = sanity_code == "ok"

    return GradeResult(
        grader_version=GRADER_VERSION,
        rubric_id=rubric.rubric_id,
        rubric_version=rubric.version,
        verb_slug=rubric.verb_slug,
        method_points=method_points,
        method_points_max=max_pts,
        method_percent=method_percent,
        method_label_ar=label,
        order_ok=order,
        science_status=science_status,  # type: ignore[arg-type]
        science_flags=science_flags,
        science_capped=capped,
        sanity_code=sanity_code,
        stuffing_suspected=stuffing,
        diagnosis=diag,
        praise_ar=praise_ar,
        next_step_ar=next_step,
        phrase_ar=phrase_ar,
        criteria=hits,
        overall_training_percent=int(overall),
        cacheable=cacheable,
        caps_applied=caps_applied,
    )


def grade_question(question_id: str, student_answer: str) -> GradeResult:
    """Charge la Rubric + Document puis note. Sans Rubric → UngradedError."""
    from services.rubric_store import load

    packed = load(question_id)
    if packed is None:
        raise UngradedError(question_id)
    return grade(
        student_answer=student_answer,
        rubric=packed.rubric,
        document=packed.document,
    )
