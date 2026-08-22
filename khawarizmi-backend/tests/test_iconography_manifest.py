"""Garde-fous de publication et d'accessibilité des 35 figures SVT."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).parents[2]
MANIFEST_PATH = ROOT / "docs/audit-contenu/iconography-manifest.json"


def _png_size(path: Path) -> tuple[int, int]:
    payload = path.read_bytes()
    assert payload[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", payload[16:24])


def _manifest():
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_manifest_covers_35_unique_proposals_without_fake_validation():
    payload = _manifest()
    figures = payload["figures"]

    assert payload["metadata"]["count"] == 35
    assert payload["metadata"]["p1Count"] == 20
    assert payload["metadata"]["p2Count"] == 15
    assert payload["metadata"]["producedProposals"] == 35
    assert payload["metadata"]["humanValidated"] == 0
    assert payload["metadata"]["publicationReady"] == 0
    assert payload["metadata"]["labelOverlayComplete"] == 0
    assert len(figures) == 35
    assert len({figure["id"] for figure in figures}) == 35
    assert sum(figure["tier"] == "P1" for figure in figures) == 20
    assert sum(figure["tier"] == "P2" for figure in figures) == 15

    for figure in figures:
        assert figure["publicationStatus"] == "blocked_pending_teacher_review"
        assert figure["labelOverlayStatus"] == "pending_vector_overlay"
        assert figure["humanReview"]["status"] == "required"
        assert figure["humanReview"]["reviewer"] is None
        assert figure["humanReview"]["decision"] is None
        assert figure["humanReview"]["scientificAccuracy"] is False
        assert figure["humanReview"]["bilingualLabelsApplied"] is False


def test_every_figure_has_real_file_hash_bilingual_labels_and_alt_text():
    for figure in _manifest()["figures"]:
        path = ROOT / figure["file"]
        assert path.is_file(), figure["id"]
        assert path.as_posix().startswith((ROOT / "docs").as_posix())
        assert hashlib.sha256(path.read_bytes()).hexdigest() == figure["sha256"]
        width, height = _png_size(path)
        assert (width, height) == (figure["width"], figure["height"])
        assert width >= 768 and height >= 700
        assert len(figure["labelsAr"]) >= 4
        assert len(figure["labelsFr"]) >= 4
        assert len(figure["altAr"]) > 60
        assert len(figure["altFr"]) > 60
        assert figure["accessibility"]["bilingualTextAlternativePresent"] is True
        assert figure["accessibility"]["visualContrast"] == "requires_human_check"


def test_only_energy_pyramid_is_flagged_as_enrichment():
    enriched = [figure["id"] for figure in _manifest()["figures"] if figure["isEnrichment"]]
    assert enriched == ["u8-fig3"]


def test_no_proposal_is_exposed_in_frontend_public_assets():
    public_assets = ROOT / "khawarizmi-frontend/public"
    names = {path.name for path in public_assets.rglob("*") if path.is_file()}
    for figure in _manifest()["figures"]:
        assert Path(figure["file"]).name not in names
