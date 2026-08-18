// scripts/check-lfs-assets.mjs — Audit technique 2026-08-18 (problème critique Git LFS).
// Vérifie que les assets en production ne sont PAS des pointeurs Git LFS
// (Vercel/Railway clonent sans LFS : un pointeur de 132 octets est servi à
// la place du PDF réel, et l'embedder ONNX échoue silencieusement).
//
// Usage : node scripts/check-lfs-assets.mjs   (exit 1 si pointeur trouvé)
// À câbler dans le CI/le build dès que les vrais fichiers sont disponibles
// (CDN externe ou recommit) — PAS câblé aujourd'hui : la sandbox ne contient
// que les pointeurs, un build échouerait immédiatement.
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, "..")

const CHECK_DIRS = [
  path.join(root, "public", "pdfs"),
  path.join(root, "..", "khawarizmi-backend", "models", "minilm_onnx_int8"),
]

const LFS_SIGNATURE = "version https://git-lfs.github.com/spec/v1"
const found = []

function walk(dir) {
  if (!fs.existsSync(dir)) return
  for (const entry of fs.readdirSync(dir)) {
    const fp = path.join(dir, entry)
    const st = fs.statSync(fp)
    if (st.isDirectory()) {
      walk(fp)
    } else if (st.isFile()) {
      const head = fs.readFileSync(fp, "utf8").slice(0, 64)
      if (head.includes(LFS_SIGNATURE)) {
        found.push({ file: path.relative(root, fp), size: st.size })
      }
    }
  }
}

for (const dir of CHECK_DIRS) walk(dir)

if (found.length > 0) {
  console.error("❌ Assets Git LFS détectés — ils seront cassés en production :")
  for (const f of found) console.error(`   - ${f.file} (${f.size} octets = pointeur LFS)`)
  console.error("")
  console.error("   Correctifs : héberger les PDFs sur un CDN (S3/Cloudflare R2) ou les")
  console.error("   recommitter sans LFS ; télécharger le modèle ONNX au build Docker")
  console.error("   (RUN wget/huggingface-cli) au lieu de le copier depuis le repo.")
  process.exit(1)
}

console.log("✅ Aucun pointeur LFS dans les assets de production.")
