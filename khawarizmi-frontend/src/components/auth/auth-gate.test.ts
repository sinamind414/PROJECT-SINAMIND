/**
 * La garde ne doit plus confondre « le serveur ne répond pas » et « tu n'as pas le droit » (2026-09-01).
 *
 * Le premier cas rend l'application inutilisable pour un élève dont le contenu est déjà dans le bundle :
 * mesuré avant le changement, `curl /scanner` renvoyait 18 719 octets dont un `animate-spin`, pour une page
 * dont l'unique contenu est un panneau «🚧 قيد الإنشاء ». Le second cas doit continuer de rediriger.
 */

import { describe, expect, it, vi } from "vitest"
import { createElement as h } from "react"
import { renderToStaticMarkup } from "react-dom/server"

const auth = vi.hoisted(() => ({ current: { loading: false, isAuthenticated: false, offline: false, refreshUser: () => undefined } }))
vi.mock("@/lib/auth-context", () => ({ useAuth: () => auth.current }))
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }))

import { authGate, isNetworkFailure } from "./auth-gate"
import { AuthGuard } from "./AuthGuard"

describe("authGate — la table de décision", () => {
  const cases: Array<[string, Parameters<typeof authGate>[0], string]> = [
    ["vérification en cours", { loading: true, isAuthenticated: false, offline: false }, "checking"],
    ["session valide", { loading: false, isAuthenticated: true, offline: false }, "children"],
    ["serveur muet", { loading: false, isAuthenticated: false, offline: true }, "children"],
    ["refus d'identité (le serveur a répondu non)", { loading: false, isAuthenticated: false, offline: false }, "redirect-login"],
    // Un serveur qui répond « non » gagne, même si un appel antérieur avait été muet : la panne ne
    // construit pas un droit d'accès.
    ["réponse de rejet après une panne", { loading: false, isAuthenticated: false, offline: false }, "redirect-login"],
  ]
  for (const [nom, input, attendu] of cases) {
    it(`${nom} → ${attendu}`, () => expect(authGate(input)).toBe(attendu))
  }
})

describe("isNetworkFailure — classer sans lire une phrase traduite", () => {
  it("une erreur sans status est une absence de réponse", () => {
    expect(isNetworkFailure(new Error(" مهلة الاتصال"))).toBe(true)
    expect(isNetworkFailure(undefined)).toBe(true)
  })
  it("un HTTP code est une réponse", () => {
    const e = new Error("session") as Error & { status?: number }
    e.status = 401
    expect(isNetworkFailure(e)).toBe(false)
  })
})

describe("AuthGuard rendu", () => {
  const render = () => renderToStaticMarkup(h(AuthGuard, null, h("p", { id: "corps" }, "leçon locale")))

  it("serveur muet : le contenu est rendu, et le bandeau dit qu'il n'a pas quitté l'appareil", () => {
    auth.current = { loading: false, isAuthenticated: false, offline: true, refreshUser: () => undefined }
    const html = render()
    expect(html).toContain("leçon locale")
    expect(html).toContain("لا اتصال بالخادم")
    expect(html).toContain("إعادة المحاولة")
    // Aucun spinner infini, et aucune promesse de synchronisation.
    expect(html).not.toContain("animate-spin")
    expect(html).not.toMatch(/سُجِّل|تمت المزامنة/)
  })

  it("refus net : le contenu local n'est pas rendu, la redirection garde la main", () => {
    auth.current = { loading: false, isAuthenticated: false, offline: false, refreshUser: () => undefined }
    expect(render()).not.toContain("leçon locale")
  })

  it("vérification : le spinner reste, c'est le seul état où l'on ne sait pas", () => {
    auth.current = { loading: true, isAuthenticated: false, offline: false, refreshUser: () => undefined }
    expect(render()).toContain("animate-spin")
  })
})
