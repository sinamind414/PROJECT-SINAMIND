import type { MethodologyDocument } from "@/components/methodology/DocumentRenderer"

export type MethodologyVerbSlug =
  | "analyse"
  | "interpret"
  | "deduce"
  | "justify"
  | "hypothesis"
  | "validate-hypothesis"
  | "discuss"
  | "scientific-text"
  | "compare"
  | "relationship"

export type MethodologyQuestion = {
  id: string
  verbSlug: MethodologyVerbSlug
  n: number
  title: string
  skill: string
  docRef: string
  prompt: string
  placeholder: string
  modelAnswer: string
  learningFocus: string
}

export type MethodologyScenario = {
  id: string
  unitKey: string
  title: string
  subtitle: string
  contextAr: string
  documents: MethodologyDocument[]
  questions: readonly MethodologyQuestion[]
  dominantSkills?: string[]
}

function svgDataUri(svg: string) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const cellProteinSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#251f3d"/>
      <stop offset="1" stop-color="#121020"/>
    </linearGradient>
    <linearGradient id="cell" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#7c3aed" stop-opacity="0.55"/>
      <stop offset="1" stop-color="#10b981" stop-opacity="0.38"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg)"/>
  <ellipse cx="360" cy="215" rx="275" ry="142" fill="url(#cell)" stroke="#a78bfa" stroke-width="6"/>
  <circle cx="255" cy="205" r="74" fill="#31265d" stroke="#c4b5fd" stroke-width="5"/>
  <path d="M210 205 C235 170, 270 242, 300 202" fill="none" stroke="#60a5fa" stroke-width="8" stroke-linecap="round"/>
  <path d="M420 138 C470 122, 514 145, 530 190 C548 242, 500 291, 444 279 C395 269, 370 223, 386 180 C393 160, 405 147, 420 138Z" fill="#3b2f67" stroke="#34d399" stroke-width="5" opacity="0.9"/>
  <g fill="#fbbf24">
    <circle cx="425" cy="178" r="9"/><circle cx="458" cy="198" r="9"/><circle cx="493" cy="220" r="9"/>
    <circle cx="463" cy="250" r="9"/><circle cx="424" cy="238" r="9"/>
  </g>
  <path d="M318 205 C360 206, 384 211, 416 227" fill="none" stroke="#e879f9" stroke-width="7" stroke-linecap="round" stroke-dasharray="12 10"/>
  <text x="360" y="382" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="22">وثيقة صورية مبسطة: من المورثة إلى البروتين داخل الخلية</text>
</svg>`)

const proteinSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg2" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#1e1b3d"/>
      <stop offset="1" stop-color="#0f0d20"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg2)"/>
  <path d="M120 200 L180 150 L240 200 L300 160 L360 210 L420 170 L480 220" fill="none" stroke="#a78bfa" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M140 180 L200 220 L260 170 L320 200 L380 150 L440 210 L500 180" fill="none" stroke="#34d399" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="8 6"/>
  <circle cx="160" cy="190" r="10" fill="#7c3aed" opacity="0.8"/>
  <circle cx="250" cy="185" r="10" fill="#7c3aed" opacity="0.8"/>
  <circle cx="340" cy="195" r="10" fill="#7c3aed" opacity="0.8"/>
  <circle cx="430" cy="185" r="10" fill="#7c3aed" opacity="0.8"/>
  <text x="360" y="320" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="18">بنية البروتين الفراغية ثلاثية الأبعاد</text>
  <text x="360" y="350" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="14">تحدد سلسلة الأحماض الأمينية طريقة الطي</text>
  <text x="140" y="290" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="13">حلزون ألفا</text>
  <text x="340" y="280" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="13">صفيحة بيتا</text>
  <text x="520" y="380" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="13">موقع نشط</text>
  <circle cx="520" cy="365" r="8" fill="none" stroke="#ef4444" stroke-width="3"/>
</svg>`)

const immuneSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg3" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#1e1b3d"/>
      <stop offset="1" stop-color="#0f0d20"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg3)"/>
  <circle cx="200" cy="160" r="60" fill="#31265d" stroke="#c4b5fd" stroke-width="4"/>
  <text x="200" y="165" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="14">مستضد</text>
  <path d="M260 160 L320 160" stroke="#60a5fa" stroke-width="3"/>
  <circle cx="400" cy="160" r="45" fill="#3b2f67" stroke="#34d399" stroke-width="4"/>
  <text x="400" y="165" text-anchor="middle" fill="#34d399" font-family="Arial" font-size="13">خلايا LB</text>
  <path d="M400 115 L400 80" stroke="#fbbf24" stroke-width="3"/>
  <circle cx="400" cy="60" r="25" fill="#4b3f77" stroke="#fbbf24" stroke-width="3"/>
  <text x="400" y="65" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">أضداد</text>
  <path d="M440 160 L500 160" stroke="#60a5fa" stroke-width="3"/>
  <circle cx="550" cy="160" r="45" fill="#3b2f67" stroke="#e879f9" stroke-width="4"/>
  <text x="550" y="165" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="13">خلايا LTc</text>
  <path d="M550 205 L550 260" stroke="#ef4444" stroke-width="3"/>
  <rect x="510" y="270" width="80" height="40" rx="8" fill="#4b2f37" stroke="#ef4444" stroke-width="2"/>
  <text x="550" y="295" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="12">خلايا مصابة</text>
  <text x="360" y="380" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">الاستجابة المناعية الخلطية والخلوية</text>
  <circle cx="550" cy="365" r="5" fill="#ef4444"/>
  <circle cx="550" cy="375" r="5" fill="#34d399"/>
  <text x="570" y="370" fill="#d1d5db" font-family="Arial" font-size="11">هجوم / دفاع</text>
</svg>`)

const synapseSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg4" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#1e1b3d"/>
      <stop offset="1" stop-color="#0f0d20"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg4)"/>
  <ellipse cx="180" cy="200" rx="120" ry="80" fill="#31265d" stroke="#a78bfa" stroke-width="4"/>
  <text x="180" y="195" text-anchor="middle" fill="#c4b5fd" font-family="Arial" font-size="14">عصبون قبل مشبكي</text>
  <path d="M300 200 L380 200" stroke="#60a5fa" stroke-width="5" stroke-dasharray="8 6"/>
  <circle cx="340" cy="185" r="6" fill="#fbbf24"/>
  <circle cx="340" cy="200" r="6" fill="#fbbf24"/>
  <circle cx="340" cy="215" r="6" fill="#fbbf24"/>
  <text x="340" y="170" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">Ca2+</text>
  <text x="340" y="240" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">حويصلات</text>
  <ellipse cx="540" cy="200" rx="120" ry="80" fill="#31265d" stroke="#34d399" stroke-width="4"/>
  <text x="540" y="195" text-anchor="middle" fill="#34d399" font-family="Arial" font-size="14">عصبون بعد مشبكي</text>
  <path d="M420 200 L460 200" stroke="#e879f9" stroke-width="3"/>
  <text x="440" y="190" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="11">ناقل عصبي</text>
  <rect x="440" y="270" width="120" height="40" rx="8" fill="#4b2f37" stroke="#ef4444" stroke-width="2"/>
  <text x="500" y="295" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="12">مستقبلات غشائية</text>
  <path d="M500 250 L500 270" stroke="#ef4444" stroke-width="2"/>
  <text x="360" y="380" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">بنية المشبك العصبي وآلية النقل المشبكي</text>
</svg>`)

const chloroplastSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg5" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0a2a1a"/>
      <stop offset="1" stop-color="#051005"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg5)"/>
  <ellipse cx="360" cy="200" rx="220" ry="120" fill="#1a4a2a" stroke="#34d399" stroke-width="5"/>
  <path d="M200 160 C240 120, 300 140, 340 160 C380 180, 420 140, 480 170" fill="none" stroke="#10b981" stroke-width="4"/>
  <path d="M180 220 C220 200, 280 240, 320 210 C360 180, 420 220, 480 200" fill="none" stroke="#10b981" stroke-width="4"/>
  <circle cx="260" cy="180" r="25" fill="#2a6a3a" stroke="#fbbf24" stroke-width="2"/>
  <text x="260" y="185" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="10">حبيبة</text>
  <circle cx="380" cy="190" r="25" fill="#2a6a3a" stroke="#fbbf24" stroke-width="2"/>
  <text x="380" y="195" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="10">حبيبة</text>
  <circle cx="460" cy="180" r="25" fill="#2a6a3a" stroke="#fbbf24" stroke-width="2"/>
  <text x="460" y="185" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="10">حبيبة</text>
  <text x="180" y="140" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="12">غشاء داخلي</text>
  <text x="180" y="320" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="12">غشاء خارجي</text>
  <text x="360" y="370" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">بنية الصانع الأخضر (البلاستيدات الخضراء)</text>
  <text x="360" y="65" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="12">سترومة</text>
  <text x="540" y="300" text-anchor="middle" fill="#60a5fa" font-family="Arial" font-size="11">ثايلاكويد</text>
  <path d="M520 290 L500 180" stroke="#60a5fa" stroke-width="2" stroke-dasharray="4 3"/>
</svg>`)

const mitochondriaSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg6" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#1a0a2a"/>
      <stop offset="1" stop-color="#0a0515"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg6)"/>
  <ellipse cx="360" cy="210" rx="260" ry="100" fill="#2a1a4a" stroke="#a78bfa" stroke-width="5"/>
  <path d="M140 170 C200 130, 260 160, 300 180 C340 200, 380 160, 440 180 C500 200, 540 170, 580 190" fill="none" stroke="#c4b5fd" stroke-width="4"/>
  <path d="M140 250 C200 210, 260 240, 300 220 C340 200, 380 240, 440 220 C500 200, 540 230, 580 210" fill="none" stroke="#c4b5fd" stroke-width="4"/>
  <path d="M240 200 L280 160" stroke="#e879f9" stroke-width="3"/>
  <path d="M320 190 L360 150" stroke="#e879f9" stroke-width="3"/>
  <path d="M400 200 L440 160" stroke="#e879f9" stroke-width="3"/>
  <path d="M480 190 L520 155" stroke="#e879f9" stroke-width="3"/>
  <text x="200" y="120" text-anchor="middle" fill="#34d399" font-family="Arial" font-size="12">أعراف</text>
  <path d="M200 130 L240 165" stroke="#34d399" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="200" y="310" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="12">غشاء خارجي</text>
  <text x="460" y="310" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="12">غشاء داخلي</text>
  <text x="360" y="80" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="12">مطرس</text>
  <text x="360" y="380" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">بنية الميتوكندري</text>
</svg>`)

const cellEnergySvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg7" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0a1a2a"/>
      <stop offset="1" stop-color="#050a15"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg7)"/>
  <ellipse cx="360" cy="210" rx="300" ry="160" fill="#0d1a2d" stroke="#60a5fa" stroke-width="4"/>
  <ellipse cx="220" cy="190" rx="90" ry="60" fill="#1a4a2a" stroke="#34d399" stroke-width="4"/>
  <text x="220" y="195" text-anchor="middle" fill="#10b981" font-family="Arial" font-size="13">صانع أخضر</text>
  <path d="M310 190 L370 190" stroke="#fbbf24" stroke-width="3" stroke-dasharray="6 4"/>
  <text x="340" y="180" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">غلوكوز</text>
  <ellipse cx="500" cy="190" rx="90" ry="60" fill="#2a1a4a" stroke="#a78bfa" stroke-width="4"/>
  <text x="500" y="195" text-anchor="middle" fill="#c4b5fd" font-family="Arial" font-size="13">ميتوكندري</text>
  <path d="M220 250 L500 250" stroke="#e879f9" stroke-width="2" stroke-dasharray="8 4"/>
  <text x="360" y="260" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="11">CO2 + H2O</text>
  <path d="M500 130 L220 130" stroke="#ef4444" stroke-width="2" stroke-dasharray="8 4"/>
  <text x="360" y="125" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="11">ATP</text>
  <text x="360" y="370" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">التكامل الوظيفي بين الصانع الأخضر والميتوكندري</text>
  <text x="360" y="395" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">دورة المادة وتدفق الطاقة في الخلية</text>
</svg>`)

const earthSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg8" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#050510"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg8)"/>
  <circle cx="360" cy="200" r="170" fill="none" stroke="#60a5fa" stroke-width="2"/>
  <circle cx="360" cy="200" r="160" fill="#1a1a3a" stroke="none"/>
  <circle cx="360" cy="200" r="30" fill="#fbbf24" opacity="0.9"/>
  <text x="360" y="205" text-anchor="middle" fill="#1a1a3a" font-family="Arial" font-size="11" font-weight="bold">نواة داخلية</text>
  <circle cx="360" cy="200" r="70" fill="none" stroke="#e879f9" stroke-width="3" stroke-dasharray="6 4"/>
  <text x="360" y="145" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="12">نواة خارجية</text>
  <circle cx="360" cy="200" r="120" fill="none" stroke="#34d399" stroke-width="3" stroke-dasharray="8 6"/>
  <text x="360" y="85" text-anchor="middle" fill="#34d399" font-family="Arial" font-size="12">وشاح</text>
  <circle cx="360" cy="200" r="160" fill="none" stroke="#a78bfa" stroke-width="3"/>
  <text x="360" y="45" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="12">قشرة</text>
  <text x="510" y="300" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="11">انقطاع</text>
  <text x="510" y="315" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="11">موهو</text>
  <line x1="490" y1="290" x2="480" y2="220" stroke="#ef4444" stroke-width="1" stroke-dasharray="3 3"/>
  <line x1="490" y1="340" x2="460" y2="310" stroke="#ef4444" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="360" y="390" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">مقطع في الكرة الأرضية يبين بنيتها الداخلية</text>
</svg>`)

const tectonicSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg9" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#050510"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg9)"/>
  <ellipse cx="360" cy="200" rx="300" ry="150" fill="none" stroke="#60a5fa" stroke-width="2"/>
  <path d="M100 120 Q200 100, 300 150 Q400 200, 500 160 Q600 120, 650 180" fill="none" stroke="#34d399" stroke-width="3"/>
  <path d="M120 250 Q250 280, 360 240 Q470 200, 600 260" fill="none" stroke="#34d399" stroke-width="3"/>
  <path d="M300 80 L300 340" stroke="#ef4444" stroke-width="3" stroke-dasharray="8 4"/>
  <path d="M500 60 L500 360" stroke="#ef4444" stroke-width="3" stroke-dasharray="8 4"/>
  <path d="M200 70 L180 330" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="180" y="100" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">صفيحة</text>
  <text x="180" y="115" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">إفريقية</text>
  <text x="400" y="80" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="11">صفيحة أوراسية</text>
  <text x="550" y="100" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="11">صفيحة المحيط الهادئ</text>
  <text x="140" y="340" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">صفيحة أمريكية</text>
  <text x="580" y="340" text-anchor="middle" fill="#c4b5fd" font-family="Arial" font-size="11">صفيحة أسترالية</text>
  <text x="360" y="390" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">خريطة الصفائح التكتونية واتجاهات حركتها</text>
</svg>`)

const subductionSvg = svgDataUri(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 420">
  <defs>
    <linearGradient id="bg10" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0a0a1a"/>
      <stop offset="1" stop-color="#050510"/>
    </linearGradient>
  </defs>
  <rect width="720" height="420" fill="url(#bg10)"/>
  <rect x="0" y="280" width="720" height="140" fill="#1a1a3a" stroke="none"/>
  <path d="M0 220 L180 220 L220 180 L300 180 L340 280 L720 280" fill="none" stroke="#34d399" stroke-width="4"/>
  <path d="M300 180 L340 280 L400 320 L500 380" fill="none" stroke="#ef4444" stroke-width="4" stroke-dasharray="10 5"/>
  <text x="250" y="170" text-anchor="middle" fill="#34d399" font-family="Arial" font-size="13">صفيحة قارية</text>
  <text x="500" y="170" text-anchor="middle" fill="#a78bfa" font-family="Arial" font-size="13">صفيحة محيطية</text>
  <path d="M340 280 L400 320" stroke="#fbbf24" stroke-width="3"/>
  <text x="370" y="300" text-anchor="middle" fill="#fbbf24" font-family="Arial" font-size="11">اندساس</text>
  <path d="M420 300 L460 250" stroke="#e879f9" stroke-width="3"/>
  <text x="440" y="245" text-anchor="middle" fill="#e879f9" font-family="Arial" font-size="11">صهارة</text>
  <polygon points="460,250 480,230 490,260" fill="#ef4444" opacity="0.6"/>
  <text x="500" y="225" text-anchor="middle" fill="#ef4444" font-family="Arial" font-size="11">بركان</text>
  <line x1="340" y1="280" x2="360" y2="200" stroke="#60a5fa" stroke-width="2" stroke-dasharray="4 3"/>
  <text x="345" y="240" text-anchor="middle" fill="#60a5fa" font-family="Arial" font-size="10">زلازل</text>
  <text x="360" y="390" text-anchor="middle" fill="#d1d5db" font-family="Arial" font-size="18">مقطع يوضح ظاهرة الاندساس والبنيات المرتبطة بها</text>
</svg>`)

export const diagnosticScenario: MethodologyScenario = {
  id: "gene-expression-protein-disorder-v1",
  unitKey: "التعبير المورثي وعلاقته بتركيب البروتين",
  title: "اضطراب تركيب بروتين وظيفي",
  subtitle: "وضعية تشخيصية على نمط البكالوريا",
  contextAr:
    "قصد فهم علاقة التعبير المورثي بكمية البروتين المركب، نقترح الوثائق التالية. المطلوب ليس حفظ الدرس فقط، بل استغلال الوثائق وفق الفعل الأدائي المناسب.",
  dominantSkills: ["analyse", "interpret", "deduce", "hypothesis", "scientific-text"],
  documents: [
    {
      type: "bar-chart",
      id: "doc1-protein-quantity",
      title: "الوثيقة 1: تغير كمية البروتين المركب",
      caption: "بعد تنشيط مورثة معينة، تم قياس كمية البروتين المركب داخل الخلية خلال 30 دقيقة.",
      xLabel: "الزمن بالدقائق",
      yLabel: "كمية البروتين",
      unit: "وحدة",
      points: [
        { label: "0د", value: 2 },
        { label: "10د", value: 3.5 },
        { label: "20د", value: 5.5 },
        { label: "30د", value: 8 },
      ],
    },
    {
      type: "flow",
      id: "doc2-gene-expression-flow",
      title: "الوثيقة 2: مراحل التعبير المورثي",
      caption: "تبين الوثيقة أن تركيب البروتين يمر عبر الاستنساخ ثم الترجمة.",
      steps: ["ADN / مورثة", "ARNm", "سلسلة ببتيدية", "بروتين وظيفي"],
      arrows: ["استنساخ", "ترجمة على مستوى الريبوزومات", "اكتساب بنية فراغية"],
    },
    {
      type: "table",
      id: "doc3-healthy-affected-comparison",
      title: "الوثيقة 3: مقارنة بين شخص سليم وشخص مصاب",
      columns: ["الحالة", "المورثة", "ARNm الناتج", "البروتين المركب"],
      rows: [
        {
          tone: "success",
          cells: ["شخص سليم", "تتابع عادي", "رسالة عادية قابلة للترجمة", "بروتين وظيفي بكمية كافية"],
        },
        {
          tone: "danger",
          cells: ["شخص مصاب", "تغير في التتابع", "رسالة متغيرة", "بروتين ناقص أو غير وظيفي"],
        },
      ],
    },
    {
      type: "image",
      id: "doc4-cell-expression-image",
      title: "الوثيقة 4: صورة تفسيرية مبسطة للتعبير المورثي داخل الخلية",
      caption: "الصورة ليست للزينة: تستعمل لتدريب الطالب على قراءة الوثائق الصورية وتحديد العناصر المهمة قبل التفسير.",
      src: cellProteinSvg,
      alt: "صورة مبسطة توضح النواة والـ ARNm والريبوزومات والبروتين داخل الخلية",
      annotations: [
        { x: 35, y: 49, label: "النواة / ADN", tone: "violet" },
        { x: 51, y: 51, label: "ARNm", tone: "warning" },
        { x: 65, y: 48, label: "ريبوزومات", tone: "success" },
        { x: 67, y: 62, label: "بروتين", tone: "success" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلّل نتائج الوثيقة 1 التي تمثل تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة.",
      placeholder: "تمثل الوثيقة 1... نلاحظ أن... من... إلى... خلال...",
      modelAnswer:
        "تمثل الوثيقة 1 منحنى تغير كمية البروتين المركب داخل الخلية بدلالة الزمن بعد تنشيط مورثة معينة، حيث نلاحظ ارتفاع كمية البروتين من 2 وحدات عند 0 دقيقة إلى 8 وحدات عند 30 دقيقة.",
      learningFocus: "في التحليل يجب استغلال الوثيقة نفسها: نوع الوثيقة، المتغيرات، التغير، القيم. لا تشرح السبب هنا.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسّر ارتفاع كمية البروتين المركب في الوثيقة 1 اعتمادا على آلية التعبير المورثي الموضحة في الوثيقة 2.",
      placeholder: "يفسر ارتفاع... لأن... حسب الوثيقة 2... نعلم أن...",
      modelAnswer:
        "يفسر ارتفاع كمية البروتين المركب بتزايد نشاط التعبير المورثي، لأن الوثيقة 2 تبين أن المورثة تُستنسخ إلى ARNm ثم تترجم على مستوى الريبوزومات إلى سلسلة ببتيدية، وكلما استمر نشاط الترجمة زادت كمية البروتين المركب.",
      learningFocus: "التفسير يجب أن يربط الملاحظة من الوثيقة 1 بآلية علمية من الوثيقة 2 والمكتسبات القبلية.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثيقتان 1 و2",
      prompt: "استنتج العلاقة بين نشاط الترجمة وكمية البروتين المركب انطلاقا من الوثيقتين 1 و2.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن نشاط الترجمة يسمح بزيادة كمية البروتين المركب داخل الخلية.",
      learningFocus: "الاستنتاج نتيجة قصيرة مرتبطة بهدف الوثائق، لا فقرة شرح جديدة.",
    },
    {
      id: "hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر انخفاض البروتين الوظيفي عند الشخص المصاب.",
      placeholder: "نفترض أن سبب انخفاض البروتين الوظيفي يعود إلى... مما يؤدي إلى...",
      modelAnswer:
        "نفترض أن انخفاض البروتين الوظيفي عند الشخص المصاب يعود إلى حدوث تغير في المورثة يؤدي إلى إنتاج ARNm غير عادي، مما يسبب تركيب بروتين ناقص أو غير وظيفي.",
      learningFocus: "الفرضية يجب أن تنطلق من معطيات الوثيقة 3 وتربط سببا محتملا بنتيجة قابلة للاختبار.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اعتمادا على الوثائق ومكتسباتك، اكتب نصا علميا قصيرا تشرح فيه كيف يؤدي تغير في المعلومة الوراثية إلى اضطراب تركيب بروتين وظيفي.",
      placeholder: "مقدمة... إشكالية؟ أولا... ثانيا... في الختام...",
      modelAnswer:
        "تحمل المورثة المعلومة الضرورية لتركيب بروتين وظيفي. فكيف يؤدي تغير هذه المعلومة إلى اضطراب تركيب البروتين؟ أولا يتم استنساخ المعلومة الوراثية من ADN إلى ARNm، ثم تترجم الريبوزومات هذا الـ ARNm إلى سلسلة ببتيدية. ثانيا، إذا حدث تغير في المورثة فقد يتغير الـ ARNm الناتج، مما يؤدي إلى تركيب بروتين ناقص أو غير وظيفي كما تبينه الوثيقة 3. في الختام، يسبب تغير المعلومة الوراثية اضطرابا في التعبير المورثي وبالتالي انخفاضا أو خللا في البروتين الوظيفي.",
      learningFocus: "النص العلمي يجب أن يدمج الوثائق والمكتسبات في بناء واضح: مقدمة، إشكالية، عرض، خاتمة.",
    },
  ],
}

const proteinStructureFunctionScenario: MethodologyScenario = {
  id: "protein-structure-function-v1",
  unitKey: "العلاقة بين بنية ووظيفة البروتين",
  title: "تأثير التغيرات البنيوية على وظيفة البروتين",
  subtitle: "وضعية تعلمية: بنية البروتين وعلاقتها بالوظيفة",
  contextAr: "ترتبط وظيفة البروتين ببنيته الفراغية. من خلال الوثائق التالية، ندرس تأثير التغيرات البنيوية على النشاط الوظيفي للبروتين.",
  dominantSkills: ["analyse", "interpret", "deduce", "hypothesis", "scientific-text"],
  documents: [
    {
      type: "bar-chart",
      id: "doc1-protein-activity",
      title: "الوثيقة 1: نشاط البروتين حسب الحالة البنيوية",
      caption: "تم قياس النشاط الوظيفي للبروتين في حالات بنيوية مختلفة.",
      xLabel: "الحالة البنيوية",
      yLabel: "النشاط",
      unit: "%",
      points: [
        { label: "بنية طبيعية", value: 100 },
        { label: "تشوه بسيط", value: 65 },
        { label: "تشوه متوسط", value: 30 },
        { label: "تشوه كامل", value: 5 },
      ],
    },
    {
      type: "flow",
      id: "doc2-protein-folding",
      title: "الوثيقة 2: مراحل تشكل البروتين الوظيفي",
      caption: "تبين الوثيقة مراحل طي السلسلة الببتيدية لاكتساب البنية الوظيفية.",
      steps: ["سلسلة ببتيدية خطية", "بنية ثانوية", "بنية فراغية ثلاثية", "بروتين وظيفي"],
      arrows: ["طي", "طي نهائي", "اكتساب وظيفة"],
    },
    {
      type: "table",
      id: "doc3-normal-variant-comparison",
      title: "الوثيقة 3: مقارنة بين بروتين طبيعي ومتغير",
      columns: ["الخاصية", "بروتين طبيعي", "بروتين متغير"],
      rows: [
        { cells: ["التتابع AA", "عادي", "متغير"] },
        { cells: ["البنية الفراغية", "طبيعية", "مشوهة"] },
        { cells: ["الوظيفة", "وظيفي", "غير وظيفي"] },
        { tone: "danger", cells: ["النشاط", "100%", "0%"] },
      ],
    },
    {
      type: "image",
      id: "doc4-protein-structure-image",
      title: "الوثيقة 4: تمثيل تخطيطي لبنية البروتين الفراغية",
      caption: "توضح الصورة العلاقة بين تسلسل الأحماض الأمينية والبنية الفراغية النهائية للبروتين.",
      src: proteinSvg,
      alt: "رسم تخطيطي يبين بنية البروتين الفراغية وحلزون ألفا وصفيحة بيتا",
      annotations: [
        { x: 22, y: 68, label: "حلزون ألفا", tone: "violet" },
        { x: 47, y: 65, label: "صفيحة بيتا", tone: "success" },
        { x: 72, y: 85, label: "موقع نشط", tone: "danger" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل الوثيقة 1 التي تمثل تغير نشاط البروتين حسب حالته البنيوية. ما العلاقة بين التشوه البنيوي والنشاط؟",
      placeholder: "تمثل الوثيقة 1 أعمدة بيانية... نلاحظ أن النشاط...",
      modelAnswer: "تمثل الوثيقة 1 أعمدة بيانية لنشاط البروتين حسب الحالة البنيوية. نلاحظ أن البروتين ذو البنية الطبيعية يعطي أعلى نشاط (100%)، بينما ينخفض النشاط تدريجيا مع التشوه ليصل إلى 5% في حالة التشوه الكامل.",
      learningFocus: "ركز على قراءة الأعمدة البيانية: الحالة البنيوية على المحور الأفقي، النشاط على المحور العمودي. لاحظ الانخفاض التدريجي.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "اعتمادا على الوثيقتين 2 و3، فسر لماذا يؤدي تغير التتابع AA إلى فقدان البروتين لوظيفته.",
      placeholder: "يفسر فقدان الوظيفة بأن... حسب الوثيقة 2... بينما الوثيقة 3 تبين...",
      modelAnswer: "يفسر فقدان البروتين لوظيفته بأن تغير التتابع AA (الوثيقة 3) يؤدي إلى اضطراب في عملية الطي الموضحة في الوثيقة 2، مما يمنع تشكل البنية الفراغية الثلاثية الضرورية لاكتساب الوظيفة.",
      learningFocus: "اربط بين معطيات الوثيقتين: تغير التتابع في الوثيقة 3 يمنع الطي الصحيح في الوثيقة 2.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثيقتان 1 و3",
      prompt: "استنتج العلاقة بين البنية الفراغية والنشاط الوظيفي للبروتين انطلاقا من الوثيقتين 1 و3.",
      placeholder: "نستنتج أن...",
      modelAnswer: "نستنتج أن النشاط الوظيفي للبروتين يرتبط ارتباطا وثيقا ببنيته الفراغية السليمة، فأي تشوه بنيوي يؤدي إلى انخفاض أو فقدان النشاط.",
      learningFocus: "الاستنتاج يجب أن يعمم العلاقة بين البنية والوظيفة دون تفاصيل إضافية.",
    },
    {
      id: "hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر كيف يؤدي تغير حمض أميني واحد إلى فقدان البروتين لوظيفته.",
      placeholder: "نفترض أن تغير حمض أميني واحد يؤدي إلى... مما يسبب...",
      modelAnswer: "نفترض أن تغير حمض أميني واحد في التتابع AA يؤدي إلى تغير في طريقة طي السلسلة الببتيدية، مما يسبب تشوها في البنية الفراغية وخاصة في الموقع النشط، وبالتالي فقدان الوظيفة.",
      learningFocus: "الفرضية يجب أن تربط بين التغير الجزيئي (حمض أميني واحد) والنتيجة الوظيفية (فقدان الوظيفة).",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اعتمادا على الوثائق ومكتسباتك، اكتب نصا علميا تشرح فيه العلاقة بين بنية البروتين ووظيفته.",
      placeholder: "مقدمة... أولا: بنية البروتين... ثانيا: العلاقة بالوظيفة... خاتمة...",
      modelAnswer: "تحدد بنية البروتين الفراغية وظيفته البيولوجية. أولا، يكتسب البروتين بنيته الفراغية عبر مراحل متتالية من الطي تبدأ من السلسلة الببتيدية الخطية إلى البنية الثانوية فالثلاثية (الوثيقة 2). ثانيا، أي تغير في التتابع AA يؤدي إلى تشوه بنيوي (الوثيقة 3) مما ينعكس سلبا على النشاط الوظيفي (الوثيقة 1). في الختام، ترتبط وظيفة البروتين ارتباطا وثيقا بسلامة بنيته الفراغية.",
      learningFocus: "النص العلمي يجب أن يدمج جميع الوثائق في بناء مترابط مع مقدمة وخاتمة.",
    },
  ],
}

const enzymeActivityScenario: MethodologyScenario = {
  id: "enzyme-activity-v1",
  unitKey: "النشاط الإنزيمي للبروتينات",
  title: "العوامل المؤثرة في النشاط الإنزيمي",
  subtitle: "وضعية تعلمية: تأثير pH ودرجة الحرارة على الإنزيمات",
  contextAr: "يتأثر النشاط الإنزيمي بعوامل مختلفة مثل pH ودرجة الحرارة. تستعمل الوثائق التالية لتحليل هذه العوامل وتأثيرها على فعالية الإنزيمات.",
  dominantSkills: ["analyse", "compare", "interpret", "deduce", "hypothesis"],
  documents: [
    {
      type: "line-chart",
      id: "doc1-ph-effect",
      title: "الوثيقة 1: تأثير pH على نشاط الإنزيم",
      caption: "تم قياس نشاط إنزيم معين عند قيم pH مختلفة مع تثبيت درجة الحرارة.",
      xLabel: "pH",
      yLabel: "النشاط",
      unit: "%",
      points: [
        { label: "2", value: 10 },
        { label: "4", value: 40 },
        { label: "6", value: 85 },
        { label: "7", value: 100 },
        { label: "8", value: 70 },
        { label: "10", value: 15 },
      ],
    },
    {
      type: "line-chart",
      id: "doc2-temperature-effect",
      title: "الوثيقة 2: تأثير درجة الحرارة على نشاط الإنزيم",
      caption: "تم قياس نشاط الإنزيم نفسه عند درجات حرارة مختلفة مع تثبيت pH.",
      xLabel: "درجة الحرارة",
      yLabel: "النشاط",
      unit: "%",
      points: [
        { label: "0", value: 5 },
        { label: "20", value: 40 },
        { label: "30", value: 80 },
        { label: "37", value: 100 },
        { label: "50", value: 45 },
        { label: "70", value: 5 },
      ],
    },
    {
      type: "table",
      id: "doc3-functional-denatured-comparison",
      title: "الوثيقة 3: مقارنة إنزيم وظيفي وإنزيم منخفض",
      columns: ["الحالة", "بنية الموقع النشط", "تشكل معقد ES", "النشاط"],
      rows: [
        { tone: "success", cells: ["إنزيم وظيفي", "مطابقة تامة", "+", "100%"] },
        { tone: "danger", cells: ["إنزيم منخفض", "مشوهة", "-", "0%"] },
      ],
    },
    {
      type: "flow",
      id: "doc4-es-complex-formation",
      title: "الوثيقة 4: تشكل معقد إنزيم-ركيزة",
      caption: "المراحل المتتالية لتشكل معقد الإنزيم-الركيزة وتحرير النواتج.",
      steps: ["ركيزة + إنزيم", "ارتباط تكميلي", "تشكل معقد ES", "تحرير النواتج"],
      arrows: ["تكامل", "تفاعل", "انفصال"],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنى الوثيقة 1 الذي يمثل تغير نشاط الإنزيم بدلالة pH. حدد قيمة pH المثلى.",
      placeholder: "يمثل المنحنى... نلاحظ أن النشاط يتغير... القيمة المثلى هي...",
      modelAnswer: "يمثل المنحنى تغير نشاط الإنزيم بدلالة pH. نلاحظ أن النشاط يزداد تدريجيا من pH=2 إلى أن يبلغ أقصاه (100%) عند pH=7 (pH مثلى)، ثم ينخفض بعدها. هذا يدل على حساسية الإنزيم لتركيز H+ في الوسط.",
      learningFocus: "تحليل المنحنى: لاحظ شكل الجرس (bell curve)، حدد النشاط الأقصى، صف التغير قبل وبعد القيمة المثلى.",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 2,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقتان 1 و2",
      prompt: "قارن بين تأثير pH وتأثير درجة الحرارة على نشاط الإنزيم اعتمادا على الوثيقتين 1 و2.",
      placeholder: "يتشابه العاملان في... ويختلفان في...",
      modelAnswer: "يتشابه العاملان في أن لكل منهما قيمة مثلى (pH=7، T=37°C) حيث يكون النشاط أقصى، وينخفض النشاط بالابتعاد عن هذه القيمة. يختلفان في أن تأثير pH أكثر حدة عند القيم القصوى حيث ينخفض النشاط بسرعة، بينما تأثير درجة الحرارة يظهر انخفاضا تدريجيا مع احتمال التثبيط الحراري.",
      learningFocus: "استعمل أداة المقارنة: أوجه التشابه + أوجه الاختلاف. اعتمد على معطيات المنحنيين.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 3,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 3 و4",
      prompt: "اعتمادا على الوثيقتين 3 و4، فسر لماذا يفقد الإنزيم المنخفض نشاطه.",
      placeholder: "يفقد الإنزيم المنخفض نشاطه لأن... بنية الموقع النشط...",
      modelAnswer: "يفقد الإنزيم المنخفض نشاطه بسبب تشوه بنية الموقع النشط كما تبينه الوثيقة 3، مما يمنع الارتباط التكميلي مع الركيزة (الوثيقة 4) وبالتالي تعذر تشكل معقد ES الضروري لحدوث التفاعل.",
      learningFocus: "اربط بين تشوه الموقع النشط (الوثيقة 3) وعدم قدرته على الارتباط التكميلي بالركيزة (الوثيقة 4).",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 4,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "استنتج الشروط الضرورية لنشاط الإنزيم انطلاقا من الوثائق الأربع.",
      placeholder: "نستنتج أن نشاط الإنزيم يتطلب...",
      modelAnswer: "نستنتج أن نشاط الإنزيم يتطلب شروطا ملائمة من pH ودرجة الحرارة تحافظ على سلامة بنية الموقع النشط، مما يسمح بالارتباط التكميلي مع الركيزة وتشكل معقد ES.",
      learningFocus: "الاستنتاج يجب أن يدمج جميع العوامل المؤثرة (pH، حرارة، بنية الموقع النشط).",
    },
    {
      id: "hypothesis",
      verbSlug: "hypothesis",
      n: 5,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر العلاقة بين بنية الموقع النشط وقابلية الإنزيم للارتباط بالركيزة.",
      placeholder: "نفترض أن... بنية الموقع النشط تحدد...",
      modelAnswer: "نفترض أن سلامة بنية الموقع النشط تحدد قابلية الإنزيم على الارتباط التكميلي بالركيزة. فتشوه الموقع النشط يمنع التعرف على الركيزة وبالتالي عدم تشكل معقد ES.",
      learningFocus: "الفرضية تفسر آلية: كيف يؤدي تغير بنيوي إلى خلل وظيفي على المستوى الجزيئي.",
    },
  ],
}

const immunityDefenseScenario: MethodologyScenario = {
  id: "immunity-defense-v1",
  unitKey: "دور البروتينات في الدفاع عن الذات",
  title: "الاستجابة المناعية: الأولية والثانوية",
  subtitle: "وضعية تعلمية: آليات الدفاع عن الذات",
  contextAr: "يقوم الجهاز المناعي بدور أساسي في الدفاع عن الذات. تهدف هذه الوضعية إلى تحليل الاستجابة المناعية وتفسير آلياتها.",
  dominantSkills: ["analyse", "interpret", "compare", "deduce", "scientific-text"],
  documents: [
    {
      type: "multi-line-chart",
      id: "doc1-immune-response",
      title: "الوثيقة 1: الاستجابة المناعية الأولية والثانوية",
      caption: "مقارنة شدة الاستجابة المناعية خلال التعرض الأول والثاني لنفس المستضد.",
      xLabel: "الزمن (يوم)",
      yLabel: "تركيز الأضداد",
      unit: "وحدة",
      series: [
        {
          label: "الاستجابة الأولية",
          color: "#A78BFA",
          points: [
            { label: "J0", value: 0 },
            { label: "J7", value: 20 },
            { label: "J14", value: 50 },
            { label: "J21", value: 100 },
            { label: "J28", value: 80 },
          ],
        },
        {
          label: "الاستجابة الثانوية",
          color: "#34D399",
          points: [
            { label: "J0", value: 0 },
            { label: "J3", value: 80 },
            { label: "J7", value: 200 },
            { label: "J14", value: 150 },
            { label: "J21", value: 120 },
          ],
        },
      ],
    },
    {
      type: "flow",
      id: "doc2-lymphocyte-activation",
      title: "الوثيقة 2: تنشيط الخلايا اللمفاوية",
      caption: "تمثل الوثيقة آليات تنشيط الخلايا اللمفاوية LB و LTc.",
      steps: ["مستضد", "خلية عارضة LT4", "تنشيط LB", "تنشيط LTc", "إنتاج أضداد", "قتل الخلايا المصابة"],
      arrows: ["تقديم", "مساعدة", "تمايز", "إفراز", "هجوم"],
    },
    {
      type: "table",
      id: "doc3-primary-secondary-comparison",
      title: "الوثيقة 3: مقارنة الاستجابة الأولية والثانوية",
      columns: ["المعيار", "أولية", "ثانوية"],
      rows: [
        { cells: ["سرعة الظهور", "بطيئة 7-14 يوم", "سريعة 3-5 أيام"] },
        { cells: ["شدة الاستجابة", "ضعيفة", "قوية جدا"] },
        { cells: ["الخلايا", "LT+B ساذجة", "LT+B ذاكرة"] },
        { cells: ["المدة", "قصيرة", "طويلة"] },
      ],
    },
    {
      type: "image",
      id: "doc4-immune-response-image",
      title: "الوثيقة 4: تمثيل تخطيطي للاستجابة المناعية",
      caption: "رسم تخطيطي للاستجابة المناعية الخلطية والخلوية.",
      src: immuneSvg,
      alt: "رسم تخطيطي يبين تنشيط الخلايا اللمفاوية وإنتاج الأضداد",
      annotations: [
        { x: 28, y: 38, label: "مستضد", tone: "violet" },
        { x: 55, y: 38, label: "خلايا LB", tone: "success" },
        { x: 76, y: 38, label: "خلايا LTc", tone: "violet" },
        { x: 55, y: 14, label: "أضداد", tone: "warning" },
        { x: 76, y: 70, label: "خلايا مصابة", tone: "danger" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنيات الوثيقة 1 التي تمثل الاستجابة المناعية الأولية والثانوية. قارن بين المنحنيين.",
      placeholder: "تمثل الوثيقة 1 منحنيين... الأول يمثل... والثاني يمثل... نلاحظ أن...",
      modelAnswer: "تمثل الوثيقة 1 منحنيين للاستجابة المناعية. الأول (الأولية) يرتفع ببطء من J0 إلى قمته J21 (100 وحدة) ثم ينخفض. الثاني (الثانوية) يرتفع بسرعة كبيرة من J0 إلى قمته J7 (200 وحدة) بشكل أقوى وأسرع.",
      learningFocus: "حلل كلا المنحنيين: سرعة الارتفاع، القيمة القصوى، زمن الوصول إلى القمة، الانخفاض.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسر اعتمادا على الوثيقتين 2 و3 سبب ارتفاع الاستجابة الثانوية بشكل أسرع وأقوى من الأولية.",
      placeholder: "يفسر ارتفاع الاستجابة الثانوية بوجود... حسب الوثيقة 2... والوثيقة 3 تبين...",
      modelAnswer: "يفسر ارتفاع الاستجابة الثانوية بوجود خلايا ذاكرة (LT+B ذاكرة) كما تبين الوثيقة 3، والتي يتم تنشيطها بسرعة عند التعرض الثاني لنفس المستضد (الوثيقة 2)، بعكس الاستجابة الأولية التي تعتمد على خلايا ساذجة تحتاج وقتا أطول للتنشيط.",
      learningFocus: "اربط بين وجود خلايا الذاكرة (الوثيقة 3) وسرعة التنشيط (الوثيقة 2).",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقتان 1 و3",
      prompt: "قارن بين الاستجابة المناعية الأولية والثانوية من حيث السرعة والشدة والمدة اعتمادا على الوثيقتين 1 و3.",
      placeholder: "تختلف الاستجابة الأولية عن الثانوية في... الأولية... بينما الثانوية...",
      modelAnswer: "تختلف الاستجابة الأولية عن الثانوية في: السرعة (الأولية بطيئة 7-14 يوما، الثانوية سريعة 3-5 أيام)، الشدة (الأولية ضعيفة بقمة 100، الثانوية قوية جدا بقمة 200)، والمدة (الأولية قصيرة، الثانوية طويلة).",
      learningFocus: "استخرج المعايير من الوثيقة 3 والقيم من الوثيقة 1 لبناء مقارنة منظمة.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 4,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج أهمية خلايا الذاكرة في الاستجابة المناعية انطلاقا من الوثائق 1 و2 و3.",
      placeholder: "نستنتج أن خلايا الذاكرة تلعب دورا...",
      modelAnswer: "نستنتج أن خلايا الذاكرة تلعب دورا حاسما في تسريع وتقوية الاستجابة المناعية عند التعرض الثاني لنفس المستضد، مما يوفر حماية أسرع وأكثر فعالية.",
      learningFocus: "الاستنتاج يجب أن يبرز القيمة الوظيفية لخلايا الذاكرة في المناعة.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيف يتم التعرف على المستضد وتنشيط الخلايا اللمفاوية لإنتاج استجابة مناعية متخصصة.",
      placeholder: "مقدمة... أولا: التعرف على المستضد... ثانيا: التنشيط... ثالثا: الاستجابة... خاتمة...",
      modelAnswer: "يتعرف الجهاز المناعي على المستضد عبر الخلايا العارضة التي تقدمه للخلايا LT4 المساعدة (الوثيقة 2). أولا، تؤدي هذه الأخيرة إلى تنشيط خلايا LB المنتجة للأضداد والخلايا LTc القاتلة. ثانيا، تختلف الاستجابة حسب التعرض: أولية ضعيفة بطيئة أم ثانوية قوية سريعة بفضل خلايا الذاكرة (الوثيقتان 1 و3). في الختام، يضمن الجهاز المناعي حماية متزايدة مع كل تعرض لنفس المستضد.",
      learningFocus: "اجمع بين الخريطة المفاهيمية للتنشيط (وثيقة 2) والنتائج الكمية (وثيقة 1) وخصائص الخلايا (وثيقة 3).",
    },
  ],
}

const nervousCommunicationScenario: MethodologyScenario = {
  id: "nervous-communication-v1",
  unitKey: "دور البروتينات في الاتصال العصبي",
  title: "النقل العصبي: كمون العمل والانتقال المشبكي",
  subtitle: "وضعية تعلمية: آليات الاتصال العصبي",
  contextAr: "يعتمد الاتصال العصبي على نقل الرسائل بين الخلايا العصبية. من خلال الوثائق التالية، ندرس آليات النقل المشبكي وكمون العمل.",
  dominantSkills: ["analyse", "interpret", "deduce", "hypothesis", "scientific-text"],
  documents: [
    {
      type: "line-chart",
      id: "doc1-action-potential",
      title: "الوثيقة 1: كمون العمل",
      caption: "تغير كمون الغشاء العصبي خلال مراحل كمون العمل.",
      xLabel: "الزمن (ms)",
      yLabel: "كمون الغشاء",
      unit: "mV",
      points: [
        { label: "0", value: -70 },
        { label: "1", value: -70 },
        { label: "2", value: -55 },
        { label: "3", value: -40 },
        { label: "4", value: 0 },
        { label: "5", value: 30 },
        { label: "6", value: 20 },
        { label: "7", value: -10 },
        { label: "8", value: -55 },
        { label: "9", value: -70 },
        { label: "10", value: -70 },
      ],
    },
    {
      type: "flow",
      id: "doc2-synaptic-transmission",
      title: "الوثيقة 2: الانتقال المشبكي",
      caption: "المراحل المتتالية لنقل الرسالة العصبية عبر المشبك.",
      steps: ["وصول كمون عمل", "دخول Ca2+", "اندماج الحويصلات", "تحرير الناقل", "ارتباط بالمستقبل", "توليد كمون بعد مشبكي"],
      arrows: ["فتيلة", "إخراج", "ارتباط", "تنبيه"],
    },
    {
      type: "table",
      id: "doc3-resting-action-comparison",
      title: "الوثيقة 3: مقارنة كمون الراحة وكمون العمل",
      columns: ["الخاصية", "كمون الراحة", "كمون العمل"],
      rows: [
        { cells: ["قيمة الكمون", "-70mV", "+30mV"] },
        { cells: ["قنوات Na+", "مغلقة", "مفتوحة"] },
        { cells: ["قنوات K+", "مفتوحة جزئيا", "مفتوحة"] },
        { cells: ["مضخة Na+/K+", "نشيطة", "نشيطة"] },
      ],
    },
    {
      type: "image",
      id: "doc4-synapse-image",
      title: "الوثيقة 4: بنية المشبك العصبي",
      caption: "صورة تخطيطية للمشبك العصبي توضح العناصر الرئيسية.",
      src: synapseSvg,
      alt: "رسم تخطيطي للمشبك العصبي يبين العصبون قبل المشبكي والحويصلات والناقل العصبي والمستقبلات",
      annotations: [
        { x: 25, y: 47, label: "عصبون قبل مشبكي", tone: "violet" },
        { x: 47, y: 47, label: "حويصلات + Ca2+", tone: "warning" },
        { x: 61, y: 45, label: "ناقل عصبي", tone: "violet" },
        { x: 75, y: 47, label: "عصبون بعد مشبكي", tone: "success" },
        { x: 69, y: 70, label: "مستقبلات", tone: "danger" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنى الوثيقة 1 الذي يمثل تغير كمون الغشاء خلال كمون العمل. حدد المراحل المختلفة.",
      placeholder: "يمثل المنحنى... نلاحظ أربع مراحل...",
      modelAnswer: "يمثل المنحنى تغير كمون الغشاء خلال كمون العمل. نلاحظ أربع مراحل: 1) كمون راحة عند -70mV، 2) زوال الاستقطاب السريع من -70mV إلى +30mV، 3) عودة الاستقطاب من +30mV إلى -70mV، 4) فرط الاستقطاب العابر إلى -55mV ثم العودة للراحة.",
      learningFocus: "حدد المراحل الأربع بدقة: الراحة، زوال الاستقطاب، عودة الاستقطاب، فرط الاستقطاب. اقرأ القيم على المنحنى.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقة 2",
      prompt: "فسر آلية الانتقال المشبكي كما هي موضحة في الوثيقة 2.",
      placeholder: "يتم الانتقال المشبكي عبر المراحل التالية... أولا... ثانيا...",
      modelAnswer: "يتم الانتقال المشبكي عبر المراحل التالية: أولا، يصل كمون العمل إلى النهاية قبل المشبكية. ثانيا، يدخل Ca2+ محفزا اندماج الحويصلات مع الغشاء. ثالثا، يتحرر الناقل العصبي في الشق المشبكي. رابعا، يرتبط الناقل بمستقبلات الغشاء بعد المشبكي. خامسا، يتولد كمون بعد مشبكي.",
      learningFocus: "اتبع تسلسل الوثيقة 2 خطوة بخطوة دون إضافة معلومات غير موجودة.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثيقتان 1 و2",
      prompt: "استنتج العلاقة بين كمون العمل والانتقال المشبكي انطلاقا من الوثيقتين 1 و2.",
      placeholder: "نستنتج أن كمون العمل ضروري لـ...",
      modelAnswer: "نستنتج أن كمون العمل المنقول على طول المحور العصبي (الوثيقة 1) هو الشرط الضروري لإطلاق آلية الانتقال المشبكي (الوثيقة 2)، حيث يؤدي وصوله إلى تحرير الناقل العصبي ونقل الرسالة إلى العصبون التالي.",
      learningFocus: "الاستنتاج يربط بين الظاهرتين: كمون العمل كإشارة كهربائية والانتقال المشبكي كآلية كيميائية.",
    },
    {
      id: "hypothesis",
      verbSlug: "hypothesis",
      n: 4,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر تغير كمون الغشاء من -70mV إلى +30mV أثناء زوال الاستقطاب.",
      placeholder: "نفترض أن تغير الكمون يعود إلى...",
      modelAnswer: "نفترض أن تغير الكمون من -70mV إلى +30mV يعود إلى فتح قنوات Na+ (الموصوفة في الوثيقة 3) مما يسمح بدخول أيونات Na+ إلى الخلية بكميات كبيرة، مسببا زوال الاستقطاب.",
      learningFocus: "اربط بين تغير الكمون (الوثيقة 1) وحركة الأيونات عبر القنوات (الوثيقة 3).",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اعتمادا على الوثائق ومكتسباتك، اكتب نصا علميا تشرح فيه كيفية انتقال الرسالة العصبية من عصبون إلى آخر.",
      placeholder: "مقدمة... أولا: كمون العمل... ثانيا: الانتقال المشبكي... خاتمة...",
      modelAnswer: "تنتقل الرسالة العصبية عبر آليتين متكاملتين. أولا، ينتقل كمون العمل على طول المحور العصبي عبر تغيرات في نفاذية الغشاء للأيونات (الوثيقتان 1 و3) حيث يحدث زوال استقطاب بفتح قنوات Na+ ثم عودة استقطاب بفتح قنوات K+. ثانيا، عند الوصول إلى النهاية قبل المشبكية، يتحرر الناقل العصبي (الوثيقتان 2 و4) الذي يرتبط بمستقبلات الغشاء بعد المشبكي محدثا كمونا بعد مشبكيا. في الختام، يضمن هذا التسلسل نقل الرسالة العصبية بين الخلايا العصبية.",
      learningFocus: "اجمع بين الآلية الكهربائية (كمون العمل) والآلية الكيميائية (النقل المشبكي) في نص مترابط.",
    },
  ],
}

const photosynthesisScenario: MethodologyScenario = {
  id: "photosynthesis-v1",
  unitKey: "آليات تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة",
  title: "التركيب الضوئي: من الطاقة الضوئية إلى الطاقة الكيميائية",
  subtitle: "وضعية تعلمية: آليات التركيب الضوئي",
  contextAr: "تمثل عملية التركيب الضوئي الآلية الأساسية لتحويل الطاقة الضوئية إلى طاقة كيميائية. تهدف هذه الوضعية إلى تحليل هذه الآليات.",
  dominantSkills: ["analyse", "interpret", "relationship", "deduce", "scientific-text"],
  documents: [
    {
      type: "line-chart",
      id: "doc1-oxygen-production",
      title: "الوثيقة 1: تغير كمية O2 حسب شدة الإضاءة",
      caption: "تم قياس كمية الأكسجين المنطلق من نبات أخضر تحت إضاءة متفاوتة الشدة.",
      xLabel: "شدة الإضاءة",
      yLabel: "كمية O2",
      unit: "وحدة",
      points: [
        { label: "0", value: 0 },
        { label: "50", value: 5 },
        { label: "100", value: 12 },
        { label: "200", value: 25 },
        { label: "400", value: 40 },
        { label: "600", value: 45 },
      ],
    },
    {
      type: "flow",
      id: "doc2-photosynthesis-stages",
      title: "الوثيقة 2: مراحل التركيب الضوئي",
      caption: "المراحل المتتالية للتركيب الضوئي من التفاعلات الضوئية إلى دورة كالفن.",
      steps: ["ضوء", "تفاعلات ضوئية", "ATP+NADPH+H", "دورة كالفن", "CO2", "غلوكوز"],
      arrows: ["تنشيط اليخضور", "إنتاج", "تثبيت CO2", "اختزال"],
    },
    {
      type: "table",
      id: "doc3-light-dark-comparison",
      title: "الوثيقة 3: مقارنة بين التفاعلات الضوئية واللاضوئية",
      columns: ["المعيار", "تفاعلات ضوئية", "تفاعلات لاضوئية"],
      rows: [
        { cells: ["الموقع", "غشاء الثايلاكويد", "ستروما الصانع"] },
        { cells: ["المادة الأولية", "H2O", "CO2+ATP+NADPH"] },
        { cells: ["النواتج", "O2+ATP+NADPH", "غلوكوز"] },
        { cells: ["تحتاج ضوء", "نعم", "لا"] },
      ],
    },
    {
      type: "image",
      id: "doc4-chloroplast-image",
      title: "الوثيقة 4: بنية الصانع الأخضر",
      caption: "مقطع في الصانع الأخضر يبين الأغشية والغرف الداخلية.",
      src: chloroplastSvg,
      alt: "رسم تخطيطي للصانع الأخضر يبين الغشاء الداخلي والخارجي والثايلاكويدات والستروما",
      annotations: [
        { x: 36, y: 43, label: "حبيبة ثايلاكويد", tone: "warning" },
        { x: 53, y: 45, label: "حبيبة ثايلاكويد", tone: "warning" },
        { x: 64, y: 43, label: "حبيبة ثايلاكويد", tone: "warning" },
        { x: 25, y: 33, label: "غشاء داخلي", tone: "violet" },
        { x: 25, y: 76, label: "غشاء خارجي", tone: "violet" },
        { x: 50, y: 15, label: "سترومة", tone: "warning" },
        { x: 72, y: 72, label: "ثايلاكويد", tone: "success" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنى الوثيقة 1 الذي يمثل تغير كمية O2 المنطلق بدلالة شدة الإضاءة. حدد اتجاه التغير.",
      placeholder: "يمثل المنحنى... نلاحظ أن كمية O2... مع زيادة شدة الإضاءة...",
      modelAnswer: "يمثل المنحنى تغير كمية O2 المنطلق بدلالة شدة الإضاءة. نلاحظ زيادة كمية O2 مع زيادة شدة الإضاءة من 0 إلى 400 (حيث تبلغ 45 وحدة)، ثم تثبت عند شدة 600 (45 وحدة) مشيرة إلى ظاهرة الإشباع الضوئي.",
      learningFocus: "حلل شكل المنحنى: ارتفاع منتظم ثم تثبيت. لاحظ نقطة الإشباع حيث يبلغ النشاط حده الأقصى.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقة 2",
      prompt: "فسر تدفق الطاقة في التركيب الضوئي انطلاقا من الوثيقة 2.",
      placeholder: "يتم تحويل الطاقة الضوئية عبر... المرحلة الأولى... ثم المرحلة الثانية...",
      modelAnswer: "يتم تحويل الطاقة الضوئية على مرحلتين: أولا، في التفاعلات الضوئية (بغشاء الثايلاكويد) حيث تنشط الطاقة الضوئية اليخضور لإنتاج ATP و NADPH+H مع تحرير O2. ثانيا، في التفاعلات اللاضوئية (دورة كالفن) حيث يستعمل ATP و NADPH+H لتثبيت CO2 واختزاله إلى غلوكوز.",
      learningFocus: "اتبع مسار الطاقة: ضوء → تفاعلات ضوئية → ATP+NADPH → دورة كالفن → غلوكوز.",
    },
    {
      id: "relationship",
      verbSlug: "relationship",
      n: 3,
      title: "إقامة علاقة",
      skill: "إقامة العلاقات",
      docRef: "الوثيقتان 1 و3",
      prompt: "أقم علاقة بين زيادة إنتاج O2 في الوثيقة 1 وموقع التفاعلات الضوئية في الوثيقة 3.",
      placeholder: "يرتبط إنتاج O2 بالتفاعلات الضوئية التي تتم في...",
      modelAnswer: "يرتبط إنتاج O2 شدة ارتباطا بالتفاعلات الضوئية التي تتم في غشاء الثايلاكويد (الوثيقة 3). فزيادة شدة الإضاءة تنشط التفاعلات الضوئية مما يزيد من تحلل الماء (H2O) وإطلاق O2، وهو ما يفسر ارتفاع كمية O2 في الوثيقة 1.",
      learningFocus: "أقم علاقة سببية: الضوء → تفاعلات ضوئية (غشاء الثايلاكويد) → تحلل H2O → إطلاق O2.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 4,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج الشروط اللازمة لإنتاج الغلوكوز في النبات الأخضر انطلاقا من الوثائق 1 و2 و3.",
      placeholder: "نستنتج أن إنتاج الغلوكوز يتطلب...",
      modelAnswer: "نستنتج أن إنتاج الغلوكوز يتطلب توفر ثلاثة شروط: الضوء (الوثيقة 1) لتنشيط التفاعلات الضوئية، وثاني أكسيد الكربون CO2 (الوثيقة 2) لتثبيته في دورة كالفن، ووجود الصانع الأخضر بغشائه الثايلاكويدي وستروما (الوثيقة 3).",
      learningFocus: "الاستنتاج يجب أن يجمع الشروط الضرورية: ضوء، CO2، صانع أخضر.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه كيفية تحويل الطاقة الضوئية إلى طاقة كيميائية كامنة في النبات الأخضر.",
      placeholder: "مقدمة... أولا: التفاعلات الضوئية... ثانيا: دورة كالفن... خاتمة...",
      modelAnswer: "يحول النبات الأخضر الطاقة الضوئية إلى طاقة كيميائية عبر مرحلتين متكاملتين. أولا، في التفاعلات الضوئية التي تتم في غشاء الثايلاكويد (الوثيقتان 3 و4) حيث تنشط الطاقة الضوئية اليخضور فيحلل الماء منتجا O2 وATP وNADPH+H. ثانيا، في دورة كالفن بالستروما حيث يستعمل CO2 (الوثيقة 2) مع ATP وNADPH+H لتركيب الغلوكوز. يزداد إنتاج O2 بزيادة شدة الإضاءة حتى حد الإشباع (الوثيقة 1). في الختام، تخزن الطاقة الضوئية في الروابط الكيميائية للغلوكوز.",
      learningFocus: "اجمع بين الشروط (ضوء، CO2، صانع أخضر)، والمراحل (ضوئية ولا ضوئية)، والنواتج (O2، غلوكوز).",
    },
  ],
}

const cellularRespirationScenario: MethodologyScenario = {
  id: "cellular-respiration-v1",
  unitKey: "آليات تحويل الطاقة الكيميائية الكامنة في الجزيئات العضوية إلى ATP",
  title: "التنفس الخلوي: من الغلوكوز إلى ATP",
  subtitle: "وضعية تعلمية: مراحل التنفس الخلوي",
  contextAr: "يعتبر التنفس الخلوي العملية المسؤولة عن تحويل الطاقة الكيميائية الكامنة إلى ATP. ندرس من خلال الوثائق التالية مراحل هذه العملية.",
  dominantSkills: ["analyse", "interpret", "compare", "deduce", "scientific-text"],
  documents: [
    {
      type: "bar-chart",
      id: "doc1-atp-production",
      title: "الوثيقة 1: إنتاج ATP حسب مراحل التنفس",
      caption: "كمية ATP المنتجة في كل مرحلة من مراحل التنفس الخلوي لجزيء غلوكوز واحد.",
      xLabel: "المراحل",
      yLabel: "ATP المنتج",
      unit: "جزيء",
      points: [
        { label: "تحلل كليكوز", value: 2 },
        { label: "أكسدة حمض بيروفيك", value: 6 },
        { label: "دورة كريبس", value: 24 },
        { label: "سلسلة تنفسية", value: 34 },
      ],
    },
    {
      type: "flow",
      id: "doc2-respiration-pathway",
      title: "الوثيقة 2: مسار التنفس الخلوي",
      caption: "المراحل المتتالية للتنفس الخلوي من الغلوكوز إلى ATP.",
      steps: ["كليكوز", "حمض بيروفيك", "أستيل مرافق A", "دورة كريبس", "سلسلة تنفسية", "ATP+H2O+CO2"],
      arrows: ["تحلل", "أكسدة", "دخول", "إنتاج", "فسفرة"],
    },
    {
      type: "table",
      id: "doc3-respiration-fermentation-comparison",
      title: "الوثيقة 3: مقارنة التنفس والتخمر",
      columns: ["المعيار", "تنفس", "تخمر"],
      rows: [
        { cells: ["O2", "يحتاجه", "لا يحتاجه"] },
        { cells: ["ATP/كليكوز", "36-38", "2"] },
        { cells: ["CO2", "ينتج", "ينتج"] },
        { cells: ["المادة العضوية", "تستنفذ", "لا تستنفذ"] },
        { cells: ["المنتج النهائي", "H2O+CO2", "حمض لاكتيك/كحول"] },
      ],
    },
    {
      type: "image",
      id: "doc4-mitochondria-image",
      title: "الوثيقة 4: بنية الميتوكندري",
      caption: "مقطع في الميتوكندري يبين الغشاء الداخلي والأعراف والمطرس.",
      src: mitochondriaSvg,
      alt: "رسم تخطيطي للميتوكندري يبين الغشاءين الخارجي والداخلي والأعراف والمطرس",
      annotations: [
        { x: 36, y: 19, label: "أعراف", tone: "success" },
        { x: 28, y: 74, label: "غشاء خارجي", tone: "violet" },
        { x: 64, y: 74, label: "غشاء داخلي", tone: "violet" },
        { x: 50, y: 19, label: "مطرس", tone: "warning" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل الأعمدة البيانية في الوثيقة 1 التي تمثل إنتاج ATP حسب مراحل التنفس. حدد المرحلة الأكثر إنتاجا.",
      placeholder: "تمثل الأعمدة... نلاحظ أن إنتاج ATP يختلف حسب... المرحلة الأكثر إنتاجا هي...",
      modelAnswer: "تمثل الأعمدة البيانية إنتاج ATP في كل مرحلة من مراحل التنفس الخلوي. نلاحظ أن التحلل الكليكي ينتج 2 ATP، أكسدة حمض بيروفيك تنتج 6 ATP، دورة كريبس تنتج 24 ATP، والسلسلة التنفسية تنتج 34 ATP. المرحلة الأكثر إنتاجا هي السلسلة التنفسية.",
      learningFocus: "اقرأ القيم بدقة من الأعمدة. صنف المراحل حسب كمية ATP: تحلل كليكوز < أكسدة < دورة كريبس < سلسلة تنفسية.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و1",
      prompt: "فسر اعتمادا على الوثيقتين 2 و1 سبب زيادة إنتاج ATP تدريجيا عبر مراحل التنفس.",
      placeholder: "تزداد كمية ATP بسبب... كل مرحلة تحضر للمرحلة التالية...",
      modelAnswer: "تزداد كمية ATP تدريجيا لأن كل مرحلة تحلل جزئيا جزيء الغلوكوز وتنتج مركبات وسيطة تغذي المرحلة التالية (الوثيقة 2). نبدأ بتحلل كليكوز (2 ATP) ثم أكسدة حمض بيروفيك (6 ATP) ثم دورة كريبس (24 ATP) وأخيرا السلسلة التنفسية (34 ATP) حيث يتم الفسفرة التأكسدية (الوثيقة 1).",
      learningFocus: "اربط بين تسلسل المراحل (الوثيقة 2) وكمية ATP المتراكمة (الوثيقة 1).",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين التنفس والتخمر اعتمادا على الوثيقة 3 من حيث الحاجة إلى O2 وإنتاجية ATP.",
      placeholder: "يختلف التنفس عن التخمر في... التنفس... بينما التخمر...",
      modelAnswer: "يختلف التنفس عن التخمر: التنفس يحتاج O2 بينما التخمر لا يحتاجه. إنتاجية ATP في التنفس عالية جدا (36-38ATP) بينما التخمر ينتج 2ATP فقط. التنفس يستنفذ المادة العضوية وينتج H2O+CO2، بينما التخمر لا يستنفذها وينتج حمض لاكتيك أو كحول.",
      learningFocus: "قارن نقطة بنقطة: O2، ATP، المنتجات النهائية، استنفاذ المادة العضوية.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 4,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج أهمية التنفس الخلوي في إنتاج الطاقة انطلاقا من الوثائق 1 و2 و3.",
      placeholder: "نستنتج أن التنفس الخلوي هو...",
      modelAnswer: "نستنتج أن التنفس الخلوي هو العملية الأكثر فعالية لإنتاج ATP من جزيء الغلوكوز (36-38 ATP) عبر أربع مراحل متتالية (الوثيقتان 1 و2)، مقارنة بالتخمر الذي ينتج 2ATP فقط (الوثيقة 3).",
      learningFocus: "الاستنتاج يبرز كفاءة التنفس مقارنة بالتخمر في إنتاج الطاقة.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه المراحل الرئيسية للتنفس الخلوي وأهميته في إنتاج ATP.",
      placeholder: "مقدمة... أولا: المراحل... ثانيا: إنتاجية ATP... ثالثا: مقارنة بالتخمر... خاتمة...",
      modelAnswer: "يمثل التنفس الخلوي مجموعة من التفاعلات المتسلسلة التي تحول الطاقة الكيميائية للغلوكوز إلى ATP. أولا، في الهيولة يتحلل الكليكوز إلى حمض بيروفيك (2 ATP). ثانيا، في المطرس (الوثيقة 4) يتأكسد حمض بيروفيك إلى أستيل مرافق A لدخول دورة كريبس منتجا 24 ATP. ثالثا، على مستوى الأعراف (الوثيقة 4) تتم السلسلة التنفسية حيث تنتج 34 ATP عبر الفسفرة التأكسدية (الوثيقتان 1 و2). يعتبر التنفس أكثر فعالية من التخمر بـ 18 مرة (الوثيقة 3). في الختام، يضمن التنفس الخلوي إنتاجا وفيرا من ATP الضروري للأنشطة الحيوية.",
      learningFocus: "اجمع بين المواقع الخلوية (هيولة، مطرس، أعراف) والمراحل الأيضية والنواتج.",
    },
  ],
}

const ultrastructuralEnergyScenario: MethodologyScenario = {
  id: "ultrastructural-energy-v1",
  unitKey: "تحويل الطاقة على المستوى ما فوق البنية الخلوية",
  title: "التكامل الوظيفي بين الصانع الأخضر والميتوكندري",
  subtitle: "وضعية تعلمية: العلاقة بين التركيب الضوئي والتنفس",
  contextAr: "تتكامل عملية التركيب الضوئي والتنفس على المستوى الخلوي. ندرس من خلال الوثائق التالية العلاقة بين الصانع الأخضر والميتوكندري.",
  dominantSkills: ["analyse", "interpret", "compare", "relationship", "scientific-text"],
  documents: [
    {
      type: "multi-line-chart",
      id: "doc1-gas-exchange",
      title: "الوثيقة 1: تبادل O2 و CO2 في الضوء والظلام",
      caption: "تغير كمية O2 و CO2 المتبادلة بين النبات والوسط تحت إضاءة متفاوتة.",
      xLabel: "شدة الإضاءة",
      yLabel: "كمية الغاز",
      unit: "وحدة",
      series: [
        {
          label: "O2",
          color: "#34D399",
          points: [
            { label: "ظلام", value: 10 },
            { label: "ضوء خافت", value: 25 },
            { label: "ضوء متوسط", value: 50 },
            { label: "ضوء قوي", value: 80 },
          ],
        },
        {
          label: "CO2",
          color: "#EF4444",
          points: [
            { label: "ظلام", value: 70 },
            { label: "ضوء خافت", value: 40 },
            { label: "ضوء متوسط", value: 20 },
            { label: "ضوء قوي", value: 5 },
          ],
        },
      ],
    },
    {
      type: "flow",
      id: "doc2-organelle-integration",
      title: "الوثيقة 2: التكامل بين الصانع والميتوكندري",
      caption: "تبين الوثيقة تدفق المواد بين الصانع الأخضر والميتوكندري.",
      steps: ["CO2+H2O", "صانع أخضر", "غلوكوز", "ميتوكندري", "ATP+CO2+H2O"],
      arrows: ["تركيب ضوئي", "نقل", "تنفس", "طاقة"],
    },
    {
      type: "table",
      id: "doc3-chloroplast-mitochondria-comparison",
      title: "الوثيقة 3: مقارنة الصانع الأخضر والميتوكندري",
      columns: ["المعيار", "صانع أخضر", "ميتوكندري"],
      rows: [
        { cells: ["الوظيفة", "تركيب ضوئي", "تنفس"] },
        { cells: ["الطاقة", "تختزن", "تحرر"] },
        { cells: ["المواد الأولية", "CO2+H2O", "غلوكوز+O2"] },
        { cells: ["الناتج", "غلوكوز+O2", "ATP+CO2+H2O"] },
        { cells: ["الغشاء الداخلي", "ثايلاكويد", "أعراف"] },
      ],
    },
    {
      type: "image",
      id: "doc4-cell-energy-image",
      title: "الوثيقة 4: التكامل الوظيفي في الخلية النباتية",
      caption: "رسم تخطيطي يبين تدفق المواد بين الصانع الأخضر والميتوكندري في الخلية النباتية.",
      src: cellEnergySvg,
      alt: "رسم تخطيطي لخلية نباتية يبين الصانع الأخضر والميتوكندري وتبادل المواد بينهما",
      annotations: [
        { x: 31, y: 45, label: "صانع أخضر", tone: "success" },
        { x: 47, y: 43, label: "غلوكوز", tone: "warning" },
        { x: 69, y: 45, label: "ميتوكندري", tone: "violet" },
        { x: 50, y: 60, label: "CO2 + H2O", tone: "violet" },
        { x: 50, y: 30, label: "ATP", tone: "danger" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنيات الوثيقة 1 التي تمثل تغير O2 و CO2 بدلالة شدة الإضاءة. صف اتجاه كل منحنى.",
      placeholder: "يمثل المنحنيان... O2 يتزايد... CO2 يتناقص...",
      modelAnswer: "يمثل المنحنيان تبادل O2 و CO2. منحنى O2 يتزايد مع شدة الإضاءة من 10 (ظلام) إلى 80 (ضوء قوي). منحنى CO2 يتناقص مع شدة الإضاءة من 70 (ظلام) إلى 5 (ضوء قوي). هناك علاقة عكسية بينهما.",
      learningFocus: "حلل كلا المنحنيين معا: لاحظ العلاقة العكسية بين O2 و CO2. اربط بظاهرة التركيب الضوئي.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسر اعتمادا على الوثيقتين 2 و3 كيفية تكامل وظيفة الصانع الأخضر والميتوكندري.",
      placeholder: "يكتمل عمل الصانع الأخضر والميتوكندري حيث... الصانع ينتج... ثم ينقل إلى...",
      modelAnswer: "يكتمل عمل الصانع الأخضر والميتوكندري حيث يقوم الصانع (التركيب الضوئي) بتحويل CO2+H2O إلى غلوكوز+O2 مختزنا الطاقة (الوثيقة 3). ينقل الغلوكوز إلى الميتوكندري الذي يستعمله في التنفس لإنتاج ATP محررا الطاقة مع إطلاق CO2+H2O الذي يعاد استعماله من طرف الصانع (الوثيقة 2).",
      learningFocus: "فهم دورة المواد: ناتج أحدهما هو مادة أولية للآخر. هذه هي دورة الكربون والطاقة.",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين الصانع الأخضر والميتوكندري من حيث الوظيفة والمواد الأولية والنواتج اعتمادا على الوثيقة 3.",
      placeholder: "يتشابه العضيان في... ويختلفان في... الصانع... أما الميتوكندري...",
      modelAnswer: "يختلف الصانع الأخضر عن الميتوكندري في الوظيفة: الصانع يختزن الطاقة (تركيب ضوئي) بينما الميتوكندري يحرر الطاقة (تنفس). المواد الأولية للصانع: CO2+H2O، وللميتوكندري: غلوكوز+O2. ناتج الصانع: غلوكوز+O2، وناتج الميتوكندري: ATP+CO2+H2O. يتشابهان في وجود غشاء داخلي متخصص (ثايلاكويد/أعراف).",
      learningFocus: "قارن وفق معايير محددة: الوظيفة، الطاقة، المواد الأولية، النواتج، الغشاء الداخلي.",
    },
    {
      id: "relationship",
      verbSlug: "relationship",
      n: 4,
      title: "إقامة علاقة",
      skill: "إقامة العلاقات",
      docRef: "الوثيقتان 1 و3",
      prompt: "أقم علاقة بين تغير O2 و CO2 في الوثيقة 1 ووظيفة الصانع الأخضر في الوثيقة 3.",
      placeholder: "يرتبط تغير O2 و CO2 بنشاط الصانع الأخضر حيث...",
      modelAnswer: "يرتبط تغير O2 و CO2 (الوثيقة 1) بنشاط الصانع الأخضر (الوثيقة 3). في الضوء، يستهلك الصانع CO2 ويطلق O2 عبر التركيب الضوئي مما يفسر ارتفاع O2 وانخفاض CO2. في الظلام، يتوقف التركيب الضوئي ويبقى التنفس فقط، مما يفسر انخفاض O2 وارتفاع CO2.",
      learningFocus: "اربط بين تبادل الغازات (وثيقة 1) والنشاط الأيضي للصانع (وثيقة 3).",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه التكامل الوظيفي بين الصانع الأخضر والميتوكندري في تحويل الطاقة.",
      placeholder: "مقدمة... أولا: دور الصانع الأخضر... ثانيا: دور الميتوكندري... ثالثا: التكامل... خاتمة...",
      modelAnswer: "يتحقق تحويل الطاقة في الخلية النباتية عبر تكامل وظيفي بين الصانع الأخضر والميتوكندري. أولا، في الصانع الأخضر (الوثيقة 3 و4) يتم التركيب الضوئي بتحويل CO2+H2O إلى غلوكوز+O2 باستعمال الطاقة الضوئية. ثانيا، في الميتوكندري (الوثيقة 3 و4) يتم التنفس الخلوي بتحويل الغلوكوز+O2 إلى ATP+CO2+H2O محررا الطاقة. ثالثا، ناتج أحدهما هو مادة أولية للآخر مما يشكل دورة متكاملة (الوثيقة 2). يزداد O2 وينخفض CO2 في الضوء القوي (الوثيقة 1). في الختام، يضمن هذا التكامل تدفق الطاقة واستمرار دورة المادة في الخلية.",
      learningFocus: "اجمع بين الموقعين (صانع، ميتوكندري)، والوظيفتين (تركيب ضوئي، تنفس)، ودورة المواد بينهما.",
    },
  ],
}

const earthStructureScenario: MethodologyScenario = {
  id: "earth-structure-v1",
  unitKey: "بنية الكرة الأرضية",
  title: "البنية الداخلية للكرة الأرضية",
  subtitle: "وضعية تعلمية: دراسة بنية الأرض باستعمال الموجات الزلزالية",
  contextAr: "تتكون الكرة الأرضية من عدة طبقات مختلفة الخصائص. نستعمل الوثائق التالية لدراسة بنية الأرض الداخلية.",
  dominantSkills: ["analyse", "interpret", "deduce", "relationship", "scientific-text"],
  documents: [
    {
      type: "multi-line-chart",
      id: "doc1-seismic-waves",
      title: "الوثيقة 1: سرعة الموجات P و S حسب العمق",
      caption: "تغير سرعة الموجات الزلزالية P و S بدلالة العمق في الكرة الأرضية.",
      xLabel: "العمق (كم)",
      yLabel: "السرعة",
      unit: "كم/ثا",
      series: [
        {
          label: "الموجات P",
          color: "#A78BFA",
          points: [
            { label: "محيط", value: 6 },
            { label: "قشرة عليا", value: 7 },
            { label: "قشرة سفلية", value: 8 },
            { label: "وشاح", value: 13 },
            { label: "نواة خارجية", value: 8 },
            { label: "نواة داخلية", value: 11 },
          ],
        },
        {
          label: "الموجات S",
          color: "#34D399",
          points: [
            { label: "محيط", value: 0 },
            { label: "قشرة عليا", value: 4 },
            { label: "قشرة سفلية", value: 4.5 },
            { label: "وشاح", value: 7 },
            { label: "نواة خارجية", value: 0 },
            { label: "نواة داخلية", value: 0 },
          ],
        },
      ],
    },
    {
      type: "table",
      id: "doc2-earth-layers",
      title: "الوثيقة 2: خصائص طبقات الأرض",
      columns: ["الطبقة", "العمق كم", "الحالة", "الكثافة"],
      rows: [
        { cells: ["القشرة", "0-30", "صلبة", "2.7"] },
        { cells: ["الوشاح", "30-2900", "صلبة لزجة", "3.3-5.7"] },
        { cells: ["النواة الخارجية", "2900-5100", "سائلة", "9.9-12.2"] },
        { cells: ["النواة الداخلية", "5100-6371", "صلبة", "12.8-13.1"] },
      ],
    },
    {
      type: "flow",
      id: "doc3-earth-structure-interpretation",
      title: "الوثيقة 3: تفسير البنية الداخلية للكرة الأرضية",
      caption: "منهجية استنتاج بنية الأرض الداخلية انطلاقا من الموجات الزلزالية.",
      steps: ["الموجات الزلزالية", "سرعة الموجات P و S", "استنتاج حالة الطبقات", "نموذج البنية الداخلية"],
      arrows: ["تسجيل", "تحليل", "بناء نموذج"],
    },
    {
      type: "image",
      id: "doc4-earth-cross-section",
      title: "الوثيقة 4: مقطع في الكرة الأرضية",
      caption: "مقطع يبين الطبقات المختلفة للكرة الأرضية: القشرة، الوشاح، النواة الخارجية، النواة الداخلية.",
      src: earthSvg,
      alt: "مقطع عرضي في الكرة الأرضية يبين القشرة والوشاح والنواة الخارجية والنواة الداخلية",
      annotations: [
        { x: 50, y: 10, label: "قشرة", tone: "violet" },
        { x: 50, y: 20, label: "وشاح", tone: "success" },
        { x: 50, y: 35, label: "نواة خارجية", tone: "violet" },
        { x: 50, y: 48, label: "نواة داخلية", tone: "warning" },
        { x: 71, y: 72, label: "انقطاع موهو", tone: "danger" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل منحنيات الوثيقة 1 التي تمثل سرعة الموجات P و S بدلالة العمق. صف تغير كل منحنى.",
      placeholder: "تمثل المنحنيات... الموجات P... الموجات S... نلاحظ أن...",
      modelAnswer: "تمثل المنحنيات تغير سرعة الموجات P و S بالعمق. الموجات P تنتقل بسرعات مختلفة عبر جميع الطبقات (6-13 كم/ثا) مع تغيرات مفاجئة عند حدود الطبقات. الموجات S تنتقل عبر القشرة والوشاح (4-7 كم/ثا) لكنها تنعدم تماما في النواة الخارجية (0 كم/ثا).",
      learningFocus: "حلل كلا المنحنيين: لاحظ أين تنتقل الموجات S وأين تنعدم. لاحظ التغيرات المفاجئة في السرعة.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 1 و2",
      prompt: "فسر اعتمادا على الوثيقتين 1 و2 سبب انعدام الموجات S في النواة الخارجية.",
      placeholder: "تنعدم الموجات S في النواة الخارجية لأن... الموجات S لا تنتشر في...",
      modelAnswer: "تنعدم الموجات S في النواة الخارجية لأن الموجات S هي موجات ميكانيكية عرضية لا تنتشر في الأوساط السائلة. والوثيقة 2 تبين أن النواة الخارجية سائلة، مما يمنع مرور الموجات S عبرها.",
      learningFocus: "اربط بين سرعة الموجات (0 في النواة الخارجية) وحالة الطبقة (سائلة في الوثيقة 2). الموجات S = موجات عرضية = لا تنتشر في السوائل.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 3,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج اعتمادا على الوثائق 1 و2 و3 كيفية استنتاج حالة الطبقات الأرضية من سرعة الموجات الزلزالية.",
      placeholder: "نستنتج أن حالة الطبقة الأرضية تستنتج من...",
      modelAnswer: "نستنتج أن حالة الطبقة الأرضية (صلبة أو سائلة) تستنتج من قدرة الموجات S على العبور: فإذا عبرت الموجات S تكون الطبقة صلبة، وإذا انعدمت تكون الطبقة سائلة. كما أن سرعة الموجات P تعطي معلومات عن الكثافة والعمق.",
      learningFocus: "الاستنتاج يلخص منهجية: الموجات S تختفي في السوائل، الموجات P تعطي كثافة الطبقة.",
    },
    {
      id: "relationship",
      verbSlug: "relationship",
      n: 4,
      title: "إقامة علاقة",
      skill: "إقامة العلاقات",
      docRef: "الوثيقة 1",
      prompt: "أقم علاقة بين سرعة الموجات P في النواة الداخلية وسرعتها في النواة الخارجية (الوثيقة 1)، واستنتج دلالتها.",
      placeholder: "سرعة الموجات P في النواة الداخلية... بينما في النواة الخارجية... هذا يدل على...",
      modelAnswer: "سرعة الموجات P تزداد من 8 كم/ثا في النواة الخارجية إلى 11 كم/ثا في النواة الداخلية. هذه الزيادة في السرعة تدل على أن النواة الداخلية أكثر كثافة وصلابة من النواة الخارجية، مما يتوافق مع كونها صلبة.",
      learningFocus: "اربط بين زيادة سرعة P وزيادة الكثافة والصلابة.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه بنية الكرة الأرضية الداخلية مستعينا بالوثائق.",
      placeholder: "مقدمة... أولا: القشرة والوشاح... ثانيا: النواة... ثالثا: دور الموجات الزلزالية... خاتمة...",
      modelAnswer: "تتكون الكرة الأرضية من أربع طبقات متباينة الخصائص. أولا، القشرة (0-30 كم) وهي صلبة ذات كثافة 2.7. الوشاح (30-2900 كم) صلب لزج بكثافة 3.3-5.7. النواة الخارجية (2900-5100 كم) سائلة بكثافة 9.9-12.2، والنواة الداخلية (5100-6371 كم) صلبة بكثافة 12.8-13.1 (الوثيقتان 2 و4). تعتمد معرفتنا بهذه البنية على دراسة سرعة الموجات الزلزالية P و S (الوثيقة 1): الموجات S تنعدم في النواة الخارجية دالة على حالتها السائلة، بينما الموجات P تتغير سرعتها حسب كثافة كل طبقة (الوثيقة 3). في الختام، تقدم الموجات الزلزالية أداة غير مباشرة لاستكشاف باطن الأرض.",
      learningFocus: "اجمع بين اسم كل طبقة، عمقها، حالتها الفيزيائية، وكثافتها، مع ربط ذلك بسلوك الموجات الزلزالية.",
    },
  ],
}

const tectonicsGeneralScenario: MethodologyScenario = {
  id: "tectonics-general-v1",
  unitKey: "النشاط التكتوني للصفائح",
  title: "حركة الصفائح التكتونية وآلياتها",
  subtitle: "وضعية تعلمية: النشاط التكتوني للصفائح",
  contextAr: "تتحرك الصفائح التكتونية باستمرار محدثة ظواهر جيولوجية متنوعة. نهدف من خلال هذه الوضعية إلى تحليل آليات هذه الحركة.",
  dominantSkills: ["analyse", "interpret", "compare", "deduce", "hypothesis"],
  documents: [
    {
      type: "bar-chart",
      id: "doc1-plate-speeds",
      title: "الوثيقة 1: سرعات الصفائح التكتونية",
      caption: "معدل سرعة حركة الصفائح التكتونية الرئيسية بالسنتمتر في السنة.",
      xLabel: "الصفائح",
      yLabel: "السرعة",
      unit: "سم/سنة",
      points: [
        { label: "المحيط الهادئ", value: 10 },
        { label: "النازلة", value: 8 },
        { label: "الأسترالية", value: 7 },
        { label: "الإفريقية", value: 2.5 },
        { label: "الأوراسية", value: 2 },
        { label: "الأمريكية", value: 2.5 },
      ],
    },
    {
      type: "flow",
      id: "doc2-plate-movement-mechanism",
      title: "الوثيقة 2: آلية حركة الصفائح",
      caption: "الآليات المسؤولة عن حركة الصفائح التكتونية من تيارات الحمل إلى اندساس الصفائح.",
      steps: ["حرارة باطن الأرض", "تيارات حمل", "تصاعد الصهارة", "حركة الصفائح", "اندساس/توسع"],
      arrows: ["تسخين", "رفع", "دفع", "سحب"],
    },
    {
      type: "table",
      id: "doc3-plate-boundaries",
      title: "الوثيقة 3: أنواع حدود الصفائح",
      columns: ["النوع", "الحركة", "ظاهرة", "مثال"],
      rows: [
        { cells: ["تباعدي", "ابتعاد", "توسع محيطي", "ظهر المحيط الأطلسي"] },
        { cells: ["تقاربي", "اقتراب", "اندساس/تصادم", "جبال الأنديز/الهيمالايا"] },
        { cells: ["تحويلي", "انزلاق", "زلازل", "فالق سان أندرياس"] },
      ],
    },
    {
      type: "image",
      id: "doc4-tectonic-plates-map",
      title: "الوثيقة 4: خريطة الصفائح التكتونية",
      caption: "خريطة تظهر الصفائح التكتونية الرئيسية واتجاهات حركتها.",
      src: tectonicSvg,
      alt: "خريطة العالم تظهر الصفائح التكتونية الرئيسية وحدودها واتجاهات الحركة",
      annotations: [
        { x: 25, y: 24, label: "صفيحة إفريقية", tone: "warning" },
        { x: 56, y: 19, label: "صفيحة أوراسية", tone: "violet" },
        { x: 76, y: 24, label: "صفيحة المحيط الهادئ", tone: "violet" },
        { x: 19, y: 81, label: "صفيحة أمريكية", tone: "warning" },
        { x: 81, y: 81, label: "صفيحة أسترالية", tone: "success" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل الأعمدة البيانية في الوثيقة 1 التي تمثل سرعات الصفائح التكتونية. صنف الصفائح حسب سرعتها.",
      placeholder: "تمثل الأعمدة... نلاحظ تفاوتا في السرعات... أسرع صفيحة... أبطأ صفيحة...",
      modelAnswer: "تمثل الأعمدة البيانية سرعات الصفائح التكتونية. نلاحظ تفاوتا كبيرا في السرعات: أسرعها صفيحة المحيط الهادئ (10 سم/سنة) ثم النازلة (8) والأسترالية (7)، بينما أبطأها الأوراسية (2) والإفريقية والأمريكية (2.5).",
      learningFocus: "اقرأ القيم بدقة. صنف الصفائح: سريعة (محيط هادئ، نازلة، أسترالية) وبطيئة (أوراسية، إفريقية، أمريكية).",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسر اعتمادا على الوثيقتين 2 و3 العلاقة بين تيارات الحمل وحركة الصفائح.",
      placeholder: "تتسبب تيارات الحمل في... حيث الحرارة... تؤدي إلى...",
      modelAnswer: "تتسبب تيارات الحمل الناتجة عن حرارة باطن الأرض (الوثيقة 2) في حركة الصفائح حيث تصعد الصهارة عند الحدود التباعدية مسببة توسعا محيطيا وتغوص عند الحدود التقاربية مسببة اندساسا (الوثيقة 3). هذه الحركات المستمرة تدفع وتسحب الصفائح.",
      learningFocus: "اربط بين الآلية (تيارات الحمل) والنتيجة (حركة الصفائح بأنواعها).",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 3",
      prompt: "قارن بين أنواع حدود الصفائح الثلاثة (تباعدي، تقاربي، تحويلي) اعتمادا على الوثيقة 3.",
      placeholder: "تختلف حدود الصفائح في... الحدود التباعدية... التقاربية... التحويلية...",
      modelAnswer: "تختلف حدود الصفائح في نوع الحركة: التباعدية (ابتعاد) تؤدي إلى توسع محيطي، التقاربية (اقتراب) تؤدي إلى اندساس أو تصادم، والتحويلية (انزلاق) تؤدي إلى زلازل. أمثلة: التباعدي في ظهر الأطلسي، التقاربي في الأنديز، والتحويلي في فالق سان أندرياس.",
      learningFocus: "قارن وفق ثلاثة معايير: الحركة، الظاهرة، المثال.",
    },
    {
      id: "deduce",
      verbSlug: "deduce",
      n: 4,
      title: "صياغة استنتاج",
      skill: "الاستنتاج",
      docRef: "الوثائق 1 و2 و3",
      prompt: "استنتج العلاقة بين سرعة الصفائح (الوثيقة 1) وآلية حركتها (الوثيقة 2) والعوامل المؤثرة.",
      placeholder: "نستنتج أن سرعة حركة الصفائح تعتمد على...",
      modelAnswer: "نستنتج أن سرعة حركة الصفائح تعتمد على شدة تيارات الحمل في باطن الأرض (الوثيقة 2)، حيث تكون الصفائح المرتبطة بتيارات حمل قوية (كصفيحة المحيط الهادئ) أسرع من تلك المرتبطة بتيارات أضعف (كالصفيحة الأوراسية).",
      learningFocus: "اربط بين السرعة (الوثيقة 1) والعامل المسبب (تيارات الحمل في الوثيقة 2).",
    },
    {
      id: "hypothesis",
      verbSlug: "hypothesis",
      n: 5,
      title: "اقتراح فرضية",
      skill: "الفرضيات",
      docRef: "الوثيقة 3",
      prompt: "اعتمادا على الوثيقة 3، اقترح فرضية تفسر وجود الزلازل في مناطق الحدود التحويلية.",
      placeholder: "نفترض أن الزلازل في الحدود التحويلية تنتج عن...",
      modelAnswer: "نفترض أن الزلازل في الحدود التحويلية تنتج عن تراكم الإجهادات الناتجة عن احتكاك الصفيحتين أثناء انزلاقهما في اتجاهين متعاكسين، مما يؤدي إلى تحرير مفاجئ للطاقة على شكل زلازل.",
      learningFocus: "الفرضية تفسر آلية توليد الزلازل: احتكاك ← تراكم إجهادات ← تحرير طاقة.",
    },
  ],
}

const subductionCollisionRidgeScenario: MethodologyScenario = {
  id: "subduction-collision-ridge-v1",
  unitKey: "النشاط التكتوني والبنيات الجيولوجية المرتبطة به",
  title: "الاندساس والتصادم والظهر المحيطي",
  subtitle: "وضعية تعلمية: البنيات الجيولوجية المرتبطة بحركة الصفائح",
  contextAr: "يرتبط النشاط التكتوني بظواهر جيولوجية مختلفة كالاندساس والتصادم. تهدف هذه الوضعية إلى دراسة هذه البنيات.",
  dominantSkills: ["analyse", "interpret", "compare", "relationship", "scientific-text"],
  documents: [
    {
      type: "bar-chart",
      id: "doc1-earthquake-depth",
      title: "الوثيقة 1: توزيع الزلازل حسب العمق في منطقة اندساس",
      caption: "عدد الزلازل المسجلة في منطقة اندساس حسب عمق بؤرتها.",
      xLabel: "العمق (كم)",
      yLabel: "عدد الزلازل",
      unit: "زلزلة",
      points: [
        { label: "0-50", value: 120 },
        { label: "50-100", value: 85 },
        { label: "100-200", value: 60 },
        { label: "200-400", value: 35 },
        { label: "400-700", value: 10 },
      ],
    },
    {
      type: "table",
      id: "doc2-tectonic-structures",
      title: "الوثيقة 2: مقارنة البنيات التكتونية",
      columns: ["الخاصية", "ظهر المحيط", "اندساس", "تصادم"],
      rows: [
        { cells: ["نوع الحدود", "تباعدي", "تقاربي", "تقاربي"] },
        { cells: ["الحركة", "تمدد", "غوص", "رفع"] },
        { cells: ["صهارة", "بازلتية", "أنديزيتية", "غرانيتية"] },
        { cells: ["تشكل", "قشرة محيطية", "خندق+براكين", "سلاسل جبلية"] },
        { cells: ["مثال", "أطلسي", "أنديز", "الهيمالايا"] },
      ],
    },
    {
      type: "flow",
      id: "doc3-plate-fate",
      title: "الوثيقة 3: مصير الصفيحة في منطقة الاندساس",
      caption: "المراحل المتتالية لغوص الصفيحة المحيطية تحت الصفيحة القارية.",
      steps: ["صفيحة محيطية", "اندساس", "غوص في الوشاح", "انصهار جزئي", "صهارة أنديزيتية"],
      arrows: ["غوص", "احتكاك", "انصهار", "صعود"],
    },
    {
      type: "image",
      id: "doc4-subduction-zone-image",
      title: "الوثيقة 4: مقطع يوضح ظاهرة الاندساس",
      caption: "مقطع جيولوجي يبين اندساس الصفيحة المحيطية تحت الصفيحة القارية والبنيات المرافقة.",
      src: subductionSvg,
      alt: "رسم تخطيطي لمقطع في منطقة اندساس يبين الصفيحة المحيطية والقارية والبركان والزلازل",
      annotations: [
        { x: 35, y: 40, label: "صفيحة قارية", tone: "success" },
        { x: 69, y: 40, label: "صفيحة محيطية", tone: "violet" },
        { x: 51, y: 72, label: "اندساس", tone: "warning" },
        { x: 61, y: 58, label: "صهارة", tone: "danger" },
        { x: 69, y: 53, label: "بركان", tone: "danger" },
        { x: 48, y: 57, label: "زلازل", tone: "warning" },
      ],
    },
  ],
  questions: [
    {
      id: "analyse",
      verbSlug: "analyse",
      n: 1,
      title: "تحليل وثيقة",
      skill: "تحليل الوثائق",
      docRef: "الوثيقة 1",
      prompt: "حلل الأعمدة البيانية في الوثيقة 1 التي تمثل توزيع الزلازل حسب العمق في منطقة اندساس. صف التغير.",
      placeholder: "تمثل الأعمدة... نلاحظ أن عدد الزلازل... مع زيادة العمق...",
      modelAnswer: "تمثل الأعمدة البيانية توزيع الزلازل حسب العمق في منطقة اندساس. نلاحظ أن عدد الزلازل يتناقص مع زيادة العمق: 120 زلزلة في 0-50 كم، 85 في 50-100 كم، 60 في 100-200 كم، 35 في 200-400 كم، و10 فقط في 400-700 كم. معظم الزلازل سطحية.",
      learningFocus: "اقرأ الأعمدة: لاحظ التناقص التدريجي لعدد الزلازل مع العمق. معظم النشاط الزلزالي قريب من السطح.",
    },
    {
      id: "interpret",
      verbSlug: "interpret",
      n: 2,
      title: "تفسير نتيجة",
      skill: "التفسير العلمي",
      docRef: "الوثيقتان 2 و3",
      prompt: "فسر اعتمادا على الوثيقتين 2 و3 العلاقة بين اندساس الصفيحة وتشكل الصهارة الأنديزيتية.",
      placeholder: "يؤدي اندساس الصفيحة إلى... حيث تسبب حرارة الوشاح...",
      modelAnswer: "يؤدي اندساس الصفيحة المحيطية (الوثيقة 3) إلى غوصها في الوشاح حيث تتعرض لحرارة وضغط عاليين مما يسبب انصهارا جزئيا للصفيحة والصخور المحيطة، منتجا صهارة أنديزيتية (الوثيقة 2). تصعد هذه الصهارة مكونة براكين مميزة لمناطق الاندساس.",
      learningFocus: "اربط بين مصير الصفيحة (غوص ← انصهار) ونوع الصهارة الناتجة (أنديزيتية).",
    },
    {
      id: "compare",
      verbSlug: "compare",
      n: 3,
      title: "مقارنة",
      skill: "المقارنة",
      docRef: "الوثيقة 2",
      prompt: "قارن بين البنيات التكتونية الثلاثة (ظهر المحيط، اندساس، تصادم) اعتمادا على الوثيقة 2.",
      placeholder: "تختلف البنيات التكتونية الثلاثة في... ظهر المحيط... الاندساس... التصادم...",
      modelAnswer: "تختلف البنيات التكتونية الثلاثة: ظهر المحيط (حدود تباعدية، تمدد، صهارة بازلتية، تشكل قشرة محيطية)، الاندساس (حدود تقاربية، غوص، صهارة أنديزيتية، خندق وبراكين)، التصادم (حدود تقاربية، رفع، صهارة غرانيتية، سلاسل جبلية). أمثلة: أطلسي، أنديز، الهيمالايا.",
      learningFocus: "قارن وفق المعايير: نوع الحدود، الحركة، الصهارة، التشكل، المثال.",
    },
    {
      id: "relationship",
      verbSlug: "relationship",
      n: 4,
      title: "إقامة علاقة",
      skill: "إقامة العلاقات",
      docRef: "الوثيقة 1",
      prompt: "أقم علاقة بين توزيع الزلازل حسب العمق (الوثيقة 1) وعملية اندساس الصفيحة.",
      placeholder: "يرتبط توزيع الزلازل بعملية الاندساس حيث... الزلازل السطحية... والزلازل العميقة...",
      modelAnswer: "يرتبط توزيع الزلازل بمنطقة اندساس الصفيحة حيث تمثل الزلازل السطحية (0-100 كم) منطقة الاحتكاك الأولى بين الصفيحتين، بينما تمثل الزلازل العميقة (100-700 كم) استمرار غوص الصفيحة في الوشاح وتكسرها تحت تأثير الضغط والحرارة. تناقص عدد الزلازل مع العمق يدل على زيادة اللدونة.",
      learningFocus: "اربط بين عمق الزلزال ومرحلة الاندساس: سطحية = احتكاك، عميقة = غوص.",
    },
    {
      id: "scientific-text",
      verbSlug: "scientific-text",
      n: 5,
      title: "نص علمي قصير",
      skill: "النص العلمي",
      docRef: "الوثائق 1 و2 و3 و4",
      prompt: "اكتب نصا علميا تشرح فيه العلاقة بين حركة الصفائح والبنيات الجيولوجية المرتبطة بمناطق الاندساس.",
      placeholder: "مقدمة... أولا: اندساس الصفيحة... ثانيا: البنيات المرافقة... ثالثا: توزيع الزلازل... خاتمة...",
      modelAnswer: "تؤدي حركة الصفائح التكتونية إلى تشكل بنيات جيولوجية مميزة في مناطق الاندساس. أولا، عند تقارب صفيحة محيطية مع قارية، تغوص المحيطية تحت القارية (الوثيقتان 3 و4) مسببة زلازل على أعماق متفاوتة تتناقص مع العمق (الوثيقة 1). ثانيا، يؤدي غوص الصفيحة وانصهارها الجزئي إلى تشكل صهارة أنديزيتية تصعد مكونة براكين (الوثيقة 2). ثالثا، يتميز الاندساس بتشكل خندق محيطي وسلسلة براكين موازية له. في الختام، يعد الاندساس آلية رئيسية في تشكل القشرة القارية وإعادة تدوير القشرة المحيطية.",
      learningFocus: "اجمع بين الزلازل (الوثيقة 1)، البنيات (الوثيقة 2)، آلية الغوص (الوثيقة 3)، والمقطع الجيولوجي (الوثيقة 4).",
    },
  ],
}

export const methodologyScenarios: MethodologyScenario[] = [
  diagnosticScenario,
  proteinStructureFunctionScenario,
  enzymeActivityScenario,
  immunityDefenseScenario,
  nervousCommunicationScenario,
  photosynthesisScenario,
  cellularRespirationScenario,
  ultrastructuralEnergyScenario,
  earthStructureScenario,
  tectonicsGeneralScenario,
  subductionCollisionRidgeScenario,
]

export function getMethodologyScenario(id: string) {
  return methodologyScenarios.find((scenario) => scenario.id === id)
}
