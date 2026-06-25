"""
Flashcards Méthodologiques — Semaine 5
30 cartes verbes + 20 cartes erreurs + 15 cartes structure
"""

VERB_FLASHCARDS = [
    # === Verbes Simples (10 cartes) ===
    {"id": "v01", "front": "Que signifie le verbe 'صف' ?", "back": "Décrire avec précision les caractéristiques d'un élément.", "category": "verbe", "difficulty": "easy"},
    {"id": "v02", "front": "Quelle est la structure attendue pour 'عرف' ?", "back": "Définition concise + caractéristiques essentielles.", "category": "verbe", "difficulty": "easy"},
    {"id": "v03", "front": "Différence entre 'صف' et 'عرف' ?", "back": "'صف' = décrire les caractéristiques. 'عرف' = donner les limites précises d'un concept.", "category": "verbe", "difficulty": "medium"},
    {"id": "v04", "front": "Qu'est-ce que le verbe 'استنتج' demande ?", "back": "Tirer une conclusion logique à partir des données et documents fournis.", "category": "verbe", "difficulty": "easy"},
    {"id": "v05", "front": "Quelle est la note maximale de 'استنتج' ?", "back": "10 points (tâche simple).", "category": "verbe", "difficulty": "easy"},
    {"id": "v06", "front": "Que signifie le verbe 'أنجز رسما تخطيطيا' ?", "back": "Réaliser un schéma clair, légendé et fonctionnel.", "category": "verbe", "difficulty": "easy"},
    {"id": "v07", "front": "Quelle est l'erreur fréquente avec 'أنجز رسما تخطيطيا' ?", "back": "Schéma illisible ou légendes manquantes.", "category": "verbe", "difficulty": "medium"},
    {"id": "v08", "front": "Qu'est-ce que le verbe 'عدد' demande ?", "back": "Indiquer le nombre exact d'éléments.", "category": "verbe", "difficulty": "easy"},
    {"id": "v09", "front": "Quelle est la note maximale de 'سمّ' ?", "back": "2 points (nommer un élément).", "category": "verbe", "difficulty": "easy"},
    {"id": "v10", "front": "Qu'est-ce que le verbe 'حدد' demande ?", "back": "Repérer et délimiter précisément un élément dans un ensemble.", "category": "verbe", "difficulty": "easy"},
    # === Verbes Complexes (20 cartes) ===
    {"id": "v11", "front": "Note maximale du verbe 'وضّح في نص علمي' ?", "back": "20 points (tâche complexe).", "category": "verbe", "difficulty": "easy"},
    {"id": "v12", "front": "Structure obligatoire pour 'وضّح في نص علمي' ?", "back": "Introduction → Développement → Conclusion.", "category": "verbe", "difficulty": "medium"},
    {"id": "v13", "front": "Que signifie 'أثبت' ?", "back": "Prouver / Démontrer avec des arguments et preuves.", "category": "verbe", "difficulty": "easy"},
    {"id": "v14", "front": "Note maximale de 'أثبت' ?", "back": "15 points.", "category": "verbe", "difficulty": "easy"},
    {"id": "v15", "front": "Comment structurer une réponse pour 'أثبت' ?", "back": "Arguments clairs + exploitation des documents + lien preuve → conclusion.", "category": "verbe", "difficulty": "medium"},
    {"id": "v16", "front": "Note maximale de 'برّر' ?", "back": "15 points.", "category": "verbe", "difficulty": "easy"},
    {"id": "v17", "front": "Différence entre 'برّر' et 'أثبت' ?", "back": "'برّر' = justifier pourquoi. 'أثبت' = prouver que.", "category": "verbe", "difficulty": "medium"},
    {"id": "v18", "front": "Que signifie 'فسر' ?", "back": "Expliquer / Interpréter un résultat scientifique.", "category": "verbe", "difficulty": "easy"},
    {"id": "v19", "front": "Note maximale de 'فسر' ?", "back": "15 points.", "category": "verbe", "difficulty": "easy"},
    {"id": "v20", "front": "Que signifie 'ناقش' ?", "back": "Analyser différents points de vue et prendre position argumentée.", "category": "verbe", "difficulty": "medium"},
    {"id": "v21", "front": "Note maximale de 'ناقش' ?", "back": "15 points.", "category": "verbe", "difficulty": "easy"},
    {"id": "v22", "front": "Que signifie 'اقترح فرضية' ?", "back": "Formuler une ou plusieurs hypothèses logiques et scientifiques.", "category": "verbe", "difficulty": "medium"},
    {"id": "v23", "front": "Note maximale de 'اقترح فرضية' ?", "back": "10 points.", "category": "verbe", "difficulty": "easy"},
    {"id": "v24", "front": "Exemple de verbe simple vs complexe ?", "back": "Simple : صف / عرف. Complexe : وضّح في نص علمي / أثبت.", "category": "verbe", "difficulty": "medium"},
    {"id": "v25", "front": "Qu'est-ce que le verbe 'حلّل' demande ?", "back": "Décomposer un sujet en ses éléments constitutifs pour les étudier.", "category": "verbe", "difficulty": "hard"},
    {"id": "v26", "front": "Qu'est-ce que 'قيّم' demande ?", "back": "Porter un jugement argumenté sur la validité ou la pertinence.", "category": "verbe", "difficulty": "hard"},
    {"id": "v27", "front": "Qu'est-ce que 'قارن' demande ?", "back": "Mettre en parallèle deux éléments pour identifier ressemblances et différences.", "category": "verbe", "difficulty": "hard"},
    {"id": "v28", "front": "Quand utilise-t-on une tâche complexe ?", "back": "Quand le verbe demande une explication, preuve, justification ou discussion.", "category": "verbe", "difficulty": "medium"},
    {"id": "v29", "front": "Qu'est-ce que 'استخرج' demande ?", "back": "Tirer une information d'un document ou d'un ensemble de données.", "category": "verbe", "difficulty": "easy"},
    {"id": "v30", "front": "Combien de verbes complexes existe-t-il dans la base Khawarizmi ?", "back": "11 verbes complexes (وضّح, أثبت, برّر, فسر, ناقش, اقترح فرضية, حلّل, قيّم, قارن, أنجز رسما, استنتج).", "category": "verbe", "difficulty": "medium"},
]

ERROR_FLASHCARDS = [
    {"id": "e01", "front": "Erreur fréquente avec 'وضّح في نص علمي' ?", "back": "Faire une simple liste ou description au lieu d'un texte structuré.", "category": "erreur", "difficulty": "medium"},
    {"id": "e02", "front": "Confusion classique entre verbes ?", "back": "Utiliser 'صف' alors que l'instruction demande 'وضّح في نص علمي'.", "category": "erreur", "difficulty": "medium"},
    {"id": "e03", "front": "Erreur sur 'أثبت' ?", "back": "Donner des arguments sans lien avec les documents.", "category": "erreur", "difficulty": "medium"},
    {"id": "e04", "front": "Erreur sur 'برّر' ?", "back": "Justification sans preuve scientifique.", "category": "erreur", "difficulty": "easy"},
    {"id": "e05", "front": "Erreur fréquente sur la conclusion ?", "back": "Absence de conclusion dans les tâches complexes.", "category": "erreur", "difficulty": "medium"},
    {"id": "e06", "front": "Erreur d'exploitation des documents ?", "back": "Réponse uniquement basée sur les connaissances personnelles sans citer les docs.", "category": "erreur", "difficulty": "medium"},
    {"id": "e07", "front": "Erreur sur 'اقترح فرضية' ?", "back": "Hypothèse non scientifique ou hors contexte.", "category": "erreur", "difficulty": "medium"},
    {"id": "e08", "front": "Erreur sur 'ناقش' ?", "back": "Position sans argumentation.", "category": "erreur", "difficulty": "medium"},
    {"id": "e09", "front": "Erreur de structure ?", "back": "Mélange des idées sans organisation (Introduction / Développement / Conclusion).", "category": "erreur", "difficulty": "medium"},
    {"id": "e10", "front": "Erreur sur 'فسر' ?", "back": "Explication trop descriptive au lieu d'explication scientifique.", "category": "erreur", "difficulty": "medium"},
    {"id": "e11", "front": "Erreur sur 'صف' ?", "back": "Réponse trop générale ou trop courte.", "category": "erreur", "difficulty": "easy"},
    {"id": "e12", "front": "Erreur sur 'عرف' ?", "back": "Définition trop longue ou vague, confusion avec 'صف'.", "category": "erreur", "difficulty": "easy"},
    {"id": "e13", "front": "Pourquoi perd-on des points sur l'introduction ?", "back": "Quand l'introduction ne pose pas clairement le problème scientifique.", "category": "erreur", "difficulty": "medium"},
    {"id": "e14", "front": "Erreur de hors-sujet ?", "back": "Répondre à une question différente de celle posée.", "category": "erreur", "difficulty": "medium"},
    {"id": "e15", "front": "Erreur de vocabulaire scientifique ?", "back": "Utiliser des termes approximatifs au lieu des termes exacts du programme.", "category": "erreur", "difficulty": "medium"},
    {"id": "e16", "front": "Erreur de temps ?", "back": "Passer trop de temps sur une question simple au détriment des questions à fort coefficient.", "category": "erreur", "difficulty": "easy"},
    {"id": "e17", "front": "Erreur sur 'استنتج' ?", "back": "Conclusion non justifiée ou hors sujet.", "category": "erreur", "difficulty": "medium"},
    {"id": "e18", "front": "Erreur sur 'أنجز رسما' ?", "back": "Schéma illisible ou légendes incorrectes.", "category": "erreur", "difficulty": "easy"},
    {"id": "e19", "front": "Erreur de raisonnement ?", "back": "Affirmation sans preuve, conclusion sans démonstration.", "category": "erreur", "difficulty": "medium"},
    {"id": "e20", "front": "Comment éviter les erreurs méthodologiques ?", "back": "Identifier d'abord le verbe, structurer la réponse, exploiter les documents, conclure.", "category": "erreur", "difficulty": "medium"},
]

STRUCTURE_FLASHCARDS = [
    {"id": "s01", "front": "Que doit contenir l'Introduction ?", "back": "Poser clairement le problème scientifique ou l'objectif.", "category": "structure", "difficulty": "easy"},
    {"id": "s02", "front": "Que doit contenir le Développement ?", "back": "Explication structurée + arguments + exploitation des documents.", "category": "structure", "difficulty": "medium"},
    {"id": "s03", "front": "Que doit contenir la Conclusion ?", "back": "Répondre au problème posé + synthèse des résultats.", "category": "structure", "difficulty": "easy"},
    {"id": "s04", "front": "Score maximum de la structure ?", "back": "16 points (Intro 5 + Dev 7 + Conc 4).", "category": "structure", "difficulty": "easy"},
    {"id": "s05", "front": "Marqueurs d'Introduction ?", "back": "مقدمة، المشكل، يهدف، يتمثل، الهدف من.", "category": "structure", "difficulty": "medium"},
    {"id": "s06", "front": "Marqueurs de Développement ?", "back": "عرض، تطوير، من خلال، لأن، حسب الوثيقة، نلاحظ.", "category": "structure", "difficulty": "medium"},
    {"id": "s07", "front": "Marqueurs de Conclusion ?", "back": "خاتمة، إذن، نستنتج، لذلك، مما سبق، يتبين.", "category": "structure", "difficulty": "medium"},
    {"id": "s08", "front": "Que faire si la structure est insuffisante ?", "back": "Ajouter les parties manquantes : Introduction, Développement ou Conclusion.", "category": "structure", "difficulty": "easy"},
    {"id": "s09", "front": "Pourquoi la structure est-elle importante ?", "back": "Elle permet une réponse méthodologiquement correcte pour les tâches complexes.", "category": "structure", "difficulty": "medium"},
    {"id": "s10", "front": "Exemple de mauvaise structure ?", "back": "Réponse sous forme de liste pour 'وضّح في نص علمي'.", "category": "structure", "difficulty": "medium"},
    {"id": "s11", "front": "Quand faut-il structurer sa réponse en 3 parties ?", "back": "Pour les tâches complexes uniquement (وضّح, أثبت, برّر, ناقش, فسر...).", "category": "structure", "difficulty": "medium"},
    {"id": "s12", "front": "Quelle est la partie la mieux notée de la structure ?", "back": "Le Développement (8 points sur 16).", "category": "structure", "difficulty": "easy"},
    {"id": "s13", "front": "Combien de points pour l'Introduction ?", "back": "4 points (ou 5 selon le barème utilisé).", "category": "structure", "difficulty": "easy"},
    {"id": "s14", "front": "Quel mot arabe indique le début de l'Introduction ?", "back": "مقدمة (Muqaddima).", "category": "structure", "difficulty": "easy"},
    {"id": "s15", "front": "Structure idéale d'un paragraphe de développement ?", "back": "Idée principale → Donnée du document → Analyse → Lien avec le problème.", "category": "structure", "difficulty": "hard"},
]


def get_all_methodology_flashcards():
    return VERB_FLASHCARDS + ERROR_FLASHCARDS + STRUCTURE_FLASHCARDS


def get_flashcards_by_category(category: str):
    all_cards = get_all_methodology_flashcards()
    return [card for card in all_cards if card["category"] == category]
