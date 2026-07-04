"use client"

import { useParams } from "next/navigation"
import { AppShell } from "@/components/layout/AppShell"
import GenZQCMFlow from "@/components/lessons/GenZQCMFlow"

export default function GenZExercicesPage() {
  const params = useParams()
  const chapitre = decodeURIComponent((params.chapitre as string) || "")

  const questions = [
    { id: 1, question: `ما هو المفهوم الأساسي في "${chapitre}"؟`, options: ["البنية والوظيفة", "الحفظ فقط", "الرسم", "الكتابة"], correct: 0 },
    { id: 2, question: "أفضل طريقة للإجابة في البكالوريا؟", options: ["استخدام المصطلحات بدقة", "الكتابة الطويلة", "الرسوم فقط", "الرأي الشخصي"], correct: 0 },
  ]

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 pt-6 pb-16" dir="rtl">
        <h1 className="text-3xl font-black mb-6">{chapitre}</h1>
        <GenZQCMFlow titleAr={chapitre} questions={questions} />
      </div>
    </AppShell>
  )
}
