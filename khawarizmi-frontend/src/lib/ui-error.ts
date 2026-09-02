import { UI_AR } from "./translations"

/**
 * Un message d'erreur à mettre devant un élève — une seule fois, au bon endroit.
 *
 * Le problème mesuré (rapport §13) : huit pages faisaient `setError(e.message)` ou
 * `setError(String(e))`. Depuis F20, le client remonte enfin le message du serveur — donc ce
 * chemin affiche correctement l'arabe quand il existe. Mais dès que le serveur ne parle pas
 * (panic réseau, `Failed to fetch`, page HTML de porte d'entrée, `SyntaxError` d'un corps non JSON,
 * message technique français), l'élève arabe RTL lit une chaîne d'ingénieur. Sur un site dont la
 * promesse est « ta copie est corrigée », `Unexpected token 'O'…` se lit comme : *ta réponse est
 * invalide*. C'est exactement le contre-sens à supprimer.
 *
 * Ordre de priorité — dans cet ordre, et pas un autre :
 *   1. le message du serveur, quand il est déjà en arabe (il est plus précis que n'importe quelle
 *      formule générique, et c'est lui qui explique quoi refaire) ;
 *   2. le statut HTTP, quand il est connu (401 session, 404 indisponible, 429 limite, 5xx panne) ;
 *   3. les pannes locales reconnaissables (réseau, délai, corps illisible) ;
 *   4. un repli arabe — jamais le texte brut, jamais le HTML, jamais une chaîne française.
 */

const ARABIC_SCRIPT = /[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]/
/** Marqueurs d'une chaîne technique qu'il ne faut PAS montrer à un élève. */
const TECHNICAL = [
  /not valid JSON/i,
  /unexpected (token|end of input|data)/i,
  /^\s*<(!doctype|html|\?xml)/i,
  /failed to fetch|networkerror|err_network|net::/i,
  /cannot read propert|is not a function|undefined is not/i,
  /\bhttps?:\/\/\S+/i,
]

const LONG_ARABIC_MAX = 240

/** `Error: …` / `TypeError: …` : le nom du type n'est pas une information pour l'élève. */
function bareMessage(error: unknown): string {
  const raw =
    error instanceof Error
      ? error.message
      : typeof error === "string"
        ? error
        : error && typeof error === "object" && "message" in error
          ? String((error as { message?: unknown }).message ?? "")
          : ""
  return raw.replace(/^\w*Error:\s*/, "").trim()
}

function httpStatus(error: unknown): number | null {
  if (error && typeof error === "object" && "status" in error) {
    const s = (error as { status?: unknown }).status
    if (typeof s === "number" && s >= 100 && s <= 599) return s
  }
  return null
}

export function readableError(error: unknown, fallback?: string): string {
  const message = bareMessage(error)

  // 1. Le serveur a parlé arabe : on le garde, c'est le seul à savoir quoi réparer.
  if (message && ARABIC_SCRIPT.test(message) && message.length <= LONG_ARABIC_MAX) return message

  // 2. Un statut connu vaut une phrase exacte plutôt qu'un « خطأ 500 » comptable.
  const status = httpStatus(error)
  if (status === 401) return "انتهت الجلسة. سجّل الدخول من جديد للمتابعة."
  if (status === 403) return "هذه الصفحة مخصصة لحساب مفعّل. أعد تسجيل الدخول أو راجع حسابك."
  if (status === 404) return "هذا المحتوى غير متوفر على الخادم بعد."
  if (status === 429) return UI_AR.limite_atteinte
  if (status !== null && status >= 500) return "الخادم غير متاح حاليا. حاول بعد قليل — المشكلة ليست في إجابتك."

  // 3. Pannes reconnaissables côté navigateur.
  if (/timeout|timed out|مهلة/i.test(message)) return "انتهت مهلة الانتظار. أعد المحاولة."
  if (/abort/i.test(message)) return "تم إيقاف الطلب. أعد المحاولة عند الرغبة."
  if (/failed to fetch|networkerror|err_network|net::|load failed/i.test(message)) {
    return "تعذر الاتصال بالخادم. تحقق من اتصالك بالإنترنت ثم أعد المحاولة."
  }
  if (/not valid json|unexpected token/i.test(message)) return UI_AR.reponse_illisible

  // 4. Repli — et on ne remonte JAMAIS une chaîne technique brute.
  if (!message || TECHNICAL.some((re) => re.test(message))) {
    return fallback || UI_AR.erreur_chargement || "تعذر تحميل البيانات. أعد المحاولة."
  }
  // Message non arabe, non reconnu (vieux texte français d'une page, log d'une lib) : il n'a
  // rien à faire à l'écran. Le fallback reste plus utile qu'un texte que l'élève ne lit pas.
  return fallback || UI_AR.erreur_chargement || "تعذر تحميل البيانات. أعد المحاولة."
}
