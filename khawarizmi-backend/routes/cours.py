import json
import logging
import re
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from deps import get_current_user

logger = logging.getLogger("khawarizmi.api")
router = APIRouter(prefix="/api/cours", tags=["Cours"])

MAPPING_PATH = Path(__file__).resolve().parent.parent / "data" / "chapter_mapping.json"
with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    CHAPTER_MAPPING = json.load(f)

# Source de vérité du cours (markdown canonique de 10 000 lignes).
# La table rag_chunks est censée le contenir, mais l'ingest
# (scripts/ingest_claude_opus.py) insère sous le nom
# 'programme_national_svt_claude_opus.md'. On lit le fichier directement
# en fallback quand la DB est vide — extract_section() fonctionnant sur
# headers markdown, le résultat est identique au RAG pour un cours structuré.
COURSE_FILE = Path(__file__).resolve().parent.parent / "data" / "courses" / "programme_national_svt_claude_opus.md"
COURSE_SOURCE = "programme_national_svt_claude_opus.md"


def score_match(chapitre: str, keywords: list[str]) -> int:
    c = chapitre.lower()
    return sum(1 for k in keywords if k.lower() in c)


def clean_ascii_tables(content: str) -> str:
    lines = content.split("\n")
    decorative_pattern = re.compile(
        r"^\s*[╔╗╚╝═║╠╣╦╩╬─│┌┐└┘├┤┬┴┼╞╡╪╫╤╧╨╥╙╘╒╓╫╪▐▌▀▄█▓▒░]+\s*$"
    )
    cleaned = [line for line in lines if not decorative_pattern.match(line)]
    return "\n".join(cleaned)


def convert_ascii_table_to_markdown(content: str) -> str:
    lines = content.split("\n")
    result = []
    in_table = False
    table_buffer = []
    header_separator_pattern = re.compile(
        r"^\|[\s═─║╞╪╫╬]+\|$"
    )

    def flush_table():
        if len(table_buffer) >= 1:
            header = table_buffer[0]
            nb_cols = header.count("|") - 1
            if nb_cols > 0:
                sep = "|" + "|".join(["---"] * nb_cols) + "|"
                result.append(header)
                result.append(sep)
                for row in table_buffer[1:]:
                    result.append(row)
            else:
                result.extend(table_buffer)

    for line in lines:
        stripped = line.strip()
        # normaliser les bordures unicode en pipe standard
        normalized = stripped.replace("║", "|").replace("║", "|")
        # ligne de tableau : commence et finit par |, au moins 3 pipes
        is_table = (
            normalized.startswith("|")
            and normalized.endswith("|")
            and normalized.count("|") >= 3
        )
        if is_table:
            # nettoyer les caractères décoratifs dans les cellules
            clean_line = re.sub(r"[═─║╞╪╫╬╔╗╚╝╠╣╦╩]", " ", line)
            clean_line = re.sub(r"\|+", "|", clean_line)
            # éviter ligne de séparation décorative vide
            if not header_separator_pattern.match(stripped):
                table_buffer.append(clean_line)
                in_table = True
                continue
            else:
                # ligne séparatrice décorative → la sauter
                continue
        else:
            if in_table:
                flush_table()
                in_table = False
                table_buffer = []
        result.append(line)

    if in_table:
        flush_table()

    return "\n".join(result)


def remove_ascii_art(content: str) -> str:
    lines = content.split("\n")
    border_chars = set("═║╔╗╚╝╠╣╦╩╬─│┌┐└┘├┤┬┴┼|+- ")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            cleaned.append(line)
            continue
        char_count = len(stripped)
        border_count = sum(1 for c in stripped if c in border_chars)
        if char_count > 5 and (border_count / char_count) > 0.7:
            continue
        cleaned_line = re.sub(r"[╔╗╚╝═║╠╣╦╩╬┌┐└┘├┤┬┴┼]+", "", line)
        if cleaned_line.strip():
            cleaned.append(cleaned_line)
    return "\n".join(cleaned)


def fix_markdown_tables(content: str) -> str:
    lines = content.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip separator |---|---| lines, they're already correct
        if "---" in stripped and stripped.startswith("|") and stripped.endswith("|"):
            result.append(line)
            i += 1
            continue

        is_table_row = (
            stripped.startswith("|")
            and stripped.endswith("|")
            and stripped.count("|") >= 3
        )

        if is_table_row:
            nb_cols = stripped.count("|") - 1
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            # Check if next line is a separator
            has_separator = next_line.startswith("|") and "---" in next_line

            result.append(line)

            if has_separator:
                # Table already has a separator → consume all data rows as-is
                i += 1
                while i < len(lines):
                    ns = lines[i].strip()
                    if "---" in ns and ns.startswith("|") and ns.endswith("|"):
                        result.append(lines[i])
                        i += 1
                        continue  # pass separator through
                    if ns.startswith("|") and ns.endswith("|"):
                        result.append(lines[i])
                        i += 1
                    else:
                        break
                continue

            # No separator → this is a header row, add one
            separator = "|" + "|".join(["---"] * nb_cols) + "|"
            result.append(separator)
            i += 1
            while i < len(lines):
                ns = lines[i].strip()
                if ns.startswith("|") and ns.endswith("|"):
                    result.append(lines[i])
                    i += 1
                else:
                    break
            continue
        else:
            result.append(line)

        i += 1

    return "\n".join(result)


def split_flat_tables(content: str) -> str:
    lines = content.split("\n")
    result = []

    for line in lines:
        stripped = line.strip()

        if stripped.count("|") >= 6:
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if len(cells) >= 6:
                nb_cols = 3
                table_lines = []
                for i in range(0, len(cells), nb_cols):
                    row_cells = cells[i:i + nb_cols]
                    if len(row_cells) == nb_cols:
                        table_lines.append("| " + " | ".join(row_cells) + " |")
                if table_lines:
                    separator = "|" + "|".join(["---"] * nb_cols) + "|"
                    result.append(table_lines[0])
                    result.append(separator)
                    result.extend(table_lines[1:])
                    continue

        result.append(line)

    return "\n".join(result)


def convert_numbered_lists(content: str) -> str:
    lines = content.split("\n")
    result = []
    for line in lines:
        match = re.match(r"^\s*([①②③④⑤⑥⑦⑧⑨⑩])\s*(.+)$", line)
        if match:
            number_map = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5", "⑥": "6", "⑦": "7", "⑧": "8", "⑨": "9", "⑩": "10"}
            num = number_map.get(match.group(1), "1")
            text = match.group(2)
            result.append(f"{num}. {text}")
        else:
            result.append(line)
    return "\n".join(result)


def remove_ascii_schemas(content: str) -> str:
    lines = content.split("\n")
    cleaned = []
    in_code_block = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        ascii_chars = set("═║╔╗╚╝╠╣╦╩╬─│┌┐└┘├┤┬┴┼↔↕←↑→↓")
        if stripped and len(stripped) > 3:
            ratio = sum(1 for c in stripped if c in ascii_chars) / len(stripped)
            if ratio > 0.4:
                continue
        cleaned.append(line)
    return "\n".join(cleaned)


def fix_inline_tables(content: str) -> str:
    lines = content.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        pipe_count = stripped.count("|")
        if pipe_count >= 6 and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if len(cells) >= 6:
                best_nb_cols = None
                for nb_cols in [3, 4, 2, 5, 6]:
                    if len(cells) % nb_cols == 0:
                        best_nb_cols = nb_cols
                        break
                if best_nb_cols is None:
                    best_nb_cols = 3
                    while len(cells) % best_nb_cols != 0:
                        cells.append("")
                table_lines = []
                for i in range(0, len(cells), best_nb_cols):
                    row = cells[i:i + best_nb_cols]
                    table_lines.append("| " + " | ".join(row) + " |")
                if len(table_lines) >= 2:
                    separator = "|" + "|".join(["---"] * best_nb_cols) + "|"
                    result.append("")
                    result.append(table_lines[0])
                    result.append(separator)
                    result.extend(table_lines[1:])
                    result.append("")
                    continue
        result.append(line)
    return "\n".join(result)


# Mots-clés pour trouver la bonne section dans le contenu de l'unité
# On utilise à la fois les termes arabes (en-têtes réels) et français
SECTION_KEYWORDS = {
    "Rappel des acquis": ["تذكير", "Rappel", "القسم الأول", "المكتسبات القبلية"],
    "Rappel des acquis (conditions et manifestations de la photosynthese)": ["تذكير", "Rappel", "photosynth"],
    "Siege de la synthese des proteines": ["مقر تركيب البروتين", "Siège", "الريبوزوم", "Ribosome", "القسم الثاني"],
    "Transcription de l'information genetique au niveau de l'ADN": ["الاستنساخ", "Transcription", "ADN", "القسم الثالث"],
    "La traduction": ["الترجمة", "Translation", "القسم الرابع"],
    "Les etapes de la traduction": ["مراحل الترجمة", "les étapes", "القسم الخامس"],
    "Notion d'enzyme et son importance": ["مفهوم الإنزيم", "Notion d'enzyme", "Enzyme"],
    "L'activite enzymatique et sa relation avec la structure de l'enzyme": ["النشاط الإنزيمي", "activité enzymatique", "Site actif"],
    "Etude de l'influence de la temperature sur l'activite enzymatique": ["température", "temperature", "dénaturation"],
    "Etude de l'influence du pH du milieu sur l'activite enzymatique": ["pH"],
    "Niveaux de la structure spatiale des proteines": ["Structure spatiale", "Niveaux", "البنية", "primaire", "secondaire", "tertiaire"],
    "Relation entre structure et fonction de la proteine": ["Structure", "Fonction", "Relation"],
    "Representation de la structure tridimensionnelle de la proteine": ["tridimensionnelle", "3D"],
    "Le soi et le non-soi": ["Soi", "non-soi", "الذات", "Antigène"],
    "Les elements de defense dans le deuxieme cas (immunite specifique)": ["spécifique", "specificité"],
    "Les molecules de defense dans le premier cas (immunite non specifique)": ["non spécifique", "non specifique"],
    "Origine des anticorps": ["Anticorps", "أجسام مضادة"],
    "Origine des lymphocytes LTc": ["LTc", "lymphocyte T"],
    "Modes d'action des lymphocytes LTc": ["LTc", "cytotoxique", "perforine"],
    "Le complexe immun": ["complexe immun", "Immun"],
    "Choix du type de reponse immunitaire": ["réponse immunitaire", "reponse immunitaire"],
    "Activation des cellules LB et LT": ["LB", "LT", "lymphocyte"],
    "Cause de la perte de l'immunite acquise (SIDA)": ["SIDA", "VIH", "immunité acquise"],
    "La transmission synaptique (potentiel membranaire)": ["synaptique", "membranaire", "potentiel"],
    "Le potentiel de repos": ["potentiel de repos", "كمون الراحة"],
    "Le potentiel d'action": ["potentiel d'action", "كمون العمل", "dépolarisation"],
    "Mecanisme de la transmission synaptique": ["transmission synaptique", "neurotransmetteur"],
    "Mecanisme de l'integration nerveuse": ["intégration nerveuse", "integration", "sommation"],
    "Effet des drogues au niveau des synapses": ["drogues", "synapses", "drogue"],
    "Siege de la photosynthese - Ultrastructure du chloroplaste": ["chloroplaste", "Photosynthèse", "photosynth"],
    "Reactions de la phase photochimique (phase claire)": ["phase photochimique", "phase claire", "photophosphorylation"],
    "Reactions de la phase chimique (cycle de Calvin - phase sombre)": ["Calvin", "phase sombre", "cycle de Calvin"],
    "La glycolyse": ["glycolyse", "Glycolyse", "glucose"],
    "Siege de l'oxydation respiratoire": ["mitochondrie", "oxydation respiratoire"],
    "Etapes de degradation de l'acide pyruvique (reactions du cycle de Krebs)": ["Krebs", "pyruvique", "cycle de Krebs"],
    "La phosphorylation oxydative": ["phosphorylation oxydative", "ATP", "ATP synthase"],
    "Les transformations energetiques au niveau cellulaire": ["Transformations Énergétiques", "énergétique"],
    "Mecanismes de conversion en milieu anaerobie (fermentation)": ["fermentation", "anaérobie", "fermentation lactique"],
    "Identification des plaques tectoniques": ["plaques tectoniques", "Identification", "lithosphère"],
    "Mouvements des plaques tectoniques": ["plaques tectoniques", "Mouvements", "plaques"],
    "Les ondes sismiques": ["ondes sismiques", "Sismique", "séisme"],
    "Indices d'un ancien ocean (ophiolites)": ["ophiolite", "ancien océan", "océanique"],
    "Indices du raccourcissement": ["raccourcissement", "plis", "failles"],
    "Phenomenes lies a la subduction": ["subduction", "plongement", "fosse"],
    "Disparition de la plaque oceanique et phenomenes lies a la subduction": ["plaque océanique", "subduction", "disparition"],
    "Le magmatisme et la formation de la plaque oceanique": ["magmatisme", "plaque océanique", "dorsale"],
    "Caracteristiques des dorsales medio-oceaniques": ["dorsale", "médio-océanique"],
    "Formation des roches caracteristiques de la dorsale medio-oceanique": ["dorsale", "roches", "basalte"],
    "Modelisation de la structure interne du globe terrestre": ["structure interne", "globe"],
    "L'energie interne du globe terrestre": ["énergie interne"],
    "Reliefs resultant de la collision": ["collision", "relief"],
    "Composition chimique des roches de la croute terrestre et du manteau": ["croute terrestre", "manteau", "roches"],
}


# Tous les emojis pouvant introduire un titre de section
SECTION_EMOJI_PATTERN = re.compile(
    r"^([\U0001F4D4\U0001F4D8\U0001F3AF\U0001F4CC\U0001F5C3"
    r"\U0001F4C2\U0001F50D\U0001F4D6\U0001F30D\U0001F525"
    r"\U0001F30A\U0001F33F\U0001F30C\U0001F9A0\U0001F41F"
    r"\U0001F31E\U0001F30B\U0001F30E\U0001F9EC"
    r"\u2705\u26A1\u26A0\u2696"
    r"])\s+(.+)$"
)


def _clean_course_content(raw: str, chapitre: str) -> str:
    """Pipeline de nettoyage partagé : extraction de section + nettoyage ASCII."""
    focused = extract_section(raw, chapitre)
    no_schemas = remove_ascii_schemas(focused)
    cleaned = clean_ascii_tables(no_schemas)
    no_ascii = remove_ascii_art(cleaned)
    fixed_tables = fix_markdown_tables(no_ascii)
    split_tables = split_flat_tables(fixed_tables)
    inline_fixed = fix_inline_tables(split_tables)
    return convert_numbered_lists(inline_fixed)


def extract_section(content: str, chapitre: str) -> str:
    """Extrait la section du cours correspondant au chapitre demandé.

    Stratégie robuste : collecte TOUS les headers markdown (#{1,4})
    contenant un keyword, puis choisit celui de niveau le plus haut (= le
    moins de #). On évite ainsi le faux départ sur un sous-header ### quand
    une vraie section ## existe plus loin (keyword générique type "ADN").
    On extrait ensuite jusqu'au prochain header de niveau <= au niveau retenu.

    NOTE : on ignore les lignes commençant par un emoji sans '#'. Dans ce
    markdown, TOUS les vrais headers de section sont en '## emoji' (regex
    markdown ci-dessus), et les lignes 'emoji-nu' sont des occurrences
    parasites (légendes de schémas, encadrés "le saviez-vous", résumés) qui
    pollueraient la sélection (faux niveau 1 gagnant sur la vraie section ##).
    """
    keywords = SECTION_KEYWORDS.get(chapitre, [chapitre])
    lines = content.split("\n")

    # 1. Collecter tous les headers markdown (#{1,4}) qui matchent un keyword.
    candidates = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        m = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            if any(kw.lower() in title.lower() for kw in keywords):
                candidates.append((i, level))

    if not candidates:
        return content  # aucun match → l'appelant filtre (rejette si trop long)

    # 2. Niveau le plus haut disponible (priorité aux sections ##), puis 1er index.
    best_level = min(c[1] for c in candidates)
    start_idx, current_level = next(c for c in candidates if c[1] == best_level)

    # 3. Extraire depuis start_idx jusqu'au prochain header de niveau <= current_level.
    extracted_lines = []
    for i in range(start_idx, len(lines)):
        line = lines[i]
        stripped = line.strip()
        if i == start_idx:
            extracted_lines.append(line)
            continue
        m = re.match(r"^(#{1,4})\s+", stripped)
        if m and len(m.group(1)) <= current_level:
            break
        extracted_lines.append(line)

    result = "\n".join(extracted_lines).strip()
    return result if result else content


@router.get("/list")
async def list_chapitres(
    current_user: dict = Depends(get_current_user),
):
    """Retourne la liste de tous les chapitres disponibles."""
    return sorted(CHAPTER_MAPPING.keys())


@router.get("/{chapitre_title}")
async def get_cours(
    chapitre_title: str,
    db: AsyncSession = Depends(get_db),
):
    decoded = chapitre_title.replace("%20", " ").replace("+", " ")

    keywords = CHAPTER_MAPPING.get(decoded, None)

    if keywords:
        conditions = " OR ".join(
            f"LOWER(chapitre) LIKE LOWER(:kw{i})" for i in range(len(keywords))
        )
        params = {f"kw{i}": f"%{k}%" for i, k in enumerate(keywords)}
        params["source"] = COURSE_SOURCE

        result = await db.execute(
            text(f"""
                SELECT content, chunk_index, importance, chapitre
                FROM rag_chunks
                WHERE source = :source
                AND ({conditions})
                AND LENGTH(content) > 200
                AND content NOT LIKE '%تمارين%'
                AND content NOT LIKE '%التمرين%'
                AND content NOT LIKE '%إجابة%'
                AND content NOT LIKE '%Exercice%'
                AND content NOT LIKE '%Correction%'
                AND content NOT LIKE '%منهجية%'
                AND content NOT LIKE '%سلّم%'
                ORDER BY chunk_index ASC
                LIMIT 30
            """),
            params,
        )
        rows = result.fetchall()

        if not rows:
            result = await db.execute(
                text(f"""
                    SELECT content, chunk_index, importance, chapitre
                    FROM rag_chunks
                    WHERE ({conditions})
                    AND LENGTH(content) > 200
                    AND content NOT LIKE '%تمارين%'
                    AND content NOT LIKE '%التمرين%'
                    AND content NOT LIKE '%إجابة%'
                    AND content NOT LIKE '%Exercice%'
                    AND content NOT LIKE '%Correction%'
                    AND content NOT LIKE '%منهجية%'
                    AND content NOT LIKE '%سلّم%'
                    ORDER BY chunk_index ASC
                    LIMIT 30
                """),
                {k: v for k, v in params.items() if k != "source"},
            )
            rows = result.fetchall()

        if rows:
            groups = {}
            for r in rows:
                g = groups.setdefault(r.chapitre, {"chunks": [], "score": 0})
                g["chunks"].append(r)
                g["score"] += score_match(r.chapitre, keywords)
            best = max(groups.values(), key=lambda x: (x["score"], len(x["chunks"])))
            rows = best["chunks"]
    else:
        result = await db.execute(
            text("""
                SELECT content, chunk_index, importance, chapitre
                FROM rag_chunks
                WHERE source = :course_source
                AND LOWER(chapitre) = LOWER(:chapitre)
                AND LENGTH(content) > 200
                AND content NOT LIKE '%تمارين%'
                AND content NOT LIKE '%التمرين%'
                AND content NOT LIKE '%إجابة%'
                AND content NOT LIKE '%Exercice%'
                AND content NOT LIKE '%Correction%'
                AND content NOT LIKE '%منهجية%'
                AND content NOT LIKE '%سلّم%'
                ORDER BY chunk_index ASC
                LIMIT 30
            """),
            {"chapitre": decoded, "course_source": COURSE_SOURCE},
        )
        rows = result.fetchall()

        if not rows:
            mots = [m for m in decoded.replace("-", " ").split() if len(m) > 2]
            if mots:
                clauses = []
                params = {}
                for i, m in enumerate(mots):
                    params[f"w{i}"] = f"%{m}%"
                    clauses.append(f"LOWER(chapitre) LIKE LOWER(:w{i})")
                cond = " OR ".join(clauses)
                result = await db.execute(
                    text(f"""
                        SELECT chapitre, COUNT(*) as nb
                        FROM rag_chunks
                        WHERE ({cond})
                        GROUP BY chapitre
                    """),
                    params,
                )
                chapters_found = result.fetchall()
                if chapters_found:
                    scored = [
                        (score_match(r.chapitre, mots), r.nb, r.chapitre)
                        for r in chapters_found
                    ]
                    scored.sort(key=lambda x: (-x[0], -x[1]))
                    best_chapitre = scored[0][2]
                    result = await db.execute(
                        text("""
                            SELECT content, chunk_index, importance, chapitre
                            FROM rag_chunks
                            WHERE chapitre = :chapitre
                            AND LENGTH(content) > 200
                            AND content NOT LIKE '%تمارين%'
                            AND content NOT LIKE '%التمرين%'
                            AND content NOT LIKE '%إجابة%'
                            AND content NOT LIKE '%Exercice%'
                            AND content NOT LIKE '%Correction%'
                            AND content NOT LIKE '%منهجية%'
                            AND content NOT LIKE '%سلّم%'
                            ORDER BY chunk_index ASC
                            LIMIT 30
                        """),
                        {"chapitre": best_chapitre},
                    )
                    rows = result.fetchall()

    if not rows:
        # FALLBACK : lecture directe du markdown quand la DB est vide
        # ou le nom source ne matche pas. Le contenu de cours étant structuré
        # par headers, extract_section() récupère la bonne section sans RAG.
        if not COURSE_FILE.exists():
            logger.error(f"Fallback cours : fichier absent {COURSE_FILE}")
            raise HTTPException(
                status_code=404,
                detail=f"Aucun contenu trouve pour : {decoded}",
            )
        try:
            raw = COURSE_FILE.read_text(encoding="utf-8")
            final_content = _clean_course_content(raw, decoded)
            # extract_section() retourne tout le contenu si rien ne matche :
            # on refuse alors pour éviter de servir 10 000 lignes hors-sujet.
            if len(final_content.strip()) < 100:
                logger.warning(
                    f"Section vide pour '{decoded}' (fallback fichier) — "
                    f"keywords={SECTION_KEYWORDS.get(decoded, [decoded])}"
                )
                raise HTTPException(
                    status_code=404,
                    detail=f"Aucun contenu trouve pour : {decoded}",
                )
            logger.info(f"Cours servi depuis fallback fichier : {decoded}")
            return {
                "chapitre": decoded,
                "chapitre_rag": decoded,
                "contenu": final_content,
                "sources": [COURSE_SOURCE],
                "total_chunks": 1,
                "importance": "moyenne",
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Fallback cours fichier échoué pour '{decoded}' : {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la lecture du cours : {decoded}",
            )

    content = "\n\n".join(r.content for r in rows)
    chapitre_reel = rows[0].chapitre
    importance = rows[0].importance if rows[0].importance else "moyenne"

    final_content = _clean_course_content(content, decoded)

    return {
        "chapitre": decoded,
        "chapitre_rag": chapitre_reel,
        "contenu": final_content,
        "sources": [COURSE_SOURCE],
        "total_chunks": len(rows),
        "importance": importance,
    }
