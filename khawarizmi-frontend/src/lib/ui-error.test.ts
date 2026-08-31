import { readFileSync, readdirSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"
import { readableError } from "./ui-error"
import { UI_AR } from "./translations"

/**
 * Ce que l'élève lit quand le serveur ne parle pas (rapport §13).
 *
 * Huit pages faisaient `setError(e.message)` : depuis F20 le message arabe du serveur remonte
 * enfin, mais une panne réseau, un corps HTML, un `SyntaxError` ou un vieux repli français
 * arrivaient tels quels sur un écran RTL. Ces tests verrouillent la table de traduction et, en
 * garde source, interdisent de revenir à la chaîne brute.
 */

const arabe = (s: string) => /[؀-ۿ]/.test(s)
const err = (message: string, status?: number) => {
  const e = new Error(message) as Error & { status?: number }
  if (status !== undefined) e.status = status
  return e
}

describe("readableError — la parole au serveur quand elle est utile", () => {
  it("le message arabe du serveur passe intact, sans le préfixe « Error: »", () => {
    expect(readableError(err("Error: لا يوجد موضوع مُدخَل لهذا الموضوع بعد."))).toBe(
      "لا يوجد موضوع مُدخَل لهذا الموضوع بعد."
    )
  })

  it("un objet { message, status } est compris (appel depuis le client API)", () => {
    expect(readableError({ message: "الخادم مشغول", status: 503 })).toBe("الخادم مشغول")
  })

  it("un message serveur trop long n'est pas recraché tel quel", () => {
    const huge = "خطأ ".repeat(200)
    expect(readableError(err(huge))).not.toBe(huge)
  })
})

describe("readableError — un statut connu vaut une phrase, pas un chiffre", () => {
  it.each([
    [401, "انتهت الجلسة"],
    [403, "حساب مفعّل"],
    [404, "غير متوفر على الخادم"],
    [500, "المشكلة ليست في إجابتك"],
    [502, "المشكلة ليست في إجابتك"],
  ])("status %i →arabe %s", (status, fragment) => {
    const out = readableError(err("Internal Server Error", status))
    expect(out).toContain(fragment)
    expect(arabe(out)).toBe(true)
  })

  it("429 réutilise le libellé de limite déjà connu de l'élève", () => {
    expect(readableError(err("Too Many Requests", 429))).toBe(UI_AR.limite_atteinte)
  })
})

describe("readableError — le technique ne traverse pas la frontière", () => {
  it.each([
    ["Failed to fetch", "تعذر الاتصال بالخادم"],
    ["TypeError: Failed to fetch", "تعذر الاتصال بالخادم"],
    ['Unexpected token \'O\', "OK" is not valid JSON', UI_AR.reponse_illisible],
    ["timeout of 30000ms exceeded", "انتهت مهلة الانتظار"],
    ["AbortError: signal is aborted", "تم إيقاف الطلب"],
    ["<!DOCTYPE html><h1>502 Bad Gateway</h1>", undefined],
    ["NetworkError when attempting to fetch resource.", "تعذر الاتصال بالخادم"],
  ])("%#… %s → contient %s", (raw, fragment) => {
    const out = readableError(err(raw))
    expect(arabe(out)).toBe(true)
    if (fragment) expect(out).toContain(fragment)
    // aucune de ces chaînes ne doit être recrachée telle quelle
    expect(out).not.toBe(raw)
    expect(out).not.toMatch(/fetch|JSON|DOCTYPE|Abort/i)
  })

  it("un vieux repli français ne remonte jamais à l'écran arabe", () => {
    expect(readableError(err("Erreur de chargement"))).not.toContain("Erreur")
    expect(arabe(readableError(err("Erreur de chargement")))).toBe(true)
  })

  it("le repli fourni par l'appelant gagne quand le serveur est muet", () => {
    expect(readableError(new Error(""), "تعذر تسجيل الدخول")).toBe("تعذر تسجيل الدخول")
    expect(readableError(undefined, "تعذر تسجيل الدخول")).toBe("تعذر تسجيل الدخول")
    expect(readableError(null)).toBe(UI_AR.erreur_chargement)
    expect(readableError("chaîne quelconque")).toBe(UI_AR.erreur_chargement)
  })
})

describe("garde source — plus de chaîne technique dans les écrans élèves", () => {
  const SRC = fileURLToPath(new URL("../../src", import.meta.url))

  it("aucune page ne recolle e.message / String(e) dans un état d'erreur", () => {
    const offenders: string[] = []
    const walk = (dir: string) => {
      for (const e of readdirSync(dir, { withFileTypes: true })) {
        const abs = `${dir}/${e.name}`
        if (e.isDirectory()) walk(abs)
        else if (e.name.endsWith(".tsx")) {
          const t = readFileSync(abs, "utf8")
          if (/setError\(\s*(String\(|\w+ instanceof Error)/.test(t) || /setError\(\s*e\.message/.test(t)) {
            offenders.push(abs.replace(SRC, ""))
          }
        }
      }
    }
    walk(SRC)
    expect(offenders).toEqual([])
  })
})
