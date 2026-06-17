import json
import os

filepath = r'c:\Users\zakaria\Documents\SITE FEHAM\programme_maths_3as.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

chapitre_2 = {
  'id': 'CHAP_MATH_02',
  'titre': 'Fonctions Numériques : Exponentielle et Logarithme',
  'titre_ar': 'الدوال العددية: الأسية واللوغاريتمية',
  'ordre': 2,
  'description': 'Étude complète des fonctions Ln et Exp, croissances comparées, TVI, dérivées, asymptotes et tracés de courbes.',
  'micro_concepts': [
    {
      'id': 'MC_FONC_01',
      'nom': 'Propriétés algébriques de ln et exp',
      'nom_ar': 'الخواص الجبرية للدالة الأسية واللوغاريتمية',
      'description': 'Simplification d\'expressions, ln(a*b) = ln(a)+ln(b), exp(a+b) = exp(a)*exp(b).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_ALG_CONC_01', 'description': 'L\'élève invente des règles comme ln(a+b) = ln(a)+ln(b).', 'traitement_socratique': 'Si ln(a+b) = ln(a)+ln(b), essaie avec a=1 et b=1. Est-ce que ln(2) = ln(1) + ln(1) ? Sachant que ln(1) = 0... Le log transforme uniquement la MULTIPLICATION en ADDITION.'}
        ],
        'methode': [
          {'id': 'ERR_ALG_METH_01', 'description': 'N\'utilise pas e^(ln(x)) = x ou ln(e^x) = x pour simplifier.', 'traitement_socratique': 'L\'exponentielle et le logarithme sont des ennemis jurés. Que se passe-t-il quand ils se rencontrent directement ? Ils s\'annulent !'}
        ],
        'execution': [
          {'id': 'ERR_ALG_EXEC_01', 'description': 'Erreur de signe avec les puissances et quotients : e^(a) / e^(b) devient e^(a/b) au lieu de e^(a-b).', 'traitement_socratique': 'Rappelle-toi les règles du collège sur les puissances de 10. 10^5 / 10^2, ça fait 10^3, pas 10^(2.5). C\'est la soustraction !'}
        ],
        'panique': [
          {'id': 'ERR_ALG_PAN_01', 'description': 'Panique face à ln(sqrt(x)).', 'traitement_socratique': 'Une racine carrée, c\'est juste une puissance cachée. Quelle est la puissance équivalente à une racine carrée ? C\'est 1/2. Utilise la règle ln(x^n).'}
        ]
      }
    },
    {
      'id': 'MC_FONC_02',
      'nom': 'Équations et inéquations avec exp et ln',
      'nom_ar': 'المعادلات والمتراجحات الأسية واللوغاريتمية',
      'description': 'Résolution de e^a = b, ln(a) = b, changement de variable (X = e^x).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_EQ_CONC_01', 'description': 'Applique ln des deux côtés mais sur des valeurs négatives (ex: e^x = -2 -> x = ln(-2)).', 'traitement_socratique': 'L\'exponentielle e^x est le résultat d\'une puissance de nombre positif. Peut-elle produire un nombre négatif ? Que dit ta calculatrice pour ln(-2) ?'}
        ],
        'methode': [
          {'id': 'ERR_EQ_METH_01', 'description': 'Ne reconnait pas l\'équation du second degré cachée (X = e^x) dans e^(2x) - 3e^x + 2 = 0.', 'traitement_socratique': 'Regarde bien e^(2x). C\'est la même chose que (e^x)^2. Si tu remplaces e^x par la lettre majuscule X, que devient ton équation ?'}
        ],
        'execution': [
          {'id': 'ERR_EQ_EXEC_01', 'description': 'Oublie de vérifier les conditions d\'existence (domaine de définition) pour le ln avant de garder les solutions.', 'traitement_socratique': 'Tu as trouvé x=-5. Mais regarde ton équation de départ : ln(x+2). Est-ce que tu as le droit de donner à manger -5 au logarithme ?'}
        ],
        'panique': [
          {'id': 'ERR_EQ_PAN_01', 'description': 'Se bloque devant une inéquation avec un ln(x) au dénominateur.', 'traitement_socratique': 'C\'est juste un tableau de signes ! Trouve quand ln(x) s\'annule. Quelle valeur de x donne ln(x)=0 ? (C\'est 1). Place le dans le tableau.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_03',
      'nom': 'Croissances comparées (Limites)',
      'nom_ar': 'التزايد المقارن (النهايات)',
      'description': 'Limites du type e^x/x, x*ln(x), etc.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_CC_CONC_01', 'description': 'Confusion sur \'qui gagne\' entre ln(x), x, et e^x à l\'infini.', 'traitement_socratique': 'Imagine une course vers l\'infini. ln(x) avance en marchant, x court, e^x est dans une fusée. Si on divise la fusée par le coureur (e^x / x), qui impose sa limite ?'}
        ],
        'methode': [
          {'id': 'ERR_CC_METH_01', 'description': 'Essayer d\'appliquer la croissance comparée en un point fini (ex: x->0 pour e^x/x) au lieu de l\'infini.', 'traitement_socratique': 'La croissance comparée, c\'est un duel de titans à l\'INFINI. En x=0, e^0 / 0 n\'est pas une forme indéterminée de ce type, c\'est juste 1/0.'}
        ],
        'execution': [
          {'id': 'ERR_CC_EXEC_01', 'description': 'Erreur de signe lors du passage à la limite de x*e^x en -infini (répond +infini au lieu de 0).', 'traitement_socratique': 'Attention, x tend vers -infini, mais x*e^x est une limite du cours. L\'exponentielle écrase tout et impose le zéro. 0 n\'a pas de signe absolu ici, mais il s\'approche par valeurs négatives.' }
        ],
        'panique': [
          {'id': 'ERR_CC_PAN_01', 'description': 'Abandonne face à ln(x)/x^2 parce que le cours parle de ln(x)/x.', 'traitement_socratique': 'Si le coureur x bat le marcheur ln(x), que penses-tu du coureur dopé x^2 ? Il l\'écrase encore plus vite ! La limite est la même : zéro.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_04',
      'nom': 'Théorème des Valeurs Intermédiaires (TVI)',
      'nom_ar': 'مبرهنة القيم المتوسطة',
      'description': 'Preuve de l\'existence et de l\'unicité de la solution alpha pour f(x)=k.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_TVI_CONC_01', 'description': 'L\'élève confond l\'existence de la solution (f continue) et son unicité (f strictement monotone).', 'traitement_socratique': 'Si la route monte et descend plusieurs fois, tu peux croiser la ligne d\'altitude 100m plusieurs fois. Comment garantir que tu ne la croiseras qu\'UNE SEULE fois ?'}
        ],
        'methode': [
          {'id': 'ERR_TVI_METH_01', 'description': 'Oubli de citer l\'une des 3 conditions : Continuité, Stricte Monotonie, k compris entre f(a) et f(b).', 'traitement_socratique': 'Le correcteur du BAC a une grille de mots-clés. Il cherche \'Continue\' et \'Strictement croissante/décroissante\'. Les as-tu écrits noir sur blanc ?'}
        ],
        'execution': [
          {'id': 'ERR_TVI_EXEC_01', 'description': 'Calcule mal f(a) et f(b) à la calculatrice et conclut que k n\'est pas entre les deux.', 'traitement_socratique': 'Vérifie le réglage de ta calculatrice (degrés/radians, parenthèses) et recalcule tes valeurs f(a) et f(b). Leur produit f(a)*f(b) doit être négatif si k=0.' }
        ],
        'panique': [
          {'id': 'ERR_TVI_PAN_01', 'description': 'Panique quand on lui demande \'Déduire un encadrement de alpha à 10^-2 près\'.', 'traitement_socratique': 'C\'est un jeu de \'plus grand, plus petit\' (le balayage à la calculatrice). Règle le pas (STEP) de la table sur 0.01 et cherche l\'endroit où f(x) change de signe.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_05',
      'nom': 'Dérivabilité et calcul de dérivées',
      'nom_ar': 'الاشتقاقية وحساب المشتقات',
      'description': 'Dérivées de fonctions composées exp(u) et ln(u) et des produits u*v.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_DERIV_CONC_01', 'description': 'Dérive e^(u(x)) en donnant e^(u(x)) sans multiplier par u\'(x).', 'traitement_socratique': 'L\'exponentielle est paresseuse, elle reste elle-même. Mais ce qu\'il y a DANS sa puissance est sous pression : il doit sortir et se faire dériver en premier ! u\'.e^u.'}
        ],
        'methode': [
          {'id': 'ERR_DERIV_METH_01', 'description': 'Dérive ln(u(x)) comme 1/u(x) au lieu de u\'(x)/u(x).', 'traitement_socratique': 'Le logarithme fonctionne comme un entonnoir : le bloc de l\'intérieur passe au dénominateur tel quel, mais il laisse sa dérivée au numérateur.' }
        ],
        'execution': [
          {'id': 'ERR_DERIV_EXEC_01', 'description': 'Erreur dans la dérivée du produit u*v (fait u\'*v\' au lieu de u\'v + uv\').', 'traitement_socratique': 'On ne dérive pas une multiplication en bloc. C\'est un travail d\'équipe : l\'un travaille (dérive) pendant que l\'autre se repose, puis on inverse. u\'v + uv\'.' }
        ],
        'panique': [
          {'id': 'ERR_DERIV_PAN_01', 'description': 'S\'effondre devant la dérivée de (ax+b)e^(cx) qui est le grand classique du BAC.', 'traitement_socratique': 'C\'est un u*v tout à fait normal. Identifie u, identifie v, calcule u\' et v\' proprement sur un brouillon avant d\'assembler le puzzle.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_06',
      'nom': 'Sens de variation et Tableau',
      'nom_ar': 'اتجاه التغير وجدول التغيرات',
      'description': 'Lien entre le signe de la dérivée et les variations de f.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_TAB_CONC_01', 'description': 'Oublie que le signe de f\'(x) détermine si f monte ou descend.', 'traitement_socratique': 'La dérivée f\'(x), c\'est la VITESSSE. Si la vitesse est positive, la voiture avance (monte). Si elle est négative, elle recule (descend).' }
        ],
        'methode': [
          {'id': 'ERR_TAB_METH_01', 'description': 'Ne cherche pas à factoriser f\'(x) pour trouver son signe, ou étudie le signe de termes toujours positifs (ex: e^x).', 'traitement_socratique': 'L\'exponentielle est TON AMIE. Elle est TOUJOURS positive. Tu peux complètement l\'ignorer pour l\'étude du signe et te concentrer sur l\'autre facteur de la multiplication.' }
        ],
        'execution': [
          {'id': 'ERR_TAB_EXEC_01', 'description': 'Erreur de signe dans le tableau (règle du signe du trinôme non respectée).', 'traitement_socratique': 'Pour un polynôme du second degré : signe de \'a\' à l\'extérieur des racines, signe contraire de \'a\' à l\'intérieur. Quel est le signe de \'a\' ici ?' }
        ],
        'panique': [
          {'id': 'ERR_TAB_PAN_01', 'description': 'Panique totale quand le tableau contient une valeur interdite (double barre).', 'traitement_socratique': 'La double barre, c\'est juste un mur. La courbe n\'a pas le droit d\'y toucher. Tire deux traits rouges et traite les côtés gauche et droit séparément.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_07',
      'nom': 'Asymptotes et Position Relative',
      'nom_ar': 'المستقيمات المقاربة والوضع النسبي',
      'description': 'Montrer que lim [f(x) - (ax+b)] = 0 et étudier le signe de la différence.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_ASYMP_CONC_01', 'description': 'Ne comprend pas la différence entre une asymptote horizontale (limite en l\'infini) et verticale (limite au point).', 'traitement_socratique': 'Si x part vers l\'infini et f(x) donne un nombre, c\'est un plafond horizontal. Si x s\'approche d\'un nombre et que f(x) explose vers l\'infini, c\'est un mur vertical.' }
        ],
        'methode': [
          {'id': 'ERR_ASYMP_METH_01', 'description': 'Étudie le signe de f(x) au lieu de f(x) - y pour la position relative.', 'traitement_socratique': 'Pour savoir qui est le plus grand entre Toi et Ton frère, on vous met dos à dos (on soustrait vos tailles). Pour deux courbes, c\'est pareil : on étudie le signe de la SOUSTRACTION (f(x) - y).' }
        ],
        'execution': [
          {'id': 'ERR_ASYMP_EXEC_01', 'description': 'Oublie de distribuer le signe moins lors de la soustraction f(x) - (ax+b).', 'traitement_socratique': 'Attention au tueur silencieux des mathématiques : le signe MOINS devant des parenthèses ! -(ax+b) devient -ax - b.' }
        ],
        'panique': [
          {'id': 'ERR_ASYMP_PAN_01', 'description': 'Ne sait plus quoi répondre quand on lui demande de déduire l\'asymptote oblique.', 'traitement_socratique': 'Regarde l\'expression de f(x). N\'a-t-elle pas la forme (ax+b) + (un reste qui tend vers 0) ? L\'asymptote est là, juste sous tes yeux.' }
        ]
      }
    },
    {
      'id': 'MC_FONC_08',
      'nom': 'Représentation Graphique',
      'nom_ar': 'الرسم البياني',
      'description': 'Tracé de la courbe représentative C_f en utilisant tangentes, extremums et asymptotes.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_GRAPH_CONC_01', 'description': 'Trace la courbe en traversant une asymptote verticale ou sans respecter les limites.', 'traitement_socratique': 'Une asymptote verticale est un MUR INFRANCHISSABLE. Ta courbe ne doit jamais, au grand jamais, croiser la ligne pointillée verticale.' }
        ],
        'methode': [
          {'id': 'ERR_GRAPH_METH_01', 'description': 'Oublie de placer les tangentes horizontales (extremums locaux) ou les points d\'intersection avec les axes.', 'traitement_socratique': 'Avant de tracer la courbe à main levée, place tes clous : les asymptotes (en pointillés), les extremums (traits horizontaux), et les points d\'intersection avec (Ox) et (Oy).' }
        ],
        'execution': [
          {'id': 'ERR_GRAPH_EXEC_01', 'description': 'Mauvaise échelle sur le repère (ne lit pas l\'énoncé qui dit 2cm pour l\'unité).', 'traitement_socratique': 'Le correcteur va mesurer avec sa règle. Si l\'énoncé dit 1 unité = 2cm, tu dois prendre 2 carreaux (souvent 1cm/carreau) pour le 1 !' }
        ],
        'panique': [
          {'id': 'ERR_GRAPH_PAN_01', 'description': 'La peur de mal dessiner fige l\'élève à la fin de l\'épreuve.', 'traitement_socratique': 'Ta courbe ne sera jamais parfaite et on ne te demande pas d\'être Picasso. On veut voir : asymptotes respectées, sommets au bon endroit, et courbure logique. Fais un brouillon, puis trace en une seule fois.' }
        ]
      }
    }
  ]
}

data['chapitres'].append(chapitre_2)

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Chapitre 2 (Exponentielle et Logarithme) ajouté avec succès. ' + str(len(data['chapitres'])) + ' chapitres maintenant dans le fichier.')
