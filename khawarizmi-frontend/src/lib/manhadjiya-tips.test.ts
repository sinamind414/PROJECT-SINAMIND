/**
 * Contrat des données officielles Manhadjiya affichées par le panneau « المرجع الرسمي ».
 *
 * Contexte (audit 2026-08-31, rapport §15) : `ManhadjiyaTips` était orphelin AUCUNE page ne
 * le montait, et il était faux sur deux points mesurés :
 *   - `Promise.all([fetch, fetch, fetch])` sans contrôle de statut : un seul endpoint en
 *     panne (404 HTML en prod, par exemple) faisait lever `.json()` → les TROIS onglets
 *     vides, un simple `console.error`, et aucun moyen de réessayer ;
 *   - tables de libellés/couleurs indexées sur des clés arabes alors que le backend renvoie
 *     `in_class`, `remember`, `compare_and_analyse` … → icônes et échelle de Bloom toutes en
 *     repli.
 *
 * Style du repo : assertions pures, sans DOM (vitest est en environnement `node`).
 */

import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

import {
  BLOOM_LABELS_AR,
  ERROR_LABELS_AR,
  MANHADJIYA_TIPS_ENDPOINTS,
  TIP_LABELS_AR,
  bloomLabel,
  countItems,
  errorLabel,
  fetchManhadjiyaTips,
  normalizeCategoryMap,
  orderedEntries,
  tipIcon,
  tipLabel,
  tipsFullyFailed,
  type FetchTipsFn,
} from "./manhadjiya-tips"

const FRONTEND_ROOT = new URL("../", import.meta.url)
const readFront = (rel: string) => readFileSync(fileURLToPath(new URL(rel, FRONTEND_ROOT)), "utf-8")
// Le dépôt est un monorepo : la source backend est lisible ici, ce qui permet de garder le
// libellier synchronisé avec les dictionnaires réels plutôt qu'avec une copie de fixture.
const readBackend = (rel: string) =>
  readFileSync(fileURLToPath(new URL(`../../khawarizmi-backend/${rel}`, FRONTEND_ROOT)), "utf-8")

/** Clés de premier niveau d'un dictionnaire Python, en ignorant les chaînes et les {} imbriqués. */
function topLevelKeys(src: string, constName: string): string[] {
  const header = new RegExp(`^${constName}\\s*(?::[^=\\n]+)?=\\s*\\{`, "m").exec(src)
  expect(header, `${constName} introuvable dans la source backend`).not.toBeNull()
  let i = header!.index + header![0].length // juste après l'accolade ouvrante
  let depth = 1
  const keys: string[] = []
  while (i < src.length && depth > 0) {
    const c = src[i]
    if (c === '"' || c === "'") {
      const str = c === '"' ? /^"((?:[^"\\]|\\.)*)"/ : /^'((?:[^'\\]|\\.)*)'/
      const m = str.exec(src.slice(i))
      if (!m) {
        i++
        continue
      }
      // Une chaîne suivie de « : » à la profondeur 1 est une clé ; sinon c'est du contenu.
      if (depth === 1 && /^\s*:/.test(src.slice(i + m[0].length))) keys.push(m[1])
      i += m[0].length
      continue
    }
    if (c === "#") {
      const nl = src.indexOf("\n", i)
      i = nl === -1 ? src.length : nl
      continue
    }
    if (c === "{" || c === "[" || c === "(") depth++
    else if (c === "}" || c === "]" || c === ")") depth--
    i++
  }
  return keys
}

const PROMPT_SRC = readBackend("prompts/correction_prompt.py")

describe("manhadjiya-tips — le libellier couvre les clés réellement envoyées", () => {
  it.each([
    ["REVISION_TIPS_AR", TIP_LABELS_AR],
    ["COMMON_BAC_ERRORS", ERROR_LABELS_AR],
    ["VERB_COGNITIVE_LEVELS", BLOOM_LABELS_AR],
  ] as const)("chaque clé de %s a un libellé arabe côté UI", (constName, labels) => {
    const keys = topLevelKeys(PROMPT_SRC, constName)
    expect(keys.length).toBeGreaterThan(0)
    const orphan = keys.filter((k) => !(k in labels))
    // Un libellé manquant = une clé technique affichée à un élève arabophone.
    expect(orphan).toEqual([])
  })

  it("les icônes des conseils ne retombent pas toutes sur le défaut", () => {
    const keys = topLevelKeys(PROMPT_SRC, "REVISION_TIPS_AR")
    const withIcon = keys.filter((k) => tipIcon(k) !== "📌")
    expect(withIcon.length).toBe(keys.length - 1) // seul official_recommendations est 📌
  })

  it("un titre inconnu reste affiché tel quel (pas de clé masquée, pas de plantage)", () => {
    expect(tipLabel("categorie_nouvelle")).toBe("categorie_nouvelle")
    expect(errorLabel("unknown")).toBe("unknown")
    expect(bloomLabel("evaluate")).toBe("evaluate")
  })
})

describe("normalizeCategoryMap — la réponse du backend n'est jamais supposée propre", () => {
  it("garde les listes de chaînes sous `data`", () => {
    expect(
      normalizeCategoryMap({ data: { in_class: ["a", "b"], at_home: [] }, count: 2 })
    ).toEqual({ in_class: ["a", "b"] })
  })

  it("jette les éléments non chaînes et les blancs (un <li> vide n'est pas un conseil)", () => {
    expect(normalizeCategoryMap({ data: { x: ["ok", 42, null, "   ", {}] } })).toEqual({ x: ["ok"] })
  })

  it.each([
    ["payload nul", null],
    ["page HTML (404 Vercel→Railway)", "<!doctype html>"],
    ["tableau au lieu d'un objet", [1, 2]],
    ["`data` absent (contrat non respecté)", { erreur: "boom" }],
    ["`data` non objet", { data: "aucune donnée" }],
  ])("→ null pour %s (= échec, et non « vide »)", (_label, payload) => {
    expect(normalizeCategoryMap(payload)).toBeNull()
  })

  it("distincte « endpoint qui répond vide » de « endpoint en panne »", () => {
    expect(normalizeCategoryMap({ data: {} })).toEqual({})
    expect(normalizeCategoryMap({ data: { a: [1, 2] } })).toEqual({})
  })
})

describe("orderedEntries — l'ordre pédagogique, sans inventer de catégorie", () => {
  const map = { at_home: ["x"], in_class: ["y"], zzz: ["w"], aaa: ["v"] }

  it("pose les clés connues dans l'ordre déclaré, puis les inconnues triées", () => {
    expect(orderedEntries(map, ["in_class", "at_home"]).map(([k]) => k)).toEqual([
      "in_class",
      "at_home",
      "aaa",
      "zzz",
    ])
  })

  it("ne crée jamais une catégorie absente du payload", () => {
    expect(orderedEntries({ in_class: ["y"] }, ["in_class", "at_home", "group_study"])).toEqual([
      ["in_class", ["y"]],
    ])
  })

  it("countItems somme les entrées réellement retenues", () => {
    expect(countItems(map)).toBe(4)
    expect(countItems({})).toBe(0)
  })
})

const okJson = (body: unknown): Response =>
  new Response(JSON.stringify(body), { status: 200, headers: { "content-type": "application/json" } })
const htmlError = (status = 404): Response =>
  new Response("<!doctype html><title>404</title>", { status })

function fakeFetch(perUrl: Record<string, Response | Error>): FetchTipsFn {
  return async (url) => {
    const behaviour = perUrl[url]
    if (behaviour === undefined) throw new Error(`URL non attendue dans le test : ${url}`)
    if (behaviour instanceof Error) throw behaviour
    return behaviour
  }
}

describe("fetchManhadjiyaTips — dégradation par onglet, jamais de rejet", () => {
  const { tips: tipsUrl, errors: errorsUrl, levels: levelsUrl } = MANHADJIYA_TIPS_ENDPOINTS

  it("les trois répondent → rien en échec, tout est normalisé", async () => {
    const r = await fetchManhadjiyaTips(
      fakeFetch({
        [tipsUrl]: okJson({ data: { in_class: ["a"] } }),
        [errorsUrl]: okJson({ data: { methodology: ["m"] } }),
        [levelsUrl]: okJson({ data: { remember: ["عرف"] } }),
      })
    )
    expect(r.failed).toEqual([])
    expect(r.tips).toEqual({ in_class: ["a"] })
    expect(r.errors).toEqual({ methodology: ["m"] })
    expect(r.levels).toEqual({ remember: ["عرف"] })
    expect(tipsFullyFailed(r)).toBe(false)
  })

  it("régression du bug n° 1 : un 404 HTML ne vide plus les deux autres onglets", async () => {
    const r = await fetchManhadjiyaTips(
      fakeFetch({
        [tipsUrl]: htmlError(404),
        [errorsUrl]: okJson({ data: { form: ["f"] } }),
        [levelsUrl]: okJson({ data: { apply: ["احسب"] } }),
      })
    )
    expect(r.failed).toEqual(["tips"])
    expect(r.tips).toEqual({})
    expect(r.errors).toEqual({ form: ["f"] })
    expect(r.levels).toEqual({ apply: ["احسب"] })
  })

  it("200 mais corps invraisemblable → échec de section, pas de crash du rendu", async () => {
    const r = await fetchManhadjiyaTips(
      fakeFetch({
        [tipsUrl]: new Response("ups", { status: 200 }),
        [errorsUrl]: okJson({ data: null }),
        [levelsUrl]: okJson({ data: {} }),
      })
    )
    expect(r.failed).toEqual(["tips", "errors"]) // `data: {}` = vide mais bien répondu
    expect(r.levels).toEqual({})
    expect(tipsFullyFailed(r)).toBe(false)
  })

  it("panne réseau sur les trois → échec total signalé comme tel", async () => {
    const down = () => Promise.reject(new Error("Failed to fetch"))
    const r = await fetchManhadjiyaTips(down as FetchTipsFn)
    expect(r.failed).toEqual(["tips", "errors", "levels"])
    expect(tipsFullyFailed(r)).toBe(true)
  })

  it("une requête qui pend est coupée par le timeout, et l'élève n'attend pas le spinner", async () => {
    const hangUntilAbort: FetchTipsFn = (_url, init) =>
      new Promise((_resolve, reject) => {
        init?.signal?.addEventListener("abort", () =>
          reject(Object.assign(new Error("aborted"), { name: "AbortError" }))
        )
      })
    const r = await fetchManhadjiyaTips(hangUntilAbort, 5)
    expect(r.failed).toEqual(["tips", "errors", "levels"])
  })

  it("la requête est annulée sur le timeout (pas de requête zombie après rendu)", async () => {
    let sawAbortSignal = false
    const spy: FetchTipsFn = (_url, init) => {
      sawAbortSignal = Boolean(init?.signal)
      return Promise.resolve(okJson({ data: {} }))
    }
    await fetchManhadjiyaTips(spy)
    expect(sawAbortSignal).toBe(true)
  })
})

describe("câblage du panneau (il était orphelin — on ne le redétache pas)", () => {
  const page = readFront("app/methodology/page.tsx")
  const component = readFront("components/methodology/ManhadjiyaTips.tsx")

  it("/methodology monte le panneau", () => {
    expect(page).toContain('import ManhadjiyaTips from "@/components/methodology/ManhadjiyaTips"')
    expect(page).toContain("<ManhadjiyaTips />")
  })

  it("le composant ne rejoue plus son propre contrat réseau", () => {
    expect(component).not.toContain("console.error")
    expect(component).not.toContain("fetch(")
    expect(component).not.toContain("/api/manhadjiya/") // une seule source : le lib
    expect(component).toContain("fetchManhadjiyaTips()")
  })

  it("un échec se dit et se relance, il ne s'affiche pas comme un « 0 »", () => {
    expect(component).toContain("إعادة المحاولة")
    expect(component).toContain("tipsFullyFailed")
    expect(component).toContain("غير متاح")
  })

  it("l'échelle de Bloom est indexée sur les clés du backend", () => {
    for (const key of Object.keys(BLOOM_LABELS_AR)) {
      expect(component).toContain(`${key}:`)
    }
  })
})
