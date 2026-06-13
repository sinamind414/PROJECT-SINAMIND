/* ============================================
   NAVIGATION - Génération Dynamique des Pages
   ============================================ */

function getBacYear() {
  const now = new Date();
  return now.getMonth() >= 9 ? now.getFullYear() + 1 : now.getFullYear();
}

const SiteNavigator = {
  
  renderHero() {
    const container = document.getElementById('heroSection');
    if (!container) return;
    
    const totalChapters = PROGRAM.getTotalChapters();
    
    container.innerHTML = `
      <section class="hero-program">
        <div class="hero-program-content">
          <div class="logo-showcase">
            <div class="logo-glow"></div>
            <img src="assets/logo.png" alt="Khawarizmi IA" class="hero-logo">
          </div>
          
          <div class="hero-program-badge">
            <span>🇩🇿</span>
            <span>المنهاج الرسمي الجزائري</span>
          </div>
          
          <h1 class="hero-program-title">
            ${PROGRAM.meta.title}<br>
            <span class="highlight">للبكالوريا <span class="bac-year">${getBacYear()}</span></span>
          </h1>
          
          <p class="hero-program-subtitle">
            ${PROGRAM.meta.titleFr} — Programme complet
          </p>
          
          <div class="hero-program-meta">
            📚 ${PROGRAM.meta.level}
          </div>
          
          <p class="hero-program-tagline">
            🎓 المنصة الذكية الأولى في الجزائر لتحضير البكالوريا<br>
            <em>La 1ère plateforme IA en Algérie pour réussir le BAC</em>
          </p>
          
          <div class="hero-stats">
            <div class="hero-stat-item" style="border-top-color:#A78BFA;">
              <div class="hero-stat-number">${PROGRAM.meta.totalDomains}</div>
              <div class="hero-stat-label">🌐 مجالات</div>
            </div>
            <div class="hero-stat-item" style="border-top-color:#FB7185;">
              <div class="hero-stat-number">${PROGRAM.meta.totalUnits}</div>
              <div class="hero-stat-label">📚 وحدات</div>
            </div>
            <div class="hero-stat-item" style="border-top-color:#60A5FA;">
              <div class="hero-stat-number">${totalChapters}+</div>
              <div class="hero-stat-label">📖 فصل</div>
            </div>
            <div class="hero-stat-item" style="border-top-color:#C9A961;">
              <div class="hero-stat-number">∞</div>
              <div class="hero-stat-label">🤖 مع IA</div>
            </div>
          </div>
          
          <div style="display:flex; gap:16px; justify-content:center; flex-wrap:wrap; margin-top:30px;">
            <a href="inscription.html" class="btn-gold">🚀 إنشاء حساب مجاني</a>
            <a href="#domains" class="btn-outline-gold">📖 استكشف البرنامج</a>
          </div>
        </div>
      </section>
    `;
  },
  
  renderQuickNav() {
    const container = document.getElementById('quickNav');
    if (!container) return;
    
    container.innerHTML = `
      <a href="#domains" class="quick-nav-btn active">🏠 الرئيسية</a>
      ${PROGRAM.domains.map(d => `
        <a href="#${d.id}" class="quick-nav-btn">
          ${d.icon} ${d.titleAr}
        </a>
      `).join('')}
      <a href="#revision" class="quick-nav-btn">📅 المراجعة</a>
      <a href="#graph" class="quick-nav-btn">🕸️ الخريطة</a>
    `;
  },
  
  renderDomains() {
    const container = document.getElementById('domainsSection');
    if (!container) return;
    
    container.innerHTML = `
      <section class="domains-section" id="domains">
        <div class="section-header-center">
          <span class="section-tag">📚 المجالات الثلاث</span>
          <h2 class="section-main-title">استكشف المنهاج الكامل</h2>
          <p class="section-main-desc">
            3 مجالات رئيسية تغطي كل ما تحتاجه للنجاح في بكالوريا علوم الطبيعة والحياة
          </p>
        </div>
        
        <div class="domains-grid">
          ${PROGRAM.domains.map(domain => this.renderDomainCard(domain)).join('')}
        </div>
      </section>
    `;
  },
  
  renderDomainCard(domain) {
    return `
      <article class="domain-card" id="${domain.id}">
        <div class="domain-card-header" style="background: ${domain.gradient};">
          <div class="domain-number">المجال ${domain.number} • Domaine ${domain.number}</div>
          <span class="domain-icon-big">${domain.icon}</span>
          <h3 class="domain-title-ar">${domain.titleAr}</h3>
          <p class="domain-title-fr">${domain.titleFr}</p>
        </div>
        
        <div class="domain-card-body">
          <p class="domain-description">${domain.description}</p>
          
          <div class="domain-meta-stats">
            <div class="domain-meta-item">
              <span class="domain-meta-num">${domain.unitsCount}</span>
              <span class="domain-meta-label">وحدات</span>
            </div>
            <div class="domain-meta-item">
              <span class="domain-meta-num">${domain.chaptersCount}</span>
              <span class="domain-meta-label">فصل</span>
            </div>
          </div>
          
          <div class="domain-units-preview">
            <div class="units-preview-title">📋 الوحدات الرئيسية:</div>
            ${domain.units.map(u => `
              <span class="unit-pill">
                ${u.icon} ${u.titleAr}
              </span>
            `).join('')}
          </div>
          
          <a href="#toc-${domain.id}" class="domain-cta" onclick="SiteNavigator.expandDomain('${domain.id}')">
            <span>اكتشف المحتوى</span>
            <span class="arrow">←</span>
          </a>
        </div>
      </article>
    `;
  },
  
  renderTOC() {
    const container = document.getElementById('programTOC');
    if (!container) return;
    
    container.innerHTML = `
      <section class="program-toc" id="program-toc">
        <div class="section-header-center">
          <span class="section-tag">📑 الفهرس التفاعلي</span>
          <h2 class="section-main-title">البرنامج التفصيلي الكامل</h2>
          <p class="section-main-desc">
            انقر على أي وحدة لاستكشاف فصولها والوصول السريع للمحتوى
          </p>
        </div>
        
        <div class="toc-container">
          ${PROGRAM.domains.map(d => this.renderTOCDomain(d)).join('')}
        </div>
      </section>
    `;
    
    this.attachTOCEvents();
  },
  
  renderTOCDomain(domain) {
    return `
      <div class="toc-domain" id="toc-${domain.id}" data-domain="${domain.id}">
        <div class="toc-domain-header" style="background: ${domain.gradient};" onclick="SiteNavigator.toggleDomain('${domain.id}')">
          <div class="toc-domain-icon">${domain.icon}</div>
          <div class="toc-domain-info">
            <div class="toc-domain-name">المجال ${domain.number}: ${domain.titleAr}</div>
            <div class="toc-domain-meta">
              ${domain.titleFr} • ${domain.unitsCount} وحدات • ${domain.chaptersCount} فصل
            </div>
          </div>
          <div class="toc-domain-toggle">▼</div>
        </div>
        
        <div class="toc-domain-content">
          ${domain.units.map(u => this.renderTOCUnit(u, domain)).join('')}
        </div>
      </div>
    `;
  },
  
  renderTOCUnit(unit, domain) {
    return `
      <div class="toc-unit" data-unit="${unit.id}">
        <div class="toc-unit-header" onclick="SiteNavigator.toggleUnit('${unit.id}')">
          <div class="toc-unit-icon">${unit.icon}</div>
          <div class="toc-unit-info">
            <div class="toc-unit-title">الوحدة ${unit.number}: ${unit.titleAr}</div>
            <div class="toc-unit-title-fr">${unit.titleFr}</div>
          </div>
          <div class="toc-unit-badge">${unit.chapters.length} فصول</div>
        </div>
        
        <div class="toc-chapters">
          ${unit.chapters.map(c => `
            <a href="#chapter-${c.id}" class="toc-chapter" onclick="SiteNavigator.openChapter('${c.id}'); return false;">
              <div class="toc-chapter-num">${c.num}</div>
              <div class="toc-chapter-title">
                ${c.titleAr}
                <div style="font-size:0.75rem; color:var(--text-light); font-style:italic; margin-top:2px;">
                  ${c.titleFr}
                </div>
              </div>
              <div class="toc-chapter-page">📄 ${c.page}</div>
            </a>
          `).join('')}
        </div>
      </div>
    `;
  },
  
  attachTOCEvents() {
    setTimeout(() => {
      const first = document.querySelector('.toc-domain');
      if (first) first.classList.add('expanded');
    }, 300);
  },
  
  toggleDomain(domainId) {
    const el = document.querySelector(`[data-domain="${domainId}"]`);
    if (el) el.classList.toggle('expanded');
  },
  
  toggleUnit(unitId) {
    const el = document.querySelector(`[data-unit="${unitId}"]`);
    if (el) el.classList.toggle('expanded');
  },
  
  expandDomain(domainId) {
    setTimeout(() => {
      const el = document.querySelector(`[data-domain="${domainId}"]`);
      if (el && !el.classList.contains('expanded')) {
        el.classList.add('expanded');
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 500);
  },
  
  openChapter(chapterId) {
    const result = PROGRAM.getChapterById(chapterId);
    if (!result) return;
    
    const { chapter, unit, domain } = result;
    this.showChapterModal(chapter, unit, domain);
  },
  
  showChapterModal(chapter, unit, domain) {
    let modal = document.getElementById('chapterModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'chapterModal';
      modal.className = 'chapter-modal';
      document.body.appendChild(modal);
    }
    
    modal.innerHTML = `
      <div class="chapter-modal-overlay" onclick="SiteNavigator.closeModal()"></div>
      <div class="chapter-modal-content">
        <button class="chapter-modal-close" onclick="SiteNavigator.closeModal()">✕</button>
        
        <div class="chapter-modal-header" style="background: ${domain.gradient};">
          <div class="chapter-modal-breadcrumb">
            ${domain.icon} ${domain.titleAr} › ${unit.icon} الوحدة ${unit.number}
          </div>
          <div class="chapter-modal-number">الفصل ${chapter.num}</div>
          <h2 class="chapter-modal-title">${chapter.titleAr}</h2>
          <p class="chapter-modal-title-fr">${chapter.titleFr}</p>
        </div>
        
        <div class="chapter-modal-body">
          <div class="chapter-info-grid">
            <div class="chapter-info-item">
              <div class="info-icon">📄</div>
              <div>
                <div class="info-label">الصفحة المرجعية</div>
                <div class="info-value">${chapter.page}</div>
              </div>
            </div>
            <div class="chapter-info-item">
              <div class="info-icon">📚</div>
              <div>
                <div class="info-label">الوحدة</div>
                <div class="info-value">${unit.titleAr}</div>
              </div>
            </div>
          </div>
          
          <div class="chapter-actions-grid">
            <button class="chapter-action-btn" onclick="SiteNavigator.closeModal(); setTimeout(() => { if (typeof Chatbot !== 'undefined') { Chatbot.toggleChat(); setTimeout(() => { const inp = document.getElementById('chatbotInput'); if(inp) inp.value = 'اشرح لي ${chapter.titleAr}'; }, 400); } }, 300);">
              <span class="action-icon">🤖</span>
              <span class="action-text">اسأل خوارزمي</span>
            </button>
            <button class="chapter-action-btn" onclick="SiteNavigator.startChapterReview()">
              <span class="action-icon">🧪</span>
              <span class="action-text">اختبار سريع</span>
            </button>
            <button class="chapter-action-btn" onclick="SiteNavigator.scrollTo('revision'); SiteNavigator.closeModal();">
              <span class="action-icon">📅</span>
              <span class="action-text">أضف للمراجعة</span>
            </button>
            <button class="chapter-action-btn" onclick="SiteNavigator.scrollTo('graph'); SiteNavigator.closeModal();">
              <span class="action-icon">🕸️</span>
              <span class="action-text">في خريطة المفاهيم</span>
            </button>
          </div>
          
          <div class="chapter-coming-soon">
            <div style="font-size:3rem; text-align:center; margin-bottom:10px;">🚧</div>
            <h3>المحتوى التفصيلي قيد التطوير</h3>
            <p>سيتم قريباً إضافة دروس تفصيلية، فيديوهات، تمارين محلولة لهذا الفصل.<br>
            في الانتظار، يمكنك استخدام <strong>الأدوات المتاحة أعلاه</strong> للمراجعة! 🌟</p>
          </div>
        </div>
      </div>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  },
  
  closeModal() {
    const modal = document.getElementById('chapterModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  },
  
  scrollTo(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },
  
  startChapterReview() {
    this.closeModal();
    this.scrollTo('revision');
    setTimeout(() => {
      if (typeof FSRS !== 'undefined') FSRS.startSession();
    }, 500);
  },
  
  init() {
    this.renderHero();
    this.renderQuickNav();
    this.renderDomains();
    this.renderTOC();
    this.attachScrollHandlers();
  },
  
  attachScrollHandlers() {
    const navBtns = document.querySelectorAll('.quick-nav-btn');
    if (navBtns.length === 0) return;
    
    window.addEventListener('scroll', () => {
      const scrollPos = window.scrollY + 200;
      let activeId = '';
      
      ['domains', ...PROGRAM.domains.map(d => d.id), 'revision', 'graph'].forEach(id => {
        const el = document.getElementById(id);
        if (el && el.offsetTop <= scrollPos) {
          activeId = id;
        }
      });
      
      navBtns.forEach(btn => {
        const href = btn.getAttribute('href')?.replace('#', '');
        btn.classList.toggle('active', href === activeId);
      });
    });
  }
};

document.addEventListener('DOMContentLoaded', () => SiteNavigator.init());
