#!/usr/bin/env node
/**
 * Inventaire honnête des PDF d'annales réellement servis.
 *
 * Contexte mesuré (audit 2026-08-31) : les 12 fichiers de `public/pdfs/` font **131-132 octets**
 * et commencent par `version https://git-lfs.github.com/spec/v1` — ce sont des pointeurs Git LFS,
 * pas des sujets. Un `<iframe>` qui reçoit ce texte n'affiche rien. La page `/annales/{slug}/read`
 * le savait déjà, mais par une constante `return false` : elle avait raison aujourd'hui et aurait
 * eu tort le jour où les fichiers seraient restaurés.
 *
 * Ce script remplace la constante par un fait vérifiable. Il régénère
 * `src/lib/pdf-availability.ts` : la liste des URL utilisables, et la liste des pointeurs LFS.
 *
 *   node scripts/pdf-availability.mjs           → régénère
 *   node scripts/pdf-availability.mjs --check    → ne written rien, sort en 1 si le fichier est périmé
 *
 * Seuil : 100 000 octets (un vrai sujet scanné dépasse largement), plus le test du preambule LFS.
 */

import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs"
import { join, relative, sep } from "node:path"
import { fileURLToPath } from "node:url"

const FRONTEND = fileURLToPath(new URL("..", import.meta.url))
const PUBLIC_DIR = join(FRONTEND, "public")
const PDF_ROOT = "pdfs"
const OUT = join(FRONTEND, "src", "lib", "pdf-availability.ts")
const MIN_BYTES = 100_000
const LFS_PREAMBLE = "version https://git-lfs.github.com/"
const CHECK = process.argv.includes("--check")

/** Toutes les URL publiques `/pdfs/...`, triées, avec leur statut. */
function scan() {
  const root = join(PUBLIC_DIR, PDF_ROOT)
  /** @type {{ url: string, bytes: number, state: "ok" | "lfs" | "trop_petit" }[]} */
  const found = []
  if (!existsSync(root)) return found
  const walk = (dir) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const abs = join(dir, entry.name)
      if (entry.isDirectory()) walk(abs)
      else if (entry.isFile() && /\.pdf$/i.test(entry.name)) {
        const bytes = statSync(abs).size
        const head = readFileSync(abs).subarray(0, LFS_PREAMBLE.length).toString("latin1")
        const state = head === LFS_PREAMBLE ? "lfs" : bytes < MIN_BYTES ? "trop_petit" : "ok"
        found.push({ url: "/" + relative(PUBLIC_DIR, abs).split(sep).join("/"), bytes, state })
      }
    }
  }
  walk(root)
  return found.sort((a, b) => (a.url < b.url ? -1 : 1))
}

function render(rows) {
  const ok = rows.filter((r) => r.state === "ok").map((r) => r.url)
  const lfs = rows.filter((r) => r.state === "lfs").map((r) => r.url)
  const small = rows.filter((r) => r.state === "trop_petit").map((r) => r.url)
  const list = (xs) => (xs.length ? `[${xs.map((x) => `\n  "${x}",`).join("")}\n]` : "[]")
  return `/**
 * GÉNÉRÉ par \`scripts/pdf-availability.mjs\` — ne pas éditer à la main.
 * État de \`public/pdfs\` au moment de la génération : ${ok.length} PDF utilisable(s),
 * ${lfs.length} pointeur(s) Git LFS (${lfs.length ? "lance \`git lfs pull\`" : "—"}),
 * ${small.length} fichier(s) trop petit(s).
 *
 * Un test garde ce fichier synchronisé avec le disque :
 * \`src/lib/pdf-available.test.ts\`.
 */

/** URL publiques dont le fichier est présent ET est un vrai PDF (pas un pointeur LFS). */
export const PDF_AVAILABLE_URLS: readonly string[] = ${list(ok)}

/** URL publiques présentes sur le disque mais sous forme de pointeur Git LFS non restauré. */
export const PDF_LFS_POINTER_URLS: readonly string[] = ${list(lfs)}

/** URL publiques présentes mais sous le seuil de taille (100 Ko) : suspect, non exploitable. */
export const PDF_TOO_SMALL_URLS: readonly string[] = ${list(small)}
`
}

const rows = scan()
const body = render(rows)
if (CHECK) {
  const current = existsSync(OUT) ? readFileSync(OUT, "utf8") : ""
  const fresh = current === body
  const ok = rows.filter((r) => r.state === "ok").length
  console.log(
    `[pdf-availability] ${rows.length} fichier(s) scanné(s) · ${ok} utilisable(s) · ` +
      `${rows.filter((r) => r.state === "lfs").length} pointeur(s) LFS · ` +
      `${fresh ? "génération à jour" : "GÉNÉRATION PÉRIMÉE"}`
  )
  if (!fresh) console.error("→ lancer : node scripts/pdf-availability.mjs")
  process.exit(fresh ? 0 : 1)
}

mkdirSync(join(FRONTEND, "src", "lib"), { recursive: true })
writeFileSync(OUT, body, "utf8")
console.log(
  `[pdf-availability] écrit ${relative(FRONTEND, OUT)} · ` +
    `${rows.filter((r) => r.state === "ok").length}/${rows.length} PDF utilisables`
)
