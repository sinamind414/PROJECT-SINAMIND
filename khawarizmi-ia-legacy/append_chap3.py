import json
import os

filepath = r'c:\Users\zakaria\Documents\SITE FEHAM\programme_maths_3as.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

chapitre_3 = {
  'id': 'CHAP_MATH_03',
  'titre': 'Les Nombres Complexes',
  'titre_ar': 'الأعداد المركبة',
  'ordre': 3,
  'description': 'Étude des nombres complexes : formes algébrique, trigonométrique, exponentielle, géométrie du plan, équations du 2nd degré, et transformations complexes.',
  'micro_concepts': [
    {
      'id': 'MC_COMP_01',
      'nom': 'Forme algébrique et Conjugué',
      'nom_ar': 'الشكل الجبري والمرافق',
      'description': 'Opérations sur z = x + iy, calcul de puissances de i, utilisation du conjugué pour diviser.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_ALG_CONC_01', 'description': 'L\'élève pense que la partie imaginaire inclut le i (ex: y = 2i au lieu de y = 2).', 'traitement_socratique': 'La partie imaginaire est un nombre réel. C\'est le coefficient devant le i. Si z = 3 + 4i, la partie réelle est 3 et la partie imaginaire est 4, pas 4i !'}
        ],
        'methode': [
          {'id': 'ERR_ALG_METH_01', 'description': 'Ne sait pas comment écrire une fraction 1/(a+ib) sous forme algébrique.', 'traitement_socratique': 'On n\'aime pas les i au dénominateur. Pour s\'en débarrasser, on utilise l\'arme absolue : on multiplie en haut et en bas par le conjugué du dénominateur.'}
        ],
        'execution': [
          {'id': 'ERR_ALG_EXEC_01', 'description': 'Oublie que i^2 = -1 lors du développement (ex: (2+i)^2 calculé comme 4 + i^2 au lieu de 4 + 4i - 1).', 'traitement_socratique': 'Attention aux identités remarquables ! (a+b)^2 = a^2 + 2ab + b^2. Et n\'oublie pas le super-pouvoir de i : dès qu\'il est au carré, il se transforme en -1.'}
        ],
        'panique': [
          {'id': 'ERR_ALG_PAN_01', 'description': 'Panique face à i^2026.', 'traitement_socratique': 'Les puissances de i tournent en rond par cycles de 4 : i, -1, -i, 1. Divise 2026 par 4, prends le reste, et tu auras ta réponse instantanément.'}
        ]
      }
    },
    {
      'id': 'MC_COMP_02',
      'nom': 'Forme Trigonométrique, Module et Argument',
      'nom_ar': 'الشكل المثلثي، الطويلة والعمدة',
      'description': 'Calcul de r = |z| et de l\'argument theta, passage de la forme algébrique à trigonométrique.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_TRIG_CONC_01', 'description': 'Confond l\'argument (un angle en radians) avec le module (une distance positive).', 'traitement_socratique': 'Imagine le nombre complexe comme un point sur un radar. Le module, c\'est la distance jusqu\'au centre (positive). L\'argument, c\'est l\'angle de rotation pour pointer vers lui.'}
        ],
        'methode': [
          {'id': 'ERR_TRIG_METH_01', 'description': 'Ne sait pas placer l\'angle dans le bon quadrant trigonométrique après avoir calculé cos et sin.', 'traitement_socratique': 'Fais un petit dessin du cercle ! Si cos est négatif et sin est positif, tu es dans le quart en haut à gauche. L\'angle sera donc pi - alpha.'}
        ],
        'execution': [
          {'id': 'ERR_TRIG_EXEC_01', 'description': 'Erreur de calcul du module |z| = sqrt(x^2 + y^2) en incluant le i (fait sqrt(x^2 - y^2)).', 'traitement_socratique': 'Alerte rouge ! Le i n\'entre JAMAIS dans le calcul du module. Le module c\'est Pythagore avec des longueurs réelles : x au carré PLUS y au carré.'}
        ],
        'panique': [
          {'id': 'ERR_TRIG_PAN_01', 'description': 'Bloque quand on lui demande l\'argument d\'un nombre réel pur négatif (ex: z = -5).', 'traitement_socratique': 'Pas besoin de calculs compliqués ! -5 est sur l\'axe des réels, à gauche. Quel angle dois-tu faire depuis l\'axe de droite pour regarder vers la gauche ? Un demi-tour exact : Pi !'}
        ]
      }
    },
    {
      'id': 'MC_COMP_03',
      'nom': 'Forme Exponentielle et Formule de Moivre',
      'nom_ar': 'الشكل الأسي ودستور موافر',
      'description': 'Utilisation de z = r e^(i theta) pour simplifier les puissances (z^n).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_EXP_CONC_01', 'description': 'Pense que r e^(i theta) + r\' e^(i theta\') = (r+r\') e^(i(theta+theta\')).', 'traitement_socratique': 'L\'exponentielle transforme les multiplications en additions d\'angles, MAIS elle ne marche absolument pas pour les additions directes. Repasse par la forme algébrique si tu dois additionner !'}
        ],
        'methode': [
          {'id': 'ERR_EXP_METH_01', 'description': 'Essaie de calculer (1+i)^10 en développant la forme algébrique.', 'traitement_socratique': 'Développer à la puissance 10 te prendrait 3 heures. Passe le nombre sous forme exponentielle ! La puissance 10 va juste multiplier l\'angle par 10 grâce à Moivre.'}
        ],
        'execution': [
          {'id': 'ERR_EXP_EXEC_01', 'description': 'Oublie de mettre le module r à la puissance n dans z^n = r^n e^(in theta).', 'traitement_socratique': 'La puissance s\'applique à tout le monde. L\'angle est multiplié par n, mais le module r, qui est une distance, est bien mis à la puissance n !'}
        ],
        'panique': [
          {'id': 'ERR_EXP_PAN_01', 'description': 'Fige devant la consigne "Montrer que (z/z\')^2024 est un réel".', 'traitement_socratique': 'Un nombre est réel si son argument est un multiple de Pi (k*Pi). Calcule juste l\'argument de la fraction avec les propriétés de l\'exponentielle, multiplie par 2024, et regarde si ça fait k*Pi.'}
        ]
      }
    },
    {
      'id': 'MC_COMP_04',
      'nom': 'Équations du second degré dans C',
      'nom_ar': 'معادلات الدرجة الثانية في مجموعة الأعداد المركبة',
      'description': 'Résolution de az^2 + bz + c = 0 avec Delta négatif.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_EQ2_CONC_01', 'description': 'Arrête l\'exercice car Delta est négatif et "pas de solution".', 'traitement_socratique': 'Tu n\'es plus chez les réels ! Chez les complexes, un Delta négatif est une excellente nouvelle. Il admet deux racines complexes conjuguées. Remplace le signe - par i^2.'}
        ],
        'methode': [
          {'id': 'ERR_EQ2_METH_01', 'description': 'Ne sait pas trouver les racines de Delta si Delta est lui-même complexe (ex: Delta = 3 + 4i).', 'traitement_socratique': 'Si Delta n\'est pas réel, pose w = x + iy tel que w^2 = Delta. Cela va te donner un petit système de 3 équations réelles (dont x^2+y^2 = |Delta|).'}
        ],
        'execution': [
          {'id': 'ERR_EQ2_EXEC_01', 'description': 'Erreur de signe dans l\'application de la formule (-b +/- i sqrt(-Delta)) / 2a.', 'traitement_socratique': 'Attention à la formule ! C\'est -b, pas b. Et on divise par 2a, pas juste 2. Prends le temps de poser a=..., b=..., c=... au brouillon.'}
        ],
        'panique': [
          {'id': 'ERR_EQ2_PAN_01', 'description': 'Se bloque devant z^3 + 8 = 0.', 'traitement_socratique': 'C\'est une équation de degré 3. L\'énoncé te demande toujours de vérifier qu\'une racine évidente (comme -2) marche, puis de factoriser par (z - racine) pour retomber sur un degré 2 !'}
        ]
      }
    },
    {
      'id': 'MC_COMP_05',
      'nom': 'Ensembles de points',
      'nom_ar': 'مجموعة النقط',
      'description': 'Recherche du lieu géométrique de M(z) : cercles ou médiatrices.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_ENS_CONC_01', 'description': 'Ne fait pas le lien géométrique : voit |z - zA| comme un calcul abstrait au lieu de la distance AM.', 'traitement_socratique': 'Magie des complexes : le module d\'une différence, c\'est une DISTANCE. |z - zA|, c\'est littéralement la distance AM avec ta règle ! Que signifie AM = 5 ?'}
        ],
        'methode': [
          {'id': 'ERR_ENS_METH_01', 'description': 'Essaie de remplacer z par x+iy et de résoudre de longues équations cartésiennes pour |z-zA| = |z-zB|.', 'traitement_socratique': 'Tu te noies dans les calculs (x, y) ! Traduis-le géométriquement. AM = BM. Où sont les points situés à égale distance de A et de B ? Sur la médiatrice de [AB] ! Terminé.'}
        ],
        'execution': [
          {'id': 'ERR_ENS_EXEC_01', 'description': 'Erreur dans l\'identification du centre : lit |z + 3 - 2i| = r et dit que le centre est A(3; -2).', 'traitement_socratique': 'Attention, la formule c\'est |z - zA|. Il faut factoriser le signe MOINS. |z - (-3 + 2i)|. Donc le centre est A(-3; 2). Les signes sont inversés.'}
        ],
        'panique': [
          {'id': 'ERR_ENS_PAN_01', 'description': 'Panique face à arg(z - zA) = Pi/4.', 'traitement_socratique': 'L\'argument, c\'est un angle. Cela veut dire que l\'angle entre le vecteur unitaire horizontal et le vecteur AM est constant. C\'est donc une demi-droite d\'origine A !'}
        ]
      }
    },
    {
      'id': 'MC_COMP_06',
      'nom': 'Interprétation géométrique du rapport (zC-zA)/(zB-zA)',
      'nom_ar': 'التفسير الهندسي للنسبة',
      'description': 'Utilisation du rapport pour trouver la nature d\'un triangle ou l\'alignement.',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_RAP_CONC_01', 'description': 'L\'élève calcule le rapport mais ne sait pas interpréter le module et l\'argument séparément.', 'traitement_socratique': 'Ce rapport est une mine d\'or. Son MODULE te donne le rapport des longueurs AC/AB. Son ARGUMENT te donne l\'angle géométrique (AB, AC). Que se passe-t-il si l\'angle est de Pi/2 ?'}
        ],
        'methode': [
          {'id': 'ERR_RAP_METH_01', 'description': 'Conclut qu\'un triangle est isocèle et rectangle juste parce que le rapport donne i, sans le prouver.', 'traitement_socratique': 'Si le rapport vaut i, quel est son module ? |i| = 1, donc AC=AB (isocèle). Quel est son argument ? arg(i) = Pi/2, donc angle droit (rectangle). Écris ces deux étapes clairement !'}
        ],
        'execution': [
          {'id': 'ERR_RAP_EXEC_01', 'description': 'Fait une erreur dans le calcul du rapport complexe (erreur de conjugué au dénominateur).', 'traitement_socratique': 'Prends ton temps pour la division. Multiplie soigneusement par le conjugué du dénominateur, numérateur et dénominateur. Vérifie tes signes.'}
        ],
        'panique': [
          {'id': 'ERR_RAP_PAN_01', 'description': 'Le calcul du rapport donne une expression horrible et il ne trouve pas de forme trigonométrique.', 'traitement_socratique': 'Si le résultat est très moche, 99% du temps tu as fait une erreur de calcul juste avant pour zA, zB ou zC. Au BAC algérien, ce rapport donne TOUJOURS quelque chose de propre (comme i, -1/2 + i sqrt(3)/2, etc.). Refais le calcul.'}
        ]
      }
    },
    {
      'id': 'MC_COMP_07',
      'nom': 'Transformations du plan complexe',
      'nom_ar': 'التحويلات النقطية في المستوي',
      'description': 'Translation, Homothétie, Rotation (z\' = az + b).',
      'error_autopsy': {
        'concept': [
          {'id': 'ERR_TRANS_CONC_01', 'description': 'Ne comprend pas la différence entre l\'écriture complexe (z\' = az + b) et la nature géométrique.', 'traitement_socratique': 'Tout dépend du nombre complexe "a". Si a=1, on glisse (translation). Si "a" est un réel différent de 1, on zoome (homothétie). Si "a" est complexe de module 1, on tourne (rotation).'}
        ],
        'methode': [
          {'id': 'ERR_TRANS_METH_01', 'description': 'Ne sait pas trouver le centre Oméga d\'une rotation ou homothétie.', 'traitement_socratique': 'Le centre, c\'est le point qui ne bouge pas pendant la transformation (point invariant). Remplace z\' et z par z_omega et résous l\'équation ! z_omega = a z_omega + b.'}
        ],
        'execution': [
          {'id': 'ERR_TRANS_EXEC_01', 'description': 'Erreur lors du calcul de l\'image d\'un point par une rotation : confond angle et module.', 'traitement_socratique': 'Dans z\' - w = e^(i theta) * (z - w), e^(i theta) est juste un nombre complexe. Remplace le par sa forme algébrique (cos theta + i sin theta) pour faire ton calcul.'}
        ],
        'panique': [
          {'id': 'ERR_TRANS_PAN_01', 'description': 'Se bloque sur "Reconnaître la transformation f".', 'traitement_socratique': 'Regarde juste le nombre "a" collé à z. Est-ce qu\'il vaut 1 ? Non. Est-ce qu\'il est réel ? Non. Calcule son module. S\'il vaut 1, c\'est une rotation !'}
        ]
      }
    }
  ]
}

data['chapitres'].append(chapitre_3)

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Chapitre 3 (Nombres Complexes) ajouté avec succès. ' + str(len(data['chapitres'])) + ' chapitres maintenant dans le fichier.')
