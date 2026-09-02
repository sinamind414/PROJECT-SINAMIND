import { afterEach, describe, expect, it, vi } from "vitest"
import { apiClient } from "./api-client"

/**
 * S39 (audit surfaces de correction 2026-08-30) — le quota côté élève.
 *
 * Avant : /api/grade en surquota renvoyait un 429 → `apiClient.grade` LEVAIT →
 * le `Promise.all` de ScenarioRunner rejetait → TOUTES les copies du scénario
 * étaient déclarées « تعذر التصحيح », les notes déjà calculées perdues, et
 * l'élève ne savait pas qu'il s'agissait d'un quota horaire.
 *
 * Après : un 429 est un « non noté » honnête muni du message serveur et du délai
 * de reprise — une panne HTTP (5xx) reste une panne.
 */

const QUOTA_BODY = {
  erreur: "تم بلوغ حد التصحيح. ليست علامة بكالوريا رسمية.",
  code: "quota_exceeded",
  status: 429,
  banner_ar: "تم بلوغ حد التصحيح — 15 تصحيحًا في الساعة.",
  retry_after_s: 870,
}

function httpResp(status: number, data: unknown): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => data,
  } as Response
}

type QuotaAware = {
  ungraded?: boolean
  question_id?: string
  banner_ar?: string
  quota?: boolean
  retry_after_s?: number
}

async function gradeWith(status: number, data: unknown): Promise<QuotaAware> {
  const fetchMock = vi.fn(async () => httpResp(status, data))
  vi.stubGlobal("fetch", fetchMock)
  return (await apiClient.grade({
    question_id: "enzyme-temp-analyse",
    answer: "تمثل الوثيقة منحنى النشاط.",
    surface: "da",
  })) as QuotaAware
}

describe("apiClient.grade — 429 quota dépassé", () => {
  afterEach(() => vi.unstubAllGlobals())

  it("ne lève plus : ungraded + banner_ar du serveur + retry_after_s", async () => {
    const r = await gradeWith(429, QUOTA_BODY)
    expect(r.ungraded).toBe(true)
    expect(r.quota).toBe(true)
    expect(r.banner_ar).toContain("تم بلوغ حد التصحيح")
    expect(r.retry_after_s).toBe(870)
    expect(r.question_id).toBe("enzyme-temp-analyse")
  })

  it("429 sans JSON lisible -> bannière de secours arabe, jamais un throw", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 429,
        json: async () => {
          throw new Error("not json")
        },
      })),
    )
    const r = (await apiClient.grade({ question_id: "x", answer: "ي" })) as QuotaAware
    expect(r.ungraded).toBe(true)
    expect(r.banner_ar).toContain("ليست علامة بكالوريا رسمية")
    expect(r.retry_after_s).toBeUndefined()
  })

  it("429 avec seulement `erreur` -> le message serveur est repris", async () => {
    const r = await gradeWith(429, { erreur: "حد التصحيح", code: "quota_exceeded" })
    expect(r.banner_ar).toBe("حد التصحيح")
    expect(r.quota).toBe(true)
  })

  it("une vraie panne (500) reste une panne : throw", async () => {
    await expect(gradeWith(500, { detail: "boom" })).rejects.toBeInstanceOf(Error)
  })

  it("422 ungraded (sans grille) reste mappé comme avant — non-régression S3", async () => {
    const r = await gradeWith(422, { code: "ungraded", question_id: "sans-grille", banner_ar: "بلا شبكة" })
    expect(r.ungraded).toBe(true)
    expect(r.quota).toBeUndefined()
    expect(r.question_id).toBe("sans-grille")
  })
})
