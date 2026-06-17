/* ============================================
   STORAGE.JS - Centralized localStorage System
   ============================================ */

const Storage = {
  KEYS: {
    PROGRESS: 'bac_progress',
    QUIZ_SCORES: 'bac_quiz_scores',
    VISITED: 'bac_visited_sections',
    THEME: 'theme',
    LANG: 'lang',
    USER: 'bac_user',
    BOOKMARKS: 'bac_bookmarks',
    NOTES: 'bac_notes'
  },
  
  // ============ User Management ============
  getUser() {
    const user = localStorage.getItem(this.KEYS.USER);
    return user ? JSON.parse(user) : { name: 'طالب', joinDate: new Date().toISOString() };
  },
  
  setUser(name) {
    const user = { name, joinDate: new Date().toISOString() };
    localStorage.setItem(this.KEYS.USER, JSON.stringify(user));
    return user;
  },
  
  // ============ Quiz Scores ============
  saveQuizScore(quizId, score, total) {
    const scores = this.getAllScores();
    const percentage = Math.round((score / total) * 100);
    
    if (!scores[quizId] || percentage > scores[quizId].percentage) {
      scores[quizId] = {
        score,
        total,
        percentage,
        date: new Date().toISOString(),
        attempts: (scores[quizId]?.attempts || 0) + 1
      };
    } else {
      scores[quizId].attempts = (scores[quizId]?.attempts || 0) + 1;
    }
    
    localStorage.setItem(this.KEYS.QUIZ_SCORES, JSON.stringify(scores));
    return scores[quizId];
  },
  
  getAllScores() {
    const scores = localStorage.getItem(this.KEYS.QUIZ_SCORES);
    return scores ? JSON.parse(scores) : {};
  },
  
  getScore(quizId) {
    return this.getAllScores()[quizId] || null;
  },
  
  // ============ Progress Tracking ============
  markSectionVisited(sectionId) {
    const visited = this.getVisitedSections();
    if (!visited.includes(sectionId)) {
      visited.push(sectionId);
      localStorage.setItem(this.KEYS.VISITED, JSON.stringify(visited));
    }
  },
  
  getVisitedSections() {
    const visited = localStorage.getItem(this.KEYS.VISITED);
    return visited ? JSON.parse(visited) : [];
  },
  
  getProgress() {
    const sections = ['transcription', 'code', 'translation', 'fate'];
    const visited = this.getVisitedSections();
    const scores = this.getAllScores();
    
    const sectionsVisited = sections.filter(s => visited.includes(s)).length;
    const quizzesCompleted = sections.filter(s => scores[s]).length;
    const totalScore = sections.reduce((sum, s) => sum + (scores[s]?.percentage || 0), 0);
    const avgScore = quizzesCompleted > 0 ? Math.round(totalScore / quizzesCompleted) : 0;
    
    return {
      sectionsVisited,
      totalSections: sections.length,
      quizzesCompleted,
      totalQuizzes: sections.length,
      avgScore,
      progressPercent: Math.round(((sectionsVisited + quizzesCompleted) / (sections.length * 2)) * 100)
    };
  },
  
  // ============ Bookmarks ============
  toggleBookmark(sectionId, title) {
    const bookmarks = this.getBookmarks();
    const index = bookmarks.findIndex(b => b.id === sectionId);
    
    if (index > -1) {
      bookmarks.splice(index, 1);
    } else {
      bookmarks.push({ id: sectionId, title, date: new Date().toISOString() });
    }
    
    localStorage.setItem(this.KEYS.BOOKMARKS, JSON.stringify(bookmarks));
    return bookmarks;
  },
  
  getBookmarks() {
    const bookmarks = localStorage.getItem(this.KEYS.BOOKMARKS);
    return bookmarks ? JSON.parse(bookmarks) : [];
  },
  
  // ============ Notes ============
  saveNote(sectionId, content) {
    const notes = this.getAllNotes();
    notes[sectionId] = { content, date: new Date().toISOString() };
    localStorage.setItem(this.KEYS.NOTES, JSON.stringify(notes));
  },
  
  getNote(sectionId) {
    return this.getAllNotes()[sectionId]?.content || '';
  },
  
  getAllNotes() {
    const notes = localStorage.getItem(this.KEYS.NOTES);
    return notes ? JSON.parse(notes) : {};
  },
  
  // ============ Reset ============
  resetAll() {
    if (confirm('هل أنت متأكد من حذف جميع بياناتك؟')) {
      Object.values(this.KEYS).forEach(key => {
        if (key !== 'theme' && key !== 'lang') {
          localStorage.removeItem(key);
        }
      });
      window.location.reload();
    }
  }
};
