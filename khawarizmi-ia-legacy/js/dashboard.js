/* ============================================
   DASHBOARD.JS - Student Dashboard Logic
   ============================================ */

const sectionsInfo = {
  transcription: { name: 'الاستنساخ', icon: '✍️', url: 'pages/transcription.html' },
  code: { name: 'الشفرة الوراثية', icon: '🔤', url: 'pages/code.html' },
  translation: { name: 'الترجمة', icon: '🔄', url: 'pages/translation.html' },
  fate: { name: 'مصير البروتين', icon: '🎯', url: 'pages/fate.html' }
};

const badges = [
  { id: 'first_visit', icon: '👋', name: 'البداية', desc: 'زيارتك الأولى', check: () => Storage.getVisitedSections().length >= 1 },
  { id: 'explorer', icon: '🗺️', name: 'المستكشف', desc: 'زرت 2 أقسام', check: () => Storage.getVisitedSections().length >= 2 },
  { id: 'all_sections', icon: '📚', name: 'القارئ الشامل', desc: 'زرت كل الأقسام', check: () => Storage.getVisitedSections().length >= 4 },
  { id: 'first_quiz', icon: '🧪', name: 'أول اختبار', desc: 'أكملت اختباراً', check: () => Object.keys(Storage.getAllScores()).length >= 1 },
  { id: 'perfect_score', icon: '🏆', name: 'النجم', desc: 'حصلت على 100%', check: () => Object.values(Storage.getAllScores()).some(s => s.percentage === 100) },
  { id: 'all_quizzes', icon: '🎓', name: 'المتفوق', desc: 'أكملت كل الاختبارات', check: () => Object.keys(Storage.getAllScores()).length >= 4 },
  { id: 'high_avg', icon: '⭐', name: 'الممتاز', desc: 'متوسط > 80%', check: () => Storage.getProgress().avgScore >= 80 },
  { id: 'persistent', icon: '🔥', name: 'المثابر', desc: '5 محاولات', check: () => Object.values(Storage.getAllScores()).reduce((sum, s) => sum + s.attempts, 0) >= 5 }
];

(function() {
  'use strict';
  
  function renderDashboard() {
    renderWelcome();
    renderStats();
    renderProgressRing();
    renderSectionsProgress();
    renderAchievements();
  }
  
  function renderWelcome() {
    const user = Storage.getUser();
    const welcomeEl = document.getElementById('welcomeName');
    const joinEl = document.getElementById('joinDate');
    
    if (welcomeEl) welcomeEl.textContent = user.name;
    if (joinEl) {
      const date = new Date(user.joinDate);
      joinEl.textContent = `عضو منذ ${date.toLocaleDateString('ar-DZ')}`;
    }
  }
  
  function renderStats() {
    const progress = Storage.getProgress();
    const scores = Storage.getAllScores();
    const totalAttempts = Object.values(scores).reduce((sum, s) => sum + s.attempts, 0);
    
    document.getElementById('statSections').textContent = `${progress.sectionsVisited}/${progress.totalSections}`;
    document.getElementById('statQuizzes').textContent = `${progress.quizzesCompleted}/${progress.totalQuizzes}`;
    document.getElementById('statAvg').textContent = `${progress.avgScore}%`;
    document.getElementById('statAttempts').textContent = totalAttempts;
  }
  
  function renderProgressRing() {
    const progress = Storage.getProgress();
    const circle = document.getElementById('progressRingFill');
    const percentEl = document.getElementById('progressPercent');
    
    if (!circle || !percentEl) return;
    
    const radius = 85;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (progress.progressPercent / 100) * circumference;
    
    circle.style.strokeDasharray = circumference;
    circle.style.strokeDashoffset = offset;
    
    let count = 0;
    const target = progress.progressPercent;
    if (target === 0) {
      percentEl.textContent = '0%';
      return;
    }
    const interval = setInterval(() => {
      count++;
      percentEl.textContent = `${count}%`;
      if (count >= target) clearInterval(interval);
    }, 20);
  }
  
  function renderSectionsProgress() {
    const container = document.getElementById('sectionsProgress');
    if (!container) return;
    
    const visited = Storage.getVisitedSections();
    const scores = Storage.getAllScores();
    
    container.innerHTML = Object.entries(sectionsInfo).map(([id, info]) => {
      const isVisited = visited.includes(id);
      const score = scores[id];
      let progressPercent = 0;
      let status = 'not-started';
      let statusText = 'لم يبدأ بعد';
      
      if (isVisited && score) {
        progressPercent = 100;
        status = 'complete';
        statusText = `✅ مكتمل - ${score.percentage}%`;
      } else if (isVisited) {
        progressPercent = 50;
        status = 'incomplete';
        statusText = '⏳ قيد التقدم';
      }
      
      return `
        <div class="section-progress-item">
          <div class="section-progress-icon">${info.icon}</div>
          <div class="section-progress-info">
            <h4>${info.name}</h4>
            <div class="section-progress-bar">
              <div class="section-progress-fill" style="width: ${progressPercent}%"></div>
            </div>
          </div>
          <div class="section-progress-status ${status}">${statusText}</div>
        </div>
      `;
    }).join('');
  }
  
  function renderAchievements() {
    const container = document.getElementById('badgesGrid');
    if (!container) return;
    
    container.innerHTML = badges.map(badge => {
      const unlocked = badge.check();
      return `
        <div class="badge ${unlocked ? 'unlocked' : ''}" title="${badge.desc}">
          <div class="badge-icon">${badge.icon}</div>
          <div class="badge-name">${badge.name}</div>
          <div class="badge-desc">${badge.desc}</div>
        </div>
      `;
    }).join('');
  }
  
  // ============ Edit Name ============
  window.editName = function() {
    const current = Storage.getUser().name;
    const newName = prompt('أدخل اسمك:', current);
    if (newName && newName.trim()) {
      Storage.setUser(newName.trim());
      renderWelcome();
    }
  };
  
  // ============ Reset Progress ============
  window.resetProgress = function() {
    Storage.resetAll();
  };
  
  // ============ Export PDF ============
  window.exportDashboardPDF = function() {
    if (typeof generatePDF === 'function') {
      generatePDF('dashboard');
    } else {
      alert('وظيفة PDF غير محملة');
    }
  };

  // ============ Tab Switcher ============
  window.switchTab = function(tabId) {
    // 1. Toggle tab button active state
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // 2. Toggle content panel visibility
    const panels = document.querySelectorAll('.tab-content-panel');
    panels.forEach(panel => {
      const panelId = 'tab' + tabId.charAt(0).toUpperCase() + tabId.slice(1);
      if (panel.id === panelId) {
        panel.classList.add('active');
      } else {
        panel.classList.remove('active');
      }
    });

    // 3. Initialize dynamically on tab switch
    if (tabId === 'fsrs') {
      if (typeof FSRS !== 'undefined') {
        FSRS.init();
        FSRS.renderDashboard('fsrsContainer');
      }
    } else if (tabId === 'graph') {
      if (typeof ConceptGraph !== 'undefined') {
        ConceptGraph.init('conceptGraphContainer');
      }
    }
  };
  
  // ============ Init ============
  document.addEventListener('DOMContentLoaded', renderDashboard);
})();
