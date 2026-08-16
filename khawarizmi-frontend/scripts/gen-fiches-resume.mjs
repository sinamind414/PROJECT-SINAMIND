// Générateur des fiches-résumés (1 fiche par leçon, 45 fiches)
// Source unique : src/lib/experimental-lessons-data.ts (nos leçons)
// Zéro contenu scientifique inventé : on extrait الهدف, الأفكار, تنبيه باك, quiz.
// Usage : node scripts/gen-fiches-resume.mjs
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, "..")
const srcPath = path.join(root, "src/lib/experimental-lessons-data.ts")
const outPath = path.join(root, "data/fiches-resume.json")

const src = fs.readFileSync(srcPath, "utf8")
const startMarker = "export const EXPERIMENTAL_LESSONS"
const endMarker = "export const EXPERIMENTAL_SLUGS"
const braceOpen = src.indexOf("{", src.indexOf(startMarker))
const endBrace = src.lastIndexOf("}", src.indexOf(endMarker))
const data = eval("(" + src.slice(braceOpen, endBrace + 1) + ")")

// Filtres : on écarte les consignes UI (pas du contenu à retenir)
const UI_PREFIXES = [
  "اضغط", "اختر", "قارن", "اسحب", "انقر", "شاهد", "أجب", "رتب",
  "صنّف", "صنف", "أكمل", "اكمل", "استعمل", "عيّن", "عين", "حدد",
]
const isUiPrompt = (t) => {
  const s = t.trim()
  if (s.length < 25) return true
  return UI_PREFIXES.some((p) => s.startsWith(p))
}
const clean = (t) => t.replace(/\s+/g, " ").trim()
const clip = (t, max = 150) => (t.length > max ? t.slice(0, max - 1) + "…" : t)
const stripEmoji = (t) => t.replace(/^[^\u0600-\u06FFa-zA-Z0-9]+/, "")

const fiches = []
const stats = { fichiers: 0, lecons: 0, avecQuiz: 0, ideesMin: 99, ideesMax: 0 }

for (const fileKey of Object.keys(data)) {
  stats.fichiers++
  const file = data[fileKey]
  // Découpage des leçons : chaque leçon commence par un step "1"
  const starts = []
  file.phases.forEach((p, i) => {
    if (p.step === "1") starts.push(i)
  })
  starts.forEach((si, li) => {
    const endIdx = starts[li + 1] ?? file.phases.length
    const blocks = file.phases.slice(si, endIdx).flatMap((p) => p.blocks)
    const objectives = file.objectives.slice(li * 2, li * 2 + 2)
    const objectif = clean(stripEmoji((objectives[0] || "").replace(/^🎯\s*/, "")))
    const duree = clean(stripEmoji((objectives[1] || "").replace(/^⏱️\s*/, "")))

    // الإشكالية = le bloc problem (1 par leçon)
    const problem = blocks.find((b) => b.type === "problem")
    const achkalia = problem ? clip(clean((problem.texts || [""])[0]), 160) : ""

    // الأفكار = scientific_text + text non-UI
    const idees = []
    const seen = new Set()
    const pushIdee = (t) => {
      const c = clean(t)
      if (!c || isUiPrompt(c)) return false
      const key = c.slice(0, 60) // dédoublonnage par préfixe (le source a des doublons)
      if (seen.has(key)) return false
      seen.add(key)
      idees.push(clip(c))
      return true
    }
    for (const b of blocks) {
      if (b.type === "scientific_text" || b.type === "text") {
        for (const t of b.texts || []) {
          if (pushIdee(t) && idees.length >= 5) break
        }
      }
      if (idees.length >= 5) break
    }

    // تنبيه باك = bac_tip + document (méthodologie d'examen)
    const bac = []
    for (const b of blocks) {
      if (b.type === "bac_tip" || b.type === "document") {
        for (const t of b.texts || []) {
          const c = clean(t)
          if (!c || c.length < 25) continue
          bac.push(clip(c, 200))
          if (bac.length >= 2) break
        }
      }
      if (bac.length >= 2) break
    }

    // Quiz = question + bonne réponse ; pièges = les mauvaises options
    const stripLetter = (t) => clean(t).replace(/^[أ-ي]\)\s*/, "")
    const quiz = blocks.find((b) => b.type === "quiz")
    const quizData = quiz
      ? {
          question: clean(quiz.question || ""),
          bonneReponse: stripLetter((quiz.options || [])[quiz.correct] || ""),
          pieges: (quiz.options || []).filter((_, i) => i !== quiz.correct).map(stripLetter),
        }
      : null
    if (quizData) stats.avecQuiz++

    // Fallback idées : la bonne réponse du quiz est une idée-clé de la leçon
    if (idees.length < 3 && quizData) pushIdee(quizData.bonneReponse)
    if (idees.length < 3 && achkalia) pushIdee(achkalia)

    stats.lecons++
    stats.ideesMin = Math.min(stats.ideesMin, idees.length)
    stats.ideesMax = Math.max(stats.ideesMax, idees.length)

    // Numéro de leçon : depuis la clé de fichier (chapitres_X_Y → leçons X, Y)
    const chapMatch = fileKey.match(/chapitres_(\d+)_(\d+)/)
    const num = chapMatch ? (li === 0 ? +chapMatch[1] : +chapMatch[2]) : "transcription"

    fiches.push({
      id: `${fileKey}#${li + 1}`,
      fileKey,
      num,
      titre: li === 0 ? clean(file.titleAr) : `الدرس ${num}`,
      breadcrumb: clean(file.breadcrumb || ""),
      achkalia,
      objectif,
      duree,
      idees,
      bac,
      quiz: quizData,
    })
  })
}

fs.writeFileSync(outPath, JSON.stringify(fiches, null, 2), "utf8")
console.log("✅ fiches générées :", outPath)
console.log("fichiers:", stats.fichiers, "| leçons:", stats.lecons, "| avec quiz:", stats.avecQuiz)
console.log("idées par fiche : min", stats.ideesMin, "max", stats.ideesMax)

// Contrôle qualité : toute fiche doit avoir objectif + achkalia + ≥3 idées
const faibles = fiches.filter((f) => !f.objectif || !f.achkalia || f.idees.length < 3)
if (faibles.length) {
  console.log("⚠️ fiches faibles (à vérifier) :", faibles.map((f) => f.id + " (idées=" + f.idees.length + ")").join(", "))
} else {
  console.log("✅ 45/45 fiches complètes (objectif + إشكالية + ≥3 idées)")
}
