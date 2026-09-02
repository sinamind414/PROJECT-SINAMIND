"""S40 — gate de branchement : une question n'a le droit à une grille QUE si c'est la même tâche.

Contexte (suite de l'audit surfaces 2026-08-30). Les 13 grilles git ne couvrent que
13 des 68 questions des scénarios `document-analysis` : les 11 scénarios de RUBRIQUES
(`*-v1`, ceux que ouvrent les pages `/document-analysis/chapters/...` et
`/diagnostic/chapters/...`, 55 questions) restent sur le mur `NoLocalGradeWall`.

Deux « raccourcis » ont été proposés puis écartés MESURE :
  * brancher `enzyme-temp-analyse` sur la question `analyse` d'`enzyme-activity-v1`
    -> cette question porte sur le **pH** (optimum 7), pas sur la chaleur (37 °م) ;
  * remplir `grade_question_id` du bac blanc avec `bac2023-s1-ex2-analyse-traduction`
    -> l'exercice seedé `s1-e2` est « تفسير الإشباع الضوئي » (saturation lumineuse),
    pas la traduction/ML901 du parasite.
Dans les deux cas l'élève aurait reçu une note FAUSSE (une copie juste marquée
« sans keypoint »), ce que le repo interdit plus gravement qu'une absence de note.

LA RÈGLE (implémentée ici) : pour toute question portant un `gradeQuestionId`, la
copie modèle QUE L'UI PROPOSE à l'élève (`modelAnswer` du scénario) doit être notée
**100 %** par la grille. C'est l'extension au niveau surface du gate G5 de
`scripts/validate_rubrics.py` (le `model_answer` de la grille >= 85 %) : si la tâche
diffère, la copie modèle de la question ne peut pas saturer la grille.

Ce test est donc un GARDE-FOU : il laisse passer un branchement futur correct (grille
authourée pour ce document) et fait rougir n'importe quel branchement approximatif.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "s40-test-secret-key-0123456789")

from services.local_grader import GRADER_VERSION, grade
from services.rubric_store import load

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT
FRONTEND = ROOT.parent / "khawarizmi-frontend"
DOCS_TS = FRONTEND / "src" / "lib" / "methodology-documents.ts"
INDEX = BACKEND / "data" / "rubrics" / "index.json"


def _scenario_blocks() -> list[tuple[str, str]]:
    """(id_scenario, corps) pour chaque `const X: MethodologyScenario = { ... }`."""
    src = DOCS_TS.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"(?:export )?const (\w+): MethodologyScenario = \{", src):
        i = src.index("{", m.start())
        depth, j = 0, i
        while True:
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = src[i : j + 1]
        sid = re.search(r'\n  id:\s*"([^"]+)"', body)
        out.append((sid.group(1) if sid else m.group(1), body))
    return out


def _field(block: str, name: str) -> str | None:
    m = re.search(rf'{name}:\s*\n?\s*"((?:[^"\\]|\\.)*)"', block)
    if m:
        return m.group(1)
    return None


def wired_pairs() -> list[dict]:
    """Les questions réellement branchées sur une grille, avec leur copie modèle."""
    pairs = []
    for sid, body in _scenario_blocks():
        # découpe question par question : objets au niveau 1 de `questions: [`
        qstart = body.find("questions: [")
        if qstart < 0:
            continue
        i = body.index("[", qstart)
        depth = 0
        k = i
        while k < len(body):
            c = body[k]
            if c == "{":
                depth += 1
                if depth == 1:
                    start = k
            elif c == "}":
                depth -= 1
                if depth == 0:
                    qb = body[start : k + 1]
                    gid = _field(qb, "gradeQuestionId")
                    if gid:
                        pairs.append(
                            {
                                "scenario": sid,
                                "question": _field(qb, "id") or "?",
                                "verb": _field(qb, "verbSlug") or "",
                                "grid": gid,
                                "model_answer": _field(qb, "modelAnswer") or "",
                                "doc_ref": _field(qb, "docRef") or "",
                            }
                        )
            elif c == "]" and depth == 0:
                break
            k += 1
    return pairs


class TestGateBranchement:
    def test_la_copie_modele_de_la_question_saturationne_sa_grille(self):
        """Règle centrale : la copie modèle MONTRÉE à l'élève doit obtenir 100 % sous sa grille.

        Les questions dont `modelAnswer` est vide sont hors périmètre (aucun exemple
        affiché -> rien à contrôler) ; elles sont listées dans le message d'échec pour
        qu'un branchement suspect reste lisible.
        """
        bad, skipped = [], []
        pairs = wired_pairs()
        assert len(pairs) == 13, f"13 branchements attendus, reçu {len(pairs)}"
        for p in pairs:
            packed = load(p["grid"])
            if packed is None:
                bad.append(f"{p['scenario']}/{p['question']}: grille {p['grid']} absente du store")
                continue
            if not p["model_answer"].strip():
                skipped.append(f"{p['scenario']}/{p['question']}")
                continue
            r = grade(student_answer=p["model_answer"], rubric=packed.rubric, document=packed.document)
            if not (r.method_percent == 100 and r.overall_training_percent == 100):
                bad.append(
                    f"{p['scenario']}/{p['question']} -> {p['grid']} : "
                    f"method={r.method_percent} overall={r.overall_training_percent} "
                    f"manquants={[c.id for c in r.criteria if c.status != 'full']} "
                    f"(l'exemple montré à l'élève n'est PAS la tâche de la grille)"
                )
        assert not bad, "\n".join(bad) + (f"\n(hors périmètre, modelAnswer vide : {skipped})" if skipped else "")

    def test_aucune_grille_indexee_sans_copie_modele(self):
        """Un squelette d'auteur ne doit jamais entrer dans index.json : sans model_answer,
        la grille noterait n'importe quelle copie."""
        idx = json.loads(INDEX.read_text(encoding="utf-8"))
        empty = []
        for qid, meta in idx.items():
            raw = json.loads((BACKEND / "data" / meta["rubric"]).read_text(encoding="utf-8"))
            if not (raw.get("model_answer") or "").strip():
                empty.append(qid)
        assert not empty, f"grilles sans model_answer dans l'index: {empty}"

    def test_branchements_injectifs(self):
        """Deux questions ne partagent pas la même grille : l'autre serait notée sur un
        document qui n'est pas le sien."""
        seen: dict[str, str] = {}
        dup = []
        for p in wired_pairs():
            if p["grid"] in seen:
                dup.append(f"{p['grid']} <- {seen[p['grid']]} ET {p['scenario']}/{p['question']}")
            seen.setdefault(p["grid"], f"{p['scenario']}/{p['question']}")
        assert not dup, "\n".join(dup)

    def test_version_moteur_etale(self):
        assert GRADER_VERSION == "1.2.0"

    def test_le_branchement_propose_pour_les_rubriques_est_bien_rejete(self):
        """Méta-test : la garde attrape l'erreur que nous avons failli commettre.

        `enzyme-activity-v1` question `analyse` porte sur le pH ; la grille
        `enzyme-temp-analyse` exige 37/100/80 et la conclusion « الحرارة المثلى 37 ».
        """
        scenarios = dict(_scenario_blocks())
        body = scenarios["enzyme-activity-v1"]
        qstart = body.find("questions: [")
        block = body[qstart : body.find("gradeQuestionId", qstart) if "gradeQuestionId" in body else len(body)]
        ph_model = _field(block, "modelAnswer") or ""
        assert "pH" in ph_model, "prérequis : la copie modèle de cette question parle bien du pH"
        packed = load("enzyme-temp-analyse")
        assert packed is not None
        r = grade(student_answer=ph_model, rubric=packed.rubric, document=packed.document)
        assert r.overall_training_percent < 100, (
            "la garde ne fait plus son travail : un branchement hors sujet passerait à 100 %"
        )


class TestPontBacBlanc:
    """Le pont `grade_question_id` (S39) ne doit être rempli que si c'est le même exercice.

    Preuve du piège : le sujet seed `bac-svt-2025` ex. `s1-e2` est « تفسير الإشباع الضوئي »
    (saturation lumineuse), alors que la seule grille « bac » du dépôt est
    `bac2023-s1-ex2-analyse-traduction` (traduction/ML901). Les brancher donnerait des
    notes fausses ; ce test le refuserait.
    """

    SEED = BACKEND / "scripts" / "bac_blanc_seed.json"

    def test_exercices_declares_correspondent_a_leur_grille(self):
        seed = json.loads(self.SEED.read_text(encoding="utf-8"))
        bad = []
        for subject in seed:
            for ex in subject.get("exercises", []):
                gid = (ex.get("grade_question_id") or "").strip()
                if not gid:
                    continue
                packed = load(gid)
                if packed is None:
                    bad.append(f"{subject['annale_slug']}/{ex['exercise_id']}: grille {gid} inconnue")
                    continue
                model = (ex.get("model_answer_ar") or "").strip()
                if not model:
                    bad.append(f"{subject['annale_slug']}/{ex['exercise_id']}: model_answer_ar vide")
                    continue
                r = grade(student_answer=model, rubric=packed.rubric, document=packed.document)
                if not (r.method_percent == 100 and r.overall_training_percent == 100):
                    bad.append(
                        f"{subject['annale_slug']}/{ex['exercise_id']} -> {gid}: "
                        f"overall={r.overall_training_percent} (exercice différent de la grille)"
                    )
        assert not bad, "\n".join(bad)

    def test_aucun_raccourci_sur_le_seed_actuel(self):
        """Le seed d'aujourd'hui ne déclare encore aucune grille : le bac blanc reste non noté."""
        seed = json.loads(self.SEED.read_text(encoding="utf-8"))
        declared = [e.get("grade_question_id") for s in seed for e in s["exercises"] if e.get("grade_question_id")]
        assert declared == [], (
            f"des grilles viennent d'être branchées sur le bac blanc ({declared}) : "
            "vérifier que l'exercice seedé EST bien la tâche de la grille (cf. test ci-dessus)"
        )
