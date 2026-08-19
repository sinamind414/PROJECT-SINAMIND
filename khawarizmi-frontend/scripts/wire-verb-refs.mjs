// Injection des références verbes officielles dans les écrans de la file
// fassir  -> id 7 (فسر)   ·   istintaj -> id 6 (استنتج)   ·   حلّل : pas d'id (octobre)
// allil    -> id 5 (برّر) ·   nas ilmi -> id 1 (وضّح في نص علمي) · moukhattat -> id 10 (أنجز رسما تخطيطيا)
// Source unique : khawarizmi-backend/methodology/verb_database.json
// Usage : node scripts/wire-verb-refs.mjs
// Ne touche pas aux 6 cases ni au moteur local (aucune API, aucun LLM, aucun /20 affiché).
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, "..")
const dbPath = path.resolve(root, "..", "khawarizmi-backend", "methodology", "verb_database.json")
const db = JSON.parse(fs.readFileSync(dbPath, "utf8"))

const WIRING = [
  {
    id: 7,
    outFile: path.join(root, "data/ateliers/manhadjia_02_fassir_taam.json"),
    key: "verb_ref",
  },
  {
    id: 6,
    outFile: path.join(root, "data/ateliers/manhadjia_03_istintaj_taam.json"),
    key: "verb_ref",
  },
  {
    id: 5, // برّر / Justifier — max 15
    outFile: path.join(root, "data/ateliers/manhadjia_04_allil_taam.json"),
    key: "verb_ref",
  },
  {
    id: 1, // وضّح في نص علمي / Composer — le seul verbe à max 20 (jamais affiché)
    outFile: path.join(root, "data/ateliers/manhadjia_06_nas_ilmi_taam.json"),
    key: "verb_ref",
  },
  {
    id: 10, // أنجز رسما تخطيطيا / Réaliser un schéma — max 10
    outFile: path.join(root, "data/ateliers/manhadjia_07_moukhattat_taam.json"),
    key: "verb_ref",
  },
]

for (const { id, outFile, key } of WIRING) {
  const verb = db.verbs.find((v) => v.id === id)
  if (!verb) {
    console.error(`❌ verbe id=${id} introuvable dans verb_database.json`)
    process.exit(1)
  }
  // max_score volontairement NON inclus : pas de /20 affiché à l'élève (doctrine)
  const ref = {
    id: verb.id,
    arabic: verb.arabic,
    french: verb.french,
    definition: verb.definition,
    criteria: verb.criteria,
    common_mistakes: verb.common_mistakes,
  }
  const data = JSON.parse(fs.readFileSync(outFile, "utf8"))
  data[key] = ref
  fs.writeFileSync(outFile, JSON.stringify(data, null, 2) + "\n", "utf8")
  console.log(`✅ ${path.basename(outFile)} <- verb_ref id=${ref.id} (${ref.arabic} · ${ref.french})`)
}
