"use client"
import { useParams } from "next/navigation"
import { AppShell } from "@/components/layout/AppShell"
import GenZQCMFlow from "@/components/lessons/GenZQCMFlow"

export default function GenZExercicesPage() {
  const params = useParams()
  const chapitre = decodeURIComponent((params.chapitre as string) || "")

  const getQuestions = (title: string) => {
    if (title.includes("إنزيم") || title.toLowerCase().includes("enzyme")) {
      return [
        { id: 1, question: "الإنزيم هو", options: ["بروتين", "سكر", "دهن", "ماء"], correct: 0 },
        { id: 2, question: "يؤثر على الإنزيم", options: ["الحرارة و pH", "الضوء فقط", "الريح", "الصوت"], correct: 0 },
      ]
    }
    if (title.includes("براكين") || title.includes("تكتون")) {
      return [
        { id: 1, question: "سبب البراكين؟", options: ["حركة الصفائح", "الرياح", "الأمطار", "الشمس"], correct: 0 },
        { id: 2, question: "الحدود المتقاربة تشكل", options: ["جبال", "براكين فقط", "سهول", "أنهار"], correct: 0 },
      ]
    }
    return [
      { id: 1, question: `المفهوم الأساسي في "${title}"؟`, options: ["البنية والوظيفة", "الحفظ فقط", "الرسم", "الكتابة"], correct: 0 },
      { id: 2, question: "طريقة الإجابة في البكالوريا؟", options: ["المصطلحات بدقة", "الكتابة الطويلة", "الرسوم فقط", "الرأي"], correct: 0 },
    ]
  }

  const questions = getQuestions(chapitre)

  return (
    <AppShell>
      <div className="max-w-2xl mx-auto px-4 pt-6 pb-16" dir="rtl">
        <h1 className="text-3xl font-black mb-6">{chapitre}</h1>
        <GenZQCMFlow titleAr={chapitre} questions={questions} />
      </div>
    </AppShell>
  )
}
