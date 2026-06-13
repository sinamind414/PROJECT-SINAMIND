/* ============================================
   CHATBOT - Prof Khawarizmi Interactive UI
   ============================================ */

const Chatbot = {
  // Configuration
  config: {
    freeLimit: 999999,
    isPremium: false
  },
  
  // État
  state: {
    isOpen: false,
    conversationHistory: [],
    todayUsage: 0,
    isProcessing: false,
    currentTopic: null,
    explanationCount: 0,
    tutorMode: false
  },

  // Suggestions initiales
  suggestions: [
    '🤔 ما هو ADN؟ اشرح بطريقة بسيطة',
    '🌱 لماذا الأوراق خضراء؟',
    '🛡️ كيف يدافع جسمي عن نفسه؟',
    '⚡ كيف يفكر الدماغ؟',
    '🔋 كيف تحصل خلاياي على الطاقة؟',
    '🧬 ما الفرق بين ADN و ARN؟',
    '🤷 لم أفهم درس المناعة ساعدني',
    '📚 اشرح لي التركيب الضوئي بمثال'
  ],
  
  init() {
    this.loadUsage();
    this.render();
    this.attachEventListeners();
  },
  
  loadUsage() {
    const today = new Date().toDateString();
    const stored = JSON.parse(localStorage.getItem('khawarizmi-chat-usage') || '{}');
    
    if (stored.date === today) {
      this.state.todayUsage = stored.count || 0;
    } else {
      this.state.todayUsage = 0;
      localStorage.setItem('khawarizmi-chat-usage', JSON.stringify({ date: today, count: 0 }));
    }
    
    // Check premium
    this.config.isPremium = localStorage.getItem('khawarizmi-premium') === 'true';
  },
  
  saveUsage() {
    const today = new Date().toDateString();
    localStorage.setItem('khawarizmi-chat-usage', JSON.stringify({
      date: today,
      count: this.state.todayUsage
    }));
  },
  
  render() {
    // Check if toggle already exists to prevent duplicate renders
    if (document.getElementById('chatbotToggle')) return;

    // Toggle Button
    const toggle = document.createElement('button');
    toggle.className = 'chatbot-toggle';
    toggle.id = 'chatbotToggle';
    toggle.innerHTML = `
      🤖
      <span class="chatbot-badge" style="display:none;">1</span>
    `;
    toggle.title = 'تحدث مع أستاذ خوارزمي';
    document.body.appendChild(toggle);
    
    // Chat Window
    const window = document.createElement('div');
    window.className = 'chatbot-window';
    window.id = 'chatbotWindow';
    window.innerHTML = `
        <div class="chatbot-header">
          <div class="chatbot-avatar">
            <img src="assets/logo.png" alt="خوارزمي IA" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
            <span class="avatar-fallback">خ</span>
          </div>
          <div class="chatbot-info">
            <div class="chatbot-name">أستاذ خوارزمي</div>
            <div class="chatbot-status">
              <span class="status-dot"></span>
              متاح الآن
            </div>
          </div>
          <div class="chatbot-header-actions">
            <button class="chatbot-header-btn" id="tutorToggle" title="المدرس الشخصي">🎓</button>
            <button class="chatbot-close" id="chatbotClose" title="إغلاق">✕</button>
          </div>
        </div>
      
      <div class="chatbot-messages" id="chatbotMessages">
        <div class="welcome-message">
          <div class="welcome-emoji">👋</div>
          <div class="welcome-title">مرحباً بك!</div>
          <div class="welcome-text">
            <strong>أهلاً بك في خوارزمي IA!</strong> 🎓
            <br><br>
            أستخدم <strong>طريقة فاينمان</strong> لشرح كل شيء بتشبيهات بسيطة!
            <br><br>
            ✨ <strong>كيف تستفيد مني؟</strong><br>
            1️⃣ اطرح سؤالك بأي طريقة<br>
            2️⃣ سأشرح بتشبيهات من الحياة اليومية<br>
            3️⃣ إذا لم تفهم، قل "لم أفهم"<br>
            4️⃣ سأعيد الشرح بطريقة مختلفة!<br><br>
            💡 <strong>جرب:</strong> "اشرح لي ADN كأنني طفل صغير"
          </div>
          <div class="suggestions" id="suggestions">
            ${this.suggestions.map(s => `
              <button class="suggestion-chip" data-suggestion="${s.substring(2).trim()}">${s}</button>
            `).join('')}
          </div>
        </div>
      </div>
      
      <div class="chatbot-input-area">
        <div class="chatbot-input-wrapper">
          <textarea 
            class="chatbot-input" 
            id="chatbotInput" 
            placeholder="اكتب سؤالك هنا..."
            rows="1"
          ></textarea>
          <button class="chatbot-send" id="chatbotSend" title="إرسال">
            ➤
          </button>
        </div>
        <div class="chatbot-footer-info">
          <span>🔒 محادثاتك خاصة</span>
          <span class="usage-counter" id="usageCounter">
            ${this.getUsageText()}
          </span>
        </div>
      </div>
    `;
    document.body.appendChild(window);
  },
  
  attachEventListeners() {
    const toggle = document.getElementById('chatbotToggle');
    const close = document.getElementById('chatbotClose');
    const send = document.getElementById('chatbotSend');
    const input = document.getElementById('chatbotInput');
    const suggestions = document.getElementById('suggestions');
    
    toggle.addEventListener('click', () => this.toggleChat());
    close.addEventListener('click', () => this.toggleChat());
    send.addEventListener('click', () => this.sendMessage());
    document.getElementById('tutorToggle')?.addEventListener('click', () => this.activateTutorMode());
    
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    input.addEventListener('input', (e) => {
      e.target.style.height = 'auto';
      e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
    });
    
    if (suggestions) {
      suggestions.addEventListener('click', (e) => {
        const chip = e.target.closest('.suggestion-chip');
        if (chip) {
          input.value = chip.dataset.suggestion;
          this.sendMessage();
        }
      });
    }
  },
  
  toggleChat() {
    const window = document.getElementById('chatbotWindow');
    const toggle = document.getElementById('chatbotToggle');
    const badge = toggle.querySelector('.chatbot-badge');
    
    this.state.isOpen = !this.state.isOpen;
    window.classList.toggle('active', this.state.isOpen);
    toggle.classList.toggle('active', this.state.isOpen);
    
    if (this.state.isOpen) {
      toggle.innerHTML = '✕';
      if (badge) badge.remove();
      setTimeout(() => document.getElementById('chatbotInput')?.focus(), 300);
    } else {
      toggle.innerHTML = '🤖';
    }
  },
  
  async sendMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();
    
    if (!message || this.state.isProcessing) return;
    
    if (!this.config.isPremium && this.state.todayUsage >= this.config.freeLimit) {
      this.showLimitReached();
      return;
    }
    
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.style.display = 'none';
    
    this.addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Filtrage intelligent SVT
    const hasContext = this.state.conversationHistory.length > 0;
    const filterResult = SVTFilter.checkQuestion(message, hasContext);

    if (!filterResult.accepted) {
      this.addMessage(filterResult.redirect, 'bot');
      this.state.todayUsage++; this.saveUsage(); this.updateUsageCounter();
      return;
    }

    if (hasContext) {
      this.state.explanationCount++;
    } else {
      this.state.explanationCount = 0;
    }
    
    // Chercher dans la base locale
    if (typeof SVTKnowledgeBase !== 'undefined') {
      const localAnswer = SVTKnowledgeBase.getBestAnswer(message);
      if (localAnswer && localAnswer.score >= 15) {
        let response = localAnswer.content;
        if (localAnswer.relatedTopics.length > 0) {
          response += '\n\n📚 **مواضيع ذات صلة:**\n';
          localAnswer.relatedTopics.forEach(key => {
            response += `• ${SVTKnowledgeBase.getTopicTitle(key)}\n`;
          });
        }
        response += '\n\n💡 *هل تريد معرفة المزيد عن موضوع آخر؟*';
        this.addMessage(response, 'bot');
        this.state.todayUsage++; this.saveUsage(); this.updateUsageCounter();
        this.addFeedbackButtons();
        if (typeof LearningStats !== 'undefined') {
          const topic = this.detectTopic(message) || null;
          LearningStats.trackQuestion(topic);
        }
        return;
      }
    }
    
    // Afficher message d'aide si 3+ tentatives
    if (this.state.explanationCount >= 3) {
      this.showReexplainTip();
    }
    
    // Appel à Groq
    if (typeof GeminiAPI === 'undefined') {
      this.addMessage('⚠️ عذراً، وحدة الذكاء الاصطناعي غير متوفرة. حاول تحديث الصفحة.', 'bot');
      return;
    }

    this.showTyping();
    this.state.isProcessing = true;
    
    const response = await GeminiAPI.sendMessage(message, this.state.conversationHistory);
    
    this.hideTyping();
    this.state.isProcessing = false;
    
    if (response.success) {
      const cleaned = this.validateBotResponse(response.message);
      this.addMessage(cleaned, 'bot', response.isDemo);
      
      this.state.conversationHistory.push(
        { role: 'user', parts: [{ text: message }] },
        { role: 'model', parts: [{ text: response.message }] }
      );
      
      if (this.state.conversationHistory.length > 10) {
        this.state.conversationHistory = this.state.conversationHistory.slice(-10);
      }
      
      this.state.todayUsage++; this.saveUsage(); this.updateUsageCounter();
      this.addFeedbackButtons();

      if (typeof LearningStats !== 'undefined') {
        const topic = this.detectTopic(message) || null;
        if (topic) this.state.currentTopic = topic;
        LearningStats.trackQuestion(topic);
      }
    } else {
      this.addMessage(response.message, 'bot');
    }
  },
  
  addMessage(text, sender, isDemo = false) {
    const messages = document.getElementById('chatbotMessages');
    const time = new Date().toLocaleTimeString('ar-DZ', { hour: '2-digit', minute: '2-digit' });
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    // Formatage du texte (markdown basique)
    const formattedText = this.formatMessage(text);
    
    msgDiv.innerHTML = `
      <div class="message-bubble">${formattedText}</div>
      <div class="message-time">${time}</div>
    `;
    
    messages.appendChild(msgDiv);
    messages.scrollTop = messages.scrollHeight;
  },
  
  formatMessage(text) {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code style="background:rgba(201,169,97,0.15);padding:2px 6px;border-radius:4px;">$1</code>')
      .replace(/\n/g, '<br>');
  },
  
  showTyping() {
    const messages = document.getElementById('chatbotMessages');
    const typing = document.createElement('div');
    typing.className = 'message bot';
    typing.id = 'typingIndicator';
    typing.innerHTML = `
      <div class="typing-indicator">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;
  },
  
  hideTyping() {
    document.getElementById('typingIndicator')?.remove();
  },
  
  getUsageText() {
    if (this.config.isPremium) {
      return '💎 غير محدود (Premium)';
    }
    const remaining = this.config.freeLimit - this.state.todayUsage;
    return `${remaining}/${this.config.freeLimit} أسئلة متبقية اليوم`;
  },
  
  updateUsageCounter() {
    const counter = document.getElementById('usageCounter');
    if (counter) {
      counter.textContent = this.getUsageText();
      counter.classList.toggle('limit-reached', this.state.todayUsage >= this.config.freeLimit && !this.config.isPremium);
    }
  },
  
  validateBotResponse(text) {
    const cjk = /[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]/g;
    if (cjk.test(text)) {
      text = text.replace(cjk, '');
      if (text.trim().length < 20) return '⚠️ عذراً، حدث خطأ. حاول مرة أخرى.';
    }
    return text.trim();
  },

  isContinuationQuestion(message) {
    const patterns = ['لم أفهم','لا أفهم','اشرح أكثر','أعد','مثال آخر','بسّط','وضح','مرة أخرى','صعب'];
    return patterns.some(p => message.includes(p));
  },

  showReexplainTip() {
    const messages = document.getElementById('chatbotMessages');
    const div = document.createElement('div');
    div.className = 'message bot';
    div.innerHTML = `
      <div class="message-bubble" style="background:#FEF3C7;border:2px solid #F59E0B;">
        💡 <strong>نصيحة فاينمان:</strong><br><br>
        جرب أن تقول:<br>
        • "اشرح لي كأنني طفل صغير"<br>
        • "أعطني مثالاً من الحياة اليومية"<br>
        • "ما الفرق بين ... و ... ؟"<br><br>
        💪 لا تستسلم! كل مفهوم يصبح سهلاً بالطريقة الصحيحة.
      </div>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  },

  addFeedbackButtons() {
    const messages = document.getElementById('chatbotMessages');
    const last = messages.querySelector('.message.bot:last-child');
    if (!last) return;
    const fb = document.createElement('div');
    fb.className = 'feedback-container';
    fb.innerHTML = `
      <div class="feedback-question">📊 كيف كان الشرح؟</div>
      <div class="feedback-buttons">
        <button class="feedback-btn understood" onclick="Chatbot.handleFeedback('understood')"><span>✅</span><span>فهمت!</span></button>
        <button class="feedback-btn partial" onclick="Chatbot.handleFeedback('partial')"><span>🤔</span><span>نوعاً ما</span></button>
        <button class="feedback-btn confused" onclick="Chatbot.handleFeedback('confused')"><span>❌</span><span>لم أفهم</span></button>
        <button class="feedback-btn example" onclick="Chatbot.handleFeedback('example')"><span>💡</span><span>مثال آخر</span></button>
      </div>
      <div style="margin-top:8px;text-align:center;">
        <button class="feedback-btn quiz" onclick="Chatbot.handleFeedback('quiz')" style="display:inline-flex;width:auto;padding:8px 16px;font-size:0.8rem;grid-column:unset;"><span>🧪</span><span>اختبرني</span></button>
      </div>`;
    last.appendChild(fb);
  },

  getLastUserMessage() {
    for (let i = this.state.conversationHistory.length - 1; i >= 0; i--) {
      if (this.state.conversationHistory[i].role === 'user') {
        return this.state.conversationHistory[i].parts[0].text;
      }
    }
    return '';
  },

  handleFeedback(type) {
    const input = document.getElementById('chatbotInput');
    const lastMsg = this.getLastUserMessage();
    const topic = this.detectTopic(lastMsg) || this.state.currentTopic || 'general';

    if (type === 'understood') {
      if (typeof LearningStats !== 'undefined') {
        LearningStats.trackUnderstanding(topic, 'understood');
        const newA = LearningStats.checkAchievements(LearningStats.getStats());
        if (newA.length > 0) {
          setTimeout(() => this.showAchievementUnlocked(newA), 1000);
        }
      }
      setTimeout(() => {
        this.showSuccessMessage();
      }, 500);
    } else if (type === 'partial') {
      if (typeof LearningStats !== 'undefined') LearningStats.trackUnderstanding(topic, 'partial');
      setTimeout(() => {
        input.value = 'هل يمكنك تبسيط الشرح أكثر مع مثال من الحياة اليومية؟';
        this.sendMessage();
      }, 300);
    } else if (type === 'confused') {
      if (typeof LearningStats !== 'undefined') LearningStats.trackUnderstanding(topic, 'confused');
      this.state.explanationCount++;
      setTimeout(() => {
        input.value = 'لم أفهم! اشرح بطريقة مختلفة تماماً كأنني طفل صغير 😅';
        this.sendMessage();
      }, 300);
    } else if (type === 'example') {
      setTimeout(() => {
        input.value = 'أعطني مثالاً آخر مختلفاً من الحياة اليومية';
        this.sendMessage();
      }, 300);
    } else if (type === 'quiz') {
      if (typeof PersonalTutor !== 'undefined') {
        PersonalTutor.askReviewQuestion(topic);
      } else {
        this.addMessage('🧪 لنختبر معلوماتك!', 'bot');
      }
    }
  },

  addSuggestedNext() {
    const msgs = document.getElementById('chatbotMessages');
    const div = document.createElement('div');
    div.className = 'feedback-container';
    div.innerHTML = `
      <div class="feedback-question">🚀 ماذا تريد أن تفعل الآن؟</div>
      <div class="feedback-buttons">
        <button class="feedback-btn next-topic" onclick="Chatbot.continueLearning()"><span>📚</span><span>أكمل التعلم</span></button>
        <button class="feedback-btn quiz" onclick="Chatbot.handleFeedback('quiz')"><span>🧪</span><span>اختبرني</span></button>
      </div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  },

  continueLearning() {
    const inp = document.getElementById('chatbotInput');
    inp.value = 'ما هو الموضوع التالي الذي يجب أن أتعلمه؟';
    this.sendMessage();
  },

  activateTutorMode() {
    this.state.tutorMode = !this.state.tutorMode;
    if (this.state.tutorMode) {
      if (typeof PersonalTutor !== 'undefined') {
        PersonalTutor.activateTutorMode();
      } else {
        this.addMessage('🎓 وضع المدرس الشخصي قيد التحميل... حاول مرة أخرى', 'bot');
        this.state.tutorMode = false;
      }
    } else {
      this.addMessage('✅ تم الخروج من وضع المدرس الشخصي', 'bot');
    }
    const btn = document.getElementById('tutorToggle');
    if (btn) btn.style.opacity = this.state.tutorMode ? '1' : '0.6';
  },

  detectTopic(msg) {
    const topics = [
      ['adn','ADN','الاستنساخ','transcription'], ['الترجمة','traduction','ribosome','ARN'],
      ['المناعة','مناعة','immunité','anticorps'], ['عصبون','العصبونات','communication nerveuse','تشابك'],
      ['تركيب ضوئي','photosynthèse','كلوروفيل'], ['تنفس','respiration','mitochondrie','ATP'],
      ['تكتوني','tectonique','زلزال','بركان'], ['إنزيم','enzyme','protéine'],
      ['وراثة','génétique','جين','méiose'], ['انقسام','mitose','خلوي','cycle cellulaire']
    ];
    for (const group of topics) {
      if (group.some(kw => msg.includes(kw))) return group[0];
    }
    return null;
  },

  showSuccessMessage() {
    const msgs = document.getElementById('chatbotMessages');
    const div = document.createElement('div');
    div.className = 'message bot success-animation';
    div.innerHTML = `
      <div class="message-bubble" style="background:linear-gradient(135deg,#D1FAE5,#A7F3D0);border:2px solid #10B981;text-align:center;">
        <div style="font-size:3rem;margin-bottom:8px;">🎉</div>
        <strong style="font-size:1.1rem;">ممتاز! استمر بهذه الطريقة الرائعة!</strong>
        <p style="margin-top:8px;">هل تريد:</p>
        <div style="display:flex;gap:8px;justify-content:center;margin-top:12px;flex-wrap:wrap;">
          <button onclick="PersonalTutor.changeTopic()" style="background:#2563EB;color:white;border:none;padding:8px 16px;border-radius:10px;cursor:pointer;font-family:var(--font-ar);font-weight:700;">📚 موضوع جديد</button>
          <button onclick="PersonalTutor.askReviewQuestion(Chatbot.state.currentTopic||'transcription')" style="background:#8B5CF6;color:white;border:none;padding:8px 16px;border-radius:10px;cursor:pointer;font-family:var(--font-ar);font-weight:700;">🧪 اختبار</button>
        </div>
      </div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  },

  showAchievementUnlocked(achievements) {
    const msgs = document.getElementById('chatbotMessages');
    achievements.forEach(a => {
      const div = document.createElement('div');
      div.className = 'message bot success-animation';
      div.innerHTML = `
        <div class="message-bubble" style="background:linear-gradient(135deg,#FFD700,#FFA500);border:2px solid #F59E0B;text-align:center;color:#1A2942;">
          <div style="font-size:3rem;margin-bottom:8px;">🏆</div>
          <strong>إنجاز جديد!</strong>
          <h3 style="margin:8px 0;font-family:'Cairo',sans-serif;">${a.name}</h3>
        </div>`;
      msgs.appendChild(div);
    });
    msgs.scrollTop = msgs.scrollHeight;
  },

  showLimitReached() {
    this.addMessage(`⚠️ لقد وصلت إلى الحد اليومي (${this.config.freeLimit} أسئلة).`, 'bot');
  }
};

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', () => Chatbot.init());

if (typeof window !== 'undefined') window.Chatbot = Chatbot;
