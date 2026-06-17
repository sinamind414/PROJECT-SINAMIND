/* ============================================
   THEME-SWITCHER.JS - Dark/Light Mode Toggle
   ============================================ */

(function() {
  'use strict';
  
  // Get saved theme or default
  let currentTheme = localStorage.getItem('theme') || 'light';
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    const btn = document.querySelector('.theme-switcher');
    if (btn) {
      btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
      btn.setAttribute('title', theme === 'dark' ? 'الوضع النهاري' : 'الوضع الليلي');
    }
  }
  
  window.toggleTheme = function() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(currentTheme);
  };
  
  // Apply on load
  function init() {
    applyTheme(currentTheme);
    
    // Detect system preference if no saved theme
    if (!localStorage.getItem('theme')) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        currentTheme = 'dark';
        applyTheme('dark');
      }
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
