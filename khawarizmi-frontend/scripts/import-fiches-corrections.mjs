// Import des corrections enseignant dans les fiches-résumés.
// Usage : node scripts/import-fiches-corrections.mjs
// Lit docs/fiches-corrections-template.json :
//   - corrections      : fusionne les champs corrigés dans les fiches existantes (par ficheId)
//   - nouvelles_fiches : crée les fiches manquantes (les 7 chapitres gaps) et les
//                        câble automatiquement dans data/chapitres-fiches-map.json
// Idempotent : relancer ne duplique rien.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, "..")
const FICHES_PATH = path.join(root, "data", "fiches-resume.json")
const MAP_PATH = path.join(root, "data", "chapitres-fiches-map.json")
const TEMPLATE_PATH = path.resolve(root, "..", "docs", "fiches-corrections-template.json")

if (!fs.existsSync(TEMPLATE_PATH)) {
  console.log("ℹ️  Pas de template de corrections (docs/fiches-corrections-template.json).")
  console.log("    Rien à importer — sortie normale.")
  process.exit(0)
}

const template = JSON.parse(fs.readFileSync(TEMPLATE_PATH, "utf8"))
const fiches = JSON.parse(fs.readFileSync(FICHES_PATH, "utf8"))
const map = JSON.parse(fs.readFileSync(MAP_PATH, "utf8"))

let nbCorrigees = 0
let nbCreees = 0

// ── 1. Corrections de fiches existantes ────────────────────────────
for (const c of template.corrections || []) {
  const fiche = fiches.find((f) => f.id === c.ficheId)
  if (!fiche) {
    console.warn(`⚠️  ficheId inconnu : ${c.ficheId} — ignoré`)
    continue
  }
  const champs = c.champs || {}
  for (const key of ["titre", "achkalia", "objectif", "duree", "breadcrumb"]) {
    if (typeof champs[key] === "string") fiche[key] = champs[key]
  }
  for (const key of ["idees", "bac"]) {
    if (Array.isArray(champs[key])) fiche[key] = champs[key]
  }
  if (champs.quiz && typeof champs.quiz === "object") {
    fiche.quiz = {
      question: champs.quiz.question ?? fiche.quiz?.question ?? "",
      bonneReponse: champs.quiz.bonneReponse ?? fiche.quiz?.bonneReponse ?? "",
      pieges: Array.isArray(champs.quiz.pieges) ? champs.quiz.pieges : fiche.quiz?.pieges ?? [],
    }
  }
  nbCorrigees++
  console.log(`✅ corrigée : ${fiche.id}`)
}

// ── 2. Nouvelles fiches (les 7 chapitres gaps) ─────────────────────
for (const nf of template.nouvelles_fiches || []) {
  if (!nf.chapitreSlug || !nf.titre) {
    console.warn("⚠️  nouvelle fiche sans chapitreSlug/titre — ignorée")
    continue
  }
  const id = `fiche-enseignant-${nf.chapitreSlug}`
  if (fiches.some((f) => f.id === id)) {
    console.log(`ℹ️  déjà présente : ${id}`)
    continue
  }
  fiches.push({
    id,
    fileKey: null,
    num: nf.num ?? null,
    titre: nf.titre,
    breadcrumb: nf.breadcrumb ?? "",
    achkalia: nf.achkalia ?? "",
    objectif: nf.objectif ?? "",
    duree: nf.duree ?? "",
    idees: nf.idees ?? [],
    bac: nf.bac ?? [],
    quiz: nf.quiz ?? null,
  })
  // Câblage automatique sur la page chapitre
  const existing = map.find((m) => m.chapterSlug === nf.chapitreSlug)
  if (existing) {
    if (!existing.ficheIds.includes(id)) existing.ficheIds.push(id)
  } else {
    map.push({ chapterSlug: nf.chapitreSlug, chapterAr: nf.titre, ficheIds: [id] })
  }
  nbCreees++
  console.log(`✅ créée + câblée : ${id} → ${nf.chapitreSlug}`)
}

fs.writeFileSync(FICHES_PATH, JSON.stringify(fiches, null, 2) + "\n", "utf8")
fs.writeFileSync(MAP_PATH, JSON.stringify(map, null, 2) + "\n", "utf8")

// ── 3. Rapport de validation ────────────────────────────────────────
const faibles = fiches.filter((f) => !f.objectif || !f.achkalia || f.idees.length < 3)
console.log("")
console.log(`📊 fiches totales : ${fiches.length} | corrigées : ${nbCorrigees} | créées : ${nbCreees}`)
console.log(`⚠️  fiches incomplètes (objectif/إشكالية/≥3 idées) : ${faibles.length}`)
for (const f of faibles) console.log(`   - ${f.id} (idées=${f.idees.length})`)
console.log(`🗺️  paires chapitre→fiche : ${map.length}`)
