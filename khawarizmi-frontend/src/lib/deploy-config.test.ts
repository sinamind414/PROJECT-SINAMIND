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
 * D'où ces assertions : une seule source de vérité pour l'origine, aucun hôte en dur dans la CSP,
 * aucun rewrite `/api/*` susceptible de masquer le proxy runtime, et le doublet mort du client API
 * reste marqué mort et reste non importé.
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

  it("l'origine de la CSP est dérivée de la variable d'environnement, jamais d'un hôte en dur", () => {
    // Depuis F32 + D1 : CSP, rewrite /health et proxy runtime partagent UN SEUL résolveur
    // (src/lib/api-origin.ts). Deux implémentations de la même variable, c'est exactement comment
    // la panne §11 a pu vivre : on changeait l'une, l'autre restait en retard.
    expect(cfg).toContain('import { cspApiOrigin, resolvedApiOrigin } from "./src/lib/api-origin"')
    expect(cfg).toContain("const origin = cspApiOrigin()")
    expect(cfg).toContain("destination: `${resolvedApiOrigin()}/health`")
    // `connect-src` et le proxy doivent partir de la même variable, sinon changer l'une casse l'autre.
    expect(cfg).toContain("`connect-src 'self'${origin ? ` ${origin}` : \"\"}`")
  })

  it("aucun rewrite ne précède le proxy runtime sur /api (faute de quoi il le masque)", () => {
    // Mesure du 2026-08-31 : avec `API_ORIGIN=http://127.0.0.1:8999` (port mort) et un amont vivant sur
    // :8000, la requête `/api/...` répondait le JSON de :8000 — le rewrite `afterFiles` servait la
    // requête AVANT la route dynamique. Le proxy runtime ne servait donc jamais rien en prod, malgré
    // ses tests unitaires verts. D'où cette garde : le rewrite `/api/:path*` ne doit pas revenir.
    const rewrites = cfg.slice(cfg.indexOf("async rewrites"))
    expect(rewrites).not.toMatch(/source:\s*"\/api\/:path\*"/)
    expect(rewrites).toContain('source: "/health"')
    const lib = read("src/lib/api-origin.ts")
    const proxy = read("src/app/api/[...path]/route.ts")
    // Un seul endroit lit les variables d'env ; le handler ne fait que déléguer.
    expect(lib).toContain("env.API_ORIGIN || env.NEXT_PUBLIC_API_URL")
    expect(lib).toContain('export const DEV_API_ORIGIN = "http://localhost:8000"')
    expect(proxy).toContain("resolvedApiOrigin()")
    expect(proxy).not.toContain("process.env.API_ORIGIN ||")
    // `@/lib/...` n'est pas résolvable dans next.config.ts (le bundler de la config ignore l'alias) :
    // l'import doit rester relatif, sinon la config casse au build et personne ne le voit en dev.
    expect(cfg).toMatch(/from "\.[\/"]+src\/lib\/api-origin"/)
  })

  it("une URL invalide ou absente retombe sur null, sans casser la construction de l'en-tête", () => {
    // Le contrat vit maintenant dans le résolveur partagé ; on vérifie l'écriture (style du repo :
    // pas d'exécution de la config Next dans un test).
    const lib = read("src/lib/api-origin.ts")
    expect(lib).toMatch(/if \(!raw\) return null/)
    expect(lib).toMatch(/catch \{\s*return null\s*\}/)
    expect(lib).toMatch(/u\.protocol === "http:" \|\| u\.protocol === "https:" \? u\.origin : null/)
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
