import { describe, expect, it } from "vitest"
import { existsSync } from "node:fs"
import {
  addDays,
  archiveDraft,
  commitDraft,
  countProofStates,
  createMemoryStorage,
  dayDiff,
  forgeStateOf,
  HISTORY_CAP,
  isTransferDue,
  loadDraft,
  loadForge,
  loadProof,
  localDay,
  MAX_FIELD,
  openDraft,
  proofIsEmpty,
  proofRow,
  proofStateOf,
  saveForge,
  saveProof,
  transferDueDay,
  wipeLocalEvidence,
  PROOF_BOXES,
  TRANSFER_DELAY_DAYS,
  type ProofBoxKey,
} from "./local-evidence"
import { chapterHref } from "./cours-data"
import { getAllActiveLessons } from "./active-lessons"

const DAY = "2026-09-01"
const at = (day: string, hour = 9) => new Date(`${day}T${`${hour}`.padStart(2, "0")}:00:00`)
const emptyBoxes = (): Record<ProofBoxKey, string> => ({
  wroteWithoutBook: "",
  whatWasMissing: "",
  modelLine: "",
  circledMistake: "",
})

describe("jours calendaires", () => {
  it("addDays traverse un mois et un changement d'heure sans dériver d'un jour", () => {
    expect(addDays("2026-09-01", TRANSFER_DELAY_DAYS)).toBe("2026-09-15")
    expect(addDays("2026-02-20", 14)).toBe("2026-03-06")
    expect(addDays("2026-12-31", 1)).toBe("2027-01-01")
    expect(dayDiff("2026-09-01", "2026-09-15")).toBe(14)
  })

  it("localDay compare des jours, pas des horodatages", () => {
    expect(localDay(at(DAY, 23))).toBe(DAY)
    expect(dayDiff(DAY, addDays(DAY, 0))).toBe(0)
  })
})

describe("brouillons", () => {
  it("le texte survit à un changement de page le même jour", () => {
    const store = createMemoryStorage()
    commitDraft(store, "atelier:hallil-j3", "حلّل", "نلاحظ أن التركيز ينخفض بعد الدقيقة السادسة.", at(DAY))
    const reopened = openDraft(store, "atelier:hallil-j3", "حلّل", at(DAY, 14))
    expect(reopened.text).toContain("الدقيقة السادسة")
    expect(reopened.history).toHaveLength(0)
  })

  it("le brouillon d'un autre jour est archivé et la page repart vide", () => {
    const store = createMemoryStorage()
    commitDraft(store, "k", "l", "version de lundi", at("2026-09-01"))
    const next = openDraft(store, "k", "l", at("2026-09-03"))
    expect(next.text).toBe("")
    expect(next.history[0].text).toBe("version de lundi")
    expect(next.history[0].day).toBe("2026-09-01")
  })

  it("l'archive explicite ne duplique pas la même version et respecte HISTORY_CAP", () => {
    const store = createMemoryStorage()
    for (let i = 0; i < HISTORY_CAP + 4; i++) {
      const day = addDays("2026-09-01", i)
      commitDraft(store, "k", "l", `version ${i}`, at(day))
      archiveDraft(store, "k", "l", at(day))
      archiveDraft(store, "k", "l", at(day)) // même texte : rien de neuf à archiver
    }
    const record = loadDraft(store, "k")!
    expect(record.history.length).toBe(HISTORY_CAP)
    expect(record.history[0].text).toBe(`version ${HISTORY_CAP + 3}`)
  })

  it("une case trop longue est coupée, pas stockée à l'infini", () => {
    const store = createMemoryStorage()
    const record = commitDraft(store, "k", "l", "ب".repeat(MAX_FIELD + 500), at(DAY))
    expect(record.text.length).toBe(MAX_FIELD)
  })
})

describe("preuves de compréhension", () => {
  it("rien d'écrit = « لم يُختبر », et une case vide ne crée pas d'enregistrement fantôme", () => {
    const store = createMemoryStorage()
    expect(proofStateOf(loadProof(store, "c1"))).toBe("untested")
    saveProof(store, "c1", "الفصل", emptyBoxes(), { now: at(DAY) })
    expect(proofIsEmpty(loadProof(store, "c1")!.boxes)).toBe(true)
    expect(proofStateOf(loadProof(store, "c1"))).toBe("untested")
    expect(proofRow(store, "c1", "الفصل", DAY).day).toBeNull()
  })

  it("une case remplie prouve l'épreuve, pas le transfert", () => {
    const store = createMemoryStorage()
    const boxes = { ...emptyBoxes(), wroteWithoutBook: "انخفاض معدل التفاعل مع انخفاض الحرارة." }
    const record = saveProof(store, "c1", "الفصل", boxes, { now: at(DAY) })
    expect(proofStateOf(record)).toBe("tested-no-transfer")
    expect(transferDueDay(record)).toBe(addDays(DAY, TRANSFER_DELAY_DAYS))
    expect(isTransferDue(store, "c1", addDays(DAY, 3))).toBe(false)
    expect(isTransferDue(store, "c1", addDays(DAY, TRANSFER_DELAY_DAYS))).toBe(true)
  })

  it("compléter une preuve plus tard ne repousse pas la date de l'épreuve de transfert", () => {
    const store = createMemoryStorage()
    const boxes = { ...emptyBoxes(), wroteWithoutBook: "ما كتبت" }
    saveProof(store, "c1", "الفصل", boxes, { now: at(DAY) })
    const later = saveProof(store, "c1", "الفصل", { ...boxes, modelLine: "سطر نموذجي" }, { now: at("2026-09-08") })
    expect(later.day).toBe(DAY)
    expect(later.savedAt.startsWith("2026-09-08")).toBe(true)
  })

  it("le transfert déclaré ne se retire pas en décochant la case", () => {
    const store = createMemoryStorage()
    const boxes = { ...emptyBoxes(), wroteWithoutBook: "ما كتبت" }
    saveProof(store, "c1", "الفصل", boxes, { hasTransfer: true, now: at(DAY) })
    const revoked = saveProof(store, "c1", "الفصل", boxes, { hasTransfer: false, now: at("2026-09-20") })
    expect(revoked.hasTransfer).toBe(true)
    expect(proofStateOf(revoked)).toBe("transferred")
  })

  it("aucun champ inconnu ne survit à l'écriture — ni nom d'élève, ni note", () => {
    const store = createMemoryStorage()
    const boxes = { ...emptyBoxes(), modelLine: "سطر" }
    saveProof(store, "c1", "الفصل", boxes, { now: at(DAY) })
    // Écriture directe d'un objet illégal dans le stockage : la relecture doit le nettoyer.
    const key = "khawarizmi.proof.v1:evil"
    store.setItem(
      key,
      JSON.stringify({ key: "evil", studentName: "آية", phone: "0555 00 00 00", score: 17.5, boxes }),
    )
    const read = loadProof(store, "evil")!
    expect(Object.keys(read).sort()).toEqual(
      ["boxes", "day", "hasTransfer", "key", "label", "savedAt", "transferDay"].sort(),
    )
    expect(JSON.stringify(read)).not.toContain("آية")
    expect(JSON.stringify(read)).not.toContain("0555")
    expect(read.label).toBe("")
    expect(proofStateOf(read)).toBe("tested-no-transfer")
  })

  it("les compteurs d'états se lisent sur les lignes réelles, sans inventer de denominator", () => {
    const store = createMemoryStorage()
    saveProof(store, "a", "A", { ...emptyBoxes(), modelLine: "سطر" }, { now: at(DAY) })
    const rows = ["a", "b", "c"].map((k) => proofRow(store, k, k, DAY))
    expect(countProofStates(rows)).toEqual({ untested: 2, "tested-no-transfer": 1, transferred: 0 })
  })

  it("effacer la trace locale efface brouillons, preuves et questions", () => {
    const store = createMemoryStorage()
    commitDraft(store, "k", "l", "texte", at(DAY))
    saveProof(store, "c1", "A", { ...emptyBoxes(), modelLine: "سطر" }, { now: at(DAY) })
    saveForge(store, "c1", "A", { verb: "analyse", prompt: "حلّل التغيّر مع ذكر القيم", criteria: [] })
    const removed = wipeLocalEvidence(store)
    expect(removed).toBe(3)
    expect(loadDraft(store, "k")).toBeNull()
    expect(loadProof(store, "c1")).toBeNull()
    expect(loadForge(store, "c1")).toBeNull()
  })
})

describe("l'élève fabrique l'épreuve", () => {
  it("une question n'est « جاهزة » que si elle a un verbe, une consigne et trois critères", () => {
    const store = createMemoryStorage()
    expect(forgeStateOf(loadForge(store, "c1"))).toBe("none")
    const draft = saveForge(store, "c1", "الفصل", { verb: "analyse", prompt: "حلّل", criteria: ["a", "b"] })
    expect(forgeStateOf(draft)).toBe("draft")
    const ready = saveForge(store, "c1", "الفصل", {
      verb: "analyse",
      prompt: "استنادا إلى الوثيقة 1، حلّل تغيّر معدل التفاعل مع ذكر الوحدات.",
      criteria: ["علاقة سببية", "رقم ووحدته", "جملة خلاصة"],
    })
    expect(forgeStateOf(ready)).toBe("ready")
    expect(ready.criteria).toHaveLength(3)
  })

  it("les critères vides ne comptent pas et le surplus est jeté", () => {
    const store = createMemoryStorage()
    const r = saveForge(store, "c1", "l", {
      verb: "deduce",
      prompt: "استنتج العلاقة بين العامل الحراري والتركيز في الوسط.",
      criteria: [" ", "un seul critère réel", "deuxième", "troisième", "quatrième"],
    })
    expect(r.criteria).toEqual(["un seul critère réel", "deuxième", "troisième"])
    expect(forgeStateOf(r)).toBe("ready")
  })

  it("toutes les preuves du registre pointent vers une page qui existe", () => {
    // `chapterHref` est le seul endroit qui construit le lien d'un chapitre : s'il dérive,
    // le registre devient une vitrine de liens morts.
    const route = "src/app/cours/[domaine]/[unite]/[chapitre]/page.tsx"
    expect(existsSync(route)).toBe(true) // la page est une route dynamique, pas un dossier par chapitre
    const missing: string[] = []
    for (const lesson of getAllActiveLessons()) {
      const href = chapterHref(lesson.chapterSlug)
      if (!href) missing.push(`${lesson.chapterSlug} : href absent`)
      else if (!/^\/cours\/d\d+\/[a-z0-9-]+\/[a-z0-9-]+$/.test(href)) missing.push(`${href} : forme inattendue`)
    }
    expect(missing).toEqual([])
    expect(PROOF_BOXES).toHaveLength(4)
  })
})
