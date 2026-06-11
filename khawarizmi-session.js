// ═══════════════════════════════════════════════
// khawarizmi-session.js
// ═══════════════════════════════════════════════

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://khawarizmi-ia-production-7837.up.railway.app';

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

let currentState   = null;
let currentCard    = null;  // { question_id, texte, tentative }
let sessionStats   = { correct: 0, partiel: 0, faux: 0, total: 0 };

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
    if (!res.ok) throw new Error(`${res.status}`);
    return res.json();
}

// ═══════════════════════════════════════════════
// LOGIQUE PRINCIPALE
// ═══════════════════════════════════════════════

async function loadNextQuestion() {
    transition(State.LOADING_QUESTION);
    try {
        const data = await apiPost('/api/session/next', { max_cards: 1 });

        // Queue vide → session terminée
        if (!data.session_queue || data.session_queue.length === 0) {
            transition(State.SESSION_COMPLETE);
            return;
        }

        currentCard = {
            question_id : data.session_queue[0].question_id,
            texte       : data.session_queue[0].texte,
            concept_cle : data.session_queue[0].concept_cle || "Concept Clé",
            tentative   : data.session_queue[0].tentative || 1
        };

        transition(State.QUESTION_READY);

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
            tentative     : currentCard.tentative
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
            // Injecter la question dans l'UI
            document.getElementById('questionText').textContent = 
                currentCard.texte;
            document.getElementById('conceptLabel').textContent = 
                currentCard.concept_cle;
            document.getElementById('studentAnswerInput').value = '';
            document.getElementById('studentAnswerInput').focus();

            if (questionPanel) questionPanel.hidden = false;
            if (submitBtn)     submitBtn.hidden     = false;
            if (nextBtn)       nextBtn.hidden       = true;
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
            showToast("Connexion perdue. Réessaie dans quelques secondes.");
            // Retry automatique après 3s
            setTimeout(loadNextQuestion, 3000);
            break;
    }
}

function renderFeedback(result) {
    const feedbackBox    = document.getElementById('feedbackBox');
    const feedbackText   = document.getElementById('feedbackText');
    const feedbackScore  = document.getElementById('feedbackScore');
    const nextReviewInfo = document.getElementById('nextReviewInfo');

    const colors = {
        'CORRECT' : 'var(--success, #10B981)',
        'PARTIEL' : 'var(--warning, #F59E0B)',
        'FAUX'    : 'var(--danger,  #EF4444)',
        'ERREUR'  : 'var(--muted,   #6B7280)'
    };

    if (feedbackBox) {
        feedbackBox.style.borderColor = colors[result.statut] || colors['ERREUR'];
    }
    if (feedbackText)  feedbackText.textContent  = result.feedback;
    if (feedbackScore) feedbackScore.textContent = `${result.score}/10`;

    if (nextReviewInfo) {
        if (result.next_review_date && result.source === 'GPT4O') {
            const days = daysUntil(result.next_review_date);
            nextReviewInfo.textContent = days === 0
                ? "Prochaine révision : aujourd'hui"
                : `Prochaine révision dans ${days} jour(s)`;
            nextReviewInfo.hidden = false;
        } else {
            nextReviewInfo.hidden = true;
        }
    }

    const manquantContainer = document.getElementById('manquantList');
    if (manquantContainer) {
        if (result.manquant && result.manquant.length > 0) {
            manquantContainer.innerHTML = result.manquant
                .map(m => `<span class="keyword-tag" style="background: rgba(239,68,68,0.2); color: #EF4444; padding: 4px 8px; border-radius: 4px; font-size: 0.9em; margin-right: 5px; display: inline-block; margin-bottom: 5px;">${m}</span>`)
                .join('');
            manquantContainer.hidden = false;
        } else {
            manquantContainer.hidden = true;
        }
    }
}

function renderSessionComplete() {
    const pct = sessionStats.total > 0
        ? Math.round((sessionStats.correct / sessionStats.total) * 100)
        : 0;

    const summaryEl = document.getElementById('sessionSummary');
    if (summaryEl) {
        summaryEl.innerHTML = `
            <p>${sessionStats.correct} / ${sessionStats.total} correctes</p>
            <p>Score de session : ${pct}%</p>
            <p>Reviens demain pour continuer.</p>
        `;
    }
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
    document.getElementById('submitAnswerBtn')
        ?.addEventListener('click', submitAnswer);

    document.getElementById('nextQuestionBtn')
        ?.addEventListener('click', loadNextQuestion);

    document.getElementById('studentAnswerInput')
        ?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) submitAnswer();
        });

    // Check if token exists on load
    if (getToken()) {
        const hero = document.querySelector('.hero');
        if(hero) hero.style.display = 'none';
        const betaArea = document.getElementById('betaSessionArea');
        if(betaArea) betaArea.hidden = false;
        loadNextQuestion();
    }
});
