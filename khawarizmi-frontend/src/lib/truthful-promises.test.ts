/**
 * Invariant transverse du site : **l'UI ne promet pas ce que le moteur ne sait pas corriger.**
 *
 * Mesures qui justifient ces gardes (rapport §8.5 et §9) :
 *   - 19 % de rubriques servies par un moteur, 0 % côté annales ;
 *   - la salle `/annales/[slug]/exam` ET `/bac-blanc` montent `BacBlancImmersif`, dont l'écran
 *     `phase === "intro"` ne propose AUCUN bouton : `enterExam` (seule porte vers « choix » puis
 *     l'épreuve à minuterie) n'est appelé nulle part dans le repo — le flux minuterie est
 *     implémenté mais inatteignable ;
 *   - aucune grille ne correspond aux id fallback `bac:{annale}:{ex_id}`, et `bac_subjects` ne
 *     contient que `bac-svt-2025` (∅ recoupement avec les 23 slugs d'annales).
 * Style du repo : assertions sur le texte source, sans DOM.
 *
 * Ces gardes n'interdisent pas d'améliorer une promesse — elles interdisent de la ré-infler tant
 * que le moteur (ou les données) ne suit pas.
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

const SRC = new URL("../", import.meta.url)
const read = (rel: string) => readFileSync(fileURLToPath(new URL(rel, SRC)), "utf-8")

describe("promesses de la page sujet d'annales", () => {
  const page = read("app/annales/[slug]/page.tsx")

  it("ne promet plus « امتحان كامل مع مؤقت زمني » alors qu'aucun sujet n'est chargé en base", () => {
    expect(page).not.toContain("امتحان كامل مع مؤقت زمني")
    expect(page).toContain("قاعة الامتحان غير مفتوحة بعد لهذا الموضوع")
  })

  it("n'appelle plus le bouton « ابدأ هذا الموضوع » : rien ne démarre derrière", () => {
    expect(page).not.toContain("ابدأ هذا الموضوع")
    expect(page).toContain("حالة هذا الموضوع في الموقع")
  })

  it("la carte « قراءة » rend la disponibilité du PDF depuis l'URL du sujet", () => {
    expect(page).toContain("isAnnalePdfAvailable(sujet.url_pdf)")
    // Avant : « الموضوع غير متاح (ملف ناقص) » était codé en dur pour TOUS les sujets, y compris
    // ceux dont l'URL est un PDF vérifiable — le mensonge allait dans les deux sens.
    expect(page).not.toContain("الموضوع غير متاح (ملف ناقص)")
  })
})

describe("promesse de la salle BAC blanche", () => {
  const page = read("app/bac-blanc/page.tsx")

  it("ne promet plus une minuterie « حقيقية » (l'écran intro n'a pas de porte d'entrée)", () => {
    expect(page).not.toContain("مؤقت حقيقية")
    expect(page).toContain("غير مفتوحة بعد")
  })
})

describe("écran d'entrée de la salle (BacBlancImmersif)", () => {
  const hall = read("components/bac_blanc/BacBlancImmersif.tsx")

  it("l'intro n'affiche plus « SVT · 2026 » comme si elle décrivait le sujet demandé", () => {
    expect(hall).toContain("{annaleSlug}")
    expect(hall).not.toContain('className="text-gray-400">SVT · 2026</p>')
    // Les chiffres restent, mais étiquetés comme modèle général.
    expect(hall).toContain("نموذج عام للشكل")
  })

  it("le disclaimers existants ne sont pas supprimés", () => {
    expect(hall).toContain("لا شبكة تقييم محلية لهذا الامتحان")
    expect(hall).toContain("لن نفتح قاعة وهمية")
  })
})

describe("compteurs de preuve de /methodology", () => {
  const pulse = read("components/methodology/SessionExitButton.tsx")

  it("la tuile annonce des portes ouvertes, pas une file de révisions FSRS", () => {
    expect(pulse).toContain("openRecallCount")
    expect(pulse).toContain("بوابات FSRS")
    expect(pulse).toContain("ليست مراجعات معلّقة")
  })
})
