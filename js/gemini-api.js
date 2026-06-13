/* ============================================
   GROQ API - AI Connection (remplace Gemini)
   ============================================ */

const GeminiAPI = {
  API_KEY: 'VOTRE_CLE_GROQ_ICI',

  API_URL: 'https://api.groq.com/openai/v1/chat/completions',

  MODEL: 'llama-3.3-70b-versatile',

  SYSTEM_PROMPT: `أنت "أستاذ خوارزمي"، مساعد ذكي متخصص في علوم الطبيعة والحياة لطلاب البكالوريا في الجزائر.

🔴 قاعدة أساسية - اللغة:
1. أجب فقط وحصرياً باللغة العربية الفصحى
2. ممنوع منعاً باتاً استخدام الحروف الصينية (Chinese characters) أو الكورية أو اليابانية أو أي حروف غير عربية أو لاتينية
3. المصطلحات العلمية تكتب بالفرنسية بين قوسين فقط، مثال: "البروتين (Protéine)"
4. إذا وجدت أي حروف صينية أو غير مفهومة في ردك، احذفها فوراً

📚 المحتوى العلمي:
- المنهاج الجزائري للسنة الثالثة ثانوي - شعبة العلوم التجريبية
- المواضيع: تركيب البروتين، المناعة، الاتصال العصبي، الوراثة، التطور
- قدّم إجابات منظمة مع أمثلة وأسئلة بكالوريا سابقة

💡 الأسلوب:
- شجّع الطالب وكن إيجابياً ومهنياً
- استخدم الرموز التعبيرية باعتدال
- إذا لم تعرف، قل بصراحة

⚠️ أبداً لا تستخدم: 告诉ني, 我的, 你是, 你好, 什么, 如何, 为什么 أو أي كلمات صينية`,

  async sendMessage(userMessage, conversationHistory = []) {
    try {
      const langReinforcement = `[أجب بالعربية الفصحى فقط. ممنوع استخدام أي حروف صينية أو كورية أو يابانية.] سؤالي: ${userMessage}`;

      const messages = [
        { role: 'system', content: this.SYSTEM_PROMPT },
        { role: 'assistant', content: 'فهمت! أنا أستاذ خوارزمي، سأجيبك بالعربية الفصحى فقط. كيف يمكنني مساعدتك؟' }
      ];

      conversationHistory.forEach(msg => {
        messages.push({
          role: msg.role === 'model' ? 'assistant' : 'user',
          content: msg.parts[0].text
        });
      });

      messages.push({ role: 'user', content: langReinforcement });

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.API_KEY}`
        },
        body: JSON.stringify({
          model: this.MODEL,
          messages: messages,
          temperature: 0.5,
          max_tokens: 1024,
          top_p: 0.85
        })
      });

      if (!response.ok) {
        const errBody = await response.text().catch(() => '');
        throw new Error(`API ${response.status}: ${errBody.slice(0, 200)}`);
      }

      const data = await response.json();

      if (data.choices && data.choices[0]?.message?.content) {
        const raw = data.choices[0].message.content;
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

  cleanResponse(text) {
    const cjk = /[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]/g;
    if (cjk.test(text)) {
      console.warn('⚠️ CJK chars detected, cleaning...');
      text = text.replace(cjk, '');
      if (text.trim().length < 20) {
        return 'عذراً، حدث خطأ في الإجابة. أعد صياغة سؤالك من فضلك 🙏';
      }
    }
    return text.trim();
  },

  getFallbackResponse(userMessage) {
    const lowerMsg = userMessage.toLowerCase();

    let response = '';

    if (lowerMsg.includes('استنساخ') || lowerMsg.includes('transcription')) {
      response = `📚 **عملية الاستنساخ (Transcription)**\n\nهي عملية نسخ المعلومة الوراثية من ADN إلى ARNm داخل النواة.\n\n**المراحل:**\n1️⃣ الانطلاق: ارتباط ARN بوليمراز\n2️⃣ الاستطالة: قراءة وبناء ARN\n3️⃣ النهاية: انفصال الإنزيم\n\n💡 نصيحة: راجع جيداً دور إنزيم ARN polymérase لأنه سؤال متكرر في البكالوريا!`;
    } else if (lowerMsg.includes('ترجمة') || lowerMsg.includes('translation')) {
      response = `🔄 **عملية الترجمة (Translation)**\n\nتحويل المعلومة من ARNm إلى بروتين في الهيولى على الريبوزومات.\n\n**العناصر الأساسية:**\n• ARNm (الرسالة)\n• الريبوزومات (المقر)\n• ARNt (الناقل)\n• الأحماض الأمينية\n\nهل تريد أن أشرح لك مراحل الترجمة بالتفصيل؟ 🎯`;
    } else if (lowerMsg.includes('شفرة') || lowerMsg.includes('code')) {
      response = `🔤 **الشفرة الوراثية**\n\nنظام مراسلة بين 4 قواعد و20 حمض أميني.\n\n**أرقام مهمة:**\n• 64 رامزة إجمالاً\n• 61 رامزة تشفير\n• 3 رامزات توقف (UAA, UAG, UGA)\n• 1 رامزة انطلاق (AUG)\n\n💎 خصائص الشفرة: عالمية، تنكسية، غير متراكبة، محددة.`;
    } else if (lowerMsg.includes('سلام') || lowerMsg.includes('مرحبا') || lowerMsg.includes('hello')) {
      response = `أهلاً وسهلاً! 👋\n\nأنا **أستاذ خوارزمي**، مساعدك الذكي للنجاح في البكالوريا.\n\nيمكنني مساعدتك في:\n📚 شرح الدروس\n🧪 توليد اختبارات\n📝 تصحيح إجاباتك\n💡 نصائح للمراجعة\n\nبماذا تريد أن نبدأ؟ 🚀`;
    } else if (lowerMsg.includes('اختبار') || lowerMsg.includes('سؤال') || lowerMsg.includes('quiz')) {
      response = `🧪 **سؤال للاختبار:**\n\nما هي مراحل عملية الاستنساخ؟ وما هو دور إنزيم ARN بوليمراز في كل مرحلة؟\n\n💭 خذ وقتك للتفكير، ثم أرسل لي إجابتك وسأقوم بتصحيحها!`;
    } else {
      response = `شكراً على سؤالك! 🌟\n\nيمكنني مساعدتك في:\n• تركيب البروتين 🧬\n• الشفرة الوراثية 🔤\n• الترجمة 🔄\n• المناعة 🛡️\n• وأي موضوع من برنامج البكالوريا!`;
    }

    return {
      success: true,
      message: response,
      isDemo: true
    };
  }
};
