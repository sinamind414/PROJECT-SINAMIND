"use client"

import React from "react"
import GenZPhaseFlow, { Phase } from "./GenZPhaseFlow"

interface Props {
  lessonTitle?: string
  lessonTitleAr: string
  slug: string
  phases: Phase[]
  onComplete?: (answer: string, score: number) => void
}

export default function GenZInteractiveLesson({ lessonTitleAr, phases, onComplete }: Props) {
  return (
    <GenZPhaseFlow
      title={lessonTitleAr}
      titleAr={lessonTitleAr}
      phases={phases}
      onComplete={onComplete}
      genZIntro="يلا يا خويا 17 سنة • كل فازة • ركز واربح نقاط البكالوريا 🔥"
      onSubmitPractice={async (answer: string) => {
        const keywords = ["تحليل", "تفسير", "استنتاج", "علاقة", "بنية", "وظيفة", "صفيحة", "تكتونية", "إنزيم"]
        const found = keywords.filter(k => answer.toLowerCase().includes(k.toLowerCase())).length
        const pct = Math.min(100, Math.max(40, Math.round((found / 3) * 100)))
        return {
          percentage: pct,
          feedback: pct > 70 ? "ممتاز! استخدمت المصطلحات الصحيحة" : "حاول تضيف كلمات مثل: تحليل، علاقة، بنية",
          modelAnswer: "من خلال تحليل الوثيقة نلاحظ أن..."
        }
      }}
    />
  )
}
