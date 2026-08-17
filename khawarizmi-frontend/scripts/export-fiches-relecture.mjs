// Export des 45 fiches-résumés en UN document de relecture pour l'enseignant
// Source unique : data/fiches-resume.json (généré depuis les leçons existantes)
// Usage : node scripts/export-fiches-relecture.mjs
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, "..")
const src = JSON.parse(fs.readFileSync(path.join(root, "data/fiches-resume.json"), "utf8"))
const out = path.resolve(root, "..", "docs", "fiches-resume-relecture.md")

const GAPS = [
  "د1-و1-ف1 : التركيب الكيميائي للبروتينات (composition chimique)",
  "د1-و3-ف4 : دور العوامل المساعدة للإنزيمات (cofacteurs)",
  "د1-و4-ف3 : الذاكرة المناعية (mémoire immunitaire)",
  "د1-و4-ف4 : اللقاحات والمصل (vaccins et sérum)",
  "د1-و5-ف1 : بنية النسيج العصبي (structure du tissu nerveux)",
  "د2-و1-ف4 : العوامل المؤثرة في التركيب الضوئي (facteurs)",
  "د2-و3-ف2 : نقل الغازات في الدم (transport des gaz)",
]

const order = {
  transcription: 0,
}
src.forEach((f) => {
  if (typeof f.num === "number") order[String(f.num)] = f.num
})
const sorted = [...src].sort((a, b) => (order[String(a.num)] ?? 999) - (order[String(b.num)] ?? 999))

const L = []
L.push("# خلاصات الدروس — وثيقة إعادة القراءة للأستاذ (SVT 3AS)")
L.push("")
L.push("> **Générées automatiquement** depuis les leçons existantes de la plateforme (`experimental-lessons-data.ts`). **Aucun contenu scientifique inventé** : chaque phrase vient d'une leçon déjà en ligne. L'objectif de ce document : relecture par un professeur agrégé / inspecteur en ~2 h.")
L.push("")
L.push("## ✔️ Grille de relecture (ce que l'enseignant vérifie, fiche par fiche)")
L.push("")
L.push("1. **Exactitude scientifique** — une erreur factuelle = à barrer, pas à corriger ici (retour à l'équipe).")
L.push("2. **Vocabulaire officiel** — formulation conforme au programme algérien (المصطلحات الرسمية).")
L.push("3. **Pièges** (« لا تكتب ») — vérifier qu'ils sont vrais et utiles pour l'élève.")
L.push("4. **Complétude** — une idée-clé majeure du chapitre manque-t-elle ?")
L.push("")
L.push(`## ⚠️ À savoir avant de relire`)
L.push("")
L.push(`- **45 fiches** : les 44 leçons du livre + la leçon de transcription.`)
L.push(`- **7 chapitres de la plateforme n'ont PAS de fiche** (aucune source existante — à écrire par l'enseignant, voir liste ci-dessous).`)
L.push(`- **11 chapitres « تمرين شامل »** sont des exercices de synthèse : pas de fiche par nature.`)
L.push(`- Les numéros des fiches sont ceux du **manuel** (livre de l'élève), pas ceux de la navigation de la plateforme.`)
L.push("")
L.push("---")
L.push("")
L.push("## 📋 Les 7 chapitres SANS fiche (à écrire, ~15 min chacun)")
L.push("")
L.push("| Chapitre | Contenu attendu |")
L.push("|---|---|")
for (const g of GAPS) {
  L.push(`| ${g} | هدف + إشكالية + 3-5 أفكار + تنبيه باك + سؤال اختبر نفسك |`)
}
L.push("")
L.push("---")
L.push("")

for (const f of sorted) {
  const n = f.num === "transcription" ? "النسخ (transcription)" : `الدرس ${f.num}`
  L.push(`## ${n}`)
  L.push("")
  L.push(`**المسار :** ${f.breadcrumb}`)
  L.push("")
  L.push(`**${f.titre}**`)
  L.push("")
  L.push(`### ❓ الإشكالية`)
  L.push("")
  L.push(f.achkalia)
  L.push("")
  L.push(`### 🎯 الهدف`)
  L.push("")
  L.push(f.objectif)
  L.push("")
  L.push(`> ⏱️ ${f.duree}`)
  L.push("")
  L.push(`### 🧠 الأفكار الأساسية (${f.idees.length})`)
  L.push("")
  f.idees.forEach((id, i) => {
    L.push(`${i + 1}. ${id}`)
    L.push("")
  })
  if (f.bac.length > 0) {
    L.push(`### 💡 تنبيه باك`)
    L.push("")
    f.bac.forEach((b) => {
      L.push(`- ${b}`)
      L.push("")
    })
  }
  if (f.quiz) {
    L.push(`### ✔️ اختبر نفسك`)
    L.push("")
    L.push(`**س :** ${f.quiz.question}`)
    L.push("")
    L.push(`**ج :** ${f.quiz.bonneReponse}`)
    L.push("")
    if (f.quiz.pieges.length > 0) {
      L.push(`**لا تكتب :** ${f.quiz.pieges.join(" · ")}`)
      L.push("")
    }
  }
  L.push("---")
  L.push("")
}

fs.writeFileSync(out, L.join("\n"), "utf8")
console.log("✅ document de relecture :", out)
console.log("fiches:", sorted.length, "| lignes:", L.length)
