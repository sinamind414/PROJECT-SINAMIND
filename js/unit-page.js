/* ============================================
   UNIT PAGE JS - Logique des pages d'unités
   Khawarizmi IA — BAC Algérie 2025
   ============================================ */

const UnitPage = {
  getProgress(unitId) {
    const stored = JSON.parse(localStorage.getItem('khawarizmi-progress') || '{}');
    return stored[unitId] || { completed: [], lastVisit: null };
  },
  saveProgress(unitId, chapterId) {
    const stored = JSON.parse(localStorage.getItem('khawarizmi-progress') || '{}');
    if (!stored[unitId]) stored[unitId] = { completed: [], lastVisit: null };
    if (!stored[unitId].completed.includes(chapterId)) {
      stored[unitId].completed.push(chapterId);
    }
    stored[unitId].lastVisit = new Date().toISOString();
    localStorage.setItem('khawarizmi-progress', JSON.stringify(stored));
    this.updateProgressBar(unitId);
  },
  updateProgressBar(unitId) {
    const bar = document.getElementById('progressFill');
    const text = document.getElementById('progressPercent');
    const total = document.querySelectorAll('.chapter-section').length;
    const progress = this.getProgress(unitId);
    const percent = total > 0 ? Math.round((progress.completed.length / total) * 100) : 0;
    if (bar) bar.style.width = percent + '%';
    if (text) text.textContent = percent + '%';
  },
  initScrollSpy() {
    const sections = document.querySelectorAll('.chapter-section');
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    if (sections.length === 0 || navItems.length === 0) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          navItems.forEach(item => {
            item.classList.toggle('active', item.getAttribute('href') === '#' + id);
          });
        }
      });
    }, { threshold: 0.3, rootMargin: '-140px 0px -50% 0px' });
    sections.forEach(section => observer.observe(section));
  },
  checkAnswer(button, correctIndex) {
    const quiz = button.closest('.quiz-inline');
    const options = quiz.querySelectorAll('.quiz-inline-option');
    const feedback = quiz.querySelector('.quiz-feedback');
    const clickedIndex = parseInt(button.dataset.index);
    options.forEach((opt, i) => {
      opt.classList.add('disabled');
      opt.onclick = null;
      if (i === correctIndex) opt.classList.add('correct');
      else if (i === clickedIndex && clickedIndex !== correctIndex) opt.classList.add('wrong');
    });
    if (feedback) {
      feedback.classList.add('show');
      feedback.classList.toggle('correct', clickedIndex === correctIndex);
      feedback.classList.toggle('wrong', clickedIndex !== correctIndex);
    }
  },
  initAnimations() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
  },
  initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  },
  init(unitId) {
    this.updateProgressBar(unitId);
    this.initScrollSpy();
    this.initAnimations();
    this.initSmoothScroll();
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const unitId = document.body.dataset.unitId;
  if (unitId) UnitPage.init(unitId);
});
