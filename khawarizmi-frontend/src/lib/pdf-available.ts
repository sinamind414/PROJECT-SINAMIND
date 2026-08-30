/** T1 — les PDF git sont des pointeurs LFS (~131 o), pas des sujets. */

export const PDF_MISSING_AR = "الموضوع غير متاح (ملف ناقص)"

export function isAnnalePdfAvailable(_url?: string | null): boolean {
  // Tant que les fichiers ne sont pas restaurés (> 100 Ko), aucun bouton « فتح ».
  return false
}
