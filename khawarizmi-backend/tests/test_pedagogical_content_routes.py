"""Garde-fous des corrections issues de l'audit pédagogique."""

import json
from pathlib import Path

import pytest

from routes.cours import COURSE_FILE, _clean_course_content, extract_section, remove_ascii_schemas


def test_code_blocks_keep_scientific_steps():
    content = """### مراحل\n```\n1. البدء\n2. الاستطالة\n3. الإنهاء\n════════════════════\n```\n"""
    cleaned = remove_ascii_schemas(content)
    assert "1. البدء" in cleaned
    assert "2. الاستطالة" in cleaned
    assert "3. الإنهاء" in cleaned
    assert "════════" not in cleaned


def test_unknown_section_never_returns_whole_course():
    content = "# الوحدة 1\n## قسم معروف\nمحتوى علمي طويل"
    assert extract_section(content, "chapitre-totalement-inconnu") == ""


def test_all_55_catalogue_chapters_resolve_to_specific_content():
    programme_path = Path(__file__).parents[1] / "data" / "programmes" / "svt_sciences_experimentales.json"
    programme = json.loads(programme_path.read_text(encoding="utf-8"))
    raw_course = COURSE_FILE.read_text(encoding="utf-8")
    resolved = []

    for domain in programme["domains"]:
        for unit in domain["units"]:
            for chapter in unit["chapters"]:
                content = _clean_course_content(
                    raw_course,
                    chapter["titre_fr"],
                    domain["numero"],
                    unit["numero"],
                )
                assert len(content) >= 100, (
                    domain["numero"], unit["numero"], chapter["numero"], chapter["titre_fr"]
                )
                resolved.append(chapter["titre_fr"])

    assert len(resolved) == 55


@pytest.mark.asyncio
async def test_unknown_course_is_404_not_full_corpus(client):
    response = await client.get(
        "/api/cours/chapitre-totalement-inconnu",
        params={"domain_num": 1, "unit_num": 1},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_transcription_keeps_three_steps(client):
    response = await client.get(
        "/api/cours/Transcription%20de%20l%27information%20genetique%20au%20niveau%20de%20l%27ADN",
        params={"domain_num": 1, "unit_num": 1},
    )
    assert response.status_code == 200
    content = response.json()["contenu"]
    assert "خطوات المرحلة" in content
    assert "الاستطالة" in content
    assert "الإنهاء" in content


@pytest.mark.asyncio
async def test_exercises_fallback_covers_energy_unit(client, auth_headers):
    response = await client.get(
        "/api/exercices/Reactions%20de%20la%20phase%20photochimique%20%28phase%20claire%29",
        params={"domain_num": 2, "unit_num": 1},
        headers=auth_headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["nb_exercices"] >= 3
    assert payload["nb_corrections"] >= 1
    assert "التمارين التطبيقية" in payload["contenu"]


@pytest.mark.asyncio
async def test_videos_have_seed_fallback_when_database_empty(client, auth_headers):
    response = await client.get("/api/videos/all", headers=auth_headers)
    assert response.status_code == 200
    videos = response.json()
    assert len(videos) == 10
    assert all(video.get("youtube_id") for video in videos)
