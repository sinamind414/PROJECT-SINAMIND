from methodology.verb_database import _normalize, identify_verb

SIMPLE_VERBS_NORM = [_normalize(v) for v in ["صف", "عرف", "استنتج", "أنجز رسما تخطيطيا", "عدد", "سم", "اذكر"]]
COMPLEX_VERBS_RAW = ["وضّح في نص علمي", "أثبت", "برّر", "فسر", "اقترح فرضية", "ناقش", "حلل", "قارن"]
COMPLEX_VERBS_NORM = [_normalize(v) for v in COMPLEX_VERBS_RAW]
COMPLEX_VERBS_MAP = dict(zip(COMPLEX_VERBS_NORM, COMPLEX_VERBS_RAW))


def classify_task(instruction: str) -> dict:
    found_verb = None
    verb_data = None

    verb_data = identify_verb(instruction)

    if verb_data:
        found_verb = verb_data["arabic"]
        task_type = verb_data["type"]
    else:
        norm_inst = _normalize(instruction)
        for nv, raw in COMPLEX_VERBS_MAP.items():
            if nv in norm_inst:
                found_verb = raw
                task_type = "complex"
                break
        if not found_verb:
            for nv in SIMPLE_VERBS_NORM:
                if nv in norm_inst:
                    task_type = "simple"
                    break
            else:
                task_type = "unknown"

    return {
        "verb": found_verb,
        "task_type": task_type,
        "is_complex": task_type == "complex",
        "is_simple": task_type == "simple",
    }
