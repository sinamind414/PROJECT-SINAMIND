/**
 * Rendu réel des trois surfaces de preuve (F38), sans navigateur.
 *
 * Les pages qui les hébergent sont montées côté client (`/preuve` lit le stockage de l'appareil, les
 * ateliers n'affichent la zone d'écriture qu'à la phase ب) : un `curl` ne prouvait rien. Ce fichier
 * rend les composants en HTML statique et vérifie ce que l'élève voit au premier octet — notamment
 * qu'aucun score n'apparaît là où il ne devrait pas y en avoir.
 */

import { describe, expect, it } from "vitest"
import { createElement as h } from "react"
import { renderToStaticMarkup } from "react-dom/server"
import { ProofPanel } from "./ProofPanel"
import { ItemForgePanel } from "./ItemForgePanel"
import { DraftStatus } from "./DraftStatus"
import type { PersistentDraft } from "@/hooks/usePersistentDraft"

const draft = (over: Partial<PersistentDraft> = {}): PersistentDraft => ({
  persistent: true,
  text: "نلاحظ أن معدل التفاعل ينخفض بعد الدقيقة السادسة.",
  setText: () => {},
  savedAt: "2026-09-01T08:12:00.000Z",
  history: [{ text: "نسخة الأمس", savedAt: "2026-08-30T08:00:00.000Z", day: "2026-08-30" }],
  previous: { text: "نسخة الأمس", savedAt: "2026-08-30T08:00:00.000Z", day: "2026-08-30" },
  archive: () => {},
  ...over,
})

describe("DraftStatus — ce qui est affiché sous la zone d'écriture", () => {
  it("dit où est le texte, propose l'archive, ne compare pas des versions qu'il n'a pas", () => {
    const html = renderToStaticMarkup(h(DraftStatus, { draft: draft() }))
    expect(html).toContain("حُفظ في جهازك")
    expect(html).toContain("أرشف هذه النسخة")
    expect(html).toContain("قارن مع نسختك السابقة")
    expect(html).toContain("2026-08-30")
    expect(html).toContain("نصّك لا يغادر هذا الجهاز")
  })

  it("sans clé persistante, le composant ne rend rien (pas de bandeau fantôme sur un écran sans mémoire)", () => {
    expect(renderToStaticMarkup(h(DraftStatus, { draft: draft({ persistent: false, savedAt: null, history: [], previous: null }) }))).toBe("")
  })

  it("première visite : pas de bouton de comparaison, parce qu'il n'y a rien à comparer", () => {
    const html = renderToStaticMarkup(h(DraftStatus, { draft: draft({ savedAt: null, history: [], previous: null }) }))
    expect(html).toContain("لم يُحفظ بعد")
    expect(html).not.toContain("قارن مع نسختك السابقة")
  })
})

describe("ItemForgePanel — la fabrique d'énoncés", () => {
  it("les trois critères et le verbe sont demandés, et l'absence de correction ONEC est annoncée", () => {
    const html = renderToStaticMarkup(h(ItemForgePanel, { lessonKey: "c1", chapterAr: "التركيب الكيميائي للبروتينات" }))
    expect(html).toContain("اكتب السؤال")
    expect(html).toContain("الفعل الإجرائي")
    expect(html).toContain("معايير التنقيط الثلاثة")
    expect((html.match(/placeholder="مثال/g) ?? []).length).toBe(3)
    expect(html).toContain("0 من 12 ملف")
    expect(html).toContain("لم تكتب شيئا")
  })

  it("le select propose la liste fermée des verbes du site, pas une liste inventée", () => {
    const html = renderToStaticMarkup(h(ItemForgePanel, { lessonKey: "c1", chapterAr: "فصل" }))
    for (const verb of ["حلّل", "فسّر", "استنتج", "ناقش"]) expect(html).toContain(verb)
    expect(html).not.toContain("أجب")
  })
})

describe("ProofPanel — l'état à trois valeurs", () => {
  it("au premier rendu, l'état affiché est « لم يُختبر » et aucune note n'est calculée", () => {
    const html = renderToStaticMarkup(h(ProofPanel, { lessonKey: "c1", chapterAr: "فصل" }))
    expect(html).toContain("دليل الفهم —")
    expect(html).toContain("لم يُختبر")
    expect(html).toContain("تحميل ما هو محفوظ في هذا الجهاز")
    // Aucun barème : ni « /20 », ni le mot « note » en arabe ou en français. Le seul nombre autorisé est
    // le compteur de cases remplies (x/4), qui décrit l'effort de remplissage, pas une performance.
    expect(html).not.toMatch(/\d+\s*\/\s*(10|20)/)
    expect(html).not.toContain("نقطة")
    expect(html).not.toMatch(/\bscore\b/i)
  })

  it("les quatre cases sont présentes et étiquetées, sans case cachée pour un enseignant", () => {
    const html = renderToStaticMarkup(h(ProofPanel, { lessonKey: "c1", chapterAr: "فصل" }))
    for (const label of ["ما كتبتُ دون أن أفتح الدفتر", "ما نقص في إجابتی بعد المقارنة", "السطر النموذجي الذي لم أكتبه", "الخطأ الذي داورته في ورقتي"]) {
      expect(html).toContain(label)
    }
    expect(html).not.toMatch(/name="[^"]*(teacher|prof|note)/i)
  })
})
