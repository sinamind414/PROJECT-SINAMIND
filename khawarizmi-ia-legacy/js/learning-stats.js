const LearningStats = {
    STORAGE_KEY: 'khawarizmi_learning_stats',

    init() {
        const stats = this.getStats();
        if (!stats.startDate) {
            stats.startDate = new Date().toISOString();
            this.saveStats(stats);
        }
    },

    getStats() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        return data ? JSON.parse(data) : {
            startDate: null, totalQuestions: 0, totalCorrectAnswers: 0, totalWrongAnswers: 0,
            topicsStudied: {}, sessionHistory: [], understandingLevels: {},
            streakDays: 0, lastStudyDate: null, achievements: [], totalTimeSpent: 0,
            currentSession: { startTime: Date.now(), questionsAsked: 0, topicsExplored: [] }
        };
    },

    saveStats(stats) { localStorage.setItem(this.STORAGE_KEY, JSON.stringify(stats)); },

    trackQuestion(topic) {
        const stats = this.getStats();
        stats.totalQuestions++;
        stats.currentSession.questionsAsked++;
        if (topic) {
            if (!stats.topicsStudied[topic]) {
                stats.topicsStudied[topic] = { timesAsked: 0, timesUnderstood: 0, timesConfused: 0, masteryLevel: 0 };
            }
            stats.topicsStudied[topic].timesAsked++;
            if (!stats.currentSession.topicsExplored.includes(topic)) {
                stats.currentSession.topicsExplored.push(topic);
            }
        }
        this.updateStreak(stats);
        this.saveStats(stats);
        return this.checkAchievements(stats);
    },

    trackUnderstanding(topic, level) {
        const stats = this.getStats();
        if (!stats.topicsStudied[topic]) this.trackQuestion(topic);
        const td = stats.topicsStudied[topic];
        if (level === 'understood') { td.timesUnderstood++; td.masteryLevel = Math.min(100, td.masteryLevel + 15); stats.totalCorrectAnswers++; }
        else if (level === 'partial') { td.masteryLevel = Math.min(100, td.masteryLevel + 5); }
        else if (level === 'confused') { td.timesConfused++; td.masteryLevel = Math.max(0, td.masteryLevel - 5); stats.totalWrongAnswers++; }
        stats.understandingLevels[topic] = td.masteryLevel;
        this.saveStats(stats);
        return td.masteryLevel;
    },

    updateStreak(stats) {
        const today = new Date().toDateString();
        const last = stats.lastStudyDate ? new Date(stats.lastStudyDate).toDateString() : null;
        if (last !== today) {
            const yesterday = new Date(Date.now() - 86400000).toDateString();
            stats.streakDays = last === yesterday ? stats.streakDays + 1 : 1;
            stats.lastStudyDate = new Date().toISOString();
        }
    },

    checkAchievements(stats) {
        const list = [
            { id: 'first_question', name: '🎓 الخطوة الأولى', desc: 'أول سؤال!', check: () => stats.totalQuestions >= 1 },
            { id: 'curious', name: '🤔 الفضولي', desc: '10 أسئلة', check: () => stats.totalQuestions >= 10 },
            { id: 'persistent', name: '💪 المثابر', desc: '50 سؤال', check: () => stats.totalQuestions >= 50 },
            { id: 'streak_3', name: '🔥 3 أيام', desc: '3 أيام متتالية', check: () => stats.streakDays >= 3 },
            { id: 'streak_7', name: '⚡ أسبوع', desc: '7 أيام متتالية', check: () => stats.streakDays >= 7 },
            { id: 'streak_30', name: '👑 شهر', desc: '30 يوماً متتالياً', check: () => stats.streakDays >= 30 },
            { id: 'master_topic', name: '🏆 إتقان', desc: 'إتقان موضوع 80%+', check: () => Object.values(stats.topicsStudied).some(t => t.masteryLevel >= 80) },
            { id: 'explorer', name: '🗺️ مستكشف', desc: '5 مواضيع', check: () => Object.keys(stats.topicsStudied).length >= 5 },
            { id: 'scholar', name: '🎓 عالم', desc: '10 مواضيع', check: () => Object.keys(stats.topicsStudied).length >= 10 }
        ];
        const newOnes = [];
        list.forEach(a => { if (a.check() && !stats.achievements.includes(a.id)) { stats.achievements.push(a.id); newOnes.push(a); } });
        this.saveStats(stats);
        return newOnes;
    },

    getUnlockedAchievements() {
        const all = [
            { id: 'first_question', name: '🎓 الخطوة الأولى', description: 'أول سؤال!' },
            { id: 'curious', name: '🤔 الفضولي', description: '10 أسئلة' },
            { id: 'persistent', name: '💪 المثابر', description: '50 سؤال' },
            { id: 'streak_3', name: '🔥 3 أيام', description: 'استمر 3 أيام' },
            { id: 'streak_7', name: '⚡ أسبوع', description: 'استمر 7 أيام' },
            { id: 'streak_30', name: '👑 شهر', description: '30 يوماً متتالياً' },
            { id: 'master_topic', name: '🏆 إتقان موضوع', description: 'إتقان موضوع 80%+' },
            { id: 'explorer', name: '🗺️ المستكشف', description: '5 مواضيع' },
            { id: 'scholar', name: '🎓 العالم', description: '10 مواضيع' }
        ];
        const stats = this.getStats();
        return all.map(a => ({ ...a, unlocked: stats.achievements.includes(a.id) }));
    },

    getSummary() {
        const stats = this.getStats();
        const topics = Object.keys(stats.topicsStudied);
        const mastered = Object.values(stats.topicsStudied).filter(t => t.masteryLevel >= 80).length;
        return {
            totalQuestions: stats.totalQuestions, totalCorrect: stats.totalCorrectAnswers,
            successRate: stats.totalQuestions > 0 ? Math.round((stats.totalCorrectAnswers / stats.totalQuestions) * 100) : 0,
            topicsExplored: topics.length, topicsMastered: mastered,
            streakDays: stats.streakDays, achievementsUnlocked: stats.achievements.length
        };
    },

    getTopicMastery(topic) {
        return this.getStats().topicsStudied[topic]?.masteryLevel || 0;
    }
};

if (typeof window !== 'undefined') { LearningStats.init(); window.LearningStats = LearningStats; }
