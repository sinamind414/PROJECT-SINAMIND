"use client"

import Link from "next/link"

const DOMAINS = [
  {
    name: "البروتينات",
    fr: "Protéines",
    color: "#A78BFA",
    mastery: 65,
    chapters: [
      {
        name: "Transcription de l'information genetique au niveau de l'ADN",
        ar: "استنساخ المعلومة الوراثية",
        level: 85
      },
      {
        name: "La traduction",
        ar: "الترجمة",
        level: 55
      },
      {
        name: "Les etapes de la traduction",
        ar: "مراحل الترجمة",
        level: 25
      }
    ]
  },
  {
    name: "الطاقة",
    fr: "Énergie",
    color: "#FBBF24",
    mastery: 45,
    chapters: [
      {
        name: "Reactions de la phase photochimique (phase claire)",
        ar: "تفاعلات المرحلة الكيموضوئية",
        level: 65
      },
      {
        name: "Reactions de la phase chimique (cycle de Calvin - phase sombre)",
        ar: "حلقة كالفن",
        level: 25
      }
    ]
  },
  {
    name: "التكتونية",
    fr: "Tectonique",
    color: "#34D399",
    mastery: 30,
    chapters: [
      {
        name: "Identification des plaques tectoniques",
        ar: "تحديد الصفائح التكتونية",
        level: 25
      },
      {
        name: "Phenomenes lies a la subduction",
        ar: "الظواهر المرتبطة بالغوص",
        level: 35
      }
    ]
  }
]

function getColor(level: number) {
  if (level >= 75) return "#34D399"
  if (level >= 50) return "#FBBF24"
  return "#F87171"
}

export function MasteryChapters() {
  return (
    <div
      className="rounded-3xl p-6"
      style={{ background: "#2A2540" }}
    >
      <h2 className="text-2xl font-bold text-white mb-6">
        📚 إتقان الفصول حسب المجالات
      </h2>

      <div className="space-y-6">
        {DOMAINS.map((domain) => (
          <div key={domain.name}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ background: domain.color }}
                />
                <div>
                  <h3 className="text-white font-bold text-lg">
                    {domain.name}
                  </h3>
                  <p className="text-gray-500 text-xs" dir="ltr">
                    {domain.fr}
                  </p>
                </div>
              </div>
              <div className="text-left">
                <span
                  className="text-2xl font-bold"
                  style={{ color: domain.color }}
                >
                  {domain.mastery}%
                </span>
              </div>
            </div>

            <div className="mr-6 space-y-2">
              {domain.chapters.map((ch) => (
                <Link
                  key={ch.name}
                  href={`/cours/${encodeURIComponent(ch.name)}`}
                  className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] transition-colors cursor-pointer"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium">
                      {ch.ar}
                    </p>
                    <p className="text-gray-500 text-xs" dir="ltr">
                      {ch.name}
                    </p>
                  </div>

                  <div className="w-32 flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${ch.level}%`,
                          background: getColor(ch.level)
                        }}
                      />
                    </div>
                    <span className="text-white text-xs font-bold w-10 text-left">
                      {ch.level}%
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
