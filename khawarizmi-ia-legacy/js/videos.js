/* ============================================
   VIDEOS.JS - YouTube Videos Manager
   ============================================ */

const videosData = {
  transcription: [
    {
      id: 'DooBDAEFOLI',
      title: 'عملية الاستنساخ - شرح كامل',
      channel: 'علوم BAC',
      duration: '12:45'
    },
    {
      id: 'WsofH466lqk',
      title: 'مراحل الاستنساخ بالتفصيل',
      channel: 'بكالوريا الجزائر',
      duration: '8:30'
    }
  ],
  code: [
    {
      id: 'EvwgPMKa-lY',
      title: 'الشفرة الوراثية - مفهوم شامل',
      channel: 'علوم BAC',
      duration: '10:20'
    },
    {
      id: 'Ek40fU4EZqI',
      title: 'كيف تقرأ جدول الشفرة الوراثية',
      channel: 'بكالوريا الجزائر',
      duration: '6:15'
    }
  ],
  translation: [
    {
      id: 'TfYf_rPWUdY',
      title: 'عملية الترجمة في الريبوزوم',
      channel: 'علوم BAC',
      duration: '14:30'
    },
    {
      id: 'oefAI2x2CQM',
      title: 'دور ARNt في تركيب البروتين',
      channel: 'بكالوريا الجزائر',
      duration: '9:45'
    }
  ],
  fate: [
    {
      id: 'meNEUTn9Atg',
      title: 'طي البروتين والبنية الفراغية',
      channel: 'علوم BAC',
      duration: '11:00'
    }
  ]
};

(function() {
  'use strict';
  
  window.renderVideos = function(sectionId) {
    const container = document.getElementById(`videos-${sectionId}`);
    if (!container || !videosData[sectionId]) return;
    
    const videos = videosData[sectionId];
    container.innerHTML = `
      <div class="video-grid">
        ${videos.map(video => `
          <div class="video-card" onclick="openVideo('${video.id}')">
            <div class="video-thumbnail">
              <img src="https://i.ytimg.com/vi/${video.id}/hqdefault.jpg" alt="${video.title}" loading="lazy">
              <div class="play-overlay">▶</div>
              <div class="video-duration">${video.duration}</div>
            </div>
            <div class="video-info">
              <div class="video-title">${video.title}</div>
              <div class="video-meta">
                <span>📺 ${video.channel}</span>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  };
  
  window.openVideo = function(videoId) {
    const modal = document.createElement('div');
    modal.className = 'video-modal active';
    modal.innerHTML = `
      <div class="video-modal-content">
        <button class="video-close" onclick="closeVideo(this)">✕</button>
        <iframe 
          src="https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          allowfullscreen>
        </iframe>
      </div>
    `;
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';
    
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeVideo(modal.querySelector('.video-close'));
    });
  };
  
  window.closeVideo = function(btn) {
    const modal = btn.closest('.video-modal');
    if (modal) {
      modal.remove();
      document.body.style.overflow = '';
    }
  };
})();
