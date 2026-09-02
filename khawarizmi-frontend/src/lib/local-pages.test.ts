/**
 * Verrous de la déverrouillage local (2026-09-01).
 *
 * Deux familles de régression à empêcher :
 * 1) qu'une garde de session revienne masquer un contenu qui ne dépend d'aucune API — c'était l'état de
 *    quatre pages de /cours (mesuré : le HTML serveur d'une page de chapitre contenait un spinner et
 *    zéro octet de leçon, le panneau de preuve étant dedans) ;
 * 2) qu'une dépendance réseau apparaisse dans ces pages sans qu'on se repose la question de la garde.
 * Le test lit la source : c'est un contrat sur le fichier, pas un rendu.
 */

import { describe, expect, it } from "vitest"
import { readFileSync } from "node:fs"

const read = (rel: string) => readFileSync(rel, "utf-8")
const COURS_PAGES = [
  "src/app/cours/page.tsx",
  "src/app/cours/[domaine]/page.tsx",
  "src/app/cours/[domaine]/[unite]/page.tsx",
  "src/app/cours/[domaine]/[unite]/[chapitre]/page.tsx",
]

describe("pages de cours locales", () => {
  for (const rel of COURS_PAGES) {
    it(`${rel.replace("src/app/", "/")} — aucune garde de session devant le contenu local`, () => {
      const s = read(rel)
      expect(s).not.toMatch(/<AuthGuard/)
      expect(s).not.toMatch(/import \{ AuthGuard \}/)
    })
    it(`${rel.replace("src/app/", "/")} — pas d'appel réseau dans le fichier de page`, () => {
      expect(read(rel)).not.toMatch(/apiClient\.\w+\(|await fetch\(/)
    })
  }

  it("le panneau de preuve et la fabrique d'énoncés sont montés sur la page de chapitre", () => {
    const s = read("src/app/cours/[domaine]/[unite]/[chapitre]/page.tsx")
    expect(s).toContain("<ProofPanel")
    expect(s).toContain("<ItemForgePanel")
  })

  it("/preuve est reliée depuis le menu, pas seulement depuis le bas d'une leçon", () => {
    const s = read("src/components/layout/Sidebar.tsx")
    const item = s.split("\n").find((l) => l.includes('href: "/preuve"'))
    expect(item).toBeTruthy()
    expect(item).toContain("دليل الفهم")
  })
})

describe("orthographe arabe des étiquettes", () => {
  // Un ي persan (U+06CC) dans un site algérien est une faute visible par n'importe quel élève ; elle
  // s'est glissée une fois dans un titre de case, parce que le texte était tapé à la main.
  const files = ["src/lib/local-evidence.ts", "src/components/lessons/ProofPanel.tsx", "src/components/lessons/ItemForgePanel.tsx", "src/components/lessons/DraftStatus.tsx"]
  it("ni ي ni ک/گ dans les surfaces de preuve", () => {
    for (const f of files) expect(read(f)).not.toMatch(/[یکګ]/)
  })
})
