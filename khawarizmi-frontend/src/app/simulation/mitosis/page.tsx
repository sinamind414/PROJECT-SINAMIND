"use client"

import { PageShell } from "@/components/ui/PageShell"
import { MitosisSimulation } from "@/components/simulation/MitosisSimulation"

export default function MitosisPage() {
  return (
    <PageShell wide>
      <div dir="rtl" className="mb-4 rounded-2xl border border-amber-400/30 bg-amber-400/10 p-4">
        <p className="font-black text-amber-300">إثراء — غير مطلوب كوحدة في برنامج بكالوريا 3AS</p>
        <p className="text-white/75 text-sm mt-1">هذه المحاكاة تذكير بمكتسبات سابقة، وليست فصلا من فصول البرنامج الرسمي المعروض في مسار الدروس.</p>
      </div>
      <MitosisSimulation />
    </PageShell>
  )
}
