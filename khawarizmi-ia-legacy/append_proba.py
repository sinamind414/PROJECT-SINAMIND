import json
import os

prog_path = r'c:\Users\zakaria\Documents\SITE FEHAM\programme_maths_3as.json'
annales_path = r'c:\Users\zakaria\Documents\SITE FEHAM\annales_maths_3as.json'

# --- 1. UPDATE PROGRAMME ---
with open(prog_path, 'r', encoding='utf-8') as f:
    prog_data = json.load(f)

chapitre_4 = {
  'id': 'CHAP_MATH_04',
  'titre': 'Probabilités',
  'titre_ar': 'الاحتمالات',
  'ordre': 4,
  'description': 'Dénombrement, calcul de probabilités, probabilités conditionnelles et variables aléatoires.',
  'micro_concepts': [
    {
      'id': 'MC_PROBA_01',
      'nom': 'Dénombrement (Combinaisons, Arrangements)',
      'nom_ar': 'العد (التوفيقات، الترتيبات)',
      'description': 'Choisir le bon outil (C_n^p pour tirage simultané, A_n^p pour tirage successif sans remise, n^p avec remise).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_DEN_CONC_01', 'description': 'L\'élève utilise les arrangements A_n^p au lieu des combinaisons C_n^p pour un tirage simultané.', 'traitement_socratique': '"Dans un tirage simultané (on plonge la main et on tire 3 boules d\'un coup), l\'ordre a-t-il une importance ? Si non, quel outil mathématique ignore l\'ordre ?"'}
        ],
        'methode': [
          {'id': 'ERR_DEN_METH_01', 'description': 'Oublie de multiplier les cas dans "tirer 2 rouges ET 1 verte". Fait une addition au lieu d\'une multiplication.', 'traitement_socratique': '"En dénombrement, le mot ET se traduit par une multiplication. Le mot OU se traduit par une addition. As-tu dit ET ou OU dans ta tête ?"'}
        ],
        'execution': [
          {'id': 'ERR_DEN_EXEC_01', 'description': 'Erreur de calcul de factorielle dans C_n^p.', 'traitement_socratique': '"Tu as une calculatrice ! Utilise la touche nCr pour les combinaisons. Pas besoin de calculer les factorielles à la main et risquer une erreur."'}
        ],
        'panique': [
          {'id': 'ERR_DEN_PAN_01', 'description': 'Ne sait pas comment traiter "Au moins une boule rouge".', 'traitement_socratique': '"Le contraire de \'au moins une\', c\'est \'aucune\'. Il est beaucoup plus rapide de calculer la probabilité de ne tirer AUCUNE boule rouge et de faire 1 - P(Aucune). L\'événement contraire est ton meilleur ami."'}
        ]
      }
    },
    {
      'id': 'MC_PROBA_02',
      'nom': 'Probabilités conditionnelles et Arbres',
      'nom_ar': 'الاحتمالات الشرطية وشجرة الاحتمالات',
      'description': 'Construction d\'un arbre pondéré, formule des probabilités totales.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_COND_CONC_01', 'description': 'Confond P(A inter B) et P_A(B) (probabilité de B sachant A).', 'traitement_socratique': '"P(A inter B) c\'est \'la probabilité qu\'il pleuve ET que tu prennes un parapluie\'. P_A(B) c\'est \'SACHANT qu\'il pleut, quelle est la proba que tu prennes ton parapluie ?\'. Sur un arbre, P_A(B) est sur la branche, P(A inter B) est au bout du chemin."'}
        ],
        'methode': [
          {'id': 'ERR_COND_METH_01', 'description': 'La somme des branches issues d\'un même nœud ne fait pas 1.', 'traitement_socratique': '"Règle absolue de l\'arbre pondéré : à chaque croisement (nœud), la somme de toutes les branches qui en partent DOIT être égale à 1. Vérifie ton nœud A."'}
        ],
        'execution': [
          {'id': 'ERR_COND_EXEC_01', 'description': 'Pour les probabilités totales, l\'élève multiplie les chemins au lieu de les additionner.', 'traitement_socratique': '"Pour trouver P(B), tu dois parcourir tous les chemins qui mènent à B. On MULTIPLIE le long d\'un chemin, mais on ADDITIONNE les chemins entre eux."'}
        ],
        'panique': [
          {'id': 'ERR_COND_PAN_01', 'description': 'Panique quand on demande P_B(A) (remonter l\'arbre).', 'traitement_socratique': '"Pour remonter l\'arbre, utilise la formule de Bayes : P_B(A) = P(A inter B) / P(B). Tu viens juste de calculer P(B) à la question précédente !"'}
        ]
      }
    },
    {
      'id': 'MC_PROBA_03',
      'nom': 'Variable Aléatoire et Espérance',
      'nom_ar': 'المتغير العشوائي والأمل الرياضي',
      'description': 'Loi de probabilité X, E(X), V(X).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_VA_CONC_01', 'description': 'Ne trouve pas toutes les valeurs possibles de X (ex: X = gain du jeu).', 'traitement_socratique': '"Mets-toi à la place du joueur. Quels sont tous les scénarios possibles ? Gagner 10, perdre 5 (donc -5), ou match nul (0). Liste les valeurs avant de faire le tableau."'}
        ],
        'methode': [
          {'id': 'ERR_VA_METH_01', 'description': 'La somme des p_i dans le tableau ne vaut pas 1.', 'traitement_socratique': '"Si tu additionnes toutes les probabilités de la ligne du bas de ton tableau, tu dois OBLIGATOIREMENT trouver 1 (ou 100%). Sinon, c\'est qu\'il manque une valeur de X ou qu\'il y a une erreur de calcul."'}
        ],
        'execution': [
          {'id': 'ERR_VA_EXEC_01', 'description': 'Erreur de calcul de l\'espérance (oublie de multiplier par X_i).', 'traitement_socratique': '"L\'espérance, c\'est une moyenne pondérée. Tu dois multiplier la case du haut (la valeur) par la case du bas (la probabilité), et additionner toutes ces colonnes."'}
        ],
        'panique': [
          {'id': 'ERR_VA_PAN_01', 'description': 'Panique quand on demande si le jeu est "équitable".', 'traitement_socratique': '"Un jeu est équitable si en moyenne, tu ne gagnes rien et tu ne perds rien. Quelle valeur doit donc prendre l\'Espérance E(X) pour que ce soit le cas ? (C\'est 0 !)"'}
        ]
      }
    }
  ]
}

prog_data['chapitres'].append(chapitre_4)
with open(prog_path, 'w', encoding='utf-8') as f:
    json.dump(prog_data, f, ensure_ascii=False, indent=2)


# --- 2. UPDATE ANNALES ---
with open(annales_path, 'r', encoding='utf-8') as f:
    annales_data = json.load(f)

sujet_proba = {
  "id": "BAC_MATH_2024_SC_S1_EX4",
  "source": "Annales - Probabilités (Urne et tirages)",
  "annee": 2024,
  "filiere": "Sciences Expérimentales",
  "session": "Principale",
  "sujet": 1,
  "exercice": 4,
  "theme_principal": "CHAP_MATH_04",
  "points": 4.0,
  "enonce": "Une urne contient 4 boules rouges et 3 boules vertes indiscernables au toucher. On tire simultanément et au hasard 3 boules de l'urne. On note X la variable aléatoire correspondant au nombre de boules vertes tirées.",
  "questions": [
    {
      "id": "Q1",
      "texte": "Calculer la probabilité de tirer exactement 3 boules rouges.",
      "points": 0.5,
      "micro_concept_id": "MC_PROBA_01",
      "diagnostic_erreur_cible": "ERR_DEN_CONC_01",
      "note_pedagogique": "Tirage simultané = Combinaisons C_n^p. Si l'élève utilise A_n^p, on déclenche l'autopsy sur l'ordre."
    },
    {
      "id": "Q2",
      "texte": "Calculer la probabilité de tirer au moins une boule verte.",
      "points": 0.75,
      "micro_concept_id": "MC_PROBA_01",
      "diagnostic_erreur_cible": "ERR_DEN_PAN_01",
      "note_pedagogique": "L'élève doit utiliser l'événement contraire 1 - P(Aucune verte), soit 1 - P(3 rouges). S'il calcule tous les cas 1, 2, 3 vertes et se trompe, on lui rappelle cette astuce."
    },
    {
      "id": "Q3_a",
      "texte": "Déterminer les valeurs possibles prises par la variable aléatoire X.",
      "points": 0.5,
      "micro_concept_id": "MC_PROBA_03",
      "diagnostic_erreur_cible": "ERR_VA_CONC_01",
      "note_pedagogique": "L'élève doit lister {0, 1, 2, 3}. S'il oublie 0, c'est qu'il ne conçoit pas qu'on puisse tirer aucune boule verte."
    },
    {
      "id": "Q3_b",
      "texte": "Déterminer la loi de probabilité de X.",
      "points": 1.5,
      "micro_concept_id": "MC_PROBA_03",
      "diagnostic_erreur_cible": "ERR_VA_METH_01",
      "note_pedagogique": "Test de rigueur. Si la somme des P(X=k) n'est pas égale à 1 (ou 35/35), on déclenche l'autopsy sur la somme des p_i."
    },
    {
      "id": "Q3_c",
      "texte": "Calculer l'espérance mathématique E(X).",
      "points": 0.75,
      "micro_concept_id": "MC_PROBA_03",
      "diagnostic_erreur_cible": "ERR_VA_EXEC_01",
      "note_pedagogique": "Calcul pur de moyenne pondérée. L'IA surveille les erreurs de frappe à la calculatrice."
    }
  ]
}

annales_data['sujets'].append(sujet_proba)
with open(annales_path, 'w', encoding='utf-8') as f:
    json.dump(annales_data, f, ensure_ascii=False, indent=2)

print('Chapitre 4 (Probabilités) et Sujet 4 ajoutés avec succès !')
