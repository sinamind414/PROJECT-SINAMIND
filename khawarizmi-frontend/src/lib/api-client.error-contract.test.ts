import { afterEach, describe, expect, it, vi } from "vitest"
import { apiClient, httpErrorMessage } from "./api-client"

/**
 * F20 (audit surfaces de correction) — le contrat d'erreur du backend est
 * `{"erreur", "status", "path", "method", "details"}` (khawarizmi-backend/routes/errors.py),
 * et `main.py` enregistre ce handler pour 400/401/403/404. Le front, lui, ne lisait que
 * `data.detail` : **tout** message 4xx produit par le serveur était donc jeté et l'élève
 * voyait « خطأ HTTP 404 » sans savoir ce qui manquait.
 *
 * Ces tests épinglent les deux moitiés du contrat : le message remonte, et le statut
 * reste disponible pour qu'une page affiche un mur conçu plutôt qu'une chaîne technique.
 */

function httpResp(status: number, data: unknown): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => data } as Response
}

function stub(status: number, data: unknown) {
  const fetchMock = vi.fn(async () => httpResp(status, data))
  vi.stubGlobal("fetch", fetchMock)
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Réponse au corps NON JSON : c'est ce que rendent les portes d'entrée et les proxies. */
function rawResp(status: number, body: string, contentType = "text/html; charset=utf-8"): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers({ "content-type": contentType }),
    text: async () => body,
    json: async () => {
      throw new SyntaxError(`Unexpected token '${body.slice(0, 1)}', "${body.slice(0, 20)}" is not valid JSON`)
    },
  } as unknown as Response
}



describe("httpErrorMessage — contrat backend d'abord, détail FastAPI ensuite", () => {
  it("lit « erreur » (contrat Khawarizmi)", () => {
    expect(httpErrorMessage({ erreur: "الفصل غير موجود في البرنامج الرسمي.", status: 404 }, 404)).toBe(
      "الفصل غير موجود في البرنامج الرسمي."
    )
  })

  it("accepte « detail » (réponse FastAPI brute, proxy, vieille route)", () => {
    expect(httpErrorMessage({ detail: "not found" }, 404)).toBe("not found")
  })

  it("ignore un message vide ou non-textuel et retombe sur le générique arabe", () => {
    expect(httpErrorMessage({ erreur: "   ", detail: 42 }, 500)).toBe("خطأ 500")
    expect(httpErrorMessage(null, 502, "fallback")).toBe("fallback")
  })

  it("préfère le contrat au détail quand les deux existent", () => {
    expect(httpErrorMessage({ erreur: "arabe élève", detail: "TechnicalError" }, 400)).toBe("arabe élève")
  })
})

describe("apiClient.request — l'erreur remontée à la page est lisible par l'élève", () => {
  it("404 contrat : message serveur + status attaché (pour un mur, pas une chaîne brute)", async () => {
    stub(404, { erreur: "لا يوجد موضوع مُدخَل لهذا الموضوع بعد.", status: 404, path: "/x", method: "GET" })
    const err = await apiClient.getLesson("ch-1").catch((e: unknown) => e) as Error & { status?: number }
    expect(err).toBeInstanceOf(Error)
    expect(err.message).toBe("لا يوجد موضوع مُدخَل لهذا الموضوع بعد.")
    expect(err.status).toBe(404)
  })

  it("429 : le serveur garde la main sur le texte, sinon limite_atteinte", async () => {
    stub(429, { erreur: "تم بلوغ الحد — 15 تصحيحًا في الساعة." })
    const err = (await apiClient.checkLessonAnswer("c", "b", "x").catch((e: unknown) => e)) as Error & {
      status?: number
    }
    expect(err.message).toContain("15 تصحيحًا")
    expect(err.status).toBe(429)

    stub(429, { detail: undefined })
    const err2 = (await apiClient.checkLessonAnswer("c", "b", "x").catch((e: unknown) => e)) as Error
    expect(err2.message).toBe("تم تجاوز حد الطلبات. حاول مرة أخرى لاحقا.")
  })

  it("500 sans corps : libellé générique arabe, et pas « undefined »", async () => {
    stub(500, {})
    const err = (await apiClient.checkLessonAnswer("c", "b", "x").catch((e: unknown) => e)) as Error & {
      status?: number
    }
    expect(err.message).toBe("خطأ 500")
    expect(err.status).toBe(500)
  })
})

describe("evaluateVerbAnswer — payload validé, pas affirmé", () => {
  it("200 mal formé (ni percentage ni score) → non noté honnête, jamais NaN sur le tableau de bord", async () => {
    stub(200, { message: "upstream renvoyé du HTML tronqué" })
    const r = await apiClient.evaluateVerbAnswer({ verb_slug: "analyse", answer: "x" })
    expect(r).toMatchObject({
      verb_slug: "analyse",
      percentage: 0,
      score: 0,
      score_max: 1,
      ungraded: true,
      source: "ungraded",
    })
    expect(Array.isArray(r.success)).toBe(true)
    expect(r.errors.length).toBeGreaterThan(0)
  })

  it("200 conforme → valeurs conservées, éléments non-textuels filtrés", async () => {
    stub(200, {
      verb_slug: "interpret",
      score: 2.5,
      score_max: 4,
      percentage: 63,
      success: ["lأن", 1, null],
      errors: [],
      missing_markers: ["الحرارة المثلى"],
      forbidden_found: [],
      advice: "أضف لأن.",
      allow_second_attempt: true,
    })
    const r = await apiClient.evaluateVerbAnswer({ verb_slug: "interpret", answer: "x" })
    expect(r).toMatchObject({ score: 2.5, score_max: 4, percentage: 63, allow_second_attempt: true })
    expect(r.success).toEqual(["lأن"])
    expect(r.missing_markers).toEqual(["الحرارة المثلى"])
    expect(r.ungraded).toBeUndefined()
  })

  it("le contrat optionnel lu par la page verbe passe au travers (pas de champ perdu)", async () => {
    stub(200, {
      percentage: 80,
      score: 4,
      score_max: 5,
      dominant_error_code: "NO_CONCLUSION",
      method_percent: 75,
      overall_training_percent: 80,
      science_flags: ["36 ATP"],
      caps_applied: ["cap_science"],
      order_ok: false,
      method_label_ar: "حلّل",
    })
    // Assertion sur les champs typés de l'interface : prouve qu'ils survivent à la
    // normalisation ET au contrat côté page.
    const r = await apiClient.evaluateVerbAnswer({ verb_slug: "analyse", answer: "x" })
    expect(r.percentage).toBe(80)
    expect(r.dominant_error_code).toBe("NO_CONCLUSION")
    expect(r.method_percent).toBe(75)
    expect(r.science_flags).toEqual(["36 ATP"])
    expect(r.caps_applied).toEqual(["cap_science"])
    expect(r.order_ok).toBe(false)
    expect(r.method_label_ar).toBe("حلّل")
  })

  it("200 marqué ungraded par le serveur → le drapeau est conservé", async () => {
    stub(200, { percentage: 0, source: "ungraded", banner_ar: "لا شبكة تقييم." })
    const r = await apiClient.evaluateVerbAnswer({ verb_slug: "deduce", answer: "x" })
    expect(r).toMatchObject({ ungraded: true, source: "ungraded", banner_ar: "لا شبكة تقييم." })
  })
})

describe("request() — un 200 au corps illisible n'est pas un plantage technique", () => {
  it("200 + corps texte « OK » (le cas mesuré sur le domaine fantôme) → message arabe, pas SyntaxError", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => rawResp(200, "OK", "text/plain")))
    const err = (await apiClient.getLesson("ch-1").catch((e: unknown) => e)) as Error & { status?: number }
    expect(err).toBeInstanceOf(Error)
    expect(err.name).not.toBe("SyntaxError")
    expect(err.message).toContain("تعذر قراءة استجابة الخادم")
    expect(err.status).toBe(200)
  })

  it("204 / corps vide → aucune donnée, aucune exception", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => rawResp(204, "", "application/json")))
    await expect(apiClient.getLesson("ch-1")).resolves.toBeUndefined()
  })

  it("200 JSON valide → transmis intact", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => rawResp(200, JSON.stringify({ id: 7, titre: "المحاكاة" }), "application/json"))
    )
    await expect(apiClient.getLesson("ch-1")).resolves.toMatchObject({ id: 7, titre: "المحاكاة" })
  })

  it("404 + page HTML (casse de passerelle) → libellé générique arabe, pas le HTML ni « undefined »", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => rawResp(404, "<!DOCTYPE html><h1>Not Found</h1>")))
    const err = (await apiClient.getLesson("ch-1").catch((e: unknown) => e)) as Error & { status?: number }
    expect(err.message).toBe("خطأ 404")
    expect(err.status).toBe(404)
    expect(err.message).not.toContain("<")
  })
})
