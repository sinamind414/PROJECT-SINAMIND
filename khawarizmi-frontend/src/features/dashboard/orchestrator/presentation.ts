import type { OrientationRecommendation } from "@/lib/types"

export function getUrgencyBadge(urgency?: OrientationRecommendation["niveau_urgence"]) {
  if (urgency === "critique") {
    return {
      label: "عاجل جداً",
      className: "bg-red-500/15 text-red-400 border border-red-500/30",
    }
  }

  if (urgency === "haute") {
    return {
      label: "أولوية عالية",
      className: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    }
  }

  return {
    label: "أولوية عادية",
    className: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
  }
}

export function getNeedBadge(nature?: OrientationRecommendation["nature_besoin"]) {
  switch (nature) {
    case "memoire":
      return "🧠 تثبيت الذاكرة"
    case "bac":
      return "🎯 ربح نقاط BAC"
    case "methodologie":
      return "📝 مهارة منهجية"
    case "structure":
      return "🗺️ إعادة تنظيم الفصل"
    default:
      return "📌 حاجة غير محددة"
  }
}

export function getSourceBadge(source?: OrientationRecommendation["moteur_source_principal"]) {
  switch (source) {
    case "flashcards":
      return "FSRS"
    case "document_analysis":
      return "DOC"
    case "mindmap":
      return "MINDMAP"
    case "action_verbs":
      return "VERBES"
    default:
      return "SAD"
  }
}

export function getImpactBadge(impact?: OrientationRecommendation["impact_note_estime"]) {
  if (impact === "fort") {
    return {
      label: "ربح نقاط قوي",
      className: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
    }
  }

  if (impact === "moyen") {
    return {
      label: "ربح نقاط متوسط",
      className: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
    }
  }

  return {
    label: "ربح نقاط محدود",
    className: "bg-slate-500/15 text-slate-300 border border-slate-500/30",
  }
}
