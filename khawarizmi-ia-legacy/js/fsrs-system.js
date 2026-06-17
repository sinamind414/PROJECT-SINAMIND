/* ============================================
   FSRS SYSTEM - Free Spaced Repetition Scheduler
   Inspiré de l'algorithme FSRS-4.5
   ============================================ */

const FSRS = {
  // Paramètres FSRS optimisés
  params: {
    requestRetention: 0.9,
    maxInterval: 365,
    w: [0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]
  },
  
  // États des cartes
  STATE: {
    NEW: 0,
    LEARNING: 1,
    REVIEW: 2,
    RELEARNING: 3
  },
  
  // Notes possibles
  RATING: {
    AGAIN: 1,
    HARD: 2,
    GOOD: 3,
    EASY: 4
  },
  
  // Cartes par défaut (banque de questions)
  defaultDeck: [
    {
      id: 1,
      question: 'ما هي وظيفة إنزيم ARN polymérase؟',
      answer: 'يقوم بنسخ المعلومة الوراثية من ADN إلى ARNm خلال عملية الاستنساخ. يرتبط بالمنطقة المُحفِّزة، يفتح خيطي ADN، ويبني ARN عبر إضافة النيوكليوتيدات.',
      tag: 'الاستنساخ'
    },
    {
      id: 2,
      question: 'كم عدد رامزات التوقف في الشفرة الوراثية؟ ما هي؟',
      answer: '3 رامزات توقف: UAA, UAG, UGA. عند وصول الريبوزوم إلى إحداها، تتوقف عملية الترجمة ويتحرر البروتين.',
      tag: 'الشفرة الوراثية'
    },
    {
      id: 3,
      question: 'ما الفرق بين Intron و Exon؟',
      answer: 'Exons: قطع دالة تُترجم إلى بروتين.\nIntrons: قطع غير دالة تُحذف خلال نضج ARNm.',
      tag: 'الاستنساخ'
    },
    {
      id: 4,
      question: 'أين تحدث عملية الترجمة؟ وما هي العناصر اللازمة؟',
      answer: 'تحدث في الهيولى على مستوى الريبوزومات.\nالعناصر اللازمة:\n• ARNm (الرسالة)\n• الريبوزومات (المقر)\n• ARNt (الناقل)\n• الأحماض الأمينية\n• الطاقة (GTP)',
      tag: 'الترجمة'
    },
    {
      id: 5,
      question: 'ما هي رامزة الانطلاق؟ وما الحمض الأميني الذي تشفر له؟',
      answer: 'رامزة الانطلاق هي AUG، وتشفر للحمض الأميني الميثيونين (Méthionine - Met).',
      tag: 'الشفرة الوراثية'
    },
    {
      id: 6,
      question: 'اذكر خصائص الشفرة الوراثية الأربع.',
      answer: '1. عالمية: نفسها في كل الكائنات الحية\n2. تنكسية: عدة رامزات لنفس الحمض\n3. غير متراكبة: قراءة متتالية\n4. محددة: كل رامزة تشفر لحمض واحد',
      tag: 'الشفرة الوراثية'
    },
    {
      id: 7,
      question: 'ما هو دور ARNt في عملية الترجمة؟',
      answer: 'ARNt (الناقل) ينقل الأحماض الأمينية من الهيولى إلى الريبوزوم، ويتعرف على رامزات ARNm بواسطة الـ Anticodon المكمل.',
      tag: 'الترجمة'
    },
    {
      id: 8,
      question: 'ما هو الـ Polysome؟',
      answer: 'تجمع عدة ريبوزومات تقرأ نفس جزيئة ARNm في نفس الوقت، مما يُمكّن من تركيب عدة نسخ من نفس البروتين بسرعة.',
      tag: 'الترجمة'
    },
    {
      id: 9,
      question: 'ما هي مراحل عملية الاستنساخ الثلاث؟',
      answer: '1. الانطلاق (Initiation): ارتباط ARN polymérase\n2. الاستطالة (Élongation): بناء خيط ARN\n3. النهاية (Terminaison): انفصال الإنزيم وتحرر ARNm',
      tag: 'الاستنساخ'
    },
    {
      id: 10,
      question: 'لماذا تُسمى الشفرة الوراثية "تنكسية" (Dégénérée)؟',
      answer: 'لأن معظم الأحماض الأمينية تُشفَّر لها عدة رامزات مختلفة. مثال: الليوسين له 6 رامزات (UUA, UUG, CUU, CUC, CUA, CUG). هذا يحمي من الطفرات.',
      tag: 'الشفرة الوراثية'
    }
  ],
  
  // État du système
  state: {
    cards: [],
    currentCard: null,
    sessionStats: { reviewed: 0, correct: 0 }
  },
  
  init() {
    this.loadCards();
    if (this.state.cards.length === 0) {
      this.initializeDeck();
    }
    this.renderDashboard();
  },
  
  initializeDeck() {
    this.state.cards = this.defaultDeck.map(card => ({
      ...card,
      state: this.STATE.NEW,
      difficulty: 5,
      stability: 0,
      due: new Date(),
      lastReview: null,
      reviews: 0,
      lapses: 0
    }));
    this.saveCards();
  },
  
  loadCards() {
    const stored = localStorage.getItem('khawarizmi-fsrs-cards');
    if (stored) {
      try {
        this.state.cards = JSON.parse(stored).map(c => ({
          ...c,
          due: new Date(c.due),
          lastReview: c.lastReview ? new Date(c.lastReview) : null
        }));
      } catch (e) {
        console.error('Error loading cards:', e);
        this.state.cards = [];
      }
    }
  },
  
  saveCards() {
    localStorage.setItem('khawarizmi-fsrs-cards', JSON.stringify(this.state.cards));
  },
  
  // Algorithme FSRS simplifié
  scheduleCard(card, rating) {
    const now = new Date();
    card.lastReview = now;
    card.reviews++;
    
    let interval;
    
    if (card.state === this.STATE.NEW || card.state === this.STATE.LEARNING) {
      // Nouvelle carte ou en apprentissage
      switch (rating) {
        case this.RATING.AGAIN:
          interval = 1 / 1440; // 1 minute
          card.state = this.STATE.LEARNING;
          card.lapses++;
          break;
        case this.RATING.HARD:
          interval = 10 / 1440; // 10 minutes
          card.state = this.STATE.LEARNING;
          break;
        case this.RATING.GOOD:
          interval = 1; // 1 jour
          card.state = this.STATE.REVIEW;
          card.stability = 1;
          break;
        case this.RATING.EASY:
          interval = 4; // 4 jours
          card.state = this.STATE.REVIEW;
          card.stability = 4;
          break;
      }
    } else {
      // Carte en révision
      const oldStability = card.stability || 1;
      
      switch (rating) {
        case this.RATING.AGAIN:
          interval = 1 / 1440;
          card.state = this.STATE.RELEARNING;
          card.stability = Math.max(1, oldStability * 0.2);
          card.lapses++;
          break;
        case this.RATING.HARD:
          interval = oldStability * 1.2;
          card.stability = oldStability * 1.2;
          break;
        case this.RATING.GOOD:
          interval = oldStability * 2.5;
          card.stability = oldStability * 2.5;
          break;
        case this.RATING.EASY:
          interval = oldStability * 4;
          card.stability = oldStability * 4;
          break;
      }
    }
    
    // Limiter l'intervalle max
    interval = Math.min(interval, this.params.maxInterval);
    
    // Calculer la prochaine date
    card.due = new Date(now.getTime() + interval * 24 * 60 * 60 * 1000);
    
    return interval;
  },
  
  formatInterval(days) {
    if (days < 1/24) return Math.round(days * 1440) + ' د';
    if (days < 1) return Math.round(days * 24) + ' س';
    if (days < 30) return Math.round(days) + ' ي';
    if (days < 365) return Math.round(days / 30) + ' ش';
    return Math.round(days / 365) + ' سنة';
  },
  
  getDueCards() {
    const now = new Date();
    return this.state.cards.filter(c => c.due <= now);
  },
  
  getStats() {
    const now = new Date();
    return {
      total: this.state.cards.length,
      due: this.state.cards.filter(c => c.due <= now).length,
      learning: this.state.cards.filter(c => c.state === this.STATE.LEARNING || c.state === this.STATE.RELEARNING).length,
      mastered: this.state.cards.filter(c => c.state === this.STATE.REVIEW && c.stability > 21).length,
      streak: this.getStreak()
    };
  },
  
  getStreak() {
    const stored = localStorage.getItem('khawarizmi-streak');
    if (!stored) return 0;
    try {
      const data = JSON.parse(stored);
      const today = new Date().toDateString();
      const lastDate = new Date(data.lastDate).toDateString();
      const yesterday = new Date(Date.now() - 86400000).toDateString();
      
      if (lastDate === today || lastDate === yesterday) {
        return data.count;
      }
      return 0;
    } catch (e) {
      return 0;
    }
  },
  
  updateStreak() {
    const today = new Date().toDateString();
    const stored = localStorage.getItem('khawarizmi-streak');
    let data = { count: 1, lastDate: new Date().toISOString() };
    
    if (stored) {
      try {
        const oldData = JSON.parse(stored);
        const lastDate = new Date(oldData.lastDate).toDateString();
        const yesterday = new Date(Date.now() - 86400000).toDateString();
        
        if (lastDate === today) {
          return; // Déjà mis à jour aujourd'hui
        } else if (lastDate === yesterday) {
          data.count = oldData.count + 1;
        }
      } catch (e) {}
    }
    
    localStorage.setItem('khawarizmi-streak', JSON.stringify(data));
  },
  
  // === UI Rendering ===
  
  renderDashboard() {
    const container = document.getElementById('fsrsContainer');
    if (!container) return;
    
    const stats = this.getStats();
    
    container.innerHTML = `
      <div class="fsrs-stats">
        <div class="fsrs-stat-card due">
          <div class="stat-icon">📚</div>
          <div class="stat-value">${stats.due}</div>
          <div class="stat-label">بطاقات للمراجعة الآن</div>
        </div>
        <div class="fsrs-stat-card learning">
          <div class="stat-icon">🎓</div>
          <div class="stat-value">${stats.learning}</div>
          <div class="stat-label">قيد التعلم</div>
        </div>
        <div class="fsrs-stat-card mastered">
          <div class="stat-icon">✅</div>
          <div class="stat-value">${stats.mastered}</div>
          <div class="stat-label">متقنة</div>
        </div>
        <div class="fsrs-stat-card streak">
          <div class="stat-icon">🔥</div>
          <div class="stat-value">${stats.streak}</div>
          <div class="stat-label">يوم متتالي</div>
        </div>
      </div>
      
      <div id="reviewArea">
        ${stats.due > 0 ? this.renderStartButton(stats.due) : this.renderEmptyState()}
      </div>
    `;
  },
  
  renderStartButton(count) {
    return `
      <div style="text-align:center; padding: 30px;">
        <div style="font-size: 4rem; margin-bottom: 20px;">📖</div>
        <h3 style="font-family: var(--font-calligraphy); color: var(--gold-dark); font-size: 1.6rem; margin-bottom: 12px;">
          جاهز للمراجعة؟
        </h3>
        <p style="color: var(--text-medium); margin-bottom: 24px;">
          لديك <strong>${count}</strong> بطاقة تنتظرك للمراجعة الآن
        </p>
        <button class="empty-cta" onclick="FSRS.startSession()">
          🚀 ابدأ جلسة المراجعة
        </button>
      </div>
    `;
  },
  
  renderEmptyState() {
    return `
      <div class="fsrs-empty">
        <div class="empty-emoji">🎉</div>
        <div class="empty-title">أحسنت! أنهيت كل المراجعات</div>
        <div class="empty-text">عُد لاحقاً لمراجعة بطاقات جديدة. التعلم المنظم هو سر النجاح! 🌟</div>
      </div>
    `;
  },
  
  startSession() {
    this.state.sessionStats = { reviewed: 0, correct: 0, total: this.getDueCards().length };
    this.showNextCard();
  },
  
  showNextCard() {
    const dueCards = this.getDueCards();
    
    if (dueCards.length === 0) {
      this.showCompletionScreen();
      return;
    }
    
    this.state.currentCard = dueCards[0];
    const card = this.state.currentCard;
    const total = this.state.sessionStats.total;
    const reviewed = this.state.sessionStats.reviewed;
    const progress = (reviewed / total) * 100;
    
    const reviewArea = document.getElementById('reviewArea');
    reviewArea.innerHTML = `
      <div class="review-container">
        <div class="review-progress-bar">
          <div class="review-progress-fill" style="width: ${progress}%"></div>
        </div>
        <div class="review-card-counter">${reviewed + 1} / ${total}</div>
        <div class="review-card-tag">${card.tag}</div>
        
        <div class="flashcard" id="flashcard" onclick="FSRS.flipCard()">
          <div class="flashcard-question">${card.question}</div>
          <div class="flashcard-answer">${card.answer.replace(/\n/g, '<br>')}</div>
          <div class="flashcard-hint">👆 انقر لرؤية الإجابة</div>
        </div>
        
        <button class="show-answer-btn" id="showAnswerBtn" onclick="FSRS.flipCard()">
          إظهار الإجابة
        </button>
        
        <div class="difficulty-buttons" id="diffButtons">
          <button class="diff-btn diff-again" onclick="FSRS.rateCard(1)">
            <span class="diff-emoji">😰</span>
            <span class="diff-label">صعب جداً</span>
            <span class="diff-interval">~1 د</span>
          </button>
          <button class="diff-btn diff-hard" onclick="FSRS.rateCard(2)">
            <span class="diff-emoji">😓</span>
            <span class="diff-label">صعب</span>
            <span class="diff-interval">~10 د</span>
          </button>
          <button class="diff-btn diff-good" onclick="FSRS.rateCard(3)">
            <span class="diff-emoji">🙂</span>
            <span class="diff-label">جيد</span>
            <span class="diff-interval">~1 ي</span>
          </button>
          <button class="diff-btn diff-easy" onclick="FSRS.rateCard(4)">
            <span class="diff-emoji">😎</span>
            <span class="diff-label">سهل</span>
            <span class="diff-interval">~4 ي</span>
          </button>
        </div>
      </div>
    `;
  },
  
  flipCard() {
    const flashcard = document.getElementById('flashcard');
    const btn = document.getElementById('showAnswerBtn');
    if (flashcard && !flashcard.classList.contains('flipped')) {
      flashcard.classList.add('flipped');
      if (btn) btn.style.display = 'none';
    }
  },
  
  rateCard(rating) {
    if (!this.state.currentCard) return;
    
    const interval = this.scheduleCard(this.state.currentCard, rating);
    this.state.sessionStats.reviewed++;
    if (rating >= 3) this.state.sessionStats.correct++;
    
    this.saveCards();
    
    // Petit feedback visuel
    const feedback = document.createElement('div');
    feedback.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--gold-dark);color:white;padding:20px 40px;border-radius:50px;font-weight:700;z-index:9999;animation:fadeIn 0.3s';
    feedback.textContent = `المراجعة القادمة: ${this.formatInterval(interval)}`;
    document.body.appendChild(feedback);
    setTimeout(() => feedback.remove(), 1200);
    
    setTimeout(() => this.showNextCard(), 600);
  },
  
  showCompletionScreen() {
    this.updateStreak();
    const stats = this.state.sessionStats;
    const accuracy = stats.reviewed > 0 ? Math.round((stats.correct / stats.reviewed) * 100) : 0;
    
    const reviewArea = document.getElementById('reviewArea');
    reviewArea.innerHTML = `
      <div class="fsrs-complete">
        <div class="complete-emoji">🏆</div>
        <div class="complete-title">جلسة ممتازة!</div>
        <div class="complete-stats">
          <div class="complete-stat">
            <div class="complete-stat-value">${stats.reviewed}</div>
            <div class="complete-stat-label">بطاقة مُراجعة</div>
          </div>
          <div class="complete-stat">
            <div class="complete-stat-value">${accuracy}%</div>
            <div class="complete-stat-label">دقة الإجابات</div>
          </div>
          <div class="complete-stat">
            <div class="complete-stat-value">+1</div>
            <div class="complete-stat-label">يوم في السلسلة 🔥</div>
          </div>
        </div>
        <button class="empty-cta" onclick="FSRS.renderDashboard()">
          🏠 العودة للوحة التحكم
        </button>
      </div>
    `;
  }
};

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('fsrsContainer')) {
    FSRS.init();
  }
});
