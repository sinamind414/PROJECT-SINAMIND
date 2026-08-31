import { existsSync, readFileSync, readdirSync } from "node:fs"
import { fileURLToPath } from "node:url"
import { describe, expect, it } from "vitest"

/**
 * Garde de configuration de déploiement (rapport §11, mesuré le 2026-08-31).
 *
 * Ce qui a été trouvé : la CSP Whitelistait un domaine Railway écrit en dur qui **ne sert pas ce
 * dépôt** — son `/health` répond « OK » alors que le nôtre renvoie un objet de diagnostic, et ses
 * 404 ont la forme `{"message","requestId"}` alors que `routes/errors.py` émet
 * `{"erreur","status","path","method"}` ; `requestId` n'apparaît dans aucun `.py` du repo.
 * Pendant ce temps, le `NEXT_PUBLIC_API_URL` configuré sur Vercel pointait vers un domaine Railway
 * **non provisionné** : `/api/*` servi par le frontend répond la page « The train has not arrived at
 * the station » de Railway. Donc (a) l'app production n'atteint aucune API, et (b) corriger l'URL
 * côté env sans retoucher la CSP laisse le site cassé — le navigateur bloquant la nouvelle origine.
 *
 * D'où ces trois assertions : une seule source de vérité pour l'origine, aucun hôte en dur dans la
 * CSP, et le doublet mort du client API reste marqué mort et reste non importé.
 */

const ROOT = new URL("../../", import.meta.url)
const read = (rel: string) => readFileSync(fileURLToPath(new URL(rel, ROOT)), "utf8")
const cfg = read("next.config.ts")
const legacy = read("lib/api-client.ts")

describe("CSP et proxy partagent la même origine d'API", () => {
  it("aucun domaine n'est écrit en dur dans la CSP", () => {
    // Le bloc `const csp = […]`, commentaires de documentation exclus : on juge le code, pas le prose.
    const block = cfg.slice(cfg.indexOf("const csp = ["), cfg.indexOf("].join("))
    const code = block
      .split("\n")
      .filter((l) => !/^\s*(\/\/|\*|\/\*)/.test(l))
      .join("\n")
    expect(code).toContain(`connect-src 'self'`)
    expect(code).not.toMatch(/https:\/\/[a-z0-9.-]+\./i)
  })

  it("l'origine est dérivée de la variable utilisée par les rewrites", () => {
    expect(cfg).toContain("apiOrigin(process.env.NEXT_PUBLIC_API_URL)")
    // Les deux rewrites doivent lire la MÊME variable ; sinon CSP et proxy dérivent séparément.
    const rewrites = cfg.slice(cfg.indexOf("async rewrites"))
    expect(rewrites.match(/process\.env\.NEXT_PUBLIC_API_URL/g)?.length).toBeGreaterThanOrEqual(2)
  })

  it("une URL invalide ou absente retombe sur null, sans casser la construction de l'en-tête", () => {
    // Pas d'exécution dynamique de la config : on vérifie le contrat d'écriture (style du repo).
    expect(cfg).toMatch(/if \(!raw\) return null/)
    expect(cfg).toMatch(/catch \{\s*return null\s*\}/)
    expect(cfg).toMatch(/connect-src 'self'\$\{origin \? ` \$\{origin\}` : ""\}/)
  })
})

describe("doublet mort du client API", () => {
  it("le client hérité à la racine se déclare DEAD", () => {
    expect(legacy).toContain("DEAD + DANGEREUX")
  })

  it("il n'est importé par aucun fichier de src/ (le vivant est src/lib/api-client.ts)", () => {
    const dir = fileURLToPath(new URL("src/", ROOT))
    const hits: string[] = []
    const walk = (d: string) => {
      for (const e of readdirSync(d, { withFileTypes: true })) {
        const abs = `${d}/${e.name}`
        if (e.isDirectory()) walk(abs)
        else if (/\.(ts|tsx)$/.test(e.name) && !e.name.endsWith(".test.ts")) {
          const t = readFileSync(abs, "utf8")
          const importsLegacy = [...t.matchAll(/from\s+"([^"]*lib\/api-client)"/g)].some(
            (m) => !m[1].startsWith("@/lib/")
          )
          if (importsLegacy) hits.push(abs.replace(dir, "src/"))
        }
      }
    }
    if (existsSync(dir)) walk(dir)
    expect(hits).toEqual([])
  })
})
