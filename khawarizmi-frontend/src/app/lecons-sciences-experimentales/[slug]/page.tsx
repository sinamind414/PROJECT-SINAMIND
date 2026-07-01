"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import { ChevronRight, BookOpen } from "lucide-react"
import { useEffect, useState, useRef } from "react"

const PHASE_LABELS: Record<string, { phase: number; label: string }> = {
  phase1_chapitres_1_2: { phase: 1, label: "التركيب الكيميائي للبروتين · العلاقة بين بنية البروتين ووظيفته" },
  phase2_chapitres_3_4: { phase: 2, label: "خصائص الإنزيمات · دور الإنزيمات في التفاعلات الحيوية" },
  phase3_chapitres_5_6: { phase: 3, label: "التنظيم الهرموني · دور الهرمونات في الاتصال العصبي" },
  phase4_chapitres_7_8: { phase: 4, label: "المناعة الخلطية · المناعة الخلوية" },
  phase5_chapitres_9_10: { phase: 5, label: "الأجسام المضادة · سيروم ولقاح" },
  phase6_chapitres_11_12: { phase: 6, label: "التنفس · التخمر" },
  phase7_chapitres_13_14: { phase: 7, label: "مصادر الطاقة في الكائنات الحية · امتصاص المغذيات" },
  phase8_chapitres_15_16: { phase: 8, label: "الهضم · النقل الدموي" },
  phase9_chapitres_17_18: { phase: 9, label: "التبادل الغازي التنفسي · التنظيم الدقيق للتنفس" },
  phase10_chapitres_19_20: { phase: 10, label: "الجهد العضلي · التعب العضلي" },
  phase11_chapitres_21_22: { phase: 11, label: "الحركة عند الإنسان · وضعية الانتصاب" },
  phase12_chapitres_23_24: { phase: 12, label: "البنية الدقيقة للعضلة الهيكلية · آلية التقبض العضلي" },
  phase13_chapitres_25_26: { phase: 13, label: "الطاقة الكامنة · تحويل الطاقة في العضلة" },
  phase14_chapitres_27_28: { phase: 14, label: "النشاط الإنزيمي للعضلة · تنظيم الفعل العضلي" },
  phase15_chapitres_29_30: { phase: 15, label: "الخصائص العامة للظواهر التكتونية · تكتونية الصفائح" },
  phase16_chapitres_31_32: { phase: 16, label: "بنية الغلاف الصخري · حركية الصفائح" },
  phase17_chapitres_33_34: { phase: 17, label: "الحدود المتقاربة · الحدود المتباعدة" },
  phase18_chapitres_35_36: { phase: 18, label: "التحولات الباطنية · البنية الداخلية للأرض" },
  phase19_chapitres_37_38: { phase: 19, label: "الزلازل · الموجات الزلزالية" },
  phase20_chapitres_39_40: { phase: 20, label: "التشوهات التكتونية · الطيات والفوالق" },
  phase21_chapitres_41_42: { phase: 21, label: "تشكل السلاسل الجبلية · ظاهرة الحركات البانية" },
  phase22_chapitres_43_44: { phase: 22, label: "العلاقة بين التكتونية والرسوبيات · التطبيقات الجيولوجية" },
}

export default function PhasePage() {
  const params = useParams()
  const slug = params?.slug as string
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [height, setHeight] = useState("100vh")

  const meta = PHASE_LABELS[slug]
  const phaseLabel = meta ? `المرحلة ${meta.phase} — ${meta.label}` : slug === "lecon_transcription" ? "أداة تحويل النص إلى درس تفاعلي" : slug
  const src = `/lecons-sciences-experimentales/${slug}.html`

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "iframe-height") {
        setHeight(`${event.data.height}px`)
      }
    }
    window.addEventListener("message", handleMessage)
    return () => window.removeEventListener("message", handleMessage)
  }, [])

  return (
    <AppShell>
      <div className="max-w-7xl mx-auto" dir="rtl">
        <div className="flex items-center gap-2 mb-4 text-sm">
          <Link href="/lecons-sciences-experimentales" className="text-mint hover:text-mint-soft transition font-bold">
            <ChevronRight className="w-4 h-4 inline" aria-hidden="true" />
            55 درساً
          </Link>
          <span className="text-slate-500">/</span>
          <span className="text-slate-300 font-semibold truncate">{phaseLabel}</span>
        </div>

        <div className="rounded-2xl overflow-hidden border border-white/10 bg-white/[0.02]">
          <iframe
            ref={iframeRef}
            src={src}
            title={phaseLabel}
            className="w-full border-0"
            style={{ height }}
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            onLoad={() => {
              try {
                const doc = iframeRef.current?.contentDocument || iframeRef.current?.contentWindow?.document
                if (doc) {
                  const h = doc.documentElement.scrollHeight
                  setHeight(`${Math.max(h, window.innerHeight)}px`)
                }
              } catch {}
            }}
          />
        </div>
      </div>
    </AppShell>
  )
}
