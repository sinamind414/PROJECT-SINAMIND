"use client"

import Link from "next/link"
import { AuthGuard } from "@/components/auth/AuthGuard"
import { AppShell } from "@/components/layout/AppShell"
import { ProgressivePageHeader } from "@/components/ui/ProgressivePageHeader"
import { MethodChecklistLab } from "@/components/methodology/MethodChecklistLab"
import {
  METHOD_LEVELS,
  METHOD_MODES,
  type MethodLevel,
} from "@/lib/methodology-checklists"
import {
  BookOpen,
  ClipboardList,
  Compass,
  FileSearch,
  FlaskConical,
  Target,
  Trophy,
} from "lucide-react"
import { ContractPulse } from "@/components/methodology/SessionExitButton"

const LEVEL_ORDER: MethodLevel[] = ["red", "yellow", "green"]

const DOORS = [
  {
    id: "compass",
    icon: Compass,
    titleAr: "بوصلة الأفعال",
    titleFr: "Boussole des verbes",
    descAr: "ستّة أوضاع منهجية · ثلاثة ألوان · تمرين 1 / 2 / 3",
    descFr: "Six modes · trois couleurs · exercices BAC 1 / 2 / 3",
    href: "#compass",
    accent: "border-sky-500/30 bg-sky-500/10 text-sky-300",
  },
  {
    id: "lab",
    icon: FlaskConical,
    titleAr: "مختبر قائمة التحقق",
    titleFr: "Laboratoire Checklist",
    descAr: "اختر الوضع · علّم الخطوات · اكتب بالقالب العلمي",
    descFr: "Choisir le mode · cocher · rédiger avec structure",
    href: "#lab",
    accent: "border-mint/30 bg-mint/10 text-mint",
  },
  {
    id: "challenge",
    icon: Trophy,
    titleAr: "تحدي البكالوريا",
    titleFr: "Défi BAC",
    descAr: "وثائق حقيقية · أفعال أدائية · أنال · أتمرن",
    descFr: "Documents réels · verbes · analyser · s’entraîner",
    href: "#challenge",
    accent: "border-amber-500/30 bg-amber-500/10 text-amber-300",
  },
] as const

const BAC_FLOW = [
  { n: "1", ar: "اقرأ السياق", fr: "Lire le contexte" },
  { n: "2", ar: "حدّد الفعل الأدائي", fr: "Identifier le verbe" },
  { n: "3", ar: "اختر الوضع (لون)", fr: "Choisir le mode" },
  { n: "4", ar: "علّم قائمة التحقق", fr: "Cocher la checklist" },
  { n: "5", ar: "اكتب بالروابط", fr: "Rédiger avec liens" },
  { n: "6", ar: "راجع الحكم / الاستنتاج", fr: "Vérifier conclusion" },
]

export default function MethodologyPortalPage() {
  return (
    <AuthGuard>
      <AppShell>
        <main className="flex-1 p-6 lg:p-8 overflow-auto">
          <div className="max-w-5xl mx-auto space-y-10">
            <ProgressivePageHeader
              breadcrumb={[
                { label: "المنهجية", href: "/methodology" },
                { label: "منهجية البكالوريا" },
              ]}
              title="منهجية الإجابة — البكالوريا SVT"
              subtitle="باب واحد يعلّمك كيف تجيب: فعل أدائي → وضع منهجي → قائمة تحقق → كتابة علمية. عربي مدرسي + مصطلحات Français scientifiques."
            />

            {/* Identity strip */}
            <div className="rounded-2xl border border-mint/20 bg-mint/5 p-5">
              <p className="text-white font-black text-lg">
                ستّة أوضاع. كل تمرين. حتى البكالوريا.
              </p>
              <p className="text-white/50 text-sm mt-1" dir="ltr">
                Six modes méthodologiques. Chaque exercice. Jusqu’au BAC.
              </p>
              <p className="text-white/70 text-sm mt-3 leading-relaxed">
                لا تحفظ أربعين خطوة. احفظ{" "}
                <strong className="text-mint">ستّة ردود فعل</strong>. كل تعليمة
                تدخل في وضع واحد: عرّف · حلّل · فسّر · قارن · فرضية · اربط واحكم.
              </p>
            </div>

            <div className="-mx-4">
              <ContractPulse />
            </div>

            {/* 3 doors */}
            <section aria-label="الأبواب الثلاثة">
              <h2 className="text-sm font-bold text-white/40 mb-3">
                ثلاثة أبواب · Trois portes
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {DOORS.map((door) => {
                  const Icon = door.icon
                  return (
                    <a
                      key={door.id}
                      href={door.href}
                      className={`rounded-2xl border p-4 transition hover:scale-[1.01] ${door.accent}`}
                    >
                      <Icon className="w-6 h-6 mb-3 opacity-90" />
                      <div className="font-black text-white text-base">{door.titleAr}</div>
                      <div className="text-xs opacity-70 mt-0.5" dir="ltr">
                        {door.titleFr}
                      </div>
                      <p className="text-sm text-white/70 mt-2 leading-relaxed">{door.descAr}</p>
                      <p className="text-[11px] text-white/40 mt-1" dir="ltr">
                        {door.descFr}
                      </p>
                    </a>
                  )
                })}
              </div>
            </section>

            {/* Ritual BAC */}
            <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center gap-2 mb-4">
                <Target className="w-5 h-5 text-mint" />
                <h2 className="font-black text-white">
                  طقس الإجابة · Rituel de réponse
                </h2>
              </div>
              <ol className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                {BAC_FLOW.map((step) => (
                  <li
                    key={step.n}
                    className="rounded-xl border border-white/10 bg-black/20 p-3 text-center"
                  >
                    <div className="w-7 h-7 mx-auto rounded-lg bg-mint/20 text-mint text-xs font-black flex items-center justify-center mb-2">
                      {step.n}
                    </div>
                    <div className="text-xs font-bold text-white leading-snug">{step.ar}</div>
                    <div className="text-[10px] text-white/40 mt-1" dir="ltr">
                      {step.fr}
                    </div>
                  </li>
                ))}
              </ol>
            </section>

            {/* Compass */}
            <section id="compass" className="scroll-mt-24 space-y-4">
              <div className="flex items-center gap-2">
                <Compass className="w-5 h-5 text-sky-300" />
                <h2 className="text-xl font-black text-white">
                  1. بوصلة الأفعال · Boussole
                </h2>
              </div>
              <p className="text-white/55 text-sm">
                لون واحد = مستوى واحد من امتحان البكالوريا. اختر اللون ثم الوضع.
              </p>

              {LEVEL_ORDER.map((level) => {
                const meta = METHOD_LEVELS[level]
                const modes = METHOD_MODES.filter((m) => m.level === level)
                return (
                  <div
                    key={level}
                    className={`rounded-2xl border ${meta.border} ${meta.bg} p-4`}
                  >
                    <div className={`text-sm font-black ${meta.text} mb-3`}>
                      {meta.ar}
                      <span className="opacity-60 font-bold mr-2" dir="ltr">
                        · {meta.fr}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {modes.map((m) => (
                        <div
                          key={m.id}
                          className="rounded-xl border border-white/10 bg-black/25 p-3"
                        >
                          <div className="flex items-baseline justify-between gap-2">
                            <span className="font-black text-white">
                              {m.order}. {m.mantraAr}
                            </span>
                            <span className="text-[11px] text-white/40" dir="ltr">
                              {m.mantraFr}
                            </span>
                          </div>
                          <p className="text-xs text-white/60 mt-1">{m.sloganAr}</p>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {m.verbsFr.slice(0, 4).map((v) => (
                              <span
                                key={v}
                                className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-white/50"
                                dir="ltr"
                              >
                                {v}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </section>

            {/* Lab */}
            <section id="lab" className="scroll-mt-24 space-y-4">
              <div className="flex items-center gap-2">
                <FlaskConical className="w-5 h-5 text-mint" />
                <h2 className="text-xl font-black text-white">
                  2. مختبر قائمة التحقق · Laboratoire
                </h2>
              </div>
              <p className="text-white/55 text-sm leading-relaxed">
                قبل الكتابة: اختر الوضع → علّم كل خطوة → استعمل الروابط الإلزامية
                والقالب. هذه العادة هي التي تفوز في قاعة الامتحان.
              </p>
              <MethodChecklistLab initialModeId="analyse" />
            </section>

            {/* Challenge */}
            <section id="challenge" className="scroll-mt-24 space-y-4">
              <div className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-300" />
                <h2 className="text-xl font-black text-white">
                  3. تحدي البكالوريا · Défi BAC
                </h2>
              </div>
              <p className="text-white/55 text-sm">
                طبّق الطقس على أفعال حقيقية ووثائق البرنامج.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Link
                  href="/action-verbs"
                  className="rounded-2xl border border-violet-500/25 bg-violet-500/10 p-5 hover:bg-violet-500/15 transition group"
                >
                  <ClipboardList className="w-6 h-6 text-violet-300 mb-3" />
                  <div className="font-black text-white text-lg">الأفعال الأدائية</div>
                  <div className="text-xs text-white/40 mt-0.5" dir="ltr">
                    Verbes d’action · 24 verbes
                  </div>
                  <p className="text-sm text-white/65 mt-2">
                    درّب كل فعل مع الدرس التفاعلي، ثم أجب بمنهجية الوضع المناسب.
                  </p>
                  <span className="inline-block mt-3 text-violet-300 text-sm font-bold group-hover:underline">
                    ابدأ التدريب ←
                  </span>
                </Link>

                <Link
                  href="/document-analysis"
                  className="rounded-2xl border border-cyan-500/25 bg-cyan-500/10 p-5 hover:bg-cyan-500/15 transition group"
                >
                  <FileSearch className="w-6 h-6 text-cyan-300 mb-3" />
                  <div className="font-black text-white text-lg">استغلال الوثائق</div>
                  <div className="text-xs text-white/40 mt-0.5" dir="ltr">
                    Analyse de documents
                  </div>
                  <p className="text-sm text-white/65 mt-2">
                    وثائق البرنامج: حلّل · فسّر · استنتج — بعد قائمة التحقق.
                  </p>
                  <span className="inline-block mt-3 text-cyan-300 text-sm font-bold group-hover:underline">
                    افتح الوثائق ←
                  </span>
                </Link>

                <Link
                  href="/methodology/exercices/analyse-gene-expression"
                  className="rounded-2xl border border-mint/25 bg-mint/10 p-5 hover:bg-mint/15 transition group"
                >
                  <BookOpen className="w-6 h-6 text-mint mb-3" />
                  <div className="font-black text-white text-lg">اضطراب تركيب بروتين</div>
                  <div className="text-xs text-white/40 mt-0.5" dir="ltr">
                    Analyse document — expression génétique
                  </div>
                  <p className="text-sm text-white/65 mt-2">
                    تمرين كامل مع قائمة التحقق والتصحيح — بيّن أن تنشيط المورثة يزيد تركيب البروتين.
                  </p>
                  <span className="inline-block mt-3 text-mint text-sm font-bold group-hover:underline">
                    ابدأ التمرين ←
                  </span>
                </Link>

                <Link
                  href="/annales"
                  className="rounded-2xl border border-amber-500/25 bg-amber-500/10 p-5 hover:bg-amber-500/15 transition group md:col-span-2"
                >
                  <BookOpen className="w-6 h-6 text-amber-300 mb-3" />
                  <div className="font-black text-white text-lg">مواضيع البكالوريا</div>
                  <div className="text-xs text-white/40 mt-0.5" dir="ltr">
                    Annales BAC
                  </div>
                  <p className="text-sm text-white/65 mt-2">
                    طبّق الطقس الستّة على موضوع كامل: سياق → فعل → وضع → تحقق →
                    كتابة.
                  </p>
                  <span className="inline-block mt-3 text-amber-300 text-sm font-bold group-hover:underline">
                    ادخل المواضيع ←
                  </span>
                </Link>
              </div>
            </section>

            {/* Rule of gold */}
            <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 space-y-2">
              <h2 className="font-black text-white text-sm">قاعدة ذهبية · Règle d’or</h2>
              <ul className="text-sm text-white/70 space-y-1.5 leading-relaxed">
                <li>• لا تصحيح كامل قبل محاولة التلميذ.</li>
                <li>• لا تفسير داخل تحليل (Analyser ≠ Interpréter).</li>
                <li>• لا فرضية بكلمة «ربما» — صياغة جازمة.</li>
                <li>• لا مصادقة بلا جملة حكم صريحة.</li>
                <li>• لا شارة «أتقنت» إن خرجت دون إتمام قائمة التحقق.</li>
              </ul>
            </section>
          </div>
        </main>
      </AppShell>
    </AuthGuard>
  )
}
