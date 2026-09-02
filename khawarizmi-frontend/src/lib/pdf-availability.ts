/**
 * GÉNÉRÉ par `scripts/pdf-availability.mjs` — ne pas éditer à la main.
 * État de `public/pdfs` au moment de la génération : 0 PDF utilisable(s),
 * 12 pointeur(s) Git LFS (lance `git lfs pull`),
 * 0 fichier(s) trop petit(s).
 *
 * Un test garde ce fichier synchronisé avec le disque :
 * `src/lib/pdf-available.test.ts`.
 */

/** URL publiques dont le fichier est présent ET est un vrai PDF (pas un pointeur LFS). */
export const PDF_AVAILABLE_URLS: readonly string[] = []

/** URL publiques présentes sur le disque mais sous forme de pointeur Git LFS non restauré. */
export const PDF_LFS_POINTER_URLS: readonly string[] = [
  "/pdfs/bac-svt-math/bac-svt-math-2023.pdf",
  "/pdfs/bac-svt-math/bac-svt-math-2024.pdf",
  "/pdfs/bac-svt-math/bac-svt-math-2025.pdf",
  "/pdfs/bac-svt-math/bac-svt-math-2026.pdf",
  "/pdfs/bac-svt/bac-svt-correction-2023.pdf",
  "/pdfs/bac-svt/bac-svt-correction-2024.pdf",
  "/pdfs/bac-svt/bac-svt-correction-2025.pdf",
  "/pdfs/bac-svt/bac-svt-correction-2026.pdf",
  "/pdfs/bac-svt/bac-svt-sujet-2023.pdf",
  "/pdfs/bac-svt/bac-svt-sujet-2024.pdf",
  "/pdfs/bac-svt/bac-svt-sujet-2025.pdf",
  "/pdfs/bac-svt/bac-svt-sujet-2026.pdf",
]

/** URL publiques présentes mais sous le seuil de taille (100 Ko) : suspect, non exploitable. */
export const PDF_TOO_SMALL_URLS: readonly string[] = []
