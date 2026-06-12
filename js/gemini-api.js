/* ============================================
   GEMINI API - AI Connection
   ============================================ */

const GeminiAPI = {
  // ⚠️ REMPLACE par ta vraie clé API Gemini (gratuite sur https://makersuite.google.com/app/apikey)
  API_KEY: 'YOUR_GEMINI_API_KEY_HERE',
  
  API_URL: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
  
  // System prompt pour le contexte Khawarizmi
  SYSTEM_PROMPT: `أنت "أستاذ خوارزمي"، مساعد ذكي متخصص في علوم الطبيعة والحياة لطلاب البكالوريا في الجزائر.

قواعد مهمة:
1. أجب باللغة العربية بشكل افتراضي، إلا إذا طُلب منك الإجابة بالفرنسية
2. ركّز على المنهاج الجزائري للسنة الثالثة ثانوي - شعبة العلوم التجريبية
3. المواضيع الرئيسية: تركيب البروتين، المناعة، الاتصال العصبي، علم الوراثة، التطور
4. قدّم إجابات واضحة ومنظمة مع أمثلة
5. استخدم الرموز التعبيرية باعتدال لجعل الشرح أكثر جاذبية
6. عند الإمكان، اربط المفاهيم بأسئلة بكالوريا سابقة
7. شجّع الطالب وكن إيجابياً
8. إذا لم تعرف الإجابة، قل ذلك بصراحة ولا تخترع معلومات

كن دائماً مهنياً، مفيداً ومحفزاً!`,
  
  async sendMessage(userMessage, conversationHistory = []) {
    try {
      // Clean history to match expected API format
      const messages = [
        {
          role: 'user',
          parts: [{ text: this.SYSTEM_PROMPT }]
        },
        {
          role: 'model',
          parts: [{ text: 'فهمت! أنا أستاذ خوارزمي، جاهز لمساعدة طلاب البكالوريا الجزائريين. كيف يمكنني مساعدتك اليوم؟' }]
        }
      ];

      // Format conversation history correctly
      conversationHistory.forEach(msg => {
        messages.push({
          role: msg.role,
          parts: [{ text: msg.parts[0].text }]
        });
      });

      // Add the current user message
      messages.push({
        role: 'user',
        parts: [{ text: userMessage }]
      });
      
      const response = await fetch(`${this.API_URL}?key=${this.API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contents: messages,
          generationConfig: {
            temperature: 0.7,
            topK: 40,
            topP: 0.95,
            maxOutputTokens: 1024
          },
          safetySettings: [
            { category: 'HARM_CATEGORY_HARASSMENT', threshold: 'BLOCK_MEDIUM_AND_ABOVE' },
            { category: 'HARM_CATEGORY_HATE_SPEECH', threshold: 'BLOCK_MEDIUM_AND_ABOVE' }
          ]
        })
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
        return {
          success: true,
          message: data.candidates[0].content.parts[0].text
        };
      } else {
        throw new Error('Réponse invalide de Gemini');
      }
      
    } catch (error) {
      console.error('Gemini API Error:', error);
      
      // Fallback : Réponse simulée si pas de clé API
      if (!this.API_KEY || this.API_KEY === 'YOUR_GEMINI_API_KEY_HERE') {
        return this.getFallbackResponse(userMessage);
      }
      
      return {
        success: false,
        message: 'عذراً، حدث خطأ. يرجى المحاولة مرة أخرى. 🙏'
      };
    }
  },
  
  // Réponses simulées si pas de clé API (mode demo)
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
      response = `شكراً على سؤالك! 🌟\n\n*ملاحظة: أنا حالياً في وضع تجريبي. للاستفادة الكاملة من قدراتي، يجب إضافة مفتاح API Gemini.*\n\nيمكنك سؤالي عن:\n• تركيب البروتين 🧬\n• الشفرة الوراثية 🔤\n• الترجمة 🔄\n• المناعة 🛡️\n• وأي موضوع من برنامج البكالوريا!`;
    }
    
    return {
      success: true,
      message: response,
      isDemo: true
    };
  }
};
