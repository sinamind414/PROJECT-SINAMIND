import { describe, expect, it, vi } from "vitest"
import {
  fetchContextualRemediation,
  normalizeRemediation,
  shouldFetchRemediation,
  REMEDIATION_ENDPOINT,
  type FetchRemediationFn,
} from "./manhadjia-remediation"

function okResponse(data: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  } as Response
}

function fakeFetch(handler: (url: string, init: RequestInit) => Promise<Response>): FetchRemediationFn {
  return (url, init) => handler(url, init)
}

describe("shouldFetchRemediation (garde anti-bruit)", () => {
  it("texte trop court → false, aucune requête", () => {
    expect(shouldFetchRemediation("")).toBe(false)
    expect(shouldFetchRemediation("قصير")).toBe(false)
    expect(shouldFetchRemediation("  ")).toBe(false)
    expect(shouldFetchRemediation("هذه جملة طويلة كفاية للاستدعاء")).toBe(true)
  })
})

describe("normalizeRemediation (échec silencieux)", () => {
  it("payload valide → données filtrées", () => {
    const r = normalizeRemediation({
      data: {
        verb: "deduce",
        units: ["unite2-immunite", 42, null],
        relevant_errors: ["خطأ 1", "خطأ 2", 7],
      },
    })
    expect(r).toEqual({
      verb: "deduce",
      unitIds: ["unite2-immunite"],
      errors: ["خطأ 1", "خطأ 2"],
    })
  })

  it("payloads invalides → null", () => {
    expect(normalizeRemediation(null)).toBeNull()
    expect(normalizeRemediation("texte")).toBeNull()
    expect(normalizeRemediation({})).toBeNull()
    expect(normalizeRemediation({ data: "rien" })).toBeNull()
    expect(normalizeRemediation({ error: "verb_slug requis" })).toBeNull()
  })

  it("unités et erreurs vides → null (rien à montrer)", () => {
    expect(normalizeRemediation({ data: { verb: "x", units: [], relevant_errors: [] } })).toBeNull()
  })
})

describe("fetchContextualRemediation (point d'équilibre)", () => {
  const LONG_TEXT = "تمثل الوثيقة منحنى يبين تطور عدد LTc بدلالة الأيام"

  it("succès → POST au bon endpoint avec verb_slug + context", async () => {
    // tableau plutôt que `let … | null` : l'affectation a lieu dans un callback, et
    // l'analyse de flux de TS réduisait `captured` à `never` au moment des assertions.
    const calls: { url: string; init: RequestInit }[] = []
    const r = await fetchContextualRemediation(
      "deduce",
      LONG_TEXT,
      fakeFetch(async (url, init) => {
        calls.push({ url, init })
        return okResponse({ data: { verb: "deduce", units: ["unite2-immunite"], relevant_errors: ["خطأ"] } })
      })
    )
    expect(r?.errors).toEqual(["خطأ"])
    expect(calls[0]?.url).toBe(REMEDIATION_ENDPOINT)
    expect(calls[0]?.init.method).toBe("POST")
    expect(JSON.parse(String(calls[0]?.init.body))).toEqual({ verb_slug: "deduce", context: LONG_TEXT })
  })

  it("HTTP 500 → null (silencieux)", async () => {
    const r = await fetchContextualRemediation("analyse", LONG_TEXT, fakeFetch(async () => okResponse({}, 500)))
    expect(r).toBeNull()
  })

  it("erreur réseau → null (silencieux)", async () => {
    const r = await fetchContextualRemediation(
      "analyse",
      LONG_TEXT,
      fakeFetch(async () => {
        throw new Error("network down")
      })
    )
    expect(r).toBeNull()
  })

  it("JSON invalide → null (silencieux)", async () => {
    const r = await fetchContextualRemediation(
      "analyse",
      LONG_TEXT,
      fakeFetch(async () => {
        return {
          ok: true,
          status: 200,
          json: async () => {
            throw new Error("bad json")
          },
        } as unknown as Response
      })
    )
    expect(r).toBeNull()
  })

  it("timeout → abort puis null (silencieux)", async () => {
    const r = await fetchContextualRemediation(
      "analyse",
      LONG_TEXT,
      fakeFetch(
        (_url, init) =>
          new Promise((_resolve, reject) => {
            init.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")))
          })
      ),
      10
    )
    expect(r).toBeNull()
  })

  it("texte trop court → aucune requête, null direct", async () => {
    const fn = vi.fn(async () => okResponse({ data: { units: ["u"], relevant_errors: ["e"] } }))
    const r = await fetchContextualRemediation("analyse", "قصير", fn)
    expect(r).toBeNull()
    expect(fn).not.toHaveBeenCalled()
  })

  it("payload backend réel (erreur verb_slug manquant) → null", async () => {
    const r = await fetchContextualRemediation(
      "",
      LONG_TEXT,
      fakeFetch(async () => okResponse({ error: "verb_slug requis" }))
    )
    expect(r).toBeNull()
  })
})
