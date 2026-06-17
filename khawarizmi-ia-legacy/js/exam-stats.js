/* ============================================
   EXAM STATS - Statistiques de Progression
   ============================================ */

const ExamStats = {

  STORAGE_KEY: 'khawarizmi_exam_stats',

  init() {
    const stats = this.getStats();
    if (!stats.createdAt) {
      stats.createdAt = new Date().toISOString();
      this.saveStats(stats);
    }
    return stats;
  },

  getStats() {
    const data = localStorage.getItem(this.STORAGE_KEY);
    return data ? JSON.parse(data) : {
      createdAt: null,
      exams: [],
      totalExams: 0,
      totalQuestions: 0,
      totalCorrect: 0,
      bestScore: 0,
      worstScore: 100,
      averageScore: 0,
      streakDays: 0,
      lastExamDate: null,
      timeSpentTotal: 0,
      domainStats: {
        proteines: { attempts: 0, totalScore: 0, avgScore: 0 },
        energie: { attempts: 0, totalScore: 0, avgScore: 0 },
        geologie: { attempts: 0, totalScore: 0, avgScore: 0 }
      },
      difficultyStats: {
        easy: { attempts: 0, correct: 0 },
        medium: { attempts: 0, correct: 0 },
        hard: { attempts: 0, correct: 0 }
      },
      weeklyProgress: [],
      achievements: [],
      weakTopics: [],
      strongTopics: []
    };
  },

  saveStats(stats) {
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(stats));
  },

  recordExam(examResult, timeSpent, questions) {
    const stats = this.getStats();
    const now = new Date();

    const examEntry = {
      id: Date.now(),
      date: now.toISOString(),
      score: examResult.percentage,
      totalScore: examResult.totalScore,
      maxPoints: examResult.totalMaxPoints,
      grade: examResult.grade,
      questionsCount: examResult.questionsTotal,
      answeredCount: examResult.questionsAnswered,
      timeSpent: timeSpent,
      details: examResult.results.map((r, i) => ({
        questionId: questions[i]?.id,
        domain: questions[i]?.domain,
        difficulty: questions[i]?.difficulty,
        topic: questions[i]?.topic,
        score: r.score,
        maxPoints: r.maxPoints,
        percentage: r.percentage
      }))
    };

    stats.exams.push(examEntry);
    if (stats.exams.length > 100) {
      stats.exams = stats.exams.slice(-100);
    }

    stats.totalExams++;
    stats.totalQuestions += examResult.questionsTotal;
    stats.totalCorrect += examResult.results.filter(r => r.percentage >= 70).length;
    stats.timeSpentTotal += timeSpent;

    if (examResult.percentage > stats.bestScore) {
      stats.bestScore = examResult.percentage;
    }
    if (examResult.percentage < stats.worstScore || stats.worstScore === 0) {
      stats.worstScore = examResult.percentage;
    }

    const allScores = stats.exams.map(e => e.score);
    stats.averageScore = Math.round(allScores.reduce((a, b) => a + b, 0) / allScores.length);

    examResult.results.forEach((result, i) => {
      const domain = questions[i]?.domain;
      if (domain && stats.domainStats[domain]) {
        stats.domainStats[domain].attempts++;
        stats.domainStats[domain].totalScore += result.percentage;
        stats.domainStats[domain].avgScore = Math.round(
          stats.domainStats[domain].totalScore / stats.domainStats[domain].attempts
        );
      }

      const diff = questions[i]?.difficulty;
      if (diff && stats.difficultyStats[diff]) {
        stats.difficultyStats[diff].attempts++;
        if (result.percentage >= 70) {
          stats.difficultyStats[diff].correct++;
        }
      }
    });

    this.updateStreak(stats, now);
    this.updateWeeklyProgress(stats, examResult.percentage);
    this.updateTopicAnalysis(stats);
    this.checkAchievements(stats);

    stats.lastExamDate = now.toISOString();
    this.saveStats(stats);
    return stats;
  },

  updateStreak(stats, now) {
    const today = now.toDateString();
    const lastDate = stats.lastExamDate
      ? new Date(stats.lastExamDate).toDateString()
      : null;

    if (!lastDate) {
      stats.streakDays = 1;
    } else if (lastDate === today) {
      // same day, no change
    } else {
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      if (lastDate === yesterday.toDateString()) {
        stats.streakDays++;
      } else {
        stats.streakDays = 1;
      }
    }
  },

  updateWeeklyProgress(stats, score) {
    const now = new Date();
    const weekStart = new Date(now);
    weekStart.setDate(weekStart.getDate() - weekStart.getDay());
    const weekKey = weekStart.toISOString().split('T')[0];

    let currentWeek = stats.weeklyProgress.find(w => w.week === weekKey);
    if (!currentWeek) {
      currentWeek = { week: weekKey, scores: [], avg: 0, count: 0 };
      stats.weeklyProgress.push(currentWeek);
    }

    currentWeek.scores.push(score);
    currentWeek.count++;
    currentWeek.avg = Math.round(
      currentWeek.scores.reduce((a, b) => a + b, 0) / currentWeek.scores.length
    );

    if (stats.weeklyProgress.length > 12) {
      stats.weeklyProgress = stats.weeklyProgress.slice(-12);
    }
  },

  updateTopicAnalysis(stats) {
    const topicScores = {};

    stats.exams.forEach(exam => {
      exam.details.forEach(d => {
        if (!d.topic) return;
        if (!topicScores[d.topic]) {
          topicScores[d.topic] = { total: 0, count: 0 };
        }
        topicScores[d.topic].total += d.percentage;
        topicScores[d.topic].count++;
      });
    });

    const topics = Object.entries(topicScores).map(([topic, data]) => ({
      topic,
      avg: Math.round(data.total / data.count),
      count: data.count
    }));

    topics.sort((a, b) => a.avg - b.avg);

    stats.weakTopics = topics.filter(t => t.avg < 50).slice(0, 5);
    stats.strongTopics = topics.filter(t => t.avg >= 70).sort((a, b) => b.avg - a.avg).slice(0, 5);
  },

  checkAchievements(stats) {
    const achievements = [
      { id: 'first_exam', name: '🎓 أول امتحان', condition: stats.totalExams >= 1 },
      { id: 'five_exams', name: '📚 5 امتحانات', condition: stats.totalExams >= 5 },
      { id: 'ten_exams', name: '🏆 10 امتحانات', condition: stats.totalExams >= 10 },
      { id: 'perfect_score', name: '⭐ العلامة الكاملة', condition: stats.bestScore >= 95 },
      { id: 'good_average', name: '📈 معدل جيد', condition: stats.averageScore >= 70 },
      { id: 'streak_3', name: '🔥 3 أيام متتالية', condition: stats.streakDays >= 3 },
      { id: 'streak_7', name: '⚡ أسبوع كامل', condition: stats.streakDays >= 7 },
      { id: 'all_domains', name: '🌟 كل المجالات', condition:
        stats.domainStats.proteines.attempts > 0 &&
        stats.domainStats.energie.attempts > 0 &&
        stats.domainStats.geologie.attempts > 0
      },
      { id: 'hour_spent', name: '⏱️ ساعة دراسة', condition: stats.timeSpentTotal >= 60 },
      { id: 'improvement', name: '📈 تحسّن ملحوظ', condition:
        stats.exams.length >= 3 &&
        stats.exams[stats.exams.length - 1]?.score >
        stats.exams[stats.exams.length - 3]?.score + 10
      }
    ];

    stats.achievements = achievements.filter(a => a.condition).map(a => a.id);
    return achievements;
  },

  getSummary() {
    const stats = this.getStats();
    return {
      totalExams: stats.totalExams,
      averageScore: stats.averageScore,
      bestScore: stats.bestScore,
      streakDays: stats.streakDays,
      totalTime: stats.timeSpentTotal,
      achievementsCount: stats.achievements.length,
      lastExam: stats.lastExamDate,
      domainStats: stats.domainStats,
      weakTopics: stats.weakTopics,
      strongTopics: stats.strongTopics
    };
  },

  reset() {
    if (confirm('هل تريد مسح كل الإحصائيات؟ لا يمكن التراجع!')) {
      localStorage.removeItem(this.STORAGE_KEY);
      this.init();
      return true;
    }
    return false;
  },

  export() {
    const stats = this.getStats();
    const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'khawarizmi-stats-' + Date.now() + '.json';
    a.click();
  }
};

if (typeof window !== 'undefined') {
  ExamStats.init();
  window.ExamStats = ExamStats;
}
