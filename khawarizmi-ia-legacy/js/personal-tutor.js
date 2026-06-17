const PersonalTutor = {
    state: { mode: 'normal', currentTopic: null },

    activateTutorMode() {
        this.state.mode = 'tutor';
        this.showTutorWelcome();
    },

    showTutorWelcome() {
        const summary = LearningStats.getSummary();
        const achievements = LearningStats.getUnlockedAchievements().filter(a => a.unlocked);
        const msgs = document.getElementById('chatbotMessages');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `
            <div class="message-bubble" style="background:linear-gradient(135deg,#FFF9E6,#FEF3C7);border:2px solid #F59E0B;">
                <div class="tutor-mode-badge"><span>⭐</span><span>وضع المدرس الشخصي</span></div>
                <h3 style="font-family:'Cairo',sans-serif;color:#1A2942;margin:8px 0;">🎓 أهلاً بك في وضع التدريس الشخصي!</h3>
                <p style="margin-bottom:12px;">سأتتبع تقدمك وأساعدك على إتقان كل المفاهيم!</p>
                <div class="mini-stats">
                    <div class="mini-stat"><div class="mini-stat-number">${summary.totalQuestions}</div><div class="mini-stat-label">أسئلة</div></div>
                    <div class="mini-stat"><div class="mini-stat-number">${summary.topicsExplored}</div><div class="mini-stat-label">مواضيع</div></div>
                    <div class="mini-stat"><div class="mini-stat-number">${summary.streakDays}🔥</div><div class="mini-stat-label">أيام</div></div>
                    <div class="mini-stat"><div class="mini-stat-number">${summary.successRate}%</div><div class="mini-stat-label">نجاح</div></div>
                </div>
                ${achievements.length > 0 ? `<div style="margin:12px 0;"><strong>🏆 إنجازاتك:</strong><div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">${achievements.slice(0,4).map(a => `<span style="background:#FFD700;padding:4px 10px;border-radius:12px;font-size:0.8rem;">${a.name}</span>`).join('')}</div></div>` : ''}
            </div>`;
        msgs.appendChild(div);
        this.showTutorOptions();
    },

    showTutorOptions() {
        const msgs = document.getElementById('chatbotMessages');
        const div = document.createElement('div');
        div.className = 'feedback-container';
        div.innerHTML = `
            <div class="feedback-question">اختر ما تريد:</div>
            <div class="feedback-buttons">
                <button class="feedback-btn understood" onclick="PersonalTutor.startReviewSession()"><span class="feedback-btn-icon">📚</span><span>مراجعة شاملة</span></button>
                <button class="feedback-btn confused" onclick="PersonalTutor.studyWeakTopics()"><span class="feedback-btn-icon">⚠️</span><span>تقوية الضعف</span></button>
                <button class="feedback-btn quiz" onclick="PersonalTutor.startQuiz()"><span class="feedback-btn-icon">🧪</span><span>اختبار سريع</span></button>
                <button class="feedback-btn next-topic" onclick="PersonalTutor.showAchievements()"><span class="feedback-btn-icon">🏆</span><span>الإنجازات</span></button>
            </div>`;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    },

    startReviewSession() {
        const stats = LearningStats.getStats();
        const topics = Object.keys(stats.topicsStudied);
        if (topics.length === 0) { this.addMsg('🤔 لم تدرس أي موضوع بعد! ابدأ بطرح سؤال.'); return; }
        const topic = topics.sort((a, b) => stats.topicsStudied[a].masteryLevel - stats.topicsStudied[b].masteryLevel)[0];
        const lvl = stats.topicsStudied[topic].masteryLevel || 0;
        this.addMsg(`
            <div class="tutor-mode-badge">📚 مراجعة</div>
            <p><strong>${this.getTopicName(topic)}</strong></p>
            <div class="understanding-progress">
                <div class="progress-label"><span>مستوى الإتقان</span><strong>${lvl}%</strong></div>
                <div class="progress-track"><div class="progress-fill" style="width:${lvl}%;"></div></div>
            </div>`);
        setTimeout(() => this.askReviewQuestion(topic), 1500);
    },

    askReviewQuestion(topic) {
        const db = {
            transcription: [
                { q: 'أين يحدث الاستنساخ؟', opts: ['في الهيولى', 'في النواة', 'في الميتوكوندري'], correct: 1, exp: 'في النواة لأن ADN موجود هناك!' },
                { q: 'الإنزيم المسؤول عن الاستنساخ؟', opts: ['ADN polymérase', 'ARN polymérase', 'Hélicase'], correct: 1, exp: 'ARN polymérase يقرأ ADN ويبني ARNm.' }
            ],
            traduction: [
                { q: 'أين تحدث الترجمة؟', opts: ['في النواة', 'في الهيولى', 'في الميتوكوندري'], correct: 1, exp: 'في الهيولى على الريبوزومات!' },
                { q: 'عدد رامزات التوقف؟', opts: ['1', '3', '4'], correct: 1, exp: '3: UAA, UAG, UGA' }
            ],
            immunite: [
                { q: 'أي خلايا تنتج الأجسام المضادة؟', opts: ['LT8', 'LB', 'Macrophages'], correct: 1, exp: 'LB تنتج الأجسام المضادة بعد تمايزها.' }
            ],
            photosynthese: [
                { q: 'معادلة التركيب الضوئي؟', opts: ['6CO₂+6H₂O→C₆H₁₂O₆+6O₂', 'C₆H₁₂O₆+6O₂→6CO₂+6H₂O', '6O₂+6H₂O→C₆H₁₂O₆'], correct: 0, exp: 'النبتة تستخدم CO₂ والماء+الضوء' }
            ],
            respiration: [
                { q: 'ATP من غلوكوز واحد؟', opts: ['2', '38', '100'], correct: 1, exp: '~38 ATP في التنفس الكامل!' }
            ]
        };
        const questions = db[topic] || db.transcription;
        const q = questions[Math.floor(Math.random() * questions.length)];
        this.showMiniQuiz(q, topic);
    },

    showMiniQuiz(q, topic) {
        const msgs = document.getElementById('chatbotMessages');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-bubble"><div class="mini-quiz"><div class="mini-quiz-question">🧪 ${q.q}</div><div class="mini-quiz-options">${q.opts.map((o, i) => `<button class="mini-quiz-option" onclick="PersonalTutor.checkAnswer(this,${i},${q.correct},'${topic}','${q.exp}')">${o}</button>`).join('')}</div></div></div>`;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    },

    checkAnswer(btn, selected, correct, topic, exp) {
        const parent = btn.parentElement;
        parent.querySelectorAll('.mini-quiz-option').forEach((b, i) => {
            b.disabled = true; b.style.cursor = 'not-allowed';
            if (i === correct) b.classList.add('correct');
            else if (i === selected && i !== correct) b.classList.add('wrong');
        });
        if (typeof LearningStats !== 'undefined') LearningStats.trackUnderstanding(topic, selected === correct ? 'understood' : 'confused');
        setTimeout(() => {
            const msgs = document.getElementById('chatbotMessages');
            const d = document.createElement('div');
            d.className = 'message bot';
            d.innerHTML = `<div class="message-bubble" style="background:${selected===correct?'#D1FAE5':'#FEE2E2'};border:2px solid ${selected===correct?'#10B981':'#DC2626'};"><strong>${selected===correct?'✅ ممتاز!':'❌ ليس صحيحاً'}</strong><p style="margin-top:8px;">${exp}</p></div>`;
            msgs.appendChild(d);
            setTimeout(() => this.showNextOptions(topic), 1500);
        }, 1000);
    },

    showNextOptions(topic) {
        const msgs = document.getElementById('chatbotMessages');
        const div = document.createElement('div');
        div.className = 'feedback-container';
        div.innerHTML = `
            <div class="feedback-question">ماذا تريد؟</div>
            <div class="feedback-buttons">
                <button class="feedback-btn understood" onclick="PersonalTutor.askReviewQuestion('${topic}')"><span>➡️</span><span>سؤال آخر</span></button>
                <button class="feedback-btn example" onclick="PersonalTutor.requestExplanation('${topic}')"><span>💡</span><span>اشرح أكثر</span></button>
                <button class="feedback-btn next-topic" onclick="PersonalTutor.changeTopic()"><span>🔄</span><span>موضوع آخر</span></button>
            </div>`;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    },

    requestExplanation(topic) {
        const inp = document.getElementById('chatbotInput');
        inp.value = `اشرح لي ${this.getTopicName(topic)} بطريقة بسيطة من الحياة اليومية`;
        Chatbot.sendMessage();
    },

    changeTopic() {
        const msgs = document.getElementById('chatbotMessages');
        const div = document.createElement('div');
        div.className = 'topic-selector';
        div.innerHTML = `<h4>📚 اختر موضوعاً:</h4><div class="topic-grid">
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('transcription')">🧬 الاستنساخ</button>
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('traduction')">🔄 الترجمة</button>
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('immunite')">🛡️ المناعة</button>
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('photosynthese')">☀️ التركيب الضوئي</button>
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('respiration')">🔋 التنفس الخلوي</button>
            <button class="topic-chip" onclick="PersonalTutor.studyTopic('communication_nerveuse')">⚡ العصبونات</button>
        </div>`;
        msgs.appendChild(div);
        msgs.scrollTop = msgs.scrollHeight;
    },

    studyTopic(topic) {
        const inp = document.getElementById('chatbotInput');
        inp.value = `اشرح لي ${this.getTopicName(topic)} بطريقة فاينمان`;
        Chatbot.sendMessage();
    },

    studyWeakTopics() {
        const stats = LearningStats.getStats();
        const weak = Object.entries(stats.topicsStudied).filter(([_, d]) => (d.masteryLevel || 0) < 40).map(([t]) => t);
        if (weak.length === 0) {
            this.addMsg('<strong>🌟 ممتاز!</strong><p>لا توجد نقاط ضعف!</p>');
            this.changeTopic(); return;
        }
        this.addMsg(`<strong>⚠️ سنركز على:</strong><h3>${this.getTopicName(weak[0])}</h3>`);
        setTimeout(() => this.studyTopic(weak[0]), 1500);
    },

    startQuiz() {
        const stats = LearningStats.getStats();
        const topics = Object.keys(stats.topicsStudied);
        if (topics.length === 0) { this.addMsg('🤔 ادرس أولاً قبل الاختبار!'); return; }
        this.addMsg('<div class="tutor-mode-badge">🧪 اختبار</div><p>5 أسئلة من مواضيعك المدرسة. هيا بنا! 🚀</p>');
        setTimeout(() => this.askReviewQuestion(topics[Math.floor(Math.random() * topics.length)]), 2000);
    },

    showAchievements() {
        const all = LearningStats.getUnlockedAchievements();
        const unlocked = all.filter(a => a.unlocked);
        const locked = all.filter(a => !a.unlocked);
        this.addMsg(`<div class="tutor-mode-badge">🏆 إنجازاتي</div><h3>(${unlocked.length}/${all.length})</h3><div style="display:flex;flex-wrap:wrap;gap:8px;">${unlocked.map(a => `<div style="background:linear-gradient(135deg,#FFD700,#FFA500);padding:8px 12px;border-radius:12px;font-weight:700;">${a.name}</div>`).join('')}</div>${locked.length > 0 ? `<h3 style="margin-top:12px;">المقفلة:</h3><div style="display:flex;flex-wrap:wrap;gap:8px;">${locked.slice(0,4).map(a => `<div style="background:#E8E8E8;padding:8px 12px;border-radius:12px;color:#5A6A7A;opacity:0.6;">🔒 ${a.description}</div>`).join('')}</div>` : ''}<p style="margin-top:12px;">استمر 💪</p>`);
    },

    addMsg(content) {
        const msgs = document.getElementById('chatbotMessages');
        const d = document.createElement('div');
        d.className = 'message bot';
        d.innerHTML = `<div class="message-bubble" style="background:linear-gradient(135deg,#FFF9E6,#FEF3C7);border:2px solid #F59E0B;">${content}</div>`;
        msgs.appendChild(d);
        msgs.scrollTop = msgs.scrollHeight;
    },

    getTopicName(t) {
        return ({ transcription: '🧬 الاستنساخ', traduction: '🔄 الترجمة', immunite: '🛡️ المناعة', photosynthese: '☀️ التركيب الضوئي', respiration: '🔋 التنفس الخلوي', communication_nerveuse: '⚡ العصبونات', neurone: '⚡ العصبونات', adn: '🧬 ADN', enzymes: '⚗️ الإنزيمات' })[t] || t;
    }
};

if (typeof window !== 'undefined') window.PersonalTutor = PersonalTutor;
