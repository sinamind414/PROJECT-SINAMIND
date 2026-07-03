export const QUOTES_SUCCESS_AR = [
  { text: "برافو ! راك تولي محترف الأفعال", emoji: "🏆" },
  { text: "تبارك الله عليك، استمر!", emoji: "🌟" },
  { text: "راك في الطريق الصحيح", emoji: "🚀" },
  { text: "ماشاء الله، نتيجة ممتازة", emoji: "✨" },
  { text: "هذا هو المستوى، كمّل هكذا!", emoji: "💪" },
  { text: "ممتاز، راك تفهم الدرس!", emoji: "🎓" },
  { text: "برافو، البكالوريا مالك!", emoji: "🎯" },
  { text: "نتيجة باهية، استمر على هالمستوى!", emoji: "🔥" },
  { text: "ماشاء الله عليك، تتطور بزاف!", emoji: "📈" },
  { text: "أحسنت، راك في القمة!", emoji: "👑" },
  { text: "نتيجة رائعة، فخورين بيك!", emoji: "🎉" },
  { text: "برافو، هاذي هي الروح!", emoji: "⭐" },
  { text: "ممتاز بزاف، كمّل!", emoji: "💎" },
  { text: " Rak maher, c'est ça la méthode!", emoji: "🧠" },
  { text: "ماشاء الله، عقلك شغال!", emoji: "💡" },
  { text: "هذا الإنجاز، راك تستاهل!", emoji: "🏅" },
  { text: "برافو، البكالوريا تتسنى ليك!", emoji: "📝" },
  { text: "ممتاز، راك تتقدم!", emoji: "🌊" },
  { text: "تبارك الله، نتيجة باهية بزاف!", emoji: "🎊" },
  { text: "Rien ne t'arrête,继续!", emoji: "🏁" },
]

export const QUOTES_FAILURE_AR = [
  { text: "كاش حاجة، نكملو غدا إن شاء الله", emoji: "💪" },
  { text: "هاذ المرة ما مشاتش، المراجعة الجاية أحسن", emoji: "🔄" },
  { text: "كل خطأ هو درس، راك تتقدم", emoji: "📚" },
  { text: "ما تقلقش، المرة الجاية غادي تflix", emoji: "😤" },
  { text: "هذا عادي، المهم تعاود تحاول", emoji: "🔁" },
  { text: "خطوة للوراء، خطتين للقدام!", emoji: "🐾" },
  { text: "ما نجحوش من أول مرة، المهم نتعلمو", emoji: "📖" },
  { text: "هذا مشكيل، حلو بمرجعة!", emoji: "🧩" },
  { text: "Rien n'est perdu, on reprend!", emoji: "🔄" },
  { text: "استمر، النجاح قريب إن شاء الله!", emoji: "🌟" },
  { text: "ما تحملش على راسك، تعلم وبس!", emoji: "🎓" },
  { text: "هذا التدريب غادي يflixك فالبكالوريا!", emoji: "📝" },
  { text: "كل محاولة هي خطوة للنجاح", emoji: "👣" },
  { text: "ما تنساش: المراجعة هي السر!", emoji: "🔑" },
  { text: "Hata hna, c'est pas grave!", emoji: "😅" },
  { text: "المهم تفهم الغلطة، ماشي تحفظ!", emoji: "🧠" },
  { text: "غدا نكملو بقوة!", emoji: "⚡" },
  { text: "الصبر مفتاح الفرج، كمّل!", emoji: "🗝️" },
  { text: "ما تحبطش، راك أحسن مما تتصور!", emoji: "💫" },
  { text: "C'est pas grave, tu vas y arriver!", emoji: "🌈" },
]

export function pickRandomQuote(success: boolean) {
  const pool = success ? QUOTES_SUCCESS_AR : QUOTES_FAILURE_AR
  return pool[Math.floor(Math.random() * pool.length)]
}
