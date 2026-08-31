import { execFileSync } from "node:child_process"
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"
import { isAnnalePdfAvailable, pdfUnavailabilityReason } from "./pdf-available"
import { PDF_AVAILABLE_URLS, PDF_LFS_POINTER_URLS } from "./pdf-availability"

/**
 * Un PDF « disponible » doit vouloir dire une chose vérifiable : le fichier est sur le disque,
 * il n'est pas un pointeur Git LFS, et il a une taille exploitable.
 *
 * Bug d'avant ce fichier : `isAnnalePdfAvailable()` renvoyait `false` **en dur**. L'UI avait
 * raison par accident (les 12 PDF de `public/pdfs` font 131 o — des pointeurs LFS) et aurait eu
 * tort définitivement dès que les fichiers seraient restaurés. Ici, l'affiche est branchée sur un
 * inventaire regénéré, et ces tests verrouillent les deux sens du mensonge.
 */

const ROOT = fileURLToPath(new URL("../../", import.meta.url))
const PUBLIC_PDFS = new URL("../../public/pdfs/", import.meta.url)
const MIN_BYTES = 100_000
const LFS_PREAMBLE = "version https://git-lfs.github.com/"

function scanDisk() {
  const dir = fileURLToPath(PUBLIC_PDFS)
  const out: { url: string; state: "ok" | "lfs" | "trop_petit" }[] = []
  if (!existsSync(dir)) return out
  const walk = (d: string, prefix: string) => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      const abs = `${d}/${e.name}`
      if (e.isDirectory()) walk(abs, `${prefix}/${e.name}`)
      else if (e.isFile() && /\.pdf$/i.test(e.name)) {
        const bytes = statSync(abs).size
        const head = readFileSync(abs).subarray(0, LFS_PREAMBLE.length).toString("latin1")
        out.push({
          url: `${prefix}/${e.name}`,
          state: head === LFS_PREAMBLE ? "lfs" : bytes < MIN_BYTES ? "trop_petit" : "ok",
        })
      }
    }
  }
  walk(dir, "/pdfs")
  return out
}

describe("pdf-availability — le fichier généré dit la vérité du disque", () => {
  it("la liste « utilisable » correspond exactement aux vrais PDF (ni pointeur LFS, ni jouet)", () => {
    const disk = scanDisk()
    expect(new Set(PDF_AVAILABLE_URLS)).toEqual(new Set(disk.filter((r) => r.state === "ok").map((r) => r.url)))
  })

  it("aucun pointeur LFS n'est présenté comme disponible", () => {
    const lfs = new Set(scanDisk().filter((r) => r.state === "lfs").map((r) => r.url))
    for (const url of PDF_AVAILABLE_URLS) expect(lfs.has(url)).toBe(false)
    expect(new Set(PDF_LFS_POINTER_URLS)).toEqual(lfs)
  })

  it("le fichier généré n'est pas périmé (`npm run pdfs:check`)", () => {
    // execFileSync lève si le script sort en 1 : c'est exactement le contrat de la CI.
    const out = execFileSync("node", [`${ROOT.replace(/\/$/, "")}/scripts/pdf-availability.mjs`, "--check"], {
      encoding: "utf8",
    })
    expect(out).toContain("génération à jour")
  })
})

describe("isAnnalePdfAvailable — un prédicat, pas une constante", () => {
  it("une URL vide, absente ou nulle n'est jamais « disponible »", () => {
    expect(isAnnalePdfAvailable("")).toBe(false)
    expect(isAnnalePdfAvailable(undefined)).toBe(false)
    expect(isAnnalePdfAvailable(null)).toBe(false)
    expect(isAnnalePdfAvailable("/pdfs/bac-svt/bac-svt-sujet-1900.pdf")).toBe(false)
  })

  it("un pointeur LFS est classé comme tel, pour ne pas réparer la mauvaise couche", () => {
    for (const url of PDF_LFS_POINTER_URLS) {
      expect(isAnnalePdfAvailable(url)).toBe(false)
      expect(pdfUnavailabilityReason(url)).toBe("pointeur-lfs")
    }
  })

  it("les URL déclarées par le catalogue d'annales sont toutes rendues indisponibles ou prêtes", () => {
    const src = readFileSync(fileURLToPath(new URL("./annales-bac.ts", import.meta.url)), "utf8")
    const urls = [...src.matchAll(/url_(?:pdf|corrige):\s*"([^"]+)"/g)].map((m) => m[1])
    expect(urls.length).toBeGreaterThan(0)
    for (const url of urls) {
      const file = fileURLToPath(new URL(`public${url}`, import.meta.url))
      const present = existsSync(file)
      const usable = present && statSync(file).size >= MIN_BYTES
      expect(isAnnalePdfAvailable(url)).toBe(usable)
    }
  })

  it("une absence d'URL se distingue d'un fichier absent (sinon on diagnostique à l'aveugle)", () => {
    expect(pdfUnavailabilityReason("")).toBe("aucune-url")
    expect(pdfUnavailabilityReason("/pdfs/quoi.mp3")).toBe("fichier-absent")
    if (PDF_AVAILABLE_URLS.length > 0) expect(pdfUnavailabilityReason(PDF_AVAILABLE_URLS[0])).toBe("ok")
  })
})
