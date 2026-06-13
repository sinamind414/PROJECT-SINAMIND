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
    explanationCount: 0
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
      <span class="chatbot-badge">1</span>
    `;
    toggle.title = 'تحدث مع أستاذ خوارزمي';
    document.body.appendChild(toggle);
    
    // Chat Window
    const window = document.createElement('div');
    window.className = 'chatbot-window';
    window.id = 'chatbotWindow';
    window.innerHTML = `
      <div class="chatbot-header">
        <div class="chatbot-avatar">🧠</div>
        <div class="chatbot-info">
          <div class="chatbot-name">أستاذ خوارزمي</div>
          <div class="chatbot-status">
            <span class="status-dot"></span>
            متاح الآن
          </div>
        </div>
        <button class="chatbot-close" id="chatbotClose" title="إغلاق">✕</button>
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
    
    // Détecter si l'élève continue sur le même sujet
    if (this.isContinuationQuestion(message)) {
      this.state.explanationCount++;
    } else {
      this.state.explanationCount = 0;
    }
    
    // Vérifier SVT
    if (typeof SVTKnowledgeBase !== 'undefined' && !SVTKnowledgeBase.isSVTQuestion(message)) {
      this.addMessage(SVTKnowledgeBase.getRejectionMessage(), 'bot');
      this.state.todayUsage++; this.saveUsage(); this.updateUsageCounter();
      return;
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
        return;
      }
    }
    
    // Afficher message d'aide si 3+ tentatives
    if (this.state.explanationCount >= 3) {
      this.showReexplainTip();
    }
    
    // Appel à Groq
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
      <div class="message-time">${time}${isDemo ? ' • Demo' : ''}</div>
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
    fb.style.cssText = 'display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;';
    fb.innerHTML = `
      <button onclick="Chatbot.handleFeedback('understood')" style="background:#10B981;color:white;border:none;padding:5px 12px;border-radius:20px;cursor:pointer;font-family:var(--font-ar);font-size:0.8rem;">✅ فهمت!</button>
      <button onclick="Chatbot.handleFeedback('confused')" style="background:#DC2626;color:white;border:none;padding:5px 12px;border-radius:20px;cursor:pointer;font-family:var(--font-ar);font-size:0.8rem;">❌ لم أفهم</button>
      <button onclick="Chatbot.handleFeedback('example')" style="background:#8B5CF6;color:white;border:none;padding:5px 12px;border-radius:20px;cursor:pointer;font-family:var(--font-ar);font-size:0.8rem;">💡 مثال آخر</button>`;
    last.appendChild(fb);
  },

  handleFeedback(type) {
    const input = document.getElementById('chatbotInput');
    const msgs = {
      understood: 'رائع! فهمت الفكرة شكراً 🌟',
      confused: 'لم أفهم! هل يمكنك شرح بطريقة مختلفة تماماً؟ 😅',
      example: 'هل يمكنك إعطائي مثالاً آخر من الحياة اليومية؟ 💡'
    };
    input.value = msgs[type];
    if (type === 'understood') {
      setTimeout(() => {
        this.addMessage('🎉 ممتاز! هل تريد التعمق في موضوع آخر؟', 'bot');
        input.value = '';
      }, 500);
    } else {
      this.sendMessage();
    }
  },

  showLimitReached() {
    this.addMessage(`⚠️ لقد وصلت إلى الحد اليومي (${this.config.freeLimit} أسئلة).`, 'bot');
  }
};

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', () => Chatbot.init());
