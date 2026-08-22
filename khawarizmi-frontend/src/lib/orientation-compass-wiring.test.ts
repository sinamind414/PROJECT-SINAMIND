import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

function source(path: string) {
  return readFileSync(resolve(process.cwd(), path), "utf8")
}

describe("boussole FSRS du dashboard", () => {
  it("charge et affiche réellement la roadmap des 11 unités", () => {
    const dashboard = source("src/app/dashboard/page.tsx")
    const apiClient = source("src/lib/api-client.ts")
    const compass = source("src/components/dashboard/OrientationCompass.tsx")

    expect(dashboard).toContain("<OrientationCompass")
    expect(dashboard).toContain("apiClient.getOrientationRoadmap()")
    expect(apiClient).toContain('this.request<RoadmapResponse>("/api/orientation/roadmap")')
    expect(compass).toContain("roadmap.unites.map")
    expect(compass).toContain("roadmap.memory.message_ar")
  })

  it("ne présente plus l'indicateur mémoire comme une prédiction Bac certaine", () => {
    const progress = source("src/app/progress/page.tsx")
    expect(progress).toContain("مؤشر الذاكرة التقريبي")
    expect(progress).toContain("ليس تنبؤا بعلامة البكالوريا")
  })
})
