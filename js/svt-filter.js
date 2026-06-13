const SVTFilter = {

  offTopicPatterns: [
    /\d+\s*[\+\-\*\/\×\÷]\s*\d+/,
    /^combien\s+(fait|font|égale)/i,
    /^كم\s+(يساوي|تساوي|يعمل)/,
    /^(calcule|calculer|calculez)\s+\d/i,
    /^(احسب|حساب)\s+\d/,
    /^(résous|résoudre|حل)\s+(l'équation|المعادلة)/i,
    /^(code|programme|programmation|html|css|javascript|python|java|php)/i,
    /^(كود|برمجة|تصميم موقع)/,
    /^(recette|طبخ|وصفة طبخ|كيف اطبخ)/i,
    /^(score|نتيجة مباراة|كرة قدم|ملعب)/,
    /^(film|مسلسل|أغنية|chanson|musique|موسيقى)/i,
    /^(رئيس|انتخابات|سياسة|politique|élection)/i,
    /^(فتوى|حلال|حرام|صلاة|fatwa)/i,
    /^(اكتب لي رسالة|اكتب لي قصة|write me|écris-moi)/i,
    /^(ترجم|translate)\s+(من|from)\s+(الانجليزية|anglais|english)/i,
    /^(طقس|météo|weather|أخبار|actualités|news)/i
  ],

  svtGuaranteed: [
    'خلية', 'خلايا', 'نواة', 'غشاء', 'سيتوبلازم', 'هيولى',
    'عضية', 'ميتوكوندري', 'ريبوزوم', 'غولجي', 'شبكة هيولية',
    'adn', 'arn', 'arnm', 'arnt', 'arnr', 'dna', 'rna',
    'مورثة', 'جين', 'صبغي', 'كروموزوم', 'نيوكليوتيد',
    'استنساخ', 'ترجمة', 'رامزة', 'كودون', 'بروتين',
    'حمض أميني', 'طفرة', 'وراثة', 'حليل',
    'مناعة', 'لمفاوية', 'جسم مضاد', 'مولد ضد', 'بلعمة',
    'التهاب', 'فيروس', 'بكتيريا', 'لقاح', 'تطعيم',
    'سيدا', 'vih', 'sida', 'مناعي',
    'عصبون', 'عصب', 'دماغ', 'مشبك', 'سيناب',
    'كمون', 'استقطاب', 'ناقل عصبي', 'محور',
    'دوبامين', 'أسيتيل كولين', 'مخدرات',
    'تركيب ضوئي', 'تنفس خلوي', 'كلوروفيل',
    'صانعة خضراء', 'ثايلاكويد', 'ستروما',
    'كريبس', 'تحلل سكري', 'غلوكوز',
    'atp', 'nadh', 'nadph', 'تخمر',
    'إنزيم', 'ركيزة', 'موقع فعال', 'تحفيز',
    'صفيحة', 'تكتونية', 'زلزال', 'بركان',
    'ظهرة', 'غوص', 'تصادم', 'قشرة أرضية',
    'معطف', 'بازلت', 'غرانيت', 'أوفيوليت',
    'protéine', 'proteine', 'cellule', 'enzyme',
    'immunité', 'immunite', 'neurone', 'synapse',
    'photosynthèse', 'photosynthese', 'respiration',
    'mitochondrie', 'chloroplaste', 'ribosome',
    'transcription', 'traduction', 'translation',
    'tectonique', 'plaque', 'séisme', 'seisme',
    'subduction', 'dorsale', 'ophiolite',
    'biologie', 'svt', 'génétique', 'genetique',
    'بكالوريا', 'باك', 'bac', 'programme',
    'علوم طبيعية', 'علوم الحياة', 'درس', 'فصل',
    'وحدة', 'مجال', 'منهاج'
  ],

  greetings: [
    'سلام', 'مرحبا', 'اهلا', 'صباح', 'مساء',
    'hello', 'hi', 'salut', 'bonjour', 'bonsoir',
    'شكرا', 'merci', 'thanks',
    'نعم', 'لا', 'oui', 'non',
    'ok', 'حسنا', 'طيب', 'تمام',
    'كيف حالك', 'comment vas'
  ],

  checkQuestion(message, hasContext) {
    if (!message || typeof message !== 'string') {
      return { accepted: true, reason: 'empty' };
    }

    const clean = message.trim().toLowerCase();

    if (clean.length <= 5) {
      return { accepted: true, reason: 'short_message' };
    }

    if (this.isGreeting(clean)) {
      return { accepted: true, reason: 'greeting' };
    }

    if (this.isFollowUp(clean) || hasContext) {
      return { accepted: true, reason: 'follow_up' };
    }

    if (this.containsSVTKeyword(clean)) {
      return { accepted: true, reason: 'svt_keyword' };
    }

    if (this.isClearlyOffTopic(clean)) {
      return {
        accepted: false,
        reason: 'off_topic',
        redirect: this.getRedirectMessage(clean)
      };
    }

    return { accepted: true, reason: 'benefit_of_doubt' };
  },

  isGreeting(message) {
    return this.greetings.some(g => message.includes(g));
  },

  isFollowUp(message) {
    if (message.length < 20) return true;
    return true;
  },

  containsSVTKeyword(message) {
    return this.svtGuaranteed.some(keyword =>
      message.includes(keyword.toLowerCase())
    );
  },

  isClearlyOffTopic(message) {
    return this.offTopicPatterns.some(pattern => pattern.test(message));
  },

  getRedirectMessage(message) {
    if (/\d+\s*[\+\-\*\/\×\÷]\s*\d+/.test(message) ||
        /كم\s+(يساوي|تساوي)/.test(message) ||
        /calcul/i.test(message)) {
      return `🧮 يبدو أنك تبحث عن حساب رياضي!

أنا **أستاذ خوارزمي**، متخصص فقط في **علوم الطبيعة والحياة** 🧬

لكن يمكنني مساعدتك في الرياضيات المرتبطة بالبيولوجيا:
• 🧬 حساب عدد الرامزات في تتابع ARNm
• 🔋 حساب حصيلة ATP في التنفس الخلوي
• 📊 قراءة المنحنيات البيانية
• 🧪 حساب النسب المئوية في الوراثة

💡 **جرب سؤالاً مثل:**
"كم ATP ينتج من غلوكوز واحد؟"
"احسب عدد الأحماض الأمينية في بروتين من 900 نيوكليوتيد"`;
    }

    if (/code|programme|html|css|javascript|برمجة/i.test(message)) {
      return `💻 أسئلة البرمجة ليست من اختصاصي!

أنا متخصص في **علوم الطبيعة والحياة** 🧬

لكن هل تعلم أن البيولوجيا والمعلوماتية مرتبطتان؟
• 🧬 ADN يعمل كـ "برنامج" للخلية!
• 💻 الشفرة الوراثية تشبه لغة البرمجة (4 حروف فقط!)

💡 **جرب:** "كيف يشبه ADN برنامج حاسوب؟"`;
    }

    return `🤔 سؤالك يبدو خارج مجال تخصصي!

أنا **أستاذ خوارزمي** 🧠، متخصص في **علوم الطبيعة والحياة** للبكالوريا الجزائرية.

📚 **يمكنني مساعدتك في:**

🧬 **البروتينات والوراثة**
→ "ما هو ADN؟" أو "اشرح الاستنساخ"

🛡️ **المناعة**
→ "كيف يعمل الجهاز المناعي؟"

⚡ **الجهاز العصبي**
→ "ما هو كمون العمل؟"

☀️ **الطاقة الخلوية**
→ "لماذا الأوراق خضراء؟"

🌍 **الجيولوجيا**
→ "كيف تتحرك الصفائح؟"

💬 اطرح سؤالك في أحد هذه المواضيع! 🚀`;
  }
};

if (typeof window !== 'undefined') {
  window.SVTFilter = SVTFilter;
}
