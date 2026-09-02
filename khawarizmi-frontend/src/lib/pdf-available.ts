/**
 * Disponibilité d'un sujet d'annale hébergé dans `public/pdfs`.
 *
 * Historique du bug (audit 2026-08-31) : la fonction renvoyait `false` **en dur**. L'affichage
 * était donc juste par accident — et il serait resté faux le jour où les fichiers seraient
 * restaurés. Les 12 fichiers présents sont en réalité des pointeurs Git LFS de 131 octets :
 * aucun PDF n'est servi aujourd'hui, et ce module le dit à partir de l'inventaire du dépôt.
 *
 * La source de vérité est `src/lib/pdf-availability.ts`, régénérée par
 * `node scripts/pdf-availability.mjs` (garde de fraîcheur : `src/lib/pdf-available.test.ts`).
 */

import { PDF_AVAILABLE_URLS, PDF_LFS_POINTER_URLS, PDF_TOO_SMALL_URLS } from "./pdf-availability"

/** Libellé élève : court, sans jargon, et ne promet rien. */
export const PDF_MISSING_AR = "الموضوع غير متاح (ملف ناقص)"

/** Détail pour le développeur (attribut `title`), jamais affiché comme un message à l'élève. */
export const PDF_LFS_HINT =
  "Fichier présent mais non restauré : pointeur Git LFS. Lancer `git lfs pull`, puis " +
  "`node scripts/pdf-availability.mjs`."

const AVAILABLE = new Set(PDF_AVAILABLE_URLS)
const LFS = new Set(PDF_LFS_POINTER_URLS)
const TOO_SMALL = new Set(PDF_TOO_SMALL_URLS)

export function isAnnalePdfAvailable(url?: string | null): boolean {
  return typeof url === "string" && url.length > 0 && AVAILABLE.has(url)
}

/** Pourquoi une URL n'est pas servable — distingué pour qu'on répare la bonne chose. */
export function pdfUnavailabilityReason(
  url?: string | null
): "ok" | "aucune-url" | "fichier-absent" | "pointeur-lfs" | "fichier-trop-petit" {
  if (typeof url !== "string" || url.length === 0) return "aucune-url"
  if (AVAILABLE.has(url)) return "ok"
  if (LFS.has(url)) return "pointeur-lfs"
  if (TOO_SMALL.has(url)) return "fichier-trop-petit"
  return "fichier-absent"
}
