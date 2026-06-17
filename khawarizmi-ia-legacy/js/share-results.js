const ShareResults = {
  generateShareText(examResult, timeSpent) {
    const percentage = examResult.percentage;
    let emoji;
    if (percentage >= 90) emoji = '🏆';
    else if (percentage >= 80) emoji = '🌟';
    else if (percentage >= 70) emoji = '✅';
    else if (percentage >= 50) emoji = '👍';
    else emoji = '💪';
    return `${emoji} حصلت على ${percentage}% في امتحان العلوم الطبيعية!\n\n📊 النتيجة: ${examResult.totalScore}/${examResult.totalMaxPoints}\n📝 الأسئلة: ${examResult.questionsAnswered}/${examResult.questionsTotal}\n⏱️ الوقت: ${timeSpent} دقيقة\n🎓 التقدير: ${examResult.grade}\n\n🧠 حضّر للبكالوريا مع خوارزمي IA!\n🔗 khawarizmi-ia.com\n\n#بكالوريا2025 #علوم_طبيعية #خوارزمي`;
  },

  generateStatsText() {
    const stats = ExamStats.getSummary();
    return `📊 إحصائياتي على خوارزمي IA:\n\n📝 عدد الامتحانات: ${stats.totalExams}\n📈 المعدل العام: ${stats.averageScore}%\n⭐ أفضل نتيجة: ${stats.bestScore}%\n🔥 سلسلة: ${stats.streakDays} أيام متتالية\n🏆 إنجازات: ${stats.achievementsCount}\n\n🧠 حضّر للبكالوريا مع خوارزمي IA!\n🔗 khawarizmi-ia.com\n\n#بكالوريا2025 #علوم_طبيعية`;
  },

  async shareNative(text, title) {
    if (navigator.share) {
      try {
        await navigator.share({ title: title || 'خوارزمي IA - نتيجتي', text, url: 'https://khawarizmi-ia.com' });
        return { success: true };
      } catch (e) {
        if (e.name !== 'AbortError') return { success: false, error: e.message };
      }
    }
    return { success: false, error: 'Web Share API non disponible' };
  },

  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return { success: true };
    } catch (e) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return { success: true };
    }
  },

  shareOnFacebook(text) {
    const url = encodeURIComponent('https://khawarizmi-ia.com');
    const quote = encodeURIComponent(text);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${quote}`, '_blank', 'width=600,height=400');
  },

  shareOnWhatsApp(text) {
    window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank');
  },

  shareOnTelegram(text) {
    window.open(`https://t.me/share/url?url=${encodeURIComponent('https://khawarizmi-ia.com')}&text=${encodeURIComponent(text)}`, '_blank');
  },

  shareOnTwitter(text) {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text.substring(0, 280))}`, '_blank');
  },

  async generateResultImage(examResult, timeSpent) {
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 400;
    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 600, 400);
    gradient.addColorStop(0, '#1A2942');
    gradient.addColorStop(1, '#2A3A52');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 600, 400);
    ctx.strokeStyle = '#C9A961';
    ctx.lineWidth = 4;
    ctx.strokeRect(10, 10, 580, 380);
    ctx.textAlign = 'center';
    ctx.fillStyle = '#C9A961';
    ctx.font = 'bold 24px Cairo, sans-serif';
    ctx.fillText('خوارزمي IA', 300, 50);
    ctx.fillStyle = 'white';
    ctx.font = '16px Tajawal, sans-serif';
    ctx.fillText('نتيجة الامتحان التجريبي', 300, 80);
    ctx.fillStyle = '#C9A961';
    ctx.font = 'bold 80px Cairo, sans-serif';
    ctx.fillText(examResult.percentage + '%', 300, 190);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 28px Cairo, sans-serif';
    ctx.fillText(examResult.grade + ' — ' + examResult.comment, 300, 240);
    ctx.font = '16px Tajawal, sans-serif';
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.fillText(`${examResult.totalScore}/${examResult.totalMaxPoints} نقطة  |  ${examResult.questionsAnswered} أسئلة  |  ${timeSpent} دقيقة`, 300, 290);
    ctx.fillStyle = 'rgba(255,255,255,0.5)';
    ctx.font = '14px Tajawal, sans-serif';
    ctx.fillText('#بكالوريا2025  |  khawarizmi-ia.com', 300, 370);
    return canvas.toDataURL('image/png');
  },

  showShareModal(examResult, timeSpent) {
    const text = this.generateShareText(examResult, timeSpent);
    document.getElementById('shareModal')?.remove();
    const modal = document.createElement('div');
    modal.id = 'shareModal';
    modal.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 99999; padding: 20px; animation: fadeIn 0.3s;';
    modal.innerHTML = `
      <div style="background: white; border-radius: 24px; padding: 30px; max-width: 500px; width: 100%; max-height: 90vh; overflow-y: auto;">
        <div style="text-align: center; margin-bottom: 24px;">
          <div style="font-size: 3rem; margin-bottom: 8px;">📤</div>
          <h2 style="font-family: 'Cairo', sans-serif; color: #1A2942; margin-bottom: 8px;">شارك نتيجتك!</h2>
          <p style="color: #5A6A7A;">أخبر أصدقاءك بتقدمك في التحضير للبكالوريا</p>
        </div>
        <div style="background: #FAF8F0; padding: 16px; border-radius: 12px; margin-bottom: 20px; font-size: 0.9rem; line-height: 1.8; white-space: pre-line; border: 1px solid #E8E8E8;" id="shareText">${text}</div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px;">
          <button onclick="ShareResults.shareOnWhatsApp(document.getElementById('shareText').textContent)" style="padding: 14px; background: #25D366; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.95rem;">💬 واتساب</button>
          <button onclick="ShareResults.shareOnFacebook(document.getElementById('shareText').textContent)" style="padding: 14px; background: #1877F2; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.95rem;">📘 فيسبوك</button>
          <button onclick="ShareResults.shareOnTelegram(document.getElementById('shareText').textContent)" style="padding: 14px; background: #0088cc; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.95rem;">✈️ تيليغرام</button>
          <button onclick="ShareResults.shareOnTwitter(document.getElementById('shareText').textContent)" style="padding: 14px; background: #1DA1F2; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.95rem;">🐦 تويتر</button>
        </div>
        <button onclick="ShareResults.handleCopy()" id="copyBtn" style="width: 100%; padding: 14px; background: #C9A961; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; font-size: 1rem; margin-bottom: 12px;">📋 نسخ النص</button>
        <button onclick="PrintHelper.printExamResults(); document.getElementById('shareModal').remove();" style="width: 100%; padding: 14px; background: #1A2942; color: white; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; font-size: 1rem; margin-bottom: 12px;">🖨️ طباعة النتائج</button>
        <button onclick="document.getElementById('shareModal').remove()" style="width: 100%; padding: 14px; background: #F5F5F5; color: #1A2942; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; font-family: 'Tajawal', sans-serif; font-size: 1rem;">✕ إغلاق</button>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
  },

  async handleCopy() {
    const text = document.getElementById('shareText').textContent;
    const result = await this.copyToClipboard(text);
    const btn = document.getElementById('copyBtn');
    if (result.success) {
      btn.textContent = '✅ تم النسخ!';
      btn.style.background = '#10B981';
      setTimeout(() => { btn.textContent = '📋 نسخ النص'; btn.style.background = '#C9A961'; }, 2000);
    }
  },

  showStatsShareModal() {
    const text = this.generateStatsText();
    document.getElementById('shareModal')?.remove();
    const modal = document.createElement('div');
    modal.id = 'shareModal';
    modal.style.cssText = 'position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 99999; padding: 20px;';
    modal.innerHTML = `
      <div style="background: white; border-radius: 24px; padding: 30px; max-width: 500px; width: 100%;">
        <div style="text-align: center; margin-bottom: 20px;"><div style="font-size: 3rem;">📊</div><h2 style="font-family: 'Cairo', sans-serif; color: #1A2942;">شارك إحصائياتك!</h2></div>
        <div style="background: #FAF8F0; padding: 16px; border-radius: 12px; margin-bottom: 20px; white-space: pre-line; font-size: 0.9rem;" id="shareText">${text}</div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px;">
          <button onclick="ShareResults.shareOnWhatsApp(document.getElementById('shareText').textContent)" style="padding: 12px; background: #25D366; color: white; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-family: 'Tajawal';">💬 واتساب</button>
          <button onclick="ShareResults.shareOnTelegram(document.getElementById('shareText').textContent)" style="padding: 12px; background: #0088cc; color: white; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-family: 'Tajawal';">✈️ تيليغرام</button>
        </div>
        <button onclick="ShareResults.handleCopy()" id="copyBtn" style="width: 100%; padding: 12px; background: #C9A961; color: white; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-family: 'Tajawal'; margin-bottom: 10px;">📋 نسخ</button>
        <button onclick="document.getElementById('shareModal').remove()" style="width: 100%; padding: 12px; background: #F5F5F5; color: #1A2942; border: none; border-radius: 10px; font-weight: 700; cursor: pointer; font-family: 'Tajawal';">✕ إغلاق</button>
      </div>`;
    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
  }
};

if (typeof window !== 'undefined') {
  window.ShareResults = ShareResults;
}
