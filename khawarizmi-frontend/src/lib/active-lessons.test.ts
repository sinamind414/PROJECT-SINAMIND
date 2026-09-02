/**
 * Garde-fous de D2 (leçons fabriquées par gabarit).
 *
 * Ce fichier ne demande PAS que les leçons soient longues : la longueur viendra du contenu authoré,
 * pas d'un remplissage. Ce qu'il interdit, c'est de se faire passer du gabarit pour un cours et
 * pour une correction automatique. Chaque test nomme la mesure qui l'a fait écrire.
 */
import { describe, expect, it } from "vitest"

import { activeLessons, getActiveLessonByChapterParam, lessonCorpusStats, type ReflectionCheck } from "./active-lessons"
import { EXPERIMENTAL_HUB_SLUGS } from "./experimental-hub-registry"
import { methodologyChapterLinks } from "./methodology-chapters"

const GENERATED = activeLessons

describe("provenance : le gabarit ne peut pas se faire passer pour du contenu", () => {
  it("l'état déclaré correspond à ce qui est réellement atteignable", () => {
    for (const l of GENERATED) {
      const authoredBlocks = l.lessonBlocks.filter((b) => b.provenance === "authoré")
      const attendu = authoredBlocks.length > 0 ? "authoré" : l.linkedBookPhases.length > 0 ? "lié" : "gabarit-seul"
      expect(l.contentState).toBe(attendu)
      // Un état « gabarit-seul » qui cacherait un lien existant serait un faux négatif ; l'inverse
      // serait un faux positif, plus grave : promettre un contenu qui n'est pas là.
      if (l.contentState === "gabarit-seul") expect(l.linkedBookPhases).toHaveLength(0)
    }
  })

  it("un paragraphe partagé par plus de 2 leçons est marqué gabarit (jamais présenté comme propre au chapitre)", () => {
    const contrevenants = GENERATED.flatMap((l) => l.lessonBlocks)
      .filter((b) => b.sharedWith > 1 && b.provenance === "authoré")
      .map((b) => b.id)
    expect(contrevenants).toEqual([])
  })

  it("le contenu du livre est raccordé, et uniquement à des pages qui existent", () => {
    // Le 01/09, la dette D2 a été décrite comme « le site ne contient que 2,29 % du livre ». C'était
    // mesuré sur la seule couche « leçon active ». Le hub `lecons-sciences-experimentales` contient
    // 113 240 caractères de leçons réelles (22 phases, 44 chapitres numérotés du livre), et il
    // n'était relié à rien. Ce test verrouille le raccord — et l'absence d'invention.
    const stats = lessonCorpusStats()
    expect(stats.lessonsWithLinkedContent).toBe(GENERATED.length)
    expect(stats.linkedPhases).toBe(EXPERIMENTAL_HUB_SLUGS.length)
    expect(stats.gabaritOnly).toBe(0)
    for (const l of GENERATED) {
      for (const ph of l.linkedBookPhases) {
        expect(EXPERIMENTAL_HUB_SLUGS).toContain(ph.slug)
        expect(ph.labelAr.length).toBeGreaterThan(3)
      }
    }
  })

  it("la duplication est chiffrée, pas tue : 17 leçons « processus » lisaient le même texte", () => {
    const stats = lessonCorpusStats()
    expect(stats.maxSharedParagraph).toBeGreaterThan(1)
    const processus = GENERATED.filter((l) => l.chapterType === "processus")
    const texts = new Set(processus.map((l) => l.lessonBlocks[1]?.contentAr))
    expect(processus.length).toBeGreaterThan(1)
    expect(texts.size).toBe(1) // un seul paragraphe distinct pour tous les « processus »
  })
})

describe("auto-notation : aucun contrôle de gabarit ne distribue de verdict", () => {
  it("le générateur ne produit plus de question auto-notée par mots-clés", () => {
    // Bug mesuré avant correctif : expectedKeywords = chapterFr.split("-")[0], un fragment français
    // (« Synthese des proteines »), comparé à une réponse d'élève en arabe → toute bonne réponse
    // était marquée fausse. Et le QCM avait correctIndex 1 pour les 55 leçons.
    expect(lessonCorpusStats().autoGradedGeneratedChecks).toBe(0)
    for (const l of GENERATED) for (const q of l.quickChecks) expect(q.provenance).toBe("gabarit")
  })

  it("les questions générées sont des allers-retours avec modèle, sans « bonne réponse » cachée", () => {
    for (const l of GENERATED) {
      for (const q of l.quickChecks) {
        if (q.type === "reflection") {
          const r = q as ReflectionCheck
          expect(r.modelAnswerAr.length).toBeGreaterThan(20)
          // Pas de vocabulaire de verdict : ce texte accompagne un modèle à comparer, pas une note.
          expect(r.commentAr).not.toMatch(/صحيحة|خاطئة|إجابة صحيحة/)
          expect(r.commentAr.length).toBeGreaterThan(15)
        }
      }
    }
  })

  it("les erreurs affichées comme « شائعة » sont étiquetées générales tant qu'elles ne sont pas par chapitre", () => {
    // Mesuré : les trois mêmes chaînes pour les 55 leçons. Les présenter comme un diagnostic de chapitre
    // serait un faux positif — le jour où elles deviennent propres au chapitre, ce test doit casser.
    for (const l of GENERATED) expect(l.commonMistakesProvenance).toBe("gabarit")
  })
})

describe("intégrité du rendu", () => {
  it("aucun champ élève ne contient « undefined » (données manquantes = état visible, pas fuite)", () => {
    const suspects: string[] = []
    for (const l of GENERATED) {
      const champs = [l.summaryAr, l.bacLinkAr, l.revisionPromptAr, ...l.commonMistakes]
      for (const c of l.lessonBlocks) champs.push(c.titleAr, c.contentAr)
      for (const k of l.keyConcepts) champs.push(k.term, k.meaningAr, k.commonMistakeAr ?? "")
      for (const c of champs) if (c.includes("undefined") || c.includes("null")) suspects.push(`${l.chapterSlug}: ${c.slice(0, 40)}`)
    }
    expect(suspects).toEqual([])
  })

  it("55 leçons pour 55 chapitres, et le paramètre d'URL se résout dans les deux formes", () => {
    expect(GENERATED.length).toBe(methodologyChapterLinks.length)
    const premier = GENERATED[0]
    expect(getActiveLessonByChapterParam(premier.chapterSlug)?.chapterSlug).toBe(premier.chapterSlug)
    expect(getActiveLessonByChapterParam(encodeURIComponent(premier.chapterFr))?.chapterSlug).toBe(premier.chapterSlug)
  })

  it("l'instrument sépare le contenu du remplissage par substitution de nom", () => {
    // Le nombre est un fait, pas une cible : il existe pour que D2 se re-mesure sans rouvrir une
    // conversation. Ce que ce test interdit, c'est de confondre « unique » et « propre au chapitre » :
    // insérer le nom du chapitre dans une phrase de gabarit crée 55 chaînes distinctes et zéro contenu.
    const stats = lessonCorpusStats()
    expect(stats.authoredLessons).toBe(0) // contenu écrit ICI — pas le contenu relié, qui est mesuré au-dessus
    expect(stats.displayedChars).toBeGreaterThanOrEqual(stats.distinctCorpusChars)
    expect(stats.slotSubstitutionChars).toBeGreaterThan(stats.focusCorpusChars)
    // Le corpus réellement spécifique tient dans une phrase par chapitre : ~5 000 caractères pour 55
    // leçons, contre 214 297 au livre de référence (khawarizmi-backend/LIVRE-MANHADJIYA.md, mesuré).
    expect(stats.focusCorpusChars).toBeLessThan(6000)
    expect(stats.focusCorpusChars / 214297).toBeLessThan(0.03)
  })
})
