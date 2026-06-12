/* ============================================
   TRANSLATIONS.JS - Multi-language Support
   ============================================ */

const translations = {
  ar: {
    // Navbar
    nav_home: "الرئيسية",
    nav_roadmap: "المحاور",
    nav_transcription: "الاستنساخ",
    nav_code: "الشفرة",
    nav_translation: "الترجمة",
    nav_fate: "المصير",
    nav_dashboard: "لوحتي 📊",
    
    // Hero
    hero_badge: "📚 الوحدة الأولى | السنة الثالثة ثانوي",
    hero_title_1: "رحلة داخل الخلية",
    hero_title_2: "كيف يُصنع البروتين؟",
    hero_desc: "اكتشف الأسرار الجزيئية لتركيب البروتين من الـ ADN إلى الوظيفة، بأسلوب علمي ممتع ومبسّط وفق منهاج البكالوريا الجزائري.",
    hero_btn_start: "ابدأ الرحلة ↓",
    hero_btn_code: "🔤 جدول الشفرة",
    
    // Roadmap
    roadmap_title: "خريطة الرحلة العلمية",
    roadmap_desc: "خمسة محاور تأخذك خطوة بخطوة لفهم تركيب البروتين",
    
    // Sections
    concept: "💡 المفهوم العام",
    requirements: "🔬 المتطلبات",
    stages: "📊 المراحل",
    did_you_know: "هل تعلم؟",
    bac_corner: "🎯 ما يطلبه منهاج BAC",
    quiz_title: "🧪 اختبر معلوماتك",
    quiz_desc: "أجب على الأسئلة التالية لتقييم فهمك"
  },
  
  fr: {
    nav_home: "Accueil",
    nav_roadmap: "Chapitres",
    nav_transcription: "Transcription",
    nav_code: "Code Génétique",
    nav_translation: "Traduction",
    nav_fate: "Destin",
    nav_dashboard: "Tableau 📊",
    
    hero_badge: "📚 Unité 1 | 3ème Année Secondaire",
    hero_title_1: "Voyage dans la cellule",
    hero_title_2: "Comment fabrique-t-on les protéines?",
    hero_desc: "Découvrez les secrets moléculaires de la synthèse protéique, de l'ADN à la fonction, dans un style scientifique passionnant adapté au programme BAC algérien.",
    hero_btn_start: "Commencer ↓",
    hero_btn_code: "🔤 Code Génétique",
    
    roadmap_title: "Carte du Parcours Scientifique",
    roadmap_desc: "Cinq chapitres pour comprendre la synthèse des protéines",
    
    concept: "💡 Concept Général",
    requirements: "🔬 Conditions Requises",
    stages: "📊 Les Étapes",
    did_you_know: "Le saviez-vous?",
    bac_corner: "🎯 Exigences du BAC",
    quiz_title: "🧪 Testez vos connaissances",
    quiz_desc: "Répondez aux questions pour évaluer votre compréhension"
  },
  
  en: {
    nav_home: "Home",
    nav_roadmap: "Chapters",
    nav_transcription: "Transcription",
    nav_code: "Genetic Code",
    nav_translation: "Translation",
    nav_fate: "Fate",
    nav_dashboard: "Dashboard 📊",
    
    hero_badge: "📚 Unit 1 | 3rd Year Secondary",
    hero_title_1: "Journey Inside the Cell",
    hero_title_2: "How are Proteins Made?",
    hero_desc: "Discover the molecular secrets of protein synthesis, from DNA to function, in an exciting scientific style adapted to the Algerian BAC curriculum.",
    hero_btn_start: "Start Journey ↓",
    hero_btn_code: "🔤 Genetic Code",
    
    roadmap_title: "Scientific Journey Map",
    roadmap_desc: "Five chapters to understand protein synthesis",
    
    concept: "💡 General Concept",
    requirements: "🔬 Requirements",
    stages: "📊 Stages",
    did_you_know: "Did you know?",
    bac_corner: "🎯 BAC Requirements",
    quiz_title: "🧪 Test Your Knowledge",
    quiz_desc: "Answer the questions to assess your understanding"
  }
};

(function() {
  'use strict';
  
  let currentLang = localStorage.getItem('lang') || 'ar';
  
  window.switchLanguage = function(lang) {
    if (!translations[lang]) return;
    
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    // Update HTML attributes
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[lang][key]) {
        el.textContent = translations[lang][key];
      }
    });
    
    // Update active state on language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  };
  
  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    switchLanguage(currentLang);
  });
})();
