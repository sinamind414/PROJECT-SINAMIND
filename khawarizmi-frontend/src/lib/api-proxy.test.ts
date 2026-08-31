/**
 * Le proxy d'API `/api/*` doit être transparent pour l'élève : même chemin, mêmes en-têtes de session,
 * mêmes statuts — et une erreur 502 lisible quand le pont tombe (jamais un `Failed to fetch` nu).
 *
 * Contexte (rapport §11, dette D1 ; architecture §3) : avant ce fichier, l'origine du backend était figée
 * au **build** par `next.config.ts`, pendant que la CI ne re-déploie que Railway. Changer de domaine
 * côté Railway recassait donc la production sans commit ni CI rouge. Le proxy lit `API_ORIGIN` par requête.
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

const ROUTE = fileURLToPath(new URL("../app/api/[...path]/route.ts", import.meta.url))
const read = (p: URL | string) => readFileSync(typeof p === "string" ? p : fileURLToPath(p), "utf-8")

type Call = { url: string; init: RequestInit & { headers: Headers } }

/** Enveloppe d'import : `vi.resetModules()` est obligatoire, sinon la config est figée au 1er import. */
async function load(env: Record<string, string | undefined>) {
  const prev = { ...process.env }
  for (const [k, v] of Object.entries(env)) {
    if (v === undefined) delete process.env[k]
    else process.env[k] = v
  }
  vi.resetModules()
  const mod = await import("../app/api/[...path]/route")
  return {
    mod,
    restore() {
      for (const k of Object.keys(process.env)) delete process.env[k]
      Object.assign(process.env, prev)
    },
  }
}

function fakeReq(url: string, init?: RequestInit): Request {
  return new Request(url, init)
}

const ctx = (path: string[]) => ({ params: Promise.resolve({ path }) })

let calls: Call[] = []

beforeEach(() => {
  calls = []
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL | Request, init: RequestInit = {}) => {
      calls.push({ url: String(input), init: { ...init, headers: init.headers as Headers } })
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "content-type": "application/json", "content-encoding": "gzip", "set-cookie": "sid=42; Path=/" },
      })
    }),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("résolution de l'origine", () => {
  it("API_ORIGIN prime, puis NEXT_PUBLIC_API_URL, puis le repli de dev", async () => {
    let { mod, restore } = await load({ API_ORIGIN: "https://back.example/railway", NEXT_PUBLIC_API_URL: "https://old.vercel.env" })
    expect(mod.apiOrigin()).toBe("https://back.example/railway")
    restore()

    ;({ mod, restore } = await load({ API_ORIGIN: undefined, NEXT_PUBLIC_API_URL: "https://old.vercel.env" }))
    expect(mod.apiOrigin()).toBe("https://old.vercel.env")
    restore()

    ;({ mod, restore } = await load({ API_ORIGIN: undefined, NEXT_PUBLIC_API_URL: undefined }))
    expect(mod.apiOrigin()).toBe("http://localhost:8000")
    restore()
  })

  it("ne double jamais le /api et ne garde pas de barre oblique finale", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://back.example/" })
    const req = fakeReq("https://site.dz/api/manhadjiya/verbs?page=2")
    await mod.GET(req, ctx(["manhadjiya", "verbs"]))
    restore()
    expect(calls[0].url).toBe("https://back.example/api/manhadjiya/verbs?page=2")
  })
})

describe("transparence pour l'élève", () => {
  it("reconstruit le chemin, y compris un segment encodé, et préserve la query", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://back.example" })
    await mod.GET(fakeReq("https://site.dz/api/exercices/%20chapitre-11/correct?x=1&y=2"), ctx(["exercices", " chapitre-11", "correct"]))
    restore()
    const u = new URL(calls[0].url)
    expect(u.pathname).toBe("/api/exercices/%20chapitre-11/correct")
    expect(u.searchParams.get("x")).toBe("1")
    expect(u.searchParams.get("y")).toBe("2")
  })

  it("transmet le cookie de session mais pas les en-têtes de transport", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://back.example" })
    const req = fakeReq("https://site.dz/api/progress", {
      headers: { cookie: "sid=42", authorization: "Bearer t", host: "site.dz", "accept-encoding": "gzip", "x-requested-with": "XMLHttpRequest" },
    })
    await mod.GET(req, ctx(["progress"]))
    restore()
    const h = calls[0].init.headers
    expect(h.get("cookie")).toBe("sid=42")
    expect(h.get("authorization")).toBe("Bearer t")
    expect(h.get("x-requested-with")).toBe("XMLHttpRequest")
    expect(h.get("host")).toBeNull()
    expect(h.get("accept-encoding")).toBeNull()
  })

  it("relit le corps sur un POST et passe le flux HTTP tel quel (statut + set-cookie)", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://back.example" })
    const req = fakeReq("https://site.dz/api/grade", { method: "POST", body: JSON.stringify({ q: 1 }) })
    const res = await mod.POST(req, ctx(["grade"]))
    restore()
    expect(calls[0].init.method).toBe("POST")
    expect(new TextDecoder().decode(calls[0].init.body as ArrayBuffer)).toBe('{"q":1}')
    expect(res.status).toBe(200)
    expect(res.headers.get("content-type")).toBe("application/json")
    expect(res.headers.get("set-cookie")).toContain("sid=42")
    // content-encoding retiré : undici a déjà décompressé, le double-encoder corromprait la réponse.
    expect(res.headers.get("content-encoding")).toBeNull()
  })

  it("propage un 429 de quota tel quel (le front a un contrat dessus)", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://back.example" })
    vi.mocked(fetch).mockImplementationOnce(async () => new Response(JSON.stringify({ erreur: "quota" }), { status: 429 }))
    const res = await mod.POST(fakeReq("https://site.dz/api/grade", { method: "POST", body: "{}" }), ctx(["grade"]))
    restore()
    expect(res.status).toBe(429)
  })
})

describe("quand le pont tombe", () => {
  it("répond 502 avec la forme d'erreur du backend, jamais une stack trace", async () => {
    const { mod, restore } = await load({ API_ORIGIN: "https://domaine-mort.example" })
    vi.mocked(fetch).mockImplementationOnce(async () => {
      throw new Error("getaddrinfo ENOTFOUND domaine-mort.example")
    })
    const err = vi.spyOn(console, "error").mockImplementation(() => {})
    const res = await mod.GET(fakeReq("https://site.dz/api/progress"), ctx(["progress"]))
    const body = await res.json()
    restore()
    expect(res.status).toBe(502)
    expect(body.erreur).toContain("injoignable")
    expect(body.status).toBe(502)
    expect(body.path).toBe("/api/progress")
    expect(body.method).toBe("GET")
    expect(body.requestId).toMatch(/^proxy-/)
    // La cause technique va dans les logs serveur, pas dans la copie de l'élève.
    expect(JSON.stringify(body)).not.toContain("ENOTFOUND")
    expect(err).toHaveBeenCalled()
    err.mockRestore()
  })
})

describe("câblage", () => {
  const route = read(ROUTE)
  const nextConfig = read(new URL("../../next.config.ts", import.meta.url))

  it("est monté sur le même préfixe /api que les appels du client", () => {
    expect(route).toContain("`${apiOrigin()}/api/${path}`")
    expect(route).toContain("export const runtime = \"nodejs\"")
    expect(route).toContain("export const dynamic = \"force-dynamic\"")
  })

  it("partage le repli de dev avec next.config.ts (deux sources de vérité = la panne d'origine)", () => {
    expect(route).toContain('"http://localhost:8000"')
    expect(nextConfig).toContain('"http://localhost:8000"')
  })

  it("n'écrit aucune origine en dur", () => {
    expect(route).not.toMatch(/https?:\/\/(?!localhost)[a-z0-9.-]+\.[a-z]{2,}/i)
  })
})
