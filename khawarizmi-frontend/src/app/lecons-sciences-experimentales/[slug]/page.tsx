"use client"

import { useParams } from "next/navigation"
import Link from "next/link"
import { AppShell } from "@/components/layout/AppShell"
import GenZInteractiveLesson from "@/components/lessons/GenZInteractiveLesson"
import GenZQCMFlow from "@/components/lessons/GenZQCMFlow"

const GENZ_LESSONS: Record<string, { titleAr: string; phases: any[] }> = {
  "phase15_chapitres_29_30": {
    titleAr: "الخصائص العامة للظواهر التكتونية",
    phases: [
      { id: "1", titleAr: "شنو هي التكتونية؟", content: <div className="text-[17px] leading-relaxed">حركة الصفائح اللي تخلق البراكين والزلازل والجبال. كل شيء يتحرك ببطء.</div> },
      { id: "2", titleAr: "أنواع الحدود", content: <div className="text-lg">• حدود متباعدة<br/>• حدود متقاربة<br/>• حدود منزلقة</div> },
      { id: "3", titleAr: "الآن دورك", practice: true, content: <div>اشرح كيف تتكون البراكين من حركة الصفائح</div> },
    ]
  },
  "phase2_chapitres_3_4": {
    titleAr: "خصائص الإنزيمات",
    phases: [
      { id: "1", titleAr: "شنو هو الإنزيم؟", content: <div className="text-[17px]">بروتين يسرّع التفاعلات بدون ما يتغير.</div> },
      { id: "2", titleAr: "الخصائص المهمة", content: <div>• خصوصية إنزيمية<br/>• تتأثر بالحرارة و pH<br/>• تعمل في الظروف الملائمة</div> },
      { id: "3", titleAr: "تمرين سريع", practice: true, content: <div>لماذا الإنزيمات مهمة في الخلية؟</div> },
    ]
  },
  default: {
    titleAr: "درس تفاعلي",
    phases: [
      { id: "1", titleAr: "المقدمة", content: <div>الفكرة الأساسية للدرس.</div> },
      { id: "2", titleAr: "الخطوة الرئيسية", content: <div>العلاقة والمفهوم.</div> },
      { id: "3", titleAr: "تدرب", practice: true, content: <div>اكتب إجابتك باختصار.</div> },
    ]
  }
}

const QCMS: Record<string, any[]> = {
  "phase15_chapitres_29_30": [
    { id: 1, question: "سبب البراكين الرئيسي؟", options: ["حركة الصفائح", "الرياح", "الأمطار", "الشمس"], correct: 0 },
    { id: 2, question: "الحدود المتقاربة تشكل؟", options: ["جبال", "براكين فقط", "سهول", "أنهار"], correct: 0 },
  ],
  "phase2_chapitres_3_4": [
    { id: 1, question: "الإنزيم هو", options: ["بروتين", "سكر", "دهن", "ماء"], correct: 0 },
    { id: 2, question: "يؤثر على الإنزيم", options: ["الحرارة و pH", "الضوء فقط", "الريح", "الصوت"], correct: 0 },
  ],
}

export default function GenZPhaseLesson() {
  const params = useParams()
  const slug = (params?.slug as string) || "default"
  const lesson = GENZ_LESSONS[slug] || GENZ_LESSONS.default
  const qcms = QCMS[slug] || []

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto px-4 pt-5 pb-20" dir="rtl">
        <Link href="/lecons-sciences-experimentales" className="text-mint text-sm font-semibold">← العودة</Link>
        <h1 className="text-4xl font-black tracking-tighter mt-2">{lesson.titleAr}</h1>
        <GenZInteractiveLesson lessonTitleAr={lesson.titleAr} phases={lesson.phases} slug={slug} />
        {qcms.length > 0 && (
          <div className="mt-14">
            <h3 className="text-center font-bold text-2xl mb-5">اختبر نفسك الآن</h3>
            <GenZQCMFlow titleAr="اختبار سريع" questions={qcms} />
          </div>
        )}
      </div>
    </AppShell>
  )
}
