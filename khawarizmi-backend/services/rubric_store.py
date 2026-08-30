"""services/rubric_store.py — Charge les grilles git (0 SQL v1)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from schemas.document_model import DocumentModel
from schemas.rubric import Rubric, RubricIntegrityError

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_DATA_DIR = _BACKEND_DIR / "data"
_INDEX_PATH = _DATA_DIR / "rubrics" / "index.json"
_MIXINS_DIR = _DATA_DIR / "rubrics" / "mixins"

_index_cache: dict | None = None
_rubric_cache: dict[str, "PackedRubric"] = {}


@dataclass(frozen=True)
class PackedRubric:
    rubric: Rubric
    document: DocumentModel | None
    rubric_path: str
    document_path: str | None


class RubricStoreError(RuntimeError):
    pass


def data_dir() -> Path:
    return _DATA_DIR


def _load_index() -> dict:
    global _index_cache
    if _index_cache is not None:
        return _index_cache
    if not _INDEX_PATH.is_file():
        _index_cache = {}
        return _index_cache
    raw = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RubricStoreError("index.json must be an object")
    _index_cache = raw
    return _index_cache


def reset_caches() -> None:
    global _index_cache
    _index_cache = None
    _rubric_cache.clear()
    try:
        from services.lexicon import reset_lexicon_cache

        reset_lexicon_cache()
    except Exception:
        pass


def _dedup_str(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _merge_mixin(payload: dict) -> dict:
    """Union theme/distractors/grave depuis mixins/{chapter_slug}.json.

    N'écrase pas les criteria / points. `numeric` du mixin (تصويب 10⁴)
    n'est PAS converti en grave — déjà dans detect_textbook_errata.
    """
    chapter = payload.get("chapter_slug")
    if not chapter or not isinstance(chapter, str):
        return payload
    path = _MIXINS_DIR / f"{chapter}.json"
    if not path.is_file():
        return payload
    mixin = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(mixin, dict):
        raise RubricStoreError(f"mixin invalide: {path}")
    payload = dict(payload)
    payload["theme_variants"] = _dedup_str(
        list(payload.get("theme_variants") or []) + list(mixin.get("theme_variants") or [])
    )
    payload["distractors"] = list(payload.get("distractors") or []) + list(
        mixin.get("distractors") or []
    )
    payload["grave"] = list(payload.get("grave") or []) + list(mixin.get("grave") or [])
    return payload


def list_question_ids() -> list[str]:
    idx = _load_index()
    return sorted(idx.keys())


def load(question_id: str) -> PackedRubric | None:
    if question_id in _rubric_cache:
        return _rubric_cache[question_id]
    idx = _load_index()
    entry = idx.get(question_id)
    if entry is None:
        return None
    if isinstance(entry, str):
        rubric_rel = entry
        document_rel = None
    elif isinstance(entry, dict):
        rubric_rel = entry.get("rubric")
        document_rel = entry.get("document")
    else:
        raise RubricStoreError(f"index entry invalide: {question_id}")
    if not rubric_rel:
        return None
    rubric_path = _DATA_DIR / rubric_rel
    if not rubric_path.is_file():
        raise RubricStoreError(f"rubric manquante: {rubric_path}")
    payload = json.loads(rubric_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RubricStoreError(f"rubric invalide: {rubric_path}")
    payload = _merge_mixin(payload)
    try:
        rubric = Rubric.model_validate(payload)
    except RubricIntegrityError:
        raise
    document = None
    doc_path_s = None
    if document_rel:
        doc_path = _DATA_DIR / document_rel
        if not doc_path.is_file():
            raise RubricStoreError(f"document manquant: {doc_path}")
        document = DocumentModel.model_validate(
            json.loads(doc_path.read_text(encoding="utf-8"))
        )
        doc_path_s = document_rel
        if rubric.document_id and rubric.document_id != document.doc_id:
            raise RubricStoreError(
                f"{question_id}: document_id={rubric.document_id} "
                f"!= doc_id={document.doc_id}"
            )
    packed = PackedRubric(
        rubric=rubric,
        document=document,
        rubric_path=rubric_rel,
        document_path=doc_path_s,
    )
    _rubric_cache[question_id] = packed
    return packed
