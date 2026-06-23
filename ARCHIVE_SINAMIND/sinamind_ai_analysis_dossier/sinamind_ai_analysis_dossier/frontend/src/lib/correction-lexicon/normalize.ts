export function normalizeArabicScientificText(text: string) {
  return text
    .trim()
    .toLowerCase()
    .replace(/[إأآا]/g, "ا")
    .replace(/ى/g, "ي")
    .replace(/ة/g, "ه")
    .replace(/[\u064B-\u065F\u0670]/g, "")
    .replace(/[()\[\]{}:;،,.!؟?\-_/\\]+/g, " ")
    .replace(/\s+/g, " ")
}

export function uniqueNormalized(values: string[]) {
  const seen = new Set<string>()
  const result: string[] = []

  values.forEach((value) => {
    const raw = value?.trim()
    if (!raw) return
    const normalized = normalizeArabicScientificText(raw)
    if (!normalized || seen.has(normalized)) return
    seen.add(normalized)
    result.push(raw)
  })

  return result
}
