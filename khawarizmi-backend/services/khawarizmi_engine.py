# services/khawarizmi_engine.py — VERSION 2.0 CORRIGÉE

import json
import os
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger('khawarizmi.engine')

MODES_PEDAGOGIQUES = {
    'FEYNMAN': {
        'instruction': """
Explique ce concept avec des mots simples.
Utilise une analogie de la vie quotidienne algérienne.
Maximum 150 mots. L'élève doit comprendre le POURQUOI avant le COMMENT.
""",
        'output_format': 'texte',
    },
    'RAPPEL_ACTIF': {
        'instruction': """
Génère 3 questions progressives sur ce concept.
Question 1 : Facile (définition)
Question 2 : Intermédiaire (application)
Question 3 : Difficile (type BAC)
Attends la réponse de l'élève avant de corriger.
""",
        'output_format': 'texte',
    },
    'MIND_MAP': {
        'instruction': """
Génère un plan structuré du concept en Markdown UNIQUEMENT.
TOUS les titres et labels en ARABE.
Termes scientifiques universels entre parenthèses en FR.
Format strict :
# Titre Principal (en arabe)
## Sous-concept 1 (en arabe)
- Point clé 1 (en arabe, terme FR si nécessaire)
- Point clé 2
## Sous-concept 2
...
Maximum 20 lignes. Clair. Hiérarchique.
""",
        'output_format': 'markdown',
    },
    'FLASHCARDS': {
        'instruction': """
Génère 5 flashcards recto-verso sur ce concept.
UNIQUEMENT du JSON valide. Aucun texte avant ou après.
Format strict :
[
  {"question": "...", "reponse": "..."},
  {"question": "...", "reponse": "..."}
]
""",
        'output_format': 'json',
    },
    'ANNALES_COMPLEXES': {
        'instruction': """
Tu es en mode Error Autopsy.
L'élève a soumis une réponse. Diagnostique et guide.
Méthode Socratique : jamais de réponse directe.
Voir le traitement spécifique dans la base de connaissances.
""",
        'output_format': 'json_autopsy',
    },
    'MODE_EXAMEN': {
        'instruction': """
Tu es en mode Examen.
Évalue strictement la réponse de l'élève selon le barème officiel des annales.
""",
        'output_format': 'json_autopsy',
    }
}

BLOOM_TAXONOMY_AR = {
    1: {"niveau": "التذكر", "verbes": ["عرّف", "اذكر", "عدّد", "سطّر", "سم", "ضع البيانات"], "code": "BLOOM_L1_RECALL"},
    2: {"niveau": "الفهم", "verbes": ["اشرح", "علّل", "استخلص", "فسّر"], "code": "BLOOM_L2_UNDERSTAND"},
    3: {"niveau": "التطبيق", "verbes": ["احسب", "طبّق", "صنّف", "أنجز", "لوّن", "صف"], "code": "BLOOM_L3_APPLY"},
    4: {"niveau": "التحليل", "verbes": ["قارن", "ميّز", "فرّق", "استنتج", "رتّب", "أثبت"], "code": "BLOOM_L4_ANALYZE"},
    5: {"niveau": "التأليف", "verbes": ["حوصل", "اقترح", "أعط تفسيرا", "استخلص"], "code": "BLOOM_L5_SYNTHESIZE"},
}

def detecter_niveau_bloom(texte_question: str) -> dict:
    for niveau, data in sorted(BLOOM_TAXONOMY_AR.items(), reverse=True):
        for verbe in data["verbes"]:
            if verbe in texte_question:
                return {"niveau": niveau, "label": data["niveau"], "code": data["code"]}
    return {"niveau": 1, "label": "التذكر", "code": "BLOOM_L1_RECALL"}

class KhawarizmiTutor:

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

        # === NEW: Single Source of Truth ===
        from services.data_loader import get_data_loader
        self.loader = get_data_loader(data_dir)

        self.programme_canonical = self.loader.load_canonical_programme()

        # === CONNECTION DES DONNÉES RESTANTES (SVT UNIQUEMENT) ===
        self.programme_sciences = self.programme_canonical
        self.programme_maths    = self._charger_json(data_dir, 'programme_maths_3as.json', optional=True)
        self.annales_clean      = self._charger_json(data_dir, 'annales_sciences_3as.json', optional=True)
        self.annales_sciences   = self.annales_clean
        self.lexique            = self._charger_json(data_dir, 'lexique_svt_terminale_complet.json', optional=True)
        self.lexique_complet    = self.lexique
        self.methodologie       = self._charger_json(data_dir, 'methodologie_sciences_3as.json', optional=True)

        self._index_questions        = self._construire_index()
        self._index_micro_concepts   = self._construire_index_micro_concepts()
        self._index_lexique          = self._construire_index_lexique()

        report = self.loader.get_loading_report()
        logger.info("KhawarizmiTutor initialisé avec DataLoader (deep migration)")
        logger.info(f"  Programme: {report['loaded_from'].get('programme')}")

    def _charger_json(self, data_dir: str, filename: str, optional: bool = False) -> dict:
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            if optional:
                logger.info(f"Fichier optionnel absent (ignoré) : {filename}")
                return {}
            raise FileNotFoundError(f"Fichier requis manquant : {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Chargé : {filename} ({len(str(data))} chars)")
                return data
        except json.JSONDecodeError as e:
            if optional:
                logger.error(f"JSON invalide dans {filename} : {e}")
                return {}
            raise ValueError(f"Erreur JSON dans {filename}: {e}")

    def _construire_index(self) -> dict:
        """
        Index {sujet_id: {question_id: question_data}}.
        ADAPTE la navigation selon la structure réelle du JSON.
        """
        index = {}
        
        sources = [
            ('sciences', self.annales_sciences)
        ]
        
        for matiere, annales in sources:
            if not isinstance(annales, list) and not isinstance(annales, dict):
                continue
                
            sujets = annales.get('sujets', []) if isinstance(annales, dict) else annales
            
            for sujet in sujets:
                sujet_id = sujet.get('id') or sujet.get('sujet_id')
                if not sujet_id:
                    continue
                index[sujet_id] = {}

                # Support des deux structures possibles :
                # Structure A : sujet.questions (liste plate)
                # Structure B : sujet.exercices[].sous_questions ou exercices[].questions (hiérarchique)

                if 'questions' in sujet:
                    # Structure A (plate)
                    for q in sujet.get('questions', []):
                        q_id = q.get('id') or q.get('question_id')
                        if q_id:
                            index[sujet_id][q_id] = {'question': q, 'sujet': sujet, 'matiere': matiere}

                elif 'exercices' in sujet:
                    # Structure B (hiérarchique)
                    for ex in sujet.get('exercices', []):
                        questions = ex.get('sous_questions', []) or ex.get('questions', [])
                        for sq in questions:
                            q_id = sq.get('id') or sq.get('question_id')
                            if q_id:
                                index[sujet_id][q_id] = {
                                    'question':  sq,
                                    'exercice':  ex,
                                    'sujet':     sujet,
                                    'matiere':   matiere
                                }

        logger.info(f"Index construit : {sum(len(v) for v in index.values())} questions total")
        return index

    def _construire_index_micro_concepts(self) -> dict:
        index = {}
        programmes = [self.programme_maths, self.programme_sciences]
        for programme in programmes:
            if not programme:
                continue
            if isinstance(programme, dict) and 'domaines' in programme:
                for d in programme.get('domaines', []):
                    for chapitre in d.get('chapitres', []):
                        for mc in chapitre.get('micro_concepts', []):
                            mc_id = mc.get('id')
                            if mc_id:
                                index[mc_id] = {'micro_concept': mc, 'chapitre': chapitre}
            else:
                chapitres = programme.get('chapitres', []) if isinstance(programme, dict) else programme
                for chapitre in chapitres:
                    for mc in chapitre.get('micro_concepts', []):
                        mc_id = mc.get('id')
                        if mc_id:
                            index[mc_id] = {'micro_concept': mc, 'chapitre': chapitre}
        logger.info(f"Index MC : {len(index)} micro-concepts")
        return index

    def _construire_index_lexique(self) -> dict:
        index = {}
        lexique = self.lexique_complet
        if not lexique or not isinstance(lexique, dict):
            return index

        domaines = lexique.get('domaines', [])
        for domaine in domaines:
            for categorie in domaine.get('categories', []):
                for terme in categorie.get('termes', []):
                    tid = terme.get('id')
                    if tid:
                        # Indexer par ID
                        index[tid] = {
                            **terme,
                            'domaine_fr': domaine.get('nom_fr', ''),
                            'domaine_ar': domaine.get('nom_ar', ''),
                            'categorie_fr': categorie.get('nom_fr', ''),
                            'categorie_ar': categorie.get('nom_ar', ''),
                        }
                        # Indexer par terme_fr (lowercase)
                        tf = terme.get('terme_fr', '').lower()
                        if tf:
                            index.setdefault(f'__nom__{tf}', []).append(tid)
                        # Indexer par terme_ar
                        ta = terme.get('terme_ar', '')
                        if ta:
                            index.setdefault(f'__ar__{ta}', []).append(tid)
                        # Indexer par abreviation
                        abv = terme.get('abreviation', '')
                        if abv:
                            index.setdefault(f'__abv__{abv.lower()}', []).append(tid)
                        # Indexer par tags
                        for tag in terme.get('tags', []):
                            index.setdefault(f'__tag__{tag.lower()}', []).append(tid)

        logger.info(f"Index lexique : {len(index)} entrées")
        return index

    def _enrichir_contexte_lexique(self, texte: str, mc_id: str = '') -> str:
        if not self._index_lexique or not texte:
            return ''

        texte_lower = texte.lower()
        termes_trouves = set()

        # Chercher par micro_concept_id d'abord
        if mc_id:
            for tid, terme in self._index_lexique.items():
                if tid.startswith('__'):
                    continue
                if terme.get('micro_concept_id') == mc_id and terme.get('importance') in ('critique', 'haute'):
                    termes_trouves.add(tid)

        # Chercher par correspondance textuelle
        for tid, terme in self._index_lexique.items():
            if tid.startswith('__'):
                continue
            nom_fr = terme.get('terme_fr', '').lower()
            nom_ar = terme.get('terme_ar', '')
            abv = terme.get('abreviation', '')
            if nom_fr and nom_fr in texte_lower:
                termes_trouves.add(tid)
            if nom_ar and nom_ar in texte:
                termes_trouves.add(tid)
            if abv and abv.lower() in texte_lower:
                termes_trouves.add(tid)

        if not termes_trouves:
            return ''

        blocs = []
        for tid in sorted(termes_trouves):
            t = self._index_lexique.get(tid, {})
            if not t:
                continue
            blocs.append(
                f"- {t.get('terme_fr', '')} ({t.get('terme_ar', '')}) : "
                f"{t.get('definition_fr', '')} — {t.get('definition_ar', '')} "
                f"[{t.get('importance', '')}]"
            )

        if not blocs:
            return ''

        return (
            "\n━━━ LEXIQUE DE RÉFÉRENCE (termes détectés) ━━━\n"
            + "\n".join(blocs[:8])
            + "\n"
        )

    def _get_question(self, sujet_id: str, question_id: str) -> dict:
        if sujet_id not in self._index_questions:
            available = list(self._index_questions.keys())[:5]
            raise ValueError(f"Sujet '{sujet_id}' introuvable. Disponibles : {available}")
        if question_id not in self._index_questions[sujet_id]:
            available = list(self._index_questions[sujet_id].keys())[:5]
            raise ValueError(f"Question '{question_id}' introuvable. Disponibles : {available}")
        return self._index_questions[sujet_id][question_id]

    def _get_socratic_treatment_for_error(self, mc_id: str, error_id: str) -> dict:
        if not mc_id:
            logger.warning("mc_id vide")
            return {}

        mc_data = self._index_micro_concepts.get(mc_id)
        if not mc_data:
            logger.warning(f"MC introuvable : '{mc_id}'")
            return {}

        if not error_id:
            logger.debug(f"Pas d'error_id pour MC={mc_id}")
            return {}

        mc        = mc_data['micro_concept']
        chapitre  = mc_data['chapitre']
        autopsy   = mc.get('error_autopsy', {})

        cat_map = {
            'concept':   'TYPE_1',
            'methode':   'TYPE_2',
            'execution': 'TYPE_3',
            'panique':   'TYPE_4',
        }

        for category, errors in autopsy.items():
            if not isinstance(errors, list):
                continue
            for err in errors:
                if err.get('id') == error_id:
                    logger.debug(f"Traitement trouvé : {error_id} → {cat_map.get(category)}")
                    return {
                        'type_erreur':           cat_map.get(category, 'INCONNU'),
                        'description_erreur':    err.get('description', ''),
                        'traitement_socratique': err.get('traitement_socratique', ''),
                        'micro_concept_nom':     mc.get('nom', ''),
                        'chapitre_nom':          chapitre.get('nom', ''),
                    }

        logger.warning(f"Erreur '{error_id}' introuvable dans MC='{mc_id}'")
        return {}

    # ═══ PRÉ-ANALYSE ════════════════════════════════════════════

    def pre_analyser_sans_ia(self, sujet_id, question_id, student_input) -> Optional[dict]:
        try:
            data = self._get_question(sujet_id, question_id)
        except ValueError as e:
            logger.warning(f"pre_analyser_sans_ia : {e}")
            return None

        question      = data['question']
        type_question = question.get('type_exercice', '')
        mc_id         = question.get('micro_concept_id', '')

        logger.debug(f"Pré-analyse : type={type_question} mc={mc_id}")

        if type_question == 'loi_probabilite' or mc_id == 'MC_PROBA_03':
            return self._verifier_somme_probabilites(student_input)

        if 'reponse_numerique_attendue' in question:
            return self._verifier_resultat_numerique(
                student_input,
                question.get('reponse_numerique_attendue'),
                question.get('pattern_recherche'),
            )

        logger.debug("Aucun pré-analyseur applicable")
        return None

    def _verifier_somme_probabilites(self, text: str) -> Optional[dict]:
        fractions = re.findall(r'(\d+)/(\d+)', text)
        if len(fractions) < 2:
            return None

        denom = int(fractions[0][1])
        if not all(int(d) == denom for _, d in fractions):
            return None

        somme_num  = sum(int(n) for n, _ in fractions)
        somme_tot  = somme_num / denom

        if abs(somme_tot - 1.0) > 0.001:
            manque = denom - somme_num
            return {
                'erreur_detectee': True,
                'type_erreur':    'TYPE_3',
                'diagnostic':     f"Somme des probabilites = {somme_num}/{denom} != 1. Il manque {manque}/{denom}.",
                'hint_socratique': f"Verifie la somme de tes probabilites : {' + '.join([f'{n}/{d}' for n,d in fractions])} = ?",
                'economie_tokens': 200,
            }

        return {
            'erreur_detectee': False,
            'diagnostic':     f"Somme des probabilites = 1 [OK]",
            'type_erreur':   'AUCUNE',
            'economie_tokens': 200,
        }

    def _verifier_resultat_numerique(
        self,
        text: str,
        reponse_attendue: Optional[float],
        pattern: Optional[str] = None,
    ) -> Optional[dict]:

        if reponse_attendue is None:
            return None

        nombre = None

        if pattern:
            match = re.search(pattern, text)
            if match:
                try:
                    nombre = float(match.group(1))
                except (ValueError, IndexError):
                    return None
        else:
            # Chercher les décimaux (plus fiable que tous les entiers)
            decimaux = re.findall(r'-?\d+\.\d+', text)
            if decimaux:
                nombre = float(decimaux[-1])

        if nombre is None:
            return None

        if abs(nombre - reponse_attendue) > 0.01:
            return {
                'erreur_detectee': True,
                'type_erreur':    'TYPE_3',
                'diagnostic':     f"Trouve : {nombre} | Attendu : {reponse_attendue}",
                'economie_tokens': 150,
            }

        return {
            'erreur_detectee': False,
            'diagnostic':     f"Resultat correct : {nombre} [OK]",
            'type_erreur':   'AUCUNE',
            'economie_tokens': 150,
        }

    # ═══ ROUTING ET MODES PÉDAGOGIQUES ══════════════════════════

    def router_par_niveau(self, niveau: int, score_actuel: float, demande_visuel: bool = False) -> str:
        """
        Décide quelle méthode pédagogique activer.
        Basé sur le niveau SM-2 (0-4) et le score actuel (0-1).
        """
        if demande_visuel:
            return 'MIND_MAP'
        if niveau <= 1 or score_actuel < 0.40:
            return 'FEYNMAN'
        elif niveau == 2 or score_actuel < 0.70:
            return 'RAPPEL_ACTIF'
        elif niveau == 3 or score_actuel < 0.90:
            return 'ANNALES_COMPLEXES'
        else:
            return 'MODE_EXAMEN'

    # ═══ BUILD_SYSTEM_PROMPT ════════════════════════════════════

    def build_system_prompt(
        self,
        sujet_id:      str,
        question_id:   str,
        student_input:  str,
        pre_analyse:   Optional[dict] = None,
        niveau_sm2:    int = 0,
        score_actuel:  float = 0.0,
        mode_force:    Optional[str] = None,
        calendar_context: Optional[dict] = None,
    ) -> str:

        data     = self._get_question(sujet_id, question_id)
        question = data['question']
        sujet    = data['sujet']
        exercice = data.get('exercice', {})

        mc_id  = question.get('micro_concept_id', '')
        err_id = question.get('diagnostic_erreur_cible', '')
        
        bloom_info = detecter_niveau_bloom(question.get('texte', question.get('question', '')))
        niveau_cognitif = bloom_info['label']

        # ─── Diagnostic — KB prime sur pré-analyse ──────────────
        db_treatment = self._get_socratic_treatment_for_error(mc_id, err_id)

        if db_treatment:
            type_erreur     = db_treatment.get('type_erreur', 'INCONNU')
            hint_socratique = db_treatment.get('traitement_socratique', '')
            chapitre_nom    = db_treatment.get('chapitre_nom', '')
        elif pre_analyse and pre_analyse.get('erreur_detectee'):
            type_erreur     = pre_analyse.get('type_erreur', 'INCONNU')
            hint_socratique = pre_analyse.get('hint_socratique', '')
            chapitre_nom    = ''
        else:
            type_erreur     = 'INCONNU'
            hint_socratique = ''
            chapitre_nom    = ''

        # Si KB n'a pas de hint mais pré-analyse en a un → enrichir
        if not hint_socratique and pre_analyse:
            hint_socratique = pre_analyse.get('hint_socratique', '')

        # ─── Contexte lexique ───────────────────────────────────
        texte_question = question.get('texte', question.get('question', ''))
        contexte_lexique = self._enrichir_contexte_lexique(
            f"{texte_question} {student_input}", mc_id
        )

        # ─── Diagnostic pré-analyse ──────────────────────────────
        pre_analyse_str = (
            f"Diagnostic automatique : {pre_analyse.get('diagnostic', 'N/A')}"
            if pre_analyse
            else "Aucune pré-analyse disponible."
        )

        # ─── Instruction hint ────────────────────────────────────
        hint_instruction = (
            f"→ Indice socratique validé à utiliser : '{hint_socratique}'"
            if hint_socratique
            else "→ Aucun indice prédéfini : génère ta propre question socratique."
        )

        # ─── Méthode socratique ──────────────────────────────────
        methode = self._get_methode_socratique(
            type_erreur, hint_socratique, mc_id, chapitre_nom
        )

        matiere = data.get('matiere', 'maths')
        nom_matiere = "Sciences Expérimentales" if matiere == 'sciences' else "Mathématiques"
        
        bloc_minhajiya = ""
        if matiere == 'sciences':
            bloc_minhajiya = """
━━━ MÉTHODOLOGIE SCIENCES (MINHAJIYA — CONSIGNES ONEC) ━━━
Tu es le gardien absolu de la méthodologie ONEC. Tu dois faire respecter les règles pour chaque verbe d'action de SVT :

1. VERBE "ANALYSER" (حلّل / Analyser) :
   - L'élève DOIT définir la وثيقة ("تمثل الوثيقة...")
   - L'élève DOIT décomposer les résultats avec des valeurs chiffrées/ شروط الشرح.
   - L'élève DOIT formuler une relation logique (العلاقة: كلما زاد... زاد/نقص...).
   - L'élève DOIT formuler une déduction (الاستنتاج) courte et directe.
   - INTERDICTION ABSOLUE d'interpréter ou expliquer les causes dans l'analyse. S'il utilise des connecteurs de cause ("راجع إلى", "بسبب", "لأن"), tu dois le corriger immédiatement et lui rappeler la règle ONEC.

2. VERBE "EXPLIQUER" (فسّر / Interpreter) :
   - L'élève DOIT formuler une relation de cause à effet ("علاقة سببية") en répondant au Pourquoi et au Comment.
   - L'élève DOIT utiliser les termes d'explication obligatoires ("راجع إلى", "يعود إلى", "سببه", "لأن").
   - L'élève DOIT lier les faits expérimentaux avec ses مكتسبات قبلية (connaissances).

3. VERBE "DÉDUIRE" (استنتاج / Déduire) :
   - L'élève DOIT formuler une conclusion courte et directe (1 ou 2 phrases max) qui répond à l'objectif de l'expérience, sans ajouter de nouvelles explications.
"""

        mode_id = mode_force if mode_force else self.router_par_niveau(niveau_sm2, score_actuel)
        mode_config = MODES_PEDAGOGIQUES.get(mode_id, MODES_PEDAGOGIQUES['ANNALES_COMPLEXES'])
        instruction_mode = mode_config['instruction']

        bloc_calendrier = ""
        if calendar_context:
            stats = calendar_context.get("user_stats", {"mastered": 0, "total": 0, "avg_stability": 0.0})
            bloc_calendrier = f"""
━━━ CONTEXTE TEMPOREL & FSRS (CALENDRIER BAC) ━━━
→ Jours restants avant le BAC : {calendar_context.get('days_to_bac', 0)} jours.
→ Phase de préparation : {calendar_context.get('phase', 'N/A')}
→ État de mémorisation FSRS de l'élève : {stats.get('mastered', 0)} concepts maîtrisés sur {stats.get('total', 0)} révisés (Stabilité moyenne : {stats.get('avg_stability', 0.0)} jours).

→ INSTRUCTIONS DE TON & COACHING :
* Si la phase contient 'Sprint final' (J-15 avant le BAC) : Sois extrêmement concis, focalisé sur l'essentiel, dynamique et encourageant. Privilégie un rythme rapide de questions/réponses socratiques (Active Recall).
* Si l'élève a une stabilité de mémoire moyenne faible : Rappelle-lui avec bienveillance que la régularité des révisions quotidiennes (FSRS) est la clé de la réussite au BAC.
* Personnalise ton introduction ou tes encouragements en faisant subtilement référence au temps restant avant le BAC pour le motiver !
"""

        format_output = ""
        if mode_config['output_format'] == 'json_autopsy':
            format_output = f"""
━━━ FORMAT JSON OBLIGATOIRE ━━━
{{
    "type_erreur": "{type_erreur}",
    "ce_qui_est_correct": "<commence par reconnaître ce qui est juste>",
    "question_socratique": "<ta question pour guider>",
    "indice_si_bloque": "<si l'élève reste bloqué après 2 échanges>",
    "feedback_bienveillant": "<message complet à l'élève>"
}}
"""
        elif mode_config['output_format'] == 'json':
            format_output = """
━━━ FORMAT JSON OBLIGATOIRE ━━━
Génère UNIQUEMENT du JSON valide. Aucun texte en dehors du JSON.
"""
        else:
            format_output = f"━━━ FORMAT ATTENDU : {mode_config['output_format'].upper()} ━━━"

        prompt = f"""
🚨 RÈGLES DE LANGUE ET FILTRAGE ABSOLUES (CRITIQUE) :
1. LANGUE ARABE OBLIGATOIRE : Tu dois répondre EXCLUSIVEMENT en arabe classique académique. Même si l'élève te pose des questions en français, anglais, russe, ou alphabet latin, ignore complètement sa langue et réponds-lui UNIQUEMENT en arabe classique. Tu dois garder uniquement les termes scientifiques universels entre parenthèses en français, ex: "الاستنساخ (la transcription)". Il est strictement interdit d'utiliser des mots français ordinaires (comme "importante") au milieu de tes phrases en arabe !
2. REJET DU HORS-SUJET (OFF-TOPIC) : Tu es un tuteur spécialisé UNIQUEMENT dans les SVT (sciences de la vie et de la terre) de Terminale Algérie. Si l'élève te pose une question hors-sujet (comme l'histoire, la philosophie, Ibn Sina, la physique générale, ou des salutations distrayantes), tu DOIS refuser de répondre avec courtoisie, lui indiquer que tu n'es configuré que pour les sciences biologiques, et le recentrer immédiatement sur le chapitre de SVT en cours.
   - Exemple de réponse type obligatoire en cas de hors-sujet: "عذراً، أنا هنا كأستاذ لمادة علوم الطبيعة والحياة فقط لمساعدتك في البكالوريا. دعنا نركز على موضوع درسنا اليوم وهو {chapitre_nom or 'العلوم الطبيعية'}..."

Tu es KHAWARIZMI, tuteur expert du BAC algérien en {nom_matiere}.

━━━ PHILOSOPHIE ABSOLUE ━━━
Tu ne donnes JAMAIS la réponse directement.
Tu guides l'élève vers la compréhension par des QUESTIONS.
Tu commences TOUJOURS par reconnaître ce qui est correct.
Tu es bienveillant mais précis.

━━━ CONTEXTE ━━━
BAC {sujet.get('annee', '?')} | {sujet.get('filiere', '?')}
Exercice : {exercice.get('titre', sujet.get('theme_principal', '?'))}
Question : {question.get('id', '?')} — {question.get('texte', question.get('question', '?'))}
Points : {question.get('points', '?')}
Micro-concept : {mc_id} ({chapitre_nom})
Niveau Cognitif (Bloom) : {niveau_cognitif} ({bloom_info['code']})

━━━ SOLUTION OFFICIELLE (CONFIDENTIELLE) ━━━
{json.dumps(question.get('solution', {}), ensure_ascii=False, indent=2)}

━━━ RÉPONSE DE L'ÉLÈVE ━━━
{student_input}
{contexte_lexique}
━━━ DIAGNOSTIC ━━━
Type d'erreur : {type_erreur}
{pre_analyse_str}

━━━ ERREURS FRÉQUENTES ━━━
{json.dumps(question.get('erreurs_frequentes', []), ensure_ascii=False, indent=2)}

━━━ MÉTHODE SOCRATIQUE ━━━
{methode}
{bloc_minhajiya}
{bloc_calendrier}

━━━ INSTRUCTION PÉDAGOGIQUE (MODE: {mode_id}) ━━━
{instruction_mode}

━━━ RÈGLES ━━━
→ Ne réponds qu'à partir du CONTEXTE FOURNI. Si l'information ne s'y trouve pas, tu as l'interdiction de l'inventer et tu dois répondre "Je n'ai pas trouvé cette information dans la base. Consulte ton manuel officiel."
→ Tu ne dois JAMAIS inventer de faits, de dates, ou de formules.
→ Ne révèle JAMAIS la solution officielle
→ Commence par ce qui est CORRECT dans la réponse de l'élève
→ Pose UNE seule question (pas plusieurs)
→ Réponds OBLIGATOIREMENT en arabe (avec les termes scientifiques universels entre parenthèses en français, ex: 'بوليميراز (ARN polymérase)')
{hint_instruction}
{format_output}
""".strip()

        logger.debug(f"Prompt construit : {len(prompt)} chars | type={type_erreur}")
        return prompt

    def _get_methode_socratique(
        self,
        type_erreur:     str,
        hint_socratique: str,
        mc_id:           str = '',
        chapitre_nom:    str = '',
    ) -> str:

        contexte = f"Chapitre : {chapitre_nom}" if chapitre_nom else ""

        if hint_socratique:
            return f"""
{contexte}
Erreur {type_erreur} identifiée.
→ Utilise cet indice expert : "{hint_socratique}"
→ Formule-le comme une question ouverte à l'élève.
→ Ne révèle pas la réponse. Juste guide.
"""

        methodes = {
            'TYPE_1': f"""
{contexte} | Erreur de CONCEPT.
→ L'élève ne comprend pas le fondement théorique.
→ Question d'ouverture : "Qu'est-ce que tu comprends par [concept] ?"
→ Guide vers la définition avant tout calcul.
""",
            'TYPE_2': f"""
{contexte} | Erreur de MÉTHODE.
→ L'élève comprend le concept mais utilise la mauvaise approche.
→ Question : "Quelle est la première étape pour ce type de problème ?"
→ Guide vers la bonne technique. Ne la nomme pas.
""",
            'TYPE_3': f"""
{contexte} | Erreur d'EXÉCUTION.
→ La démarche est correcte. Erreur de calcul ou de manipulation.
→ Question : "Vérifie ton calcul. Que trouves-tu ?"
→ Ne montre pas où est l'erreur. L'élève doit la trouver.
""",
            'TYPE_4': f"""
{contexte} | Erreur d'OMISSION.
→ L'élève sait mais oublie une étape.
→ Question : "Est-ce que ta réponse est complète ?"
→ Guide vers l'étape manquante sans la nommer.
""",
            'INCONNU': """
Type d'erreur non identifié.
→ Commence par : "Explique-moi ta démarche étape par étape."
→ Écoute. Identifie le type. Puis guide.
""",
        }

        return methodes.get(type_erreur, methodes['INCONNU'])

    async def interroger_ia(
        self,
        sujet_id: str,
        question_id: str,
        student_input: str,
        **kwargs
    ) -> str:
        """
        Méthode principale : construit le prompt ET appelle l'IA.
        Actuellement ce lien est absent du fichier.
        """
        prompt = self.build_system_prompt(
            sujet_id, question_id, student_input, **kwargs
        )
        # Appel à connecter ici avec le service LLM
        raise NotImplementedError(
            "Connecter ici openai / anthropic / google-generativeai"
        )


_instance = None

def get_tutor(data_dir: str) -> 'KhawarizmiTutor':
    global _instance
    if _instance is None:
        _instance = KhawarizmiTutor(data_dir)
    return _instance
