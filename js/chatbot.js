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
    isProcessing: false
  },
  
  // Suggestions initiales
  suggestions: [
    '🧬 اشرح لي عملية الاستنساخ',
    '🔤 ما هي الشفرة الوراثية؟',
    '🧪 أعطني سؤال اختبار',
    '📚 ما هي مراحل الترجمة؟',
    '💡 نصائح للنجاح في البكالوريا'
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
            أنا أستاذ خوارزمي، مساعدك الذكي للنجاح في البكالوريا.
            اسألني عن أي موضوع في علوم الطبيعة والحياة!
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
    
    // Vérifier la limite
    if (!this.config.isPremium && this.state.todayUsage >= this.config.freeLimit) {
      this.showLimitReached();
      return;
    }
    
    // Cacher le welcome
    const welcome = document.querySelector('.welcome-message');
    if (welcome) welcome.style.display = 'none';
    
    // Ajouter le message utilisateur
    this.addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    // Afficher typing
    this.showTyping();
    this.state.isProcessing = true;
    
    // Appel à Gemini
    const response = await GeminiAPI.sendMessage(message, this.state.conversationHistory);
    
    // Cacher typing
    this.hideTyping();
    this.state.isProcessing = false;
    
    if (response.success) {
      const cleaned = this.validateBotResponse(response.message);
      this.addMessage(cleaned, 'bot', response.isDemo);
      
      // Mettre à jour l'historique
      this.state.conversationHistory.push(
        { role: 'user', parts: [{ text: message }] },
        { role: 'model', parts: [{ text: response.message }] }
      );
      
      // Limiter l'historique
      if (this.state.conversationHistory.length > 10) {
        this.state.conversationHistory = this.state.conversationHistory.slice(-10);
      }
      
      // Incrémenter usage
      this.state.todayUsage++;
      this.saveUsage();
      this.updateUsageCounter();
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
      console.warn('⚠️ Chatbot: CJK chars detected in response');
      text = text.replace(cjk, '');
      if (text.trim().length < 20) {
        return '⚠️ عذراً، حدث خطأ في الإجابة. حاول مرة أخرى من فضلك.';
      }
    }
    return text.trim();
  },

  showLimitReached() {
    this.addMessage(`⚠️ لقد وصلت إلى الحد اليومي (${this.config.freeLimit} أسئلة).\n\n💎 **ترقّ إلى Premium بـ 2000 DA/سنة** للحصول على:\n✓ أسئلة غير محدودة\n✓ توليد اختبارات\n✓ تصحيح إجاباتك\n✓ وأكثر بكثير!\n\n[اشترك الآن](#pricing)`, 'bot');
  }
};

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', () => Chatbot.init());
