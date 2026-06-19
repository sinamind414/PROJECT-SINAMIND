// src/lib/annales-bac.ts
// Types et données — Annales immersives Bac SVT SE (10 sujets, 2 sous-sujets chacun)

export type ExerciceType = "qcm" | "analyse_document" | "raisonnement" | "schema" | "argumentation"

export interface DocumentRef {
  titre: string
  nature: string
  description: string
}

export interface Question {
  id: string
  texte: string
  verb: string
  points: number
  indices?: string[]
}

export interface Exercice {
  id: string
  titre: string
  type: ExerciceType
  duree_minutes: number
  points: number
  documents: DocumentRef[]
  questions: Question[]
}

export interface BacSubSubject {
  id: "subject-1" | "subject-2"
  titleAr: string
  estimatedPages: number
  estimatedMinutes: number
  linkedChapters: string[]
  linkedVerbs: string[]
  difficulty: string
  exercises: Exercice[]
}

export interface SujetBac {
  slug: string
  annee: number
  session: "normale" | "rattrapage"
  matiere: string
  filiere: string
  titre: string
  difficulte: "facile" | "moyen" | "difficile"
  duree: number
  totalPages: number
  chapitres: string[]
  url_pdf: string
  url_corrige?: string
  exercices: Exercice[]
  subjects: BacSubSubject[]
}

const SUJETS: SujetBac[] = [
  {
    slug: "bac-svt-se-2025",
    annee: 2025,
    session: "normale",
    matiere: "SVT",
    filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2025",
    difficulte: "moyen",
    duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie", "Système nerveux"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2025",
    url_corrige: "https://www.dzexams.com/fr/sujets/bac-svt-se-2025-corrige",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: الآليات الجزيئية للوراثة",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Décrire", "Comparer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex1-2025", titre: "Mécanismes de la transcription", type: "raisonnement",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Schéma de la transcription eucaryote" }],
            questions: [
              { id: "q1-2025", texte: "Décrivez le déroulement de la transcription chez les eucaryotes.", verb: "Décrire", points: 4, indices: ["Regarde le schéma", "Pense à l'ARN polymérase"] },
              { id: "q2-2025", texte: "Comparez la transcription procaryote et eucaryote.", verb: "Comparer", points: 4 },
            ]
          },
          {
            id: "ex1b-2025", titre: "Mutations et conséquences", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 2", nature: "Tableau", description: "Comparaison de séquences d'ADN normales et mutées" }],
            questions: [
              { id: "q1b-2025", texte: "Identifiez le type de mutation présenté.", verb: "Identifier", points: 4 },
              { id: "q2b-2025", texte: "Expliquez l'impact de cette mutation sur la protéine produite.", verb: "Expliquer", points: 6, indices: ["Décalage du cadre de lecture", "Codon stop"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: المناعة والدفاع عن الذات",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Analyser", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex2-2025", titre: "Réponse immunitaire adaptative", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Évolution des anticorps après infection" }],
            questions: [
              { id: "q3-2025", texte: "Identifiez les cellules impliquées dans la réponse humorale.", verb: "Identifier", points: 3 },
              { id: "q4-2025", texte: "Expliquez la coopération cellulaire LB-LT.", verb: "Expliquer", points: 7, indices: ["Antigène", "Présentation", "Activation"] },
            ]
          },
          {
            id: "ex2b-2025", titre: "Mémoire immunitaire", type: "raisonnement",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Expérience de seconde injection antigénique" }],
            questions: [
              { id: "q5-2025", texte: "Expliquez le phénomène de mémoire immunitaire.", verb: "Expliquer", points: 4 },
              { id: "q6-2025", texte: "Comparez réponse primaire et réponse secondaire.", verb: "Comparer", points: 4, indices: ["Délai", "Intensité"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2024",
    annee: 2024, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2024", difficulte: "moyen", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie", "Système nerveux"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2024",
    url_corrige: "https://www.dzexams.com/fr/sujets/bac-svt-se-2024-corrige",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: بنية المادة الوراثية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Décrire", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex1-2024", titre: "Structure de l'ADN", type: "analyse_document",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Structure en double hélice" }],
            questions: [
              { id: "q1-2024", texte: "Décrivez la structure de l'ADN.", verb: "Décrire", points: 4 },
              { id: "q2-2024", texte: "Expliquez le mécanisme de réplication.", verb: "Expliquer", points: 5, indices: ["ADN polymérase", "Brin leader"] },
            ]
          },
          {
            id: "ex1b-2024", titre: "Expression de l'information génétique", type: "raisonnement",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Étapes de l'expression génique" }],
            questions: [
              { id: "q1b-2024", texte: "Définissez les termes : exon, intron, épissage.", verb: "Définir", points: 3 },
              { id: "q2b-2024", texte: "Expliquez le devenir du pré-ARNm après transcription.", verb: "Expliquer", points: 6, indices: ["Maturation", "Épissage", "Export nucléaire"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: نقص المناعة المكتسب",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Analyser", "Proposer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex2-2024", titre: "Immunité et SIDA", type: "raisonnement",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Tableau", description: "Taux de LT4 chez un patient VIH" }],
            questions: [
              { id: "q3-2024", texte: "Analysez l'évolution des LT4.", verb: "Analyser", points: 4 },
              { id: "q4-2024", texte: "Proposez une explication à la perte d'immunité.", verb: "Proposer", points: 5 },
            ]
          },
          {
            id: "ex2b-2024", titre: "Moyens de lutte contre le VIH", type: "argumentation",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Traitements antirétroviraux actuels" }],
            questions: [
              { id: "q5-2024", texte: "Expliquez le mode d'action des antirétroviraux.", verb: "Expliquer", points: 4 },
              { id: "q6-2024", texte: "Discutez de l'efficacité de la trithérapie.", verb: "Discuter", points: 5, indices: ["Synergie", "Résistance", "Observance"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2023",
    annee: 2023, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2023", difficulte: "moyen", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie", "Enzymologie"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2023",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: الأنزيمات والتنظيم",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Enzymologie"], linkedVerbs: ["Définir", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex1-2023", titre: "Activité enzymatique", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Cinétique enzymatique" }],
            questions: [
              { id: "q1-2023", texte: "Définissez la notion de site actif.", verb: "Définir", points: 3 },
              { id: "q2-2023", texte: "Expliquez l'influence de la température sur l'activité enzymatique.", verb: "Expliquer", points: 7, indices: ["Dénaturation", "Énergie d'activation"] },
            ]
          },
          {
            id: "ex1b-2023", titre: "Spécificité enzymatique", type: "analyse_document",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Complexe enzyme-substrat" }],
            questions: [
              { id: "q1b-2023", texte: "Représentez le modèle clé-serrure.", verb: "Représenter", points: 4 },
              { id: "q2b-2023", texte: "Comparez les modèles de Fischer et Koshland.", verb: "Comparer", points: 4, indices: ["Flexibilité", "Induction"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: المناعة الخلطية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Expliquer", "Décrire"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex2-2023", titre: "Réponse humorale", type: "raisonnement",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Cinétique de production d'anticorps" }],
            questions: [
              { id: "q3-2023", texte: "Décrivez le rôle des plasmocytes.", verb: "Décrire", points: 4 },
              { id: "q4-2023", texte: "Expliquez le phénomène de commutation isotypique.", verb: "Expliquer", points: 5, indices: ["IgM", "IgG", "Cytokines"] },
            ]
          },
          {
            id: "ex2b-2023", titre: "Réaction antigène-anticorps", type: "analyse_document",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Précipitation antigène-anticorps" }],
            questions: [
              { id: "q5-2023", texte: "Expliquez le principe de la précipitation.", verb: "Expliquer", points: 4 },
              { id: "q6-2023", texte: "Décrivez une application diagnostique de cette réaction.", verb: "Décrire", points: 4, indices: ["Tests sérologiques", "ELISA"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2022",
    annee: 2022, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2022", difficulte: "difficile", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie", "Système nerveux", "Enzymologie"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2022",
    url_corrige: "https://www.dzexams.com/fr/sujets/bac-svt-se-2022-corrige",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: التشابك العصبي",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Système nerveux"], linkedVerbs: ["Représenter", "Expliquer"],
        difficulty: "difficile",
        exercises: [
          {
            id: "ex1-2022", titre: "Transmission synaptique", type: "schema",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Synapse chimique" }],
            questions: [
              { id: "q1-2022", texte: "Représentez le mécanisme de la transmission synaptique.", verb: "Représenter", points: 5 },
              { id: "q2-2022", texte: "Expliquez le rôle des neurotransmetteurs.", verb: "Expliquer", points: 5, indices: ["Neuropeptides", "Récepteurs"] },
            ]
          },
          {
            id: "ex1b-2022", titre: "Intégration nerveuse", type: "raisonnement",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Circuits neuronaux" }],
            questions: [
              { id: "q1b-2022", texte: "Définissez la sommation spatiale et temporelle.", verb: "Définir", points: 4 },
              { id: "q2b-2022", texte: "Expliquez comment le système nerveux intègre les signaux.", verb: "Expliquer", points: 5, indices: ["PPSE", "PPSI", "Seuil de déclenchement"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: التنوع المناعي",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie", "Génétique"], linkedVerbs: ["Expliquer", "Comparer"],
        difficulty: "difficile",
        exercises: [
          {
            id: "ex2-2022", titre: "Génération de la diversité des anticorps", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Réarrangements géniques des immunoglobulines" }],
            questions: [
              { id: "q3-2022", texte: "Expliquez le mécanisme de recombination V(D)J.", verb: "Expliquer", points: 6, indices: ["RAG", "Segments V/J/C"] },
              { id: "q4-2022", texte: "Justifiez la diversité potentielle des anticorps.", verb: "Justifier", points: 4 },
            ]
          },
          {
            id: "ex2b-2022", titre: "Sélection clonale", type: "raisonnement",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Théorie de Burnet" }],
            questions: [
              { id: "q5-2022", texte: "Expliquez la théorie de la sélection clonale.", verb: "Expliquer", points: 4 },
              { id: "q6-2022", texte: "Quelle est la différence entre tolérance centrale et périphérique ?", verb: "Comparer", points: 4 },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2021",
    annee: 2021, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2021", difficulte: "facile", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2021",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: الشيفرة الوراثية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Définir", "Citer"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex1-2021", titre: "Code génétique", type: "qcm",
            duree_minutes: 30, points: 6,
            documents: [{ titre: "Doc 1", nature: "Tableau", description: "Tableau du code génétique" }],
            questions: [
              { id: "q1-2021", texte: "Qu'est-ce qu'un codon ?", verb: "Définir", points: 2 },
              { id: "q2-2021", texte: "Citez les caractéristiques du code génétique.", verb: "Citer", points: 4 },
            ]
          },
          {
            id: "ex1b-2021", titre: "Brin matrice et traduction", type: "analyse_document",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Brin d'ADN et ARNm correspondant" }],
            questions: [
              { id: "q1b-2021", texte: "Transcrivez la séquence d'ADN donnée en ARNm.", verb: "Réaliser", points: 4 },
              { id: "q2b-2021", texte: "Traduisez l'ARNm en séquence peptidique.", verb: "Réaliser", points: 4, indices: ["Codon start", "Code génétique"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: الاستجابة الالتهابية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Décrire", "Expliquer"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex2-2021", titre: "Réponse inflammatoire", type: "raisonnement",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 1", nature: "Texte", description: "Description de l'inflammation" }],
            questions: [
              { id: "q3-2021", texte: "Décrivez les étapes de la réaction inflammatoire.", verb: "Décrire", points: 4 },
              { id: "q4-2021", texte: "Expliquez le rôle des phagocytes.", verb: "Expliquer", points: 4 },
            ]
          },
          {
            id: "ex2b-2021", titre: "Médiateurs chimiques", type: "analyse_document",
            duree_minutes: 35, points: 7,
            documents: [{ titre: "Doc 2", nature: "Tableau", description: "Principaux médiateurs de l'inflammation" }],
            questions: [
              { id: "q5-2021", texte: "Citez trois médiateurs de l'inflammation et leur rôle.", verb: "Citer", points: 3 },
              { id: "q6-2021", texte: "Expliquez le rôle de l'histamine.", verb: "Expliquer", points: 4, indices: ["Vasodilatation", "Perméabilité"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2020",
    annee: 2020, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2020", difficulte: "moyen", duree: 180,
    totalPages: 10,
    chapitres: ["Système nerveux", "Immunologie", "Génétique"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2020",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: السيالة العصبية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Système nerveux"], linkedVerbs: ["Décrire", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex1-2020", titre: "Potentiel d'action", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Courbe du potentiel d'action" }],
            questions: [
              { id: "q1-2020", texte: "Décrivez les phases du potentiel d'action.", verb: "Décrire", points: 5, indices: ["Dépolarisation", "Repolarisation"] },
              { id: "q2-2020", texte: "Expliquez le rôle des canaux ioniques.", verb: "Expliquer", points: 5 },
            ]
          },
          {
            id: "ex1b-2020", titre: "Propagation du message nerveux", type: "schema",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Propagation saltatoire" }],
            questions: [
              { id: "q1b-2020", texte: "Représentez la propagation du message le long du neurone.", verb: "Représenter", points: 5 },
              { id: "q2b-2020", texte: "Expliquez le rôle de la gaine de myéline.", verb: "Expliquer", points: 4, indices: ["Isolant", "Vitesse", "Saltatoire"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: المناعة والمشكلات الصحية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie", "Génétique"], linkedVerbs: ["Analyser", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex2-2020", titre: "Déficit immunitaire", type: "analyse_document",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Tableau", description: "Numération formule sanguine d'un patient" }],
            questions: [
              { id: "q3-2020", texte: "Analysez les résultats de la NFS.", verb: "Analyser", points: 4 },
              { id: "q4-2020", texte: "Proposez un diagnostic.", verb: "Proposer", points: 5, indices: ["Leucopénie", "Lymphopénie"] },
            ]
          },
          {
            id: "ex2b-2020", titre: "Allergies et auto-immunité", type: "raisonnement",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Cas clinique d'allergie" }],
            questions: [
              { id: "q5-2020", texte: "Expliquez la différence entre allergie et auto-immunité.", verb: "Expliquer", points: 4 },
              { id: "q6-2020", texte: "Décrivez la réaction IgE-dépendante.", verb: "Décrire", points: 4, indices: ["Mastocytes", "Histamine"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2019",
    annee: 2019, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2019", difficulte: "difficile", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Enzymologie", "Système nerveux"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2019",
    url_corrige: "https://www.dzexams.com/fr/sujets/bac-svt-se-2019-corrige",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: الطفرات الوراثية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Définir", "Comparer"],
        difficulty: "difficile",
        exercises: [
          {
            id: "ex1-2019", titre: "Mutations génétiques", type: "raisonnement",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Différents types de mutations" }],
            questions: [
              { id: "q1-2019", texte: "Définissez la notion de mutation génique.", verb: "Définir", points: 3 },
              { id: "q2-2019", texte: "Comparez mutation ponctuelle et chromosomique.", verb: "Comparer", points: 6, indices: ["Échelle", "Conséquences"] },
            ]
          },
          {
            id: "ex1b-2019", titre: "Agents mutagènes", type: "analyse_document",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Tableau", description: "Effets de différents agents mutagènes" }],
            questions: [
              { id: "q1b-2019", texte: "Citez trois agents mutagènes physiques.", verb: "Citer", points: 3 },
              { id: "q2b-2019", texte: "Expliquez le mécanisme d'action des rayonnements UV.", verb: "Expliquer", points: 6, indices: ["Dimères de thymine", "Réparation"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: الأنزيمات والطاقة الحيوية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Enzymologie", "Système nerveux"], linkedVerbs: ["Expliquer", "Schématiser"],
        difficulty: "difficile",
        exercises: [
          {
            id: "ex2-2019", titre: "Régulation enzymatique", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Cinétique en présence d'inhibiteur" }],
            questions: [
              { id: "q3-2019", texte: "Comparez inhibition compétitive et non compétitive.", verb: "Comparer", points: 5 },
              { id: "q4-2019", texte: "Expliquez l'importance de la régulation enzymatique pour la cellule.", verb: "Expliquer", points: 5, indices: ["Économie d'énergie", "Homéostasie"] },
            ]
          },
          {
            id: "ex2b-2019", titre: "Métabolisme énergétique", type: "schema",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Chaîne respiratoire mitochondriale" }],
            questions: [
              { id: "q5-2019", texte: "Schématisez la chaîne respiratoire.", verb: "Schématiser", points: 5 },
              { id: "q6-2019", texte: "Expliquez le rôle de l'ATP synthase.", verb: "Expliquer", points: 4, indices: ["Gradient de protons", "Phosphorylation oxydative"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2018",
    annee: 2018, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2018", difficulte: "facile", duree: 180,
    totalPages: 10,
    chapitres: ["Immunologie", "Génétique"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2018",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: بنية الأجسام المضادة",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Décrire", "Expliquer"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex1-2018", titre: "Anticorps et antigènes", type: "analyse_document",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Structure d'un anticorps" }],
            questions: [
              { id: "q1-2018", texte: "Décrivez la structure d'un anticorps.", verb: "Décrire", points: 4 },
              { id: "q2-2018", texte: "Expliquez la spécificité antigène-anticorps.", verb: "Expliquer", points: 4 },
            ]
          },
          {
            id: "ex1b-2018", titre: "Les classes d'immunoglobulines", type: "qcm",
            duree_minutes: 30, points: 6,
            documents: [{ titre: "Doc 2", nature: "Tableau", description: "Caractéristiques des 5 classes d'Ig" }],
            questions: [
              { id: "q1b-2018", texte: "Citez les 5 classes d'immunoglobulines.", verb: "Citer", points: 2 },
              { id: "q2b-2018", texte: "Associez chaque classe à son rôle principal.", verb: "Associer", points: 4 },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: الأمراض الوراثية",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Expliquer", "Analyser"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex2-2018", titre: "Maladies héréditaires", type: "analyse_document",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 1", nature: "Arbre généalogique", description: "Transmission d'une maladie récessive" }],
            questions: [
              { id: "q3-2018", texte: "Analysez l'arbre généalogique.", verb: "Analyser", points: 4 },
              { id: "q4-2018", texte: "Déterminez le mode de transmission.", verb: "Déterminer", points: 5, indices: ["Récessif", "Autosomique"] },
            ]
          },
          {
            id: "ex2b-2018", titre: "Conseil génétique", type: "argumentation",
            duree_minutes: 35, points: 7,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Cas d'une famille à risque" }],
            questions: [
              { id: "q5-2018", texte: "Expliquez l'intérêt du conseil génétique.", verb: "Expliquer", points: 3 },
              { id: "q6-2018", texte: "Discutez des enjeux éthiques du diagnostic prénatal.", verb: "Discuter", points: 4 },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2017",
    annee: 2017, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2017", difficulte: "moyen", duree: 180,
    totalPages: 10,
    chapitres: ["Système nerveux", "Immunologie", "Génétique", "Enzymologie"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2017",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: المشبك العصبي",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Système nerveux"], linkedVerbs: ["Représenter", "Expliquer"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex1-2017", titre: "Libération des neurotransmetteurs", type: "schema",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Vésicules synaptiques" }],
            questions: [
              { id: "q1-2017", texte: "Représentez la libération des neurotransmetteurs.", verb: "Représenter", points: 5, indices: ["Calcium", "Exocytose"] },
              { id: "q2-2017", texte: "Expliquez le rôle du calcium dans ce mécanisme.", verb: "Expliquer", points: 5 },
            ]
          },
          {
            id: "ex1b-2017", titre: "Récepteurs synaptiques", type: "analyse_document",
            duree_minutes: 45, points: 9,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Récepteurs ionotropes et métabotropes" }],
            questions: [
              { id: "q1b-2017", texte: "Comparez récepteurs ionotropes et métabotropes.", verb: "Comparer", points: 5 },
              { id: "q2b-2017", texte: "Expliquez le rôle des seconds messagers.", verb: "Expliquer", points: 4, indices: ["AMPc", "Protéine G"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: الأنزيمات في المجال الصحي",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Enzymologie", "Immunologie"], linkedVerbs: ["Expliquer", "Analyser"],
        difficulty: "moyen",
        exercises: [
          {
            id: "ex2-2017", titre: "Inhibiteurs enzymatiques médicamenteux", type: "analyse_document",
            duree_minutes: 50, points: 10,
            documents: [{ titre: "Doc 1", nature: "Graphique", description: "Effet d'un médicament sur l'activité enzymatique" }],
            questions: [
              { id: "q3-2017", texte: "Analysez l'effet de l'inhibiteur sur la cinétique.", verb: "Analyser", points: 5 },
              { id: "q4-2017", texte: "Expliquez l'intérêt thérapeutique des inhibiteurs enzymatiques.", verb: "Expliquer", points: 5, indices: ["Spécificité", "Dose"] },
            ]
          },
          {
            id: "ex2b-2017", titre: "Applications médicales des enzymes", type: "argumentation",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Texte", description: "Utilisation des enzymes en médecine" }],
            questions: [
              { id: "q5-2017", texte: "Citez trois applications médicales des enzymes.", verb: "Citer", points: 3 },
              { id: "q6-2017", texte: "Discutez de l'importance du dosage enzymatique dans le diagnostic.", verb: "Discuter", points: 5, indices: ["Marqueurs", "Spécificité tissulaire"] },
            ]
          },
        ]
      },
    ]
  },
  {
    slug: "bac-svt-se-2016",
    annee: 2016, session: "normale", matiere: "SVT", filiere: "Sciences Expérimentales",
    titre: "Sujet Bac SVT SE 2016", difficulte: "facile", duree: 180,
    totalPages: 10,
    chapitres: ["Génétique", "Immunologie"],
    url_pdf: "https://www.dzexams.com/fr/sujets/bac-svt-se-2016",
    url_corrige: "https://www.dzexams.com/fr/sujets/bac-svt-se-2016-corrige",
    exercices: [],
    subjects: [
      {
        id: "subject-1", titleAr: "الموضوع الأول: تخليق البروتين",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Génétique"], linkedVerbs: ["Décrire", "Expliquer"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex1-2016", titre: "Synthèse des protéines", type: "raisonnement",
            duree_minutes: 50, points: 9,
            documents: [{ titre: "Doc 1", nature: "Schéma", description: "Étapes de la synthèse protéique" }],
            questions: [
              { id: "q1-2016", texte: "Décrivez les étapes de la traduction.", verb: "Décrire", points: 5 },
              { id: "q2-2016", texte: "Expliquez le rôle des ARNt.", verb: "Expliquer", points: 4 },
            ]
          },
          {
            id: "ex1b-2016", titre: "Ribosomes et polymères", type: "analyse_document",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 2", nature: "Schéma", description: "Structure du ribosome" }],
            questions: [
              { id: "q1b-2016", texte: "Décrivez la structure du ribosome.", verb: "Décrire", points: 3 },
              { id: "q2b-2016", texte: "Expliquez le déroulement de l'élongation peptidique.", verb: "Expliquer", points: 5, indices: ["Site A", "Site P", "Liaison peptidique"] },
            ]
          },
        ]
      },
      {
        id: "subject-2", titleAr: "الموضوع الثاني: طرق الوقاية والعلاج المناعي",
        estimatedPages: 5, estimatedMinutes: 90,
        linkedChapters: ["Immunologie"], linkedVerbs: ["Comparer", "Argumenter"],
        difficulty: "facile",
        exercises: [
          {
            id: "ex2-2016", titre: "Sérothérapie et vaccination", type: "argumentation",
            duree_minutes: 40, points: 8,
            documents: [{ titre: "Doc 1", nature: "Texte", description: "Comparaison sérothérapie/vaccination" }],
            questions: [
              { id: "q3-2016", texte: "Comparez sérothérapie et vaccination.", verb: "Comparer", points: 4 },
              { id: "q4-2016", texte: "Justifiez l'utilisation de la sérothérapie en urgence.", verb: "Justifier", points: 4 },
            ]
          },
          {
            id: "ex2b-2016", titre: "Applications vaccinales", type: "raisonnement",
            duree_minutes: 35, points: 7,
            documents: [{ titre: "Doc 2", nature: "Graphique", description: "Couverture vaccinale et incidence des maladies" }],
            questions: [
              { id: "q5-2016", texte: "Analysez la relation entre vaccination et incidence.", verb: "Analyser", points: 4 },
              { id: "q6-2016", texte: "Discutez du principe d'immunité collective.", verb: "Discuter", points: 3, indices: ["Seuil", "Protection"] },
            ]
          },
        ]
      },
    ]
  },
]

// populate exercices from subjects for backward compatibility
for (const s of SUJETS) {
  s.exercices = s.subjects.flatMap((sub) => sub.exercises)
}

export function getAllSujets(): SujetBac[] {
  return SUJETS
}

export function getSujetBySlug(slug: string): SujetBac | undefined {
  return SUJETS.find((s) => s.slug === slug)
}

export function getAnneeRange(): number[] {
  const annees = [...new Set(SUJETS.map((s) => s.annee))]
  return annees.sort((a, b) => b - a)
}
