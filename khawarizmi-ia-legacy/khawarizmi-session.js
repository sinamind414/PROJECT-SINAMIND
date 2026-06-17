// ═══════════════════════════════════════════════
// khawarizmi-session.js
// ═══════════════════════════════════════════════

const API_BASE = window.__KHW_API_BASE__ || (
    window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://khawarizmi-ia-production.up.railway.app'
);

function getCurrentLang() {
    return localStorage.getItem('khawarizmi-lang') || 'fr';
}

// ═══════════════════════════════════════════════
// I18N SESSION
// ═══════════════════════════════════════════════

const SESSION_I18N = {
    fr: {
        spinner_text       : "Khawarizmi prepare ta question...",
        verify_btn         : "Verifier ma reponse",
        next_btn           : "Question suivante",
        answer_label       : "✏️ Ta reponse",
        answer_hint        : "Ctrl+Entree pour valider",
        answer_placeholder : "Explique avec tes propres mots...",
        concepts_manquants : "❌ Concepts manquants :",
        session_complete   : "Session terminee !",
        bar_correct        : "Correct",
        bar_partiel        : "Partiel",
        bar_faux           : "A revoir",
        btn_continue       : "Continuer a reviser",
        btn_progress       : "Voir mes progres",
        fsrs_note          : "KHAWARIZMI planifie ta prochaine revision automatiquement 🧠",
        feedback_correct   : "✓ Correct",
        feedback_partiel   : "~ Partiel",
        feedback_faux      : "✗ A revoir",
        question_counter   : "Question",
        xp_label           : "XP",
        streak_label       : "jours",
    },
    ar: {
        spinner_text       : "...يُحضِّر الخوارزمي سؤالك",
        verify_btn         : "تحقق من إجابتي",
        next_btn           : "السؤال التالي",
        answer_label       : "✏️ إجابتك",
        answer_hint        : "Ctrl+Enter للإرسال",
        answer_placeholder : "...اشرح بكلماتك الخاصة",
        concepts_manquants : "❌ المفاهيم الناقصة :",
        session_complete   : "!انتهت الجلسة",
        bar_correct        : "صحيح",
        bar_partiel        : "جزئي",
        bar_faux           : "يراجع",
        btn_continue       : "مواصلة المراجعة",
        btn_progress       : "رؤية تقدمي",
        fsrs_note          : "يخطط الخوارزمي لمراجعتك القادمة تلقائياً 🧠",
        feedback_correct   : "✓ صحيح",
        feedback_partiel   : "~ جزئي",
        feedback_faux      : "✗ يحتاج مراجعة",
        question_counter   : "سؤال",
        xp_label           : "نقطة",
        streak_label       : "أيام",
    }
};

function i18n(key) {
    const lang = getCurrentLang();
    return SESSION_I18N[lang]?.[key] || SESSION_I18N.fr[key] || key;
}

function applySessionLang() {
    const spinnerText = document.querySelector('.spinner-text');
    if (spinnerText) spinnerText.textContent = i18n('spinner_text');

    const submitBtn = document.getElementById('submitAnswerBtn');
    if (submitBtn) {
        submitBtn.innerHTML = '<span>' + i18n('verify_btn') + '</span>' +
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
    }

    const nextBtn = document.getElementById('nextQuestionBtn');
    if (nextBtn) {
        nextBtn.innerHTML = i18n('next_btn') +
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
    }

    const answerLabel = document.querySelector('.session-answer-label');
    if (answerLabel) {
        answerLabel.innerHTML = i18n('answer_label') + ' <span class="session-hint">' + i18n('answer_hint') + '</span>';
    }

    const textarea = document.getElementById('studentAnswerInput');
    if (textarea) textarea.placeholder = i18n('answer_placeholder');

    const lc = document.querySelector('.legend-correct');
    const lp = document.querySelector('.legend-partiel');
    const lf = document.querySelector('.legend-faux');
    if (lc) lc.textContent = i18n('bar_correct');
    if (lp) lp.textContent = i18n('bar_partiel');
    if (lf) lf.textContent = i18n('bar_faux');

    const titleEl = document.getElementById('sessionCompleteTitle');
    if (titleEl) titleEl.textContent = i18n('session_complete');

    const restartBtn = document.getElementById('restartSessionBtn');
    const progressBtn = document.getElementById('showLandingBtn');
    if (restartBtn) restartBtn.textContent = i18n('btn_continue');
    if (progressBtn) progressBtn.textContent = i18n('btn_progress');

    const noteEl = document.querySelector('.session-complete-note');
    if (noteEl) noteEl.textContent = i18n('fsrs_note');

    const xpEl = document.getElementById('sessionXpValue');
    if (xpEl) {
        const xp = parseInt(localStorage.getItem('khawarizmi_xp')) || 0;
        xpEl.textContent = xp + ' ' + i18n('xp_label');
    }
    const streakEl = document.getElementById('sessionStreakValue');
    if (streakEl) {
        const streak = parseInt(localStorage.getItem('khawarizmi_streak')) || 5;
        streakEl.textContent = streak + ' ' + i18n('streak_label');
    }

    const counter = document.getElementById('questionCounter');
    if (counter && window.sessionStats) {
        counter.textContent = i18n('question_counter') + ' ' + (sessionStats.total + 1);
    }

    const manquantTitle = document.querySelector('.manquant-title');
    if (manquantTitle) manquantTitle.textContent = i18n('concepts_manquants');
}

// ═══════════════════════════════════════════════
// STATE MACHINE
// ═══════════════════════════════════════════════

const State = {
    LOADING_QUESTION : 'loading_question',
    QUESTION_READY   : 'question_ready',
    EVALUATING       : 'evaluating',
    SHOWING_FEEDBACK : 'showing_feedback',
    SESSION_COMPLETE : 'session_complete',
    ERROR            : 'error'
};

let currentState    = null;
let currentCard     = null;
let sessionStats    = { correct: 0, partiel: 0, faux: 0, total: 0 };
let _errorRetryCount = 0;

function transition(newState) {
    currentState = newState;
    render(newState);
}

// ═══════════════════════════════════════════════
// API
// ═══════════════════════════════════════════════

function getToken() {
    return localStorage.getItem('khawarizmi_token');
}

async function apiPost(endpoint, body) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
        method  : 'POST',
        headers : {
            'Content-Type' : 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(body)
    });
    
    if (res.status === 401) {
        localStorage.removeItem('khawarizmi_token');
        const hero = document.querySelector('.hero');
        if (hero) hero.style.display = 'block';
        const betaArea = document.getElementById('betaSessionArea');
        if (betaArea) betaArea.hidden = true;
        if (typeof window.openWaitlistModal === 'function') {
            window.openWaitlistModal();
        }
        throw new Error("401");
    }

    if (!res.ok) throw new Error(`${res.status}`);
    return res.json();
}

// ═══════════════════════════════════════════════
// LOGIQUE PRINCIPALE
// ═══════════════════════════════════════════════

const SESSION_TARGET = 10;
let _sessionQueue   = [];
let _askedQuestions = [];

function _showNextFromQueue() {
    if (_sessionQueue.length === 0) {
        transition(State.SESSION_COMPLETE);
        return;
    }

    const q = _sessionQueue.shift();
    _askedQuestions.push(q.question_id);

    const lang = getCurrentLang();
    currentCard = {
        question_id : q.question_id,
        texte       : lang === 'ar' && q.texte_ar ? q.texte_ar : (q.texte_fr || q.texte || ''),
        concept_cle : lang === 'ar' && q.concept_cle_ar
                      ? q.concept_cle_ar
                      : (q.concept_cle_fr || q.concept_cle || "مفهوم أساسي"),
        tentative   : q.tentative || 1
    };

    transition(State.QUESTION_READY);
}

async function loadNextQuestion() {
    if (_sessionQueue.length > 0) {
        _errorRetryCount = 0;
        console.log(`Queue locale: ${_sessionQueue.length} restantes`);
        _showNextFromQueue();
        return;
    }

    sessionStats   = { correct: 0, partiel: 0, faux: 0, total: 0 };
    _sessionQueue   = [];

    transition(State.LOADING_QUESTION);
    try {
        const lang = getCurrentLang();
        console.log('>>> API /api/session/next with:', { max_cards: SESSION_TARGET, lang, exclude_count: _askedQuestions.length });

        const data = await apiPost('/api/session/next', {
            max_cards : SESSION_TARGET,
            lang      : lang,
            exclude   : _askedQuestions
        });

        console.log('<<< Reponse brute:', JSON.stringify(data).slice(0, 500));
        console.log('<<< Cartes recues:', data?.session_queue?.length);

        const queue = data?.session_queue || [];

        if (queue.length === 0) {
            console.warn('Queue FSRS vide — fallback random');
            const fallback = await apiPost('/api/session/random', {
                max_cards : 5,
                lang      : lang,
                exclude   : _askedQuestions
            }).catch(() => null);

            if (fallback?.session_queue?.length > 0) {
                console.log('Fallback random:', fallback.session_queue.length, 'cartes');
                _sessionQueue = fallback.session_queue;
                _showNextFromQueue();
                return;
            }

            console.warn('Fallback vide aussi — SESSION_COMPLETE');
            transition(State.SESSION_COMPLETE);
            return;
        }

        _sessionQueue = queue;
        _errorRetryCount = 0;
        console.log('_sessionQueue initialisee avec', _sessionQueue.length, 'cartes');
        _showNextFromQueue();

    } catch (err) {
        console.error('loadNextQuestion:', err);
        transition(State.ERROR);
    }
}

async function submitAnswer() {
    const reponse = document.getElementById('studentAnswerInput').value.trim();
    if (!reponse) return; // Amina n'a rien écrit

    transition(State.EVALUATING);

    try {
        const result = await apiPost('/api/evaluate', {
            question_id   : currentCard.question_id,
            reponse_eleve : reponse,
            tentative     : currentCard.tentative,
            lang          : getCurrentLang()
        });

        // Mise à jour stats session
        sessionStats.total++;
        if (result.statut === 'CORRECT') sessionStats.correct++;
        else if (result.statut === 'PARTIEL') sessionStats.partiel++;
        else if (result.statut === 'FAUX') sessionStats.faux++;

        renderFeedback(result);
        transition(State.SHOWING_FEEDBACK);

    } catch (err) {
        console.error('submitAnswer:', err);
        transition(State.ERROR);
    }
}

// ═══════════════════════════════════════════════
// RENDER
// ═══════════════════════════════════════════════

function render(state) {
    const questionPanel  = document.getElementById('questionPanel');
    const feedbackPanel  = document.getElementById('feedbackPanel');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const completePanel  = document.getElementById('sessionCompletePanel');
    const submitBtn      = document.getElementById('submitAnswerBtn');
    const nextBtn        = document.getElementById('nextQuestionBtn');

    // Reset visibilité
    [questionPanel, feedbackPanel, 
     loadingSpinner, completePanel].forEach(el => {
        if (el) el.hidden = true;
    });

    switch (state) {

        case State.LOADING_QUESTION:
        case State.EVALUATING:
            if (loadingSpinner) loadingSpinner.hidden = false;
            break;

        case State.QUESTION_READY:
            if (loadingSpinner) loadingSpinner.hidden = true;

            document.getElementById('questionText').textContent = currentCard.texte;
            document.getElementById('conceptLabel').textContent = currentCard.concept_cle;

            applySessionLang();

            const t = document.getElementById('studentAnswerInput');
            if (t) { t.value = ''; t.focus(); }

            if (nextBtn) nextBtn.hidden = true;

            if (window.updateSessionProgress) window.updateSessionProgress();

            if (questionPanel) questionPanel.hidden = false;
            if (submitBtn)     submitBtn.hidden     = false;
            break;

        case State.SHOWING_FEEDBACK:
            if (questionPanel) questionPanel.hidden = false;
            if (feedbackPanel) feedbackPanel.hidden = false;
            if (submitBtn)     submitBtn.hidden     = true;
            if (nextBtn)       nextBtn.hidden       = false;
            break;

        case State.SESSION_COMPLETE:
            renderSessionComplete();
            if (completePanel) completePanel.hidden = false;
            break;

        case State.ERROR:
            if (loadingSpinner) loadingSpinner.hidden = true;
            _errorRetryCount++;
            if (_errorRetryCount >= 3) {
                showToast(getCurrentLang() === 'ar'
                    ? 'تعذر الاتصال بالخادم. حاول تحديث الصفحة.'
                    : 'Connexion au serveur impossible. Rechargez la page.');
                _errorRetryCount = 0;
            } else {
                showToast(getCurrentLang() === 'ar'
                    ? 'انقطع الاتصال. إعادة محاولة...'
                    : 'Connexion perdue. Réessaie...');
                setTimeout(loadNextQuestion, 3000);
            }
            break;
    }
}

function renderFeedback(result) {
    const feedbackBox  = document.getElementById('feedbackBox');
    const feedbackText = document.getElementById('feedbackText');
    const feedbackScore= document.getElementById('feedbackScore');
    const feedbackSts  = document.getElementById('feedbackStatus');
    const nextReview   = document.getElementById('nextReviewInfo');

    const borderColors = {
        'CORRECT': 'var(--success)',
        'PARTIEL': 'var(--amber)',
        'FAUX':    'var(--danger)',
        'ERREUR':  'var(--glass-border)'
    };

    if (feedbackBox) {
        feedbackBox.style.borderColor =
            borderColors[result.statut] || borderColors['ERREUR'];
    }

    if (feedbackScore) {
        feedbackScore.textContent = `${result.score}/10`;
        feedbackScore.style.color =
            result.statut === 'CORRECT' ? 'var(--success-light)' :
            result.statut === 'PARTIEL' ? 'var(--amber-light)' :
            result.statut === 'FAUX'    ? 'var(--danger-light)' :
            'var(--text-primary)';
    }

    if (feedbackSts) {
        const statusKey = { CORRECT: 'feedback_correct', PARTIEL: 'feedback_partiel', FAUX: 'feedback_faux' };
        feedbackSts.textContent = i18n(statusKey[result.statut] || 'feedback_faux');
        feedbackSts.className =
            'session-feedback-status ' + (result.statut || 'erreur').toLowerCase();
    }

    if (feedbackText) feedbackText.textContent = result.feedback;

    if (nextReview) {
        if (result.next_review_date) {
            const days = daysUntil(result.next_review_date);
            const lang = getCurrentLang();
            nextReview.textContent = lang === 'ar'
                ? (days === 0 ? 'المراجعة القادمة : اليوم' : `المراجعة القادمة خلال ${days} يوم`)
                : (days === 0 ? "Prochaine revision : aujourd'hui" : `Prochaine revision dans ${days} jour(s)`);
            nextReview.hidden = false;
        } else {
            nextReview.hidden = true;
        }
    }

    const manquantContainer = document.getElementById('manquantList');
    if (manquantContainer) {
        if (result.manquant?.length > 0) {
            let titleEl = manquantContainer.querySelector('.manquant-title');
            if (!titleEl) {
                titleEl = document.createElement('p');
                titleEl.className = 'manquant-title';
                manquantContainer.insertAdjacentElement('afterbegin', titleEl);
            }
            titleEl.textContent = i18n('concepts_manquants');

            manquantContainer.querySelectorAll('.keyword-tag').forEach(t => t.remove());

            result.manquant.forEach(m => {
                const tag = document.createElement('span');
                tag.className = 'keyword-tag';
                tag.style.cssText = `
                    background: hsla(0,75%,60%,0.12);
                    color: var(--danger-light);
                    border: 1px solid hsla(0,75%,60%,0.2);
                    padding: 3px 10px;
                    border-radius: var(--radius-full);
                    font-size: 0.82rem;
                    font-weight: 600;
                    display: inline-block;
                    margin: 2px;
                `;
                tag.textContent = m;
                manquantContainer.appendChild(tag);
            });
            manquantContainer.hidden = false;
        } else {
            manquantContainer.hidden = true;
        }
    }
}

function renderSessionComplete() {
    _askedQuestions = []; // ← reset pour permettre de revoir les questions

    applySessionLang();

    // Fix explicite du bouton continuer (évite "✓" parasite)
    const restartBtn = document.getElementById('restartSessionBtn');
    if (restartBtn) restartBtn.textContent = i18n('btn_continue');

    console.log('sessionStats:', { ...sessionStats });

    const total = sessionStats.total;
    const safeTotal   = total > 0 ? total   : 1;
    const safeCorrect = total > 0 ? sessionStats.correct : 0;
    const safePartiel = total > 0 ? sessionStats.partiel : 0;
    const safeFaux    = total > 0 ? sessionStats.faux    : 0;
    const pct = Math.round((safeCorrect / safeTotal) * 100);

    console.log('Bars:', {
        barC: document.getElementById('barCorrect'),
        barP: document.getElementById('barPartiel'),
        barF: document.getElementById('barFaux'),
        panel: document.getElementById('sessionCompletePanel'),
    });

    const isAr = getCurrentLang() === 'ar';
    const summaryEl = document.getElementById('sessionSummary');
    if (summaryEl) {
        const emoji = pct >= 80 ? '🏆' : pct >= 60 ? '💪' : '📖';
        summaryEl.innerHTML = isAr ? `
            <p><strong>${safeCorrect}</strong> صحيحة —
               <strong>${safePartiel}</strong> جزئية —
               <strong>${safeFaux}</strong> تحتاج مراجعة</p>
            <p style="font-size:1.2rem;font-weight:800;color:var(--text-primary)">
                ${emoji} النتيجة : ${pct}%
            </p>
            <p>${pct >= 80 ? 'ممتاز ! الخوارزمي سيباعد مراجعاتك.' : 'واصل ! المفاهيم الصعبة ستعود غداً.'}</p>
        ` : `
            <p><strong>${safeCorrect}</strong> correctes —
               <strong>${safePartiel}</strong> partielles —
               <strong>${safeFaux}</strong> a revoir</p>
            <p style="font-size:1.2rem;font-weight:800;color:var(--text-primary)">
                ${emoji} Score : ${pct}%
            </p>
            <p>${pct >= 80 ? 'Excellent ! Khawarizmi espace tes revisions.' : 'Continue ! Les concepts difficiles reviendront demain.'}</p>`;
    }

    setTimeout(() => {
        const barC = document.getElementById('barCorrect');
        const barP = document.getElementById('barPartiel');
        const barF = document.getElementById('barFaux');
        if (barC) barC.style.width = `${(safeCorrect / safeTotal) * 100}%`;
        if (barP) barP.style.width = `${(safePartiel / safeTotal) * 100}%`;
        if (barF) barF.style.width = `${(safeFaux    / safeTotal) * 100}%`;
        console.log('Bar widths applied:', {
            correct: barC?.style.width,
            partiel: barP?.style.width,
            faux:    barF?.style.width,
        });
    }, 500);
}

function daysUntil(isoDate) {
    const now  = new Date();
    const then = new Date(isoDate);
    const diff = Math.round((then - now) / (1000 * 60 * 60 * 24));
    return Math.max(0, diff);
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-error glass-card';
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.background = 'var(--danger, #EF4444)';
    toast.style.color = '#fff';
    toast.style.padding = '1rem';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ═══════════════════════════════════════════════
// EVENT LISTENERS
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    applySessionLang();

    document.getElementById('submitAnswerBtn')
        ?.addEventListener('click', submitAnswer);

    document.getElementById('nextQuestionBtn')
        ?.addEventListener('click', _showNextFromQueue);

    document.getElementById('studentAnswerInput')
        ?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) submitAnswer();
        });

    function persistHudState() {
        if (typeof GameState !== 'undefined') {
            localStorage.setItem('khawarizmi_xp', GameState.getXp());
            localStorage.setItem('khawarizmi_streak', GameState.getStreak());
        }
    }

    function restoreHudState() {
        const xp = parseInt(localStorage.getItem('khawarizmi_xp')) || 0;
        const streak = parseInt(localStorage.getItem('khawarizmi_streak')) || 5;
        if (typeof GameState !== 'undefined') {
            GameState.reset();
            GameState.addXp(xp);
        }
        const xpEl     = document.getElementById('sessionXpValue');
        const streakEl = document.getElementById('sessionStreakValue');
        if (xpEl)     xpEl.textContent     = `${xp} XP`;
        if (streakEl) streakEl.textContent  = `${streak} jours`;
    }

    // Check if token exists on load
    const hasToken = getToken();
    if (hasToken) {
        const hero = document.querySelector('.hero');
        if(hero) hero.style.display = 'none';
        const betaArea = document.getElementById('betaSessionArea');
        if(betaArea) betaArea.hidden = false;
        restoreHudState();
        loadNextQuestion();
    } else {
        syncSessionHud();
    }

    // Logout
    document.getElementById('sessionLogoutBtn')
        ?.addEventListener('click', () => {
            localStorage.removeItem('khawarizmi_token');
            localStorage.removeItem('khawarizmi_xp');
            localStorage.removeItem('khawarizmi_streak');
            const hero = document.querySelector('.hero');
            if (hero) hero.style.display = 'block';
            const betaArea = document.getElementById('betaSessionArea');
            if (betaArea) betaArea.hidden = true;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

    // Sync HUD session avec GameState de app.js
    function syncSessionHud() {
        const xpEl     = document.getElementById('sessionXpValue');
        const streakEl = document.getElementById('sessionStreakValue');
        if (xpEl && typeof GameState !== 'undefined') {
            xpEl.textContent = `${GameState.getXp()} ${i18n('xp_label')}`;
        }
        if (streakEl && typeof GameState !== 'undefined') {
            streakEl.textContent = `${GameState.getStreak()} ${i18n('streak_label')}`;
        }
        persistHudState();
    }

    // Sync après chaque évaluation
    const origRenderFeedback = renderFeedback;
    renderFeedback = (result) => {
        origRenderFeedback(result);
        syncSessionHud();
    };

    // Barre progression session
    function updateSessionProgress() {
        const fill = document.getElementById('sessionProgressFill');
        const counter = document.getElementById('questionCounter');
        if (fill && sessionStats.total > 0) {
            const pct = Math.min(100, (sessionStats.total / 10) * 100);
            fill.style.width = `${pct}%`;
            fill.setAttribute('aria-valuenow', pct);
        }
        if (counter) {
            counter.textContent = i18n('question_counter') + ' ' + (sessionStats.total + 1);
        }
    }

    // Exposer pour render()
    window.updateSessionProgress = updateSessionProgress;
});

// ═══════════════════════════════════════════════
// ZOOM SCHÉMAS SVT
// ═══════════════════════════════════════════════

function initSchemaZoom() {
    document.querySelectorAll('.schema-svt').forEach(img => {
        img.addEventListener('click', () => {
            const overlay = document.createElement('div');
            overlay.className = 'schema-overlay';
            overlay.innerHTML = `
                <div class="schema-zoom-container">
                    <img src="${img.src}" alt="${img.alt}">
                    <button class="schema-close">✕</button>
                </div>
            `;
            overlay.querySelector('.schema-close')
                .addEventListener('click', () => overlay.remove());
            overlay.addEventListener('click', e => {
                if (e.target === overlay) overlay.remove();
            });
            document.body.appendChild(overlay);
        });
        img.style.cursor = 'zoom-in';
    });
}

document.addEventListener('DOMContentLoaded', initSchemaZoom);
