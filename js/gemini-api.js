/* ============================================
   GROQ API - AI Connection (remplace Gemini)
   ============================================ */

const GeminiAPI = {
  API_KEY: 'VOTRE_CLE_GROQ_ICI',

  API_URL: 'https://api.groq.com/openai/v1/chat/completions',

  MODEL: 'llama-3.3-70b-versatile',

  explanationAttempts: {},

  SYSTEM_PROMPT: `أنت "أستاذ خوارزمي"، مساعد ذكي متخصص في علوم الطبيعة والحياة لطلاب البكالوريا الجزائرية.

🎓 منهجيتك في التدريس: طريقة فاينمان (Méthode Feynman)

📋 القواعد الذهبية:

1️⃣ اشرح كأنك تكلم طفلاً عمره 12 سنة
   - استخدم كلمات بسيطة جداً
   - تجنّب المصطلحات المعقدة في البداية
   - قسّم الفكرة إلى أجزاء صغيرة

2️⃣ استخدم تشبيهات من الحياة اليومية
   - مثلاً: ADN = "كتاب وصفات في النواة"
   - الريبوزوم = "مصنع صغير للبروتين"
   - الإنزيم = "مفتاح خاص لقفل خاص"
   - الخلية = "مدينة صغيرة بسكانها وعمالها" 

3️⃣ بنية الإجابة المثالية:
   - 🎯 في جملة واحدة: تعريف بسيط جداً
   - 🌟 تشبيه من الحياة اليومية
   - 📖 شرح تدريجي: من البسيط إلى المعقد
   - 💡 مثال محسوس
   - ❓ سؤال تحقق: "هل فهمت؟" أو "ما رأيك؟"

4️⃣ إذا قال التلميذ "لم أفهم" أو "اشرح أكثر":
   - ابدأ من جديد بطريقة مختلفة تماماً
   - استخدم تشبيهاً آخر
   - بسّط أكثر وأكثر
   - "آسف، دعني أحاول بطريقة أخرى..."

5️⃣ شجّع التلميذ دائماً:
   - "سؤال رائع!"، "أنت على الطريق الصحيح!"، "لا تقلق، هذا المفهوم صعب على الجميع"

🔴 اللغة: العربية الفصحى البسيطة فقط. المصطلحات العلمية بالفرنسية بين قوسين.
🚫 ممنوع: إجابات طويلة معقدة من البداية، استخدام لغات أخرى`,

  async sendMessage(userMessage, conversationHistory = []) {
    try {
      const needsSimpler = this.detectConfusion(userMessage);
      let reinforcedMessage = userMessage;

      if (needsSimpler) {
        const topic = this.getLastTopic(conversationHistory);
        this.explanationAttempts[topic] = (this.explanationAttempts[topic] || 0) + 1;
        reinforcedMessage = `[التلميذ لم يفهم! هذه المحاولة رقم ${this.explanationAttempts[topic] + 1}. استخدم تشبيهاً مختلفاً تماماً. ابدأ بقصة قصيرة. كن أبسط بكثير من قبل.]\n\nسؤاله: ${userMessage}`;
      } else {
        const topic = this.getLastTopic(conversationHistory);
        if (topic) delete this.explanationAttempts[topic];
      }

      const messages = [
        { role: 'system', content: this.SYSTEM_PROMPT },
        { role: 'assistant', content: 'فهمت! أنا أستاذ خوارزمي، سأشرح كل شيء بطريقة فاينمان البسيطة 🤓' }
      ];

      conversationHistory.forEach(msg => {
        messages.push({
          role: msg.role === 'model' ? 'assistant' : 'user',
          content: msg.parts[0].text
        });
      });

      messages.push({ role: 'user', content: reinforcedMessage });

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.API_KEY}`
        },
        body: JSON.stringify({
          model: this.MODEL,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1500,
          top_p: 0.9
        })
      });

      if (!response.ok) {
        const errBody = await response.text().catch(() => '');
        throw new Error(`API ${response.status}: ${errBody.slice(0, 200)}`);
      }

      const data = await response.json();

      if (data.choices && data.choices[0]?.message?.content) {
        let raw = data.choices[0].message.content;
        return {
          success: true,
          message: this.cleanResponse(raw)
        };
      } else {
        throw new Error('Réponse invalide de Groq');
      }

    } catch (error) {
      console.error('Groq API Error:', error);
      return this.getFallbackResponse(userMessage);
    }
  },

  detectConfusion(message) {
    const patterns = [
      'لم أفهم','لا أفهم','صعب','معقد','اشرح أكثر',
      'وضح','بسّط','مرة أخرى','غير واضح',
      'مش فاهم','ما فهمت','صعيب','ما فهمتش',
      'أعد الشرح','مرة ثانية','بطريقة أخرى',
      'مثال آخر','مثال أبسط',
      'pas compris','difficile','compliqué',
      'je comprends pas','pas clair'
    ];
    return patterns.some(p => message.toLowerCase().includes(p));
  },

  getLastTopic(history) {
    if (history.length < 2) return null;
    const last = history[history.length - 2];
    return last?.parts?.[0]?.text?.substring(0, 50) || null;
  },

  cleanResponse(text) {
    const cjk = /[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]/g;
    if (cjk.test(text)) {
      text = text.replace(cjk, '');
      if (text.trim().length < 20) return 'عذراً، حدث خطأ. أعد صياغة سؤالك من فضلك 🙏';
    }
    return text.trim();
  },

  getFallbackResponse(userMessage) {
    const m = userMessage.toLowerCase();
    let response = '';

    if (m.includes('استنساخ') || m.includes('transcription')) {
      response = `🎬 تخيل أنك في مكتبة! النواة هي المكتبة، و ADN هو كتاب ضخم لا يمكن إخراجه.\n\n🎯 المشكلة: المصنع (الهيولى) يحتاج معلومات من هذا الكتاب!\n💡 الحل: نسخ صفحة! عملية الاستنساخ = آلة تصوير تنسخ صفحة ADN إلى ورقة صغيرة ARNm تخرج للهيولى.\n\n🖨️ الإنزيم ARN polymérase هو آلة التصوير.\n\n🤔 هل التشبيه واضح؟`;
    } else if (m.includes('ترجمة') || m.includes('traduction')) {
      response = `🎭 تخيل مسرحية! ARNm هو السيناريو مكتوب بلغة خاصة.\nالريبوزوم = المسرح، ARNt = الممثلون يحملون الأحماض الأمينية.\n\n📖 كل 3 حروف في السيناريو = رامزة (Codon) = حركة معينة.\n⏯️ الترجمة = تحويل السيناريو إلى فيلم (بروتين)!`;
    } else if (m.includes('مناعة') || m.includes('immunité')) {
      response = `🏰 جسمك قلعة محصنة!\n\n🚪 الجلد = السور الخارجي\n🛡️ البلعميات = حراس يبتلعون الأعداء\n🎯 LB = مصنع أسلحة (أجسام مضادة)\n⚔️ LT = كوماندو يقتل الخلايا المصابة\n\n🧠 الذاكرة المناعية: إذا عاد نفس العدو، يتعرف عليه الجيش فوراً!`;
    } else if (m.includes('سلام') || m.includes('مرحبا') || m.includes('hello')) {
      response = `🌟 أهلاً! أنا أستاذ خوارزمي، أشرح بطريقة فاينمان:\n\n• 🧬 الـ ADN والبروتينات\n• 🛡️ المناعة\n• ⚡ الجهاز العصبي\n• ☀️🔋 الطاقة الخلوية\n• 🌍 الجيولوجيا\n\n💬 جرب: "اشرح لي ADN كأنني طفل صغير"`;
    } else if (m.includes('لم أفهم') || m.includes('لا أفهم') || m.includes('بسط') || m.includes('صعب')) {
      response = `😊 لا تقلق! كل عالم عظيم لم يفهم من المرة الأولى.\n\n🎯 قل لي:\n• ما الجزء غير الواضح؟\n• هل تريد مثالاً آخر؟\n• هل أبدأ من الصفر؟\n\n💡 تذكّر: السؤال الجيد نصف الإجابة!`;
    } else {
      response = `🤔 سؤال رائع! دعني أشرح بطريقة فاينمان...\n\n📚 عن أي موضوع تريد أن تسأل؟\n1️⃣ 🧬 البروتينات والوراثة\n2️⃣ 🛡️ المناعة\n3️⃣ ⚡ الجهاز العصبي\n4️⃣ ☀️🔋 الطاقة الخلوية\n5️⃣ 🌍 التكتونية`;
    }

    return { success: true, message: response, isDemo: true };
  }
};
