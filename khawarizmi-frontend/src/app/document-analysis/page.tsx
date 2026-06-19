"use client"

import Link from "next/link"
import { PageShell } from "@/components/ui/PageShell"
import { PageHero } from "@/components/ui/PageHero"
import { SurfaceCard } from "@/components/ui/SurfaceCard"
import { PillChip } from "@/components/ui/PillChip"
import { methodologyScenarios } from "@/lib/methodology-documents"
import { methodologyChapterLinks } from "@/lib/methodology-chapters"

const UNIT_EMOJIS: Record<string, string> = {
  "تركيب البروتين": "🧬",
  "العلاقة بين بنية ووظيفة البروتين": "🔬",
  "النشاط الإنزيمي للبروتينات": "⚡",
  "دور البروتينات في الدفاع عن الذات": "🛡️",
  "دور البروتينات في الاتصال العصبي": "🧠",
  "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة": "☀️",
  "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP": "⚡",
  "تحويل الطاقة على المستوى ما فوق البنية الخلوية": "🔋",
  "بنية الكرة الأرضية": "🌍",
  "النشاط التكتوني للصفائح": "🌋",
  "النشاط التكتوني والبنيات الجيولوجية المرتبطة به": "🏔️",
}

const IMPORTANCE_COLORS: Record<string, string> = {
  critique: "rgba(248,113,113,0.15)",
  haute: "rgba(251,191,36,0.15)",
  moyenne: "rgba(59,130,246,0.15)",
}

const IMPORTANCE_TEXT: Record<string, string> = {
  critique: "#F87171",
  haute: "#FBBF24",
  moyenne: "#60A5FA",
}

const CHAPTER_TYPE_LABELS: Record<string, string> = {
  concept: "مفهوم",
  processus: "عملية",
  experience: "تجربة",
  rappel: "تذكير",
  synthese: "تركيب",
}

function groupChaptersByDomainAndUnit() {
  const domains: Array<{
    domainNumero: number
    domainAr: string
    domainFr: string
    units: Array<{
      unitNumero: number
      unitAr: string
      unitFr: string
      chapters: typeof methodologyChapterLinks
    }>
  }> = []

  for (const ch of methodologyChapterLinks) {
    let domain = domains.find((d) => d.domainNumero === ch.domainNumero)
    if (!domain) {
      domain = { domainNumero: ch.domainNumero, domainAr: ch.domainAr, domainFr: ch.domainFr, units: [] }
      domains.push(domain)
    }
    let unit = domain.units.find((u) => u.unitNumero === ch.unitNumero)
    if (!unit) {
      unit = { unitNumero: ch.unitNumero, unitAr: ch.unitAr, unitFr: ch.unitFr, chapters: [] }
      domain.units.push(unit)
    }
    unit.chapters.push(ch)
  }

  return domains
}

export default function DocumentAnalysisHubPage() {
  const domainGroups = groupChaptersByDomainAndUnit()

  return (
    <PageShell wide>
      <PageHero
        title="بنك السيناريوهات المنهجية"
        subtitle="القلب الحقيقي لـ SINAMIND"
        description="كل وحدة من وحدات SVT الـ 11 لها سيناريو خاص: وثائق + أسئلة منهجية + تصحيح مفصل + تسجيل الأخطاء."
      />

      <p className="text-gray-400 text-sm">
        اختر وحدة للبدء. كل سيناريو يحتوي على 4 وثائق و 5 أسئلة منهجية على نمط البكالوريا.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {methodologyScenarios.map((scenario) => {
          const isDiagnostic = scenario.id === "gene-expression-protein-disorder-v1"
          const href = isDiagnostic ? "/diagnostic/global" : `/document-analysis/${scenario.id}`
          const emoji = UNIT_EMOJIS[scenario.unitKey] || "📚"

          return (
            <Link
              key={scenario.id}
              href={href}
              className="rounded-2xl p-5 transition-all duration-200 hover:-translate-y-0.5"
              style={{ background: "#1E2030" }}
            >
              <div className="text-3xl mb-3">{emoji}</div>
              <h3 className="text-white font-bold text-sm mb-1">{scenario.title}</h3>
              <p className="text-gray-500 text-xs mb-2">{scenario.unitKey}</p>
              <p className="text-gray-400 text-xs leading-relaxed line-clamp-2">{scenario.contextAr}</p>
              <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                <span>📄 {scenario.documents.length} وثائق</span>
                <span>❓ {scenario.questions.length} أسئلة</span>
                {isDiagnostic && (
                  <PillChip label="تشخيص" color="#A78BFA" bg="rgba(139,92,246,0.1)" />
                )}
              </div>
            </Link>
          )
        })}
      </div>

      <section>
        <SurfaceCard padding={false}>
          <div className="rounded-2xl p-5" style={{ background: "linear-gradient(135deg, rgba(139,92,246,0.12), rgba(79,70,229,0.08))" }}>
            <p className="text-gray-500 text-xs mb-1">البرنامج الوطني SVT</p>
            <h2 className="text-lg font-bold text-white">الفصول الـ 55 مرتبطة بالمنهجية</h2>
            <p className="text-gray-400 text-sm mt-1 max-w-3xl leading-relaxed">
              كل فصل من فصول البرنامج الوطني الـ 55 موصول بمسار منهجي يستهدف المهارات والمفاهيم الأساسية.
              تصفّح حسب المجال والوحدة، واختر فصلا لبدء التمرين.
            </p>
          </div>
        </SurfaceCard>

        {domainGroups.map((domain) => (
          <div key={domain.domainNumero} className="mt-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-lg font-bold text-white">المجال {domain.domainNumero}</span>
              <span className="text-gray-400 text-sm">{domain.domainAr}</span>
            </div>

            <div className="space-y-4">
              {domain.units.map((unit) => (
                <SurfaceCard key={unit.unitNumero}>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-sm font-bold text-violet-400">الوحدة {unit.unitNumero}</span>
                    <span className="text-gray-300 text-sm">{unit.unitAr}</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3">
                    {unit.chapters.map((ch) => (
                      <Link
                        key={ch.slug}
                        href={`/document-analysis/chapters/${ch.slug}`}
                        className="rounded-xl p-4 transition-all hover:-translate-y-0.5"
                        style={{ background: "#141522" }}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-gray-500 text-xs">الفصل {ch.chapterNumero}</span>
                          <PillChip
                            label={ch.chapterImportance === "critique" ? "قصوى" : ch.chapterImportance === "haute" ? "عالية" : "متوسطة"}
                            color={IMPORTANCE_TEXT[ch.chapterImportance] || "#94A3B8"}
                            bg={IMPORTANCE_COLORS[ch.chapterImportance] || "rgba(255,255,255,0.06)"}
                          />
                        </div>
                        <h4 className="text-white font-bold text-sm leading-relaxed mb-1">{ch.chapterAr}</h4>
                        <p className="text-gray-500 text-xs mb-2 line-clamp-1" dir="ltr">{ch.chapterFr}</p>
                        {ch.chapterType && (
                          <PillChip
                            label={CHAPTER_TYPE_LABELS[ch.chapterType] || ch.chapterType}
                            color="#CBD5E1"
                            bg="rgba(255,255,255,0.04)"
                          />
                        )}
                        <div className="mt-2 text-xs font-bold" style={{ color: "#A78BFA" }}>
                          افتح المسار المنهجي ←
                        </div>
                      </Link>
                    ))}
                  </div>
                </SurfaceCard>
              ))}
            </div>
          </div>
        ))}

        <p className="text-gray-500 text-xs mt-6 text-center">
          {methodologyChapterLinks.length} فصلا موصولا بالمنهجية عبر {methodologyScenarios.length} سيناريو وحدة
        </p>
      </section>
    </PageShell>
  )
}
