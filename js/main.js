/* ============================================
   MAIN.JS - Menu Toggle, Smooth Scroll, Animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Navbar Menu Toggle
  const mobileToggle = document.getElementById('mobileToggle');
  const navLinks = document.getElementById('navLinks');
  
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', !expanded);
      navLinks.classList.toggle('active');
    });
  }
  
  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      const target = document.querySelector(targetId);
      
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth'
        });
        // Close mobile menu if open
        if (navLinks && navLinks.classList.contains('active')) {
          navLinks.classList.remove('active');
          mobileToggle.setAttribute('aria-expanded', 'false');
        }
      }
    });
  });
  
  // Intersection Observer for scroll animations (fade-in)
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, observerOptions);
  
  document.querySelectorAll('.fade-in').forEach(el => {
    observer.observe(el);
  });
});
