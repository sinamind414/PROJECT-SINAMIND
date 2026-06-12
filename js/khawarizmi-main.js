/* ============================================
   KHAWARIZMI MAIN JS - PREMIUM PLATFORM INTERACTIVITY
   ============================================ */

const translations = {
  ar: {
    nav_home: "الرئيسية",
    nav_features: "المميزات",
    nav_pricing: "الأسعار",
    nav_about: "من نحن",
    nav_contact: "اتصل بنا",
    btn_login: "دخول",
    btn_signup: "ابدأ مجاناً",
    hero_badge: "🇩🇿 الأولى من نوعها في الجزائر",
    hero_title_line_1: "خوارزميتك",
    hero_title_line_2: "للنجاح في البكالوريا",
    hero_cta_start: "ابدأ مجاناً الآن",
    hero_cta_demo: "تصفح المحاضرات",
    stat_students: "طالب نشط",
    stat_satisfaction: "نسبة الرضا",
    stat_available: "IA متاحة",
    scroll_more: "اكتشف المزيد",
    trust_text: "✨ معتمد من قبل أكثر من 5000 طالب في الجزائر",
    trust_1: "🏆 #1 في الجزائر",
    trust_dz: "🇩🇿 صنع في الجزائر",
    features_tag: "✨ المميزات",
    features_title: "لماذا خوارزمي IA ؟",
    features_subtitle: "5 مميزات ثورية لمساعدتك في النجاح",
    tag_new: "جديد",
    f1_title: "أستاذ خوارزمي IA",
    f1_desc: "مساعد ذكي متاح 24/7 يجيب على جميع أسئلتك في علوم الطبيعة والحياة، باللغة العربية والفرنسية.",
    f1_bullet_1: "✓ إجابات فورية",
    f1_bullet_2: "✓ شرح مبسط",
    f1_bullet_3: "✓ توليد اختبارات",
    learn_more: "اكتشف المزيد ←",
    f2_title: "المراجعة الذكية FSRS",
    f2_desc: "نظام مراجعة علمي مبني على خوارزمية FSRS لتذكر المعلومات على المدى الطويل.",
    f2_bullet_1: "✓ تذكر دائم",
    f2_bullet_2: "✓ توقيت مثالي",
    f2_bullet_3: "✓ تخصيص حسب مستواك",
    f3_title: "خريطة المفاهيم",
    f3_desc: "تصور بياني تفاعلي يربط جميع مفاهيم البرنامج، لفهم أعمق للعلاقات بين الدروس.",
    f3_bullet_1: "✓ رؤية شاملة",
    f3_bullet_2: "✓ روابط ذكية",
    f3_bullet_3: "✓ تنقل سلس",
    f4_title: "يعمل بدون إنترنت",
    f4_desc: "حمّل الدروس مرة واحدة واستعملها في أي مكان، حتى بدون اتصال بالإنترنت.",
    f4_bullet_1: "✓ تطبيق PWA",
    f4_bullet_2: "✓ مزامنة تلقائية",
    f4_bullet_3: "✓ سرعة فائقة",
    f5_title: "تحدّيات وألعاب",
    f5_desc: "تعلّم وأنت تستمتع! تحدّ أصدقاءك واصعد في الترتيب الوطني للطلاب.",
    f5_bullet_1: "✓ ترتيب وطني",
    f5_bullet_2: "✓ تحديات يومية",
    f5_bullet_3: "✓ مكافآت حصرية",
    f6_title: "100% جزائري",
    f6_desc: "محتوى مصمم خصيصاً للمنهاج الجزائري، مع أمثلة من المواضيع السابقة للبكالوريا.",
    f6_bullet_1: "✓ منهاج الجزائر",
    f6_bullet_2: "✓ بكالوريا سابقة",
    f6_bullet_3: "✓ دعم عربي/فرنسي",
    pricing_tag: "💎 الأسعار",
    pricing_title: "اختر الباقة المناسبة لك",
    pricing_subtitle: "ابدأ مجاناً، ترقَّ متى أردت",
    plan_free_title: "الطالب",
    plan_free_period: "/ مجاناً",
    plan_free_desc: "للبدء واكتشاف المنصة",
    free_feat_1: "✓ وحدة واحدة كاملة",
    free_feat_2: "✓ 5 أسئلة IA يومياً",
    free_feat_3: "✓ اختبارات أساسية",
    free_feat_4: "✗ مراجعة FSRS",
    free_feat_5: "✗ خريطة المفاهيم",
    free_feat_6: "✗ الترتيب الوطني",
    free_feat_7: "✗ الوضع غير المتصل",
    free_cta: "ابدأ مجاناً",
    badge_popular: "🏆 الأكثر شعبية",
    plan_pro_title: "الباكلوري",
    plan_pro_period: "/ سنوياً",
    plan_pro_desc: "للنجاح في البكالوريا",
    pro_feat_1: "✓ كل برنامج علوم الطبيعة",
    pro_feat_2: "✓ أستاذ IA غير محدود",
    pro_feat_3: "✓ مراجعة FSRS ذكية",
    pro_feat_4: "✓ خريطة المفاهيم الكاملة",
    pro_feat_5: "✓ الترتيب الوطني",
    pro_feat_6: "✓ الوضع غير المتصل",
    pro_feat_7: "✓ بكالوريا سابقة محلولة",
    pro_feat_8: "✓ دعم أولوية",
    pro_cta: "🚀 اشترك الآن",
    trial_desc: "14 يوماً تجربة مجانية",
    plan_school_title: "المدرسة",
    plan_school_price: "حسب الطلب",
    plan_school_desc: "للمؤسسات التعليمية",
    school_feat_1: "✓ جميع مميزات الباقة الفردية",
    school_feat_2: "✓ لوحة تحكم للأستاذ",
    school_feat_3: "✓ متابعة كل طالب",
    school_feat_4: "✓ تقارير شهرية",
    school_feat_5: "✓ تكوين الأساتذة",
    school_feat_6: "✓ خصم على الكمية",
    school_feat_7: "✓ دعم مخصص",
    school_cta: "اتصل بنا",
    payment_methods_text: "💳 طرق الدفع المتاحة:",
    bank_transfer: "تحويل بنكي",
    about_tag: "📖 قصتنا",
    about_title: "من هو الخوارزمي ؟",
    about_intro: "محمد بن موسى الخوارزمي، عالم رياضيات وفلكي، يُعتبر الأب الروحي للجبر والخوارزميات.",
    about_desc_para: "من اسمه استُلهمت كلمة \"Algorithme\" التي تُشغّل اليوم الذكاء الاصطناعي. نحن في خوارزمي IA، نواصل إرثه: توظيف العلم في خدمة التعليم.",
    val1_title: "رسالتنا",
    val1_desc: "تمكين كل طالب جزائري من النجاح في البكالوريا",
    val2_title: "رؤيتنا",
    val2_desc: "أن نصبح المنصة #1 للتعليم الذكي في شمال إفريقيا",
    val3_title: "قيمنا",
    val3_desc: "الإبتكار، الجودة، الحرص على نجاح كل طالب",
    cta_title: "جاهز لتغيير طريقة دراستك ؟",
    cta_subtitle: "انضم إلى آلاف الطلاب الذين يستعدون لبكالوريا 2026 مع خوارزمي IA",
    cta_start_free: "🚀 ابدأ مجاناً الآن",
    cta_browse_lessons: "📖 تصفح الدروس والمحاضرات",
    cta_note: "✨ بدون بطاقة ائتمان | إلغاء في أي وقت",
    footer_desc: "منصة الذكاء الاصطناعي الأولى لطلاب البكالوريا الجزائريين في علوم الطبيعة والحياة.",
    foot_col1_title: "المنصة",
    foot_col2_title: "الشركة",
    foot_col3_title: "الدعم",
    nav_lessons: "الدروس",
    nav_annales: "بكالوريا سابقة",
    nav_blog: "المدونة",
    nav_jobs: "الوظائف",
    nav_partners: "الشركاء",
    nav_help: "مركز المساعدة",
    nav_faq: "الأسئلة الشائعة",
    nav_terms: "شروط الاستخدام",
    footer_copyright: "© 2025 خوارزمي IA. صنع بـ ❤️ في الجزائر 🇩🇿",
    legal_privacy: "سياسة الخصوصية",
    legal_terms: "شروط الاستخدام",
    legal_cookies: "سياسة ملفات التعريف"
  },
  fr: {
    nav_home: "Accueil",
    nav_features: "Fonctionnalités",
    nav_pricing: "Tarifs",
    nav_about: "À Propos",
    nav_contact: "Contact",
    btn_login: "Connexion",
    btn_signup: "Démarrer",
    hero_badge: "🇩🇿 Première en son genre en Algérie",
    hero_title_line_1: "Votre Khawarizmi",
    hero_title_line_2: "Pour réussir le BAC",
    hero_cta_start: "Démarrer gratuitement",
    hero_cta_demo: "Découvrir les cours",
    stat_students: "Élèves actifs",
    stat_satisfaction: "Taux de satisfaction",
    stat_available: "IA disponible",
    scroll_more: "Découvrir plus",
    trust_text: "✨ Approuvé par plus de 5000 élèves en Algérie",
    trust_1: "🏆 N°1 en Algérie",
    trust_dz: "🇩🇿 Fait en Algérie",
    features_tag: "✨ Fonctionnalités",
    features_title: "Pourquoi Khawarizmi IA ?",
    features_subtitle: "5 fonctionnalités révolutionnaires pour votre réussite",
    tag_new: "Nouveau",
    f1_title: "Professeur Khawarizmi IA",
    f1_desc: "Un assistant intelligent disponible 24h/24 et 7j/7 pour répondre à toutes vos questions en sciences, en arabe et en français.",
    f1_bullet_1: "✓ Réponses instantanées",
    f1_bullet_2: "✓ Explications simplifiées",
    f1_bullet_3: "✓ Génération de tests",
    learn_more: "En savoir plus ←",
    f2_title: "Révision intelligente FSRS",
    f2_desc: "Un système de révision scientifique basé sur l'algorithme FSRS pour mémoriser à long terme.",
    f2_bullet_1: "✓ Mémorisation durable",
    f2_bullet_2: "✓ Timing idéal",
    f2_bullet_3: "✓ Personnalisé à votre niveau",
    f3_title: "Carte des concepts",
    f3_desc: "Une visualisation graphique interactive qui relie tous les concepts du programme.",
    f3_bullet_1: "✓ Vision globale",
    f3_bullet_2: "✓ Liens intelligents",
    f3_bullet_3: "✓ Navigation fluide",
    f4_title: "Fonctionne hors-ligne",
    f4_desc: "Téléchargez les cours une fois et accédez-y partout, même sans connexion.",
    f4_bullet_1: "✓ Application PWA",
    f4_bullet_2: "✓ Synchronisation auto",
    f4_bullet_3: "✓ Rapidité extrême",
    f5_title: "Défis et jeux",
    f5_desc: "Apprenez en vous amusant ! Défiez vos amis et montez dans le classement national.",
    f5_bullet_1: "✓ Classement national",
    f5_bullet_2: "✓ Défis quotidiens",
    f5_bullet_3: "✓ Récompenses exclusives",
    f6_title: "100% algérien",
    f6_desc: "Un contenu conçu spécifiquement pour le programme de l'éducation nationale algérienne.",
    f6_bullet_1: "✓ Programme officiel",
    f6_bullet_2: "✓ Annales corrigées",
    f6_bullet_3: "✓ Support bilingue",
    pricing_tag: "💎 Tarifs",
    pricing_title: "Choisissez votre forfait",
    pricing_subtitle: "Commencez gratuitement, passez Pro quand vous voulez",
    plan_free_title: "Élève",
    plan_free_period: "/ Gratuit",
    plan_free_desc: "Pour débuter et explorer la plateforme",
    free_feat_1: "✓ 1 module complet",
    free_feat_2: "✓ 5 questions d'IA par jour",
    free_feat_3: "✓ Quiz de base",
    free_feat_4: "✗ Révision FSRS",
    free_feat_5: "✗ Carte des concepts",
    free_feat_6: "✗ Classement national",
    free_feat_7: "✗ Mode hors-ligne",
    free_cta: "Démarrer gratuitement",
    badge_popular: "🏆 Le plus populaire",
    plan_pro_title: "Bachelier",
    plan_pro_period: "/ An",
    plan_pro_desc: "Pour assurer votre réussite au BAC",
    pro_feat_1: "✓ Programme complet de SVT",
    pro_feat_2: "✓ Professeur IA illimité",
    pro_feat_3: "✓ Révision FSRS intelligente",
    pro_feat_4: "✓ Carte des concepts complète",
    pro_feat_5: "✓ Classement national actif",
    pro_feat_6: "✓ Mode hors-ligne complet",
    pro_feat_7: "✓ Annales du BAC résolues",
    pro_feat_8: "✓ Support prioritaire",
    pro_cta: "🚀 Souscrire",
    trial_desc: "Essai gratuit de 14 jours",
    plan_school_title: "École",
    plan_school_price: "Sur devis",
    plan_school_desc: "Pour les établissements scolaires",
    school_feat_1: "✓ Toutes les fonctionnalités Pro",
    school_feat_2: "✓ Tableau de bord enseignant",
    school_feat_3: "✓ Suivi individuel des élèves",
    school_feat_4: "✓ Rapports mensuels",
    school_feat_5: "✓ Formation des professeurs",
    school_feat_6: "✓ Tarif dégressif de groupe",
    school_feat_7: "✓ Support dédié et prioritaire",
    school_cta: "Nous contacter",
    payment_methods_text: "💳 Moyens de paiement disponibles :",
    bank_transfer: "Virement bancaire",
    about_tag: "📖 Notre histoire",
    about_title: "Qui est Al-Khwarizmi ?",
    about_intro: "Al-Khwarizmi, grand mathématicien et astronome, est le père fondateur de l'algèbre.",
    about_desc_para: "C'est de son nom qu'est dérivé le mot \"Algorithme\", moteur de l'intelligence artificielle. Chez Khawarizmi IA, nous perpétuons son héritage au service de la réussite scolaire.",
    val1_title: "Notre Mission",
    val1_desc: "Permettre à chaque élève algérien de briller au BAC",
    val2_title: "Notre Vision",
    val2_desc: "Devenir le N°1 de l'éducation intelligente en Afrique du Nord",
    val3_title: "Nos Valeurs",
    val3_desc: "Innovation, qualité, engagement total pour l'élève",
    cta_title: "Prêt à transformer vos révisions ?",
    cta_subtitle: "Rejoignez des milliers de bacheliers qui préparent le BAC 2026",
    cta_start_free: "🚀 Commencer gratuitement",
    cta_browse_lessons: "📖 Accéder aux cours",
    cta_note: "✨ Sans carte bancaire | Annulation libre",
    footer_desc: "La première plateforme d'IA pour les bacheliers algériens en sciences naturelles.",
    foot_col1_title: "Plateforme",
    foot_col2_title: "Entreprise",
    foot_col3_title: "Support",
    nav_lessons: "Cours",
    nav_annales: "Annales",
    nav_blog: "Blog",
    nav_jobs: "Recrutement",
    nav_partners: "Partenaires",
    nav_help: "Centre d'aide",
    nav_faq: "FAQ",
    nav_terms: "Conditions",
    footer_copyright: "© 2025 Khawarizmi IA. Fait avec ❤️ en Algérie 🇩🇿",
    legal_privacy: "Confidentialité",
    legal_terms: "Conditions",
    legal_cookies: "Cookies"
  }
};

(function() {
  'use strict';
  
  // 1. Scrolled navbar effect
  const navbar = document.querySelector('.navbar-premium');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // 2. Mobile Menu Toggle
  const menuToggle = document.getElementById('menuToggle');
  const navMenu = document.getElementById('navMenu');
  
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      menuToggle.textContent = navMenu.classList.contains('active') ? '✕' : '☰';
    });
    
    // Close mobile menu on nav link click
    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        menuToggle.textContent = '☰';
      });
    });
  }

  // 3. Floating Gold Particles Generator
  const particleContainer = document.getElementById('goldParticles');
  if (particleContainer) {
    const particleCount = 25;
    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.style.position = 'absolute';
      particle.style.background = 'radial-gradient(circle, var(--gold-light) 0%, transparent 70%)';
      particle.style.borderRadius = '50%';
      
      const size = Math.random() * 8 + 4;
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;
      
      particle.style.top = `${Math.random() * 100}%`;
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.opacity = Math.random() * 0.4 + 0.1;
      
      // Floating animation values
      const delay = Math.random() * 5;
      const duration = Math.random() * 8 + 6;
      particle.style.animation = `float-particle ${duration}s infinite ease-in-out ${delay}s`;
      
      particleContainer.appendChild(particle);
    }
  }

  // Particle Keyframe Injection
  const styleSheet = document.createElement("style");
  styleSheet.type = "text/css";
  styleSheet.innerText = `
    @keyframes float-particle {
      0%, 100% { transform: translate(0, 0); }
      50% { transform: translate(${Math.random() * 40 - 20}px, -${Math.random() * 60 + 20}px); }
    }
  `;
  document.head.appendChild(styleSheet);

  // 4. Language switching system
  let currentLang = localStorage.getItem('lang') || 'ar';
  
  window.switchLanguage = function(lang) {
    if (!translations[lang]) return;
    
    currentLang = lang;
    localStorage.setItem('lang', lang);
    
    // Update HTML attributes
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    
    // Update all elements with data-i18n attributes
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (translations[lang][key]) {
        el.textContent = translations[lang][key];
      }
    });

    // Special subtitle update to keep structural styling
    const heroSubtitle = document.getElementById('heroSubtitle');
    if (heroSubtitle) {
      if (lang === 'ar') {
        heroSubtitle.innerHTML = `
          منصة الذكاء الاصطناعي الأولى لطلاب البكالوريا الجزائريين في علوم الطبيعة والحياة.
          <br>
          <span class="subtitle-fr">La première plateforme d'IA pour le BAC Sciences Naturelles</span>
        `;
      } else {
        heroSubtitle.innerHTML = `
          La première plateforme d'IA en Algérie pour préparer le BAC en Sciences Naturelles.
          <br>
          <span class="subtitle-fr" style="font-family: var(--font-ar); font-style: normal; font-size: 1rem;">المنصة الأولى للذكاء الاصطناعي لتحضير بكالوريا العلوم</span>
        `;
      }
    }
    
    // Update active class on buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.lang === lang);
    });
  };

  // Bind language buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      switchLanguage(btn.dataset.lang);
    });
  });
  
  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    switchLanguage(currentLang);
  });
})();
