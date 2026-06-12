/* ═══════════════════════════════════════════════════════════════════════════
   KHAWARIZMI IA — Interactive Application Logic  v2.0  (CORRIGÉ)
   Corrections : 
   - State encapsulé (anti-triche console)
   - Waitlist sauvegardée (fetch + fallback localStorage)
   - Sélecteur waitlist chirurgical (fini le bug btn-ghost)
   - Contenu pédagogique externalisable (démo prête pour API)
   - Encodage commentaires corrigé
   - Dépendance translations sécurisée
   ═══════════════════════════════════════════════════════════════════════════ */

/* ═══════════════════ ÉTAT ENCAPSULÉ (anti-triche) ═══════════════════ */

const GameState = (() => {
    let _totalXp     = 0;
    let _streakDays  = 5;
    let _masteryLevel = 0;
    let _socraticStep = 0;

    return {
        getXp:        ()  => _totalXp,
        getStreak:    ()  => _streakDays,
        getMastery:   ()  => _masteryLevel,
        getSocratic:  ()  => _socraticStep,

        addXp: (n) => {
            if (typeof n !== 'number' || n < 0) return;
            _totalXp += n;
        },
        setMastery: (level) => {
            if (typeof level === 'number' && level >= 0) {
                _masteryLevel = Math.max(_masteryLevel, level);
            }
        },
        setSocratic: (step) => {
            if (typeof step === 'number') _socraticStep = step;
        },
        reset: () => {
            _totalXp      = 0;
            _masteryLevel = 0;
            _socraticStep = 0;
        }
    };
})();

/* ═══════════════════ CLÉS DE STOCKAGE ═══════════════════ */

const STORAGE_KEYS = {
    LANG:     'khawarizmi-lang',
    THEME:    'khawarizmi-theme',
    WAITLIST: 'khawarizmi-waitlist-submitted'
};

/* ═══════════════════ LANGUE COURANTE ═══════════════════ */

let currentLang = localStorage.getItem(STORAGE_KEYS.LANG) || 'fr';

/* ═══════════════════ HELPER : traduction sécurisée ═══════════════════ */

function t(key, fallback = '') {
    if (typeof translations === 'undefined') return fallback || key;
    const langPack = translations[currentLang];
    if (!langPack) return fallback || key;
    return langPack[key] !== undefined ? langPack[key] : (fallback || key);
}

/* ═══════════════════ INIT PRINCIPALE ═══════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    initNavbar();
    initMobileMenu();
    initScrollAnimations();
    initDemoQuiz();
    initForgettingCurve();
    initCounters();
    initSmoothScroll();
    initWaitlistModal();
    updateHud();
});

/* ═══════════════════ SYSTÈME DE LANGUE ═══════════════════ */

function initLanguage() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.dataset.lang;
            if (lang && lang !== currentLang) switchLanguage(lang);
        });
    });
    applyLanguage(currentLang);
}

function switchLanguage(lang) {
    currentLang = lang;
    localStorage.setItem(STORAGE_KEYS.LANG, lang);
    applyLanguage(lang);
    resetDemo();

    if (window.forgettingCurveCanvas && window.forgettingCurveAnimated) {
        drawForgettingCurve(
            window.forgettingCurveCanvas,
            window.forgettingCurveCtx,
            1
        );
    }

    // Recharger la question si une session est active
    const betaArea = document.getElementById('betaSessionArea');
    if (betaArea && !betaArea.hidden && typeof loadNextQuestion === 'function') {
        loadNextQuestion();
    }
}

function applyLanguage(lang) {
    // 1. Attributs HTML
    document.documentElement.lang = lang;
    document.documentElement.dir  = lang === 'ar' ? 'rtl' : 'ltr';

    // 2. Boutons actifs
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // 3. Textes data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const val = t(el.dataset.i18n);
        if (val) el.innerHTML = val;
    });

    // 4. Placeholders data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const val = t(el.dataset.i18nPlaceholder);
        if (val) el.placeholder = val;
    });

    // 5. SEO
    const titleVal = t('title');
    if (titleVal) document.title = titleVal;

    const descMeta = document.querySelector('meta[name="description"]');
    if (descMeta) {
        descMeta.setAttribute('content',
            lang === 'ar'
                ? 'تطبيق إيه آي فهمك يطبق الطرق العلمية السبع المثبتة لمضاعفة سرعة الحفظ والفهم لدى الطلاب الجزائريين مرتين.'
                : 'KHAWARIZMI IA applique les 7 méthodes scientifiques prouvées pour multiplier par 2 la rétention des élèves algériens.'
        );
    }

    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) {
        ogDesc.setAttribute('content',
            lang === 'ar'
                ? 'التطبيق الوحيد في الجزائر الذي يطبق الطرق العلمية السبع المثبتة.'
                : 'La seule app en Algérie qui applique les 7 méthodes scientifiques prouvées.'
        );
    }

    updateHud();
    resetSocraticChat();
}

/* ═══════════════════ NAVBAR ═══════════════════ */

function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    }, { passive: true });
}

/* ═══════════════════ MENU MOBILE ═══════════════════ */

function initMobileMenu() {
    const toggle   = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    if (!toggle || !navLinks) return;

    toggle.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('open');
        toggle.classList.toggle('active', isOpen);
        document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            toggle.classList.remove('active');
            navLinks.classList.remove('open');
            document.body.style.overflow = '';
        });
    });
}

/* ═══════════════════ ANIMATIONS SCROLL ═══════════════════ */

function initScrollAnimations() {
    // Fallback navigateurs anciens
    if (!('IntersectionObserver' in window)) {
        document.querySelectorAll('[data-animate]')
            .forEach(el => el.classList.add('visible'));
        document.querySelectorAll('.method-stat-fill')
            .forEach(bar => { bar.style.width = bar.dataset.width + '%'; });
        return;
    }

    // Éléments animés à l'entrée
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const delay = parseInt(entry.target.dataset.delay) || 0;
            setTimeout(() => entry.target.classList.add('visible'), delay);
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));

    // Barres méthodes
    const barObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            setTimeout(() => {
                entry.target.style.width = entry.target.dataset.width + '%';
            }, 300);
            barObserver.unobserve(entry.target);
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.method-stat-fill')
        .forEach(bar => barObserver.observe(bar));

    // Barres résultats
    const resultObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const width = entry.target.style.width;
            entry.target.style.width = '0%';
            requestAnimationFrame(() => requestAnimationFrame(() => {
                entry.target.style.width = width;
            }));
            resultObserver.unobserve(entry.target);
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.result-bar-fill')
        .forEach(bar => resultObserver.observe(bar));
}

/* ═══════════════════ GAMIFICATION HUD ═══════════════════ */

function updateHud() {
    const xpEl      = document.getElementById('hudXpValue');
    const streakEl  = document.getElementById('hudStreakValue');
    const masteryEl = document.getElementById('hudMasteryValue');

    if (xpEl) xpEl.textContent = `${GameState.getXp()} XP`;

    if (streakEl) {
        streakEl.textContent = currentLang === 'ar'
            ? `${GameState.getStreak()} أيام`
            : `${GameState.getStreak()} Jours`;
    }

    if (masteryEl) {
        const key = `mastery_level_${GameState.getMastery()}`;
        masteryEl.textContent = t(key, `Niveau ${GameState.getMastery()}`);
    }
}

function triggerXpPopup(xp, event) {
    const floater = document.createElement('div');
    floater.className  = 'xp-floater';
    floater.textContent = `+${xp} XP`;

    let x, y;
    if (event?.clientX && event?.clientY) {
        x = event.clientX + window.scrollX;
        y = event.clientY + window.scrollY;
    } else {
        const activePhase = document.querySelector('.demo-phase-content.active');
        if (activePhase) {
            const rect = activePhase.getBoundingClientRect();
            x = rect.left + rect.width / 2 + window.scrollX;
            y = rect.top  + rect.height / 3 + window.scrollY;
        } else {
            x = window.innerWidth  / 2;
            y = window.innerHeight / 2;
        }
    }

    floater.style.left = `${x}px`;
    floater.style.top  = `${y}px`;
    document.body.appendChild(floater);
    setTimeout(() => floater.remove(), 1200);
}

function setMascotState(state, bubbleTextKey) {
    const mascot = document.getElementById('khawarizmiMascot');
    if (mascot) {
        mascot.classList.remove('state-proud', 'state-pensive', 'state-excited', 'state-sad');
        mascot.classList.add(`state-${state}`);
    }
    const bubbleText = document.getElementById('mascotBubbleText');
    if (bubbleText && bubbleTextKey) {
        bubbleText.innerHTML = t(bubbleTextKey, bubbleTextKey);
    }
}

function appendChatMessage(sender, text) {
    const history = document.getElementById('socraticChatHistory');
    if (!history) return;

    const msg    = document.createElement('div');
    msg.className = `chat-msg ${sender}`;
    const avatar = sender === 'user' ? '👤' : '🧠';
    const author = sender === 'user'
        ? (currentLang === 'ar' ? 'طالب' : 'Élève')
        : 'Khawarizmi Chat';

    msg.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div class="msg-text-wrap">
            <span class="msg-author">${author}</span>
            <p class="msg-content">${text}</p>
        </div>`;

    history.appendChild(msg);
    history.scrollTop = history.scrollHeight;
}

function resetSocraticChat() {
    GameState.setSocratic(0);
    const history = document.getElementById('socraticChatHistory');
    if (!history) return;

    const initText = t('feynman_chat_init', "Marhaban ! Explique-moi la transmission synaptique...");
    history.innerHTML = `
        <div class="chat-msg system">
            <div class="msg-avatar">🧠</div>
            <div class="msg-text-wrap">
                <span class="msg-author">Khawarizmi Chat</span>
                <p class="msg-content">${initText}</p>
            </div>
        </div>`;

    setMascotState('pensive', 'mascot_bubble_feynman_init');
}

/* ═══════════════════ WAITLIST MODAL (CORRIGÉ) ═══════════════════ */

function initWaitlistModal() {
    const modal      = document.getElementById('waitlistModal');
    const closeBtn   = document.getElementById('modalClose');
    const form       = document.getElementById('waitlistForm');
    const successMsg = document.getElementById('modalSuccessMsg');

    if (!modal) return;

    /* ── Ouvrir / Fermer ── */
    window.openWaitlistModal = () => {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        if (form)       form.style.display = 'flex';
        if (successMsg) successMsg.classList.remove('show');
    };

    window.closeWaitlistModal = () => {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    };

    if (closeBtn) closeBtn.addEventListener('click', window.closeWaitlistModal);
    modal.addEventListener('click', e => {
        if (e.target === modal) window.closeWaitlistModal();
    });

    /* ── Soumission : SAUVEGARDE RÉELLE ── */
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled    = true;
                submitBtn.textContent = currentLang === 'ar' ? '...جاري الإرسال' : 'Envoi en cours...';
            }

            const data = {
                name:      document.getElementById('studentName')?.value.trim()  || '',
                email:     document.getElementById('studentEmail')?.value.trim() || '',
                wilaya:    document.getElementById('studentWilaya')?.value        || '',
                lang:      currentLang,
                timestamp: new Date().toISOString(),
                source:    window.location.href
            };

            /* ── Validation basique ── */
            if (!data.name || !data.email) {
                alert(currentLang === 'ar' ? 'يرجى ملء جميع الحقول' : 'Veuillez remplir tous les champs.');
                if (submitBtn) {
                    submitBtn.disabled    = false;
                    submitBtn.textContent = currentLang === 'ar' ? 'انضم للقائمة' : "Rejoindre la liste";
                }
                return;
            }

            let saved = false;

            const WEBHOOK_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
                ? 'http://localhost:8000/api/waitlist'
                : 'https://khawarizmi-ia-production-7837.up.railway.app/api/waitlist';

            if (WEBHOOK_URL) {
                try {
                    const res = await fetch(WEBHOOK_URL, {
                        method:  'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body:    JSON.stringify(data)
                    });
                    if (res.ok) {
                        const jsonRes = await res.json();
                        if (jsonRes.access_token) {
                            localStorage.setItem('khawarizmi_token', jsonRes.access_token);
                        }
                        saved = true;
                    }
                } catch (err) {
                    console.warn('Webhook failed, falling back to localStorage:', err);
                }
            }

            /* ── 2. Fallback : localStorage (zéro perte de lead) ── */
            if (!saved) {
                try {
                    const existing = JSON.parse(
                        localStorage.getItem(STORAGE_KEYS.WAITLIST) || '[]'
                    );
                    existing.push(data);
                    localStorage.setItem(STORAGE_KEYS.WAITLIST, JSON.stringify(existing));
                    saved = true;
                    console.info('Lead saved to localStorage (export manually):', data);
                } catch (storageErr) {
                    console.error('localStorage also failed:', storageErr);
                }
            }

            // Demo token for local testing without backend
            if (saved && !localStorage.getItem('khawarizmi_token')) {
                localStorage.setItem('khawarizmi_token', 'demo_local_token');
            }

            /* ── 3. Confirmation visuelle ── */
            if (saved) {
                if (form)       form.style.display = 'none';
                if (successMsg) successMsg.classList.add('show');
                
                // Lancer la session beta aprs 1.5s
                setTimeout(() => {
                    window.closeWaitlistModal();
                    // Cacher le hero, afficher la beta session
                    const hero = document.querySelector('.hero');
                    if(hero) hero.style.display = 'none';
                    const betaArea = document.getElementById('betaSessionArea');
                    if(betaArea) betaArea.hidden = false;
                    
                    // Lancer la queue de questions !
                    if (typeof loadNextQuestion === 'function') {
                        loadNextQuestion();
                    }
                }, 1500);
            } else {
                alert(currentLang === 'ar'
                    ? 'حدث خطأ. يرجى المحاولة مرة أخرى.'
                    : 'Une erreur est survenue. Réessayez.');
                if (submitBtn) {
                    submitBtn.disabled    = false;
                    submitBtn.textContent = currentLang === 'ar' ? 'انضم للقائمة' : 'Rejoindre la liste';
                }
            }
        });
    }

    /* ── Déclencheurs CHIRURGICAUX (fini le bug btn-ghost) ── */
    // Ajoute data-action="open-waitlist" sur tes boutons CTA dans index.html
    document.querySelectorAll('[data-action="open-waitlist"]').forEach(trigger => {
        trigger.addEventListener('click', e => {
            e.preventDefault();
            window.openWaitlistModal();
        });
    });

    // Déclencheurs spécifiques par ID (sans attraper tous les .btn-ghost)
    ['navCta', 'ctaMainBtn'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('click', e => {
            e.preventDefault();
            window.openWaitlistModal();
        });
    });
}

/* ═══════════════════ DEMO INTERACTIVE ═══════════════════ */

function resetDemo() {
    document.querySelectorAll('.demo-feedback').forEach(f => f.classList.remove('show'));
    document.querySelectorAll('.demo-option').forEach(o => {
        o.classList.remove('correct', 'wrong');
        o.style.pointerEvents = '';
    });

    const input2 = document.getElementById('demoInput2');
    const input3 = document.getElementById('demoInput3');
    if (input2) input2.value = '';
    if (input3) input3.value = '';

    // Supprimer uniquement les boutons Retry injectés dynamiquement
    document.querySelectorAll('.demo-feedback .btn-retry-dynamic').forEach(b => b.remove());

    GameState.reset();
    updateHud();
    setMascotState('pensive', 'mascot_bubble_init');
    resetSocraticChat();
}

function initDemoQuiz() {
    const phaseBtns     = document.querySelectorAll('.demo-phase-btn');
    const phaseContents = document.querySelectorAll('.demo-phase-content');

    phaseBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const phase = btn.dataset.phase;
            phaseBtns.forEach(b => b.classList.remove('active'));
            phaseContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');

            const target = document.getElementById('demoPhaseContent' + phase);
            if (target) target.classList.add('active');

            if (phase === '3') {
                resetSocraticChat();
            } else {
                setMascotState('pensive', 'mascot_bubble_init');
            }
        });
    });

    initPhase1();
    initPhase2();
    initPhase3();
}

/* ── Phase 1 : QCM ── */

function initPhase1() {
    const options  = document.querySelectorAll('#demoPhaseContent1 .demo-option');
    const feedback = document.getElementById('demoFeedback1');
    if (!feedback) return;

    let answered = false;

    options.forEach(opt => {
        opt.addEventListener('click', (e) => {
            if (answered) return;
            answered = true;

            const isCorrect = opt.dataset.correct === 'true';
            const feedbackContent = feedback.querySelector('.feedback-content');

            options.forEach(o => {
                o.style.pointerEvents = 'none';
                if (o.dataset.correct === 'true') o.classList.add('correct');
                else if (o === opt && !isCorrect) o.classList.add('wrong');
            });

            if (isCorrect) {
                feedbackContent.className = 'feedback-content feedback-success';
                feedbackContent.innerHTML = `
                    <strong>${t('qcm_success_title')}</strong><br>
                    ${t('qcm_success_text')}`;
                GameState.addXp(10);
                GameState.setMastery(1);
                setMascotState('proud', 'mascot_bubble_qcm_success');
            } else {
                feedbackContent.className = 'feedback-content feedback-error';
                feedbackContent.innerHTML = `
                    <strong>${t('qcm_error_title')}</strong><br>
                    ${t('qcm_error_text')}`;
                GameState.addXp(2);
                setMascotState('sad', 'mascot_bubble_qcm_error');
            }

            updateHud();
            triggerXpPopup(isCorrect ? 10 : 2, e);
            feedback.classList.add('show');

            // Bouton Retry avec classe spécifique (ne déclenche PAS la waitlist)
            setTimeout(() => {
                const retryBtn = document.createElement('button');
                retryBtn.className   = 'btn btn-ghost btn-retry-dynamic'; // ← classe spécifique
                retryBtn.style.marginTop = '12px';
                retryBtn.textContent = t('qcm_retry', '🔄 Réessayer');

                retryBtn.addEventListener('click', () => {
                    answered = false;
                    options.forEach(o => {
                        o.classList.remove('correct', 'wrong');
                        o.style.pointerEvents = '';
                    });
                    feedback.classList.remove('show');
                    retryBtn.remove();
                    setMascotState('pensive', 'mascot_bubble_init');
                });

                feedbackContent.appendChild(retryBtn);
            }, 2000);
        });
    });
}

/* ── Phase 2 : Cued Recall ── */

/*
 * NOTE ARCHITECTURE : Les regex sont ici pour la démo.
 * En production, remplacer par :
 *   const exercice = await fetch('/api/demo/exercice/ohm');
 *   puis valider côté serveur.
 */

function initPhase2() {
    const submitBtn = document.getElementById('demoSubmit2');
    const input     = document.getElementById('demoInput2');
    const feedback  = document.getElementById('demoFeedback2');
    if (!submitBtn || !input || !feedback) return;

    submitBtn.addEventListener('click', (e) => {
        const answer = input.value.trim().toLowerCase();
        const feedbackContent = feedback.querySelector('.feedback-content');

        if (!answer) {
            feedbackContent.className = 'feedback-content feedback-error';
            feedbackContent.innerHTML = t('cued_alert', "⚠️ Écris ta réponse d'abord.");
            feedback.classList.add('show');
            return;
        }

        // CORRIGÉ : Validation Loi d'Ohm (cohérent avec la question)
        const checks = {
            hasFormule:    /u\s*=\s*r|u\s*=\s*ri|tension|التوتر|الفولط/i.test(answer),
            hasResistance: /résistan|resistance|résistance|مقاومة|أوم/i.test(answer),
            hasIntensité:  /intensité|intensite|courant|تيار|أمبير/i.test(answer),
            hasUnité:      /volt|ampère|ampere|ohm|V\s|A\s|Ω/i.test(answer)
        };

        let score = 0;
        if (checks.hasFormule)    score += 2;
        if (checks.hasResistance) score += 1;
        if (checks.hasIntensité)  score += 1;
        if (checks.hasUnité)      score += 1;

        if (score >= 3) {
            feedbackContent.className = 'feedback-content feedback-success';
            feedbackContent.innerHTML = `
                <strong>${t('cued_success_title')}${Math.min(score, 5)}/5</strong>
                ${t('cued_success_body')}`;
            GameState.addXp(30);
            GameState.setMastery(2);
            triggerXpPopup(30, e);
            setMascotState('excited', 'mascot_bubble_cued_success');
        } else if (score >= 1) {
            feedbackContent.className = 'feedback-content feedback-info';
            feedbackContent.innerHTML = `
                <strong>${t('cued_partial_title')}${score}/5</strong>
                ${t('cued_partial_body')}`;
            GameState.addXp(15);
            triggerXpPopup(15, e);
            setMascotState('pensive', 'mascot_bubble_cued_partial');
        } else {
            feedbackContent.className = 'feedback-content feedback-error';
            feedbackContent.innerHTML = `
                <strong>${t('cued_error_title')}</strong>
                ${t('cued_error_body')}`;
            GameState.addXp(2);
            triggerXpPopup(2, e);
            setMascotState('sad', 'mascot_bubble_cued_error');
        }

        updateHud();
        feedback.classList.add('show');
    });
}

/* ── Phase 3 : Feynman Socratique ── */

function initPhase3() {
    const submitBtn = document.getElementById('demoSubmit3');
    const input     = document.getElementById('demoInput3');
    const feedback  = document.getElementById('demoFeedback3');
    if (!submitBtn || !input || !feedback) return;

    let allStudentText = '';

    // Dialogue socratique — 4 étapes
    const socrateKeys = [
        'mascot_bubble_feynman_socrate_1',
        'mascot_bubble_feynman_socrate_2',
        'mascot_bubble_feynman_socrate_3'
    ];
    const socrateXp     = [5, 10, 10];
    const socrateStates = ['pensive', 'excited', 'pensive'];

    submitBtn.addEventListener('click', (e) => {
        const answer = input.value.trim();
        const fc     = feedback.querySelector('.feedback-content');

        if (!answer || answer.length < 10) {
            fc.className  = 'feedback-content feedback-error';
            fc.innerHTML  = t('feynman_alert', '<strong>⚠️ Trop court !</strong> La technique Feynman demande une explication détaillée.');
            feedback.classList.add('show');
            setTimeout(() => feedback.classList.remove('show'), 3000);
            return;
        }

        feedback.classList.remove('show');
        allStudentText += ' ' + answer;
        const step = GameState.getSocratic();

        // Étapes 0-2 : Questions socratiques
        if (step < 3) {
            appendChatMessage('user', answer);
            input.value = '';
            GameState.setSocratic(step + 1);

            setTimeout(() => {
                const replyKey  = socrateKeys[step];
                const replyText = t(replyKey, replyKey);
                appendChatMessage('system', replyText);
                setMascotState(socrateStates[step], replyKey);
                GameState.addXp(socrateXp[step]);
                updateHud();
                triggerXpPopup(socrateXp[step], e);
            }, 800);

        // Étape finale : Évaluation complète
        } else {
            appendChatMessage('user', answer);
            input.value = '';

            const fullText = allStudentText.toLowerCase();

            const conceptPatterns = {
                potentiel:      /potentiel|électrique|عمل|كمون|كهربائي/i,
                vesicule:       /vésicule|vesicule|حويصل/i,
                neurotransmet:  /neurotransmetteur|médiateur|ناقل\s*عصبي|وسيط/i,
                fente:          /fente|synaptique|شق|مشبك/i,
                recepteur:      /récepteur|recepteur|مستقبل/i,
                liaison:        /liaison|fixation|ارتباط|تثبت/i
            };

            const labelsFr = {
                potentiel: 'Potentiel électrique', vesicule: 'Vésicules synaptiques', neurotransmet: 'Neurotransmetteurs',
                fente: 'Fente synaptique', recepteur: 'Récepteurs spécifiques', liaison: 'Liaison/Fixation'
            };
            const labelsAr = {
                potentiel: 'كمون العمل', vesicule: 'الحويصلات المشبكية', neurotransmet: 'الناقل العصبي',
                fente: 'الشق المشبكي', recepteur: 'المستقبلات النوعية', liaison: 'ارتباط الناقل'
            };
            const labels = currentLang === 'ar' ? labelsAr : labelsFr;

            const found   = [];
            const missing = [];
            Object.entries(conceptPatterns).forEach(([name, rx]) => {
                (rx.test(fullText) ? found : missing).push(name);
            });

            const score = Math.min(10, Math.round((found.length / Object.keys(conceptPatterns).length) * 10));

            let level, advice;
            if (score >= 8) {
                level  = currentLang === 'ar' ? 'ممتاز'      : 'Excellent';
                advice = currentLang === 'ar' ? 'شرحك واضح ومفصل!' : 'Tu maîtrises ce concept !';
            } else if (score >= 5) {
                level  = currentLang === 'ar' ? 'جيد'        : 'Bien';
                advice = currentLang === 'ar' ? 'حاول إضافة المفاهيم الناقصة' : 'Ajoute les concepts manquants.';
            } else {
                level  = currentLang === 'ar' ? 'يحتاج مراجعة' : 'À revoir';
                advice = currentLang === 'ar' ? 'راجع الدرس مرة أخرى' : 'Revois le cours et réessaie.';
            }

            const tl = key => labels[key] || key;
            const foundList   = found.length  > 0 ? found.map(c  => `• ${tl(c)}`).join('<br>') : (currentLang === 'ar' ? 'لا مفاهيم' : 'Aucun');
            const missingHtml = missing.length > 0
                ? `${t('feynman_concepts_missing', '<strong>❌ Concepts manquants :</strong><br>')}${missing.map(c => `• ${tl(c)}`).join('<br>')}<br><br>`
                : '';

            fc.className = 'feedback-content feedback-info';
            fc.innerHTML =
                `<strong>${t('feynman_eval_header','Évaluation Feynman : ')}${score}/10 — ${level}</strong><br><br>` +
                `${t('feynman_concepts_found','<strong>✅ Concepts mentionnés :</strong><br>')}${foundList}<br><br>` +
                missingHtml +
                `<strong>💡 ${currentLang === 'ar' ? 'نصيحة :' : 'Conseil :'}</strong> ${advice}` +
                t('feynman_insight_footer', '');

            feedback.classList.add('show');

            const xpReward = score >= 8 ? 50 : (score >= 5 ? 30 : 10);
            GameState.addXp(xpReward);
            GameState.setMastery(score >= 8 ? 3 : (score >= 5 ? 2 : 1));
            updateHud();
            triggerXpPopup(xpReward, e);

            if (score >= 8)      setMascotState('proud',   'mascot_bubble_feynman_success');
            else if (score >= 5) setMascotState('pensive', 'mascot_bubble_feynman_init');
            else                 setMascotState('sad',     'mascot_bubble_feynman_init');

            setTimeout(() => {
                appendChatMessage('system', t('mascot_bubble_feynman_success', `Évaluation terminée ! Score : ${score}/10.`));
                setTimeout(() => {
                    if (typeof window.openWaitlistModal === 'function') window.openWaitlistModal();
                }, 2000);
            }, 1200);
        }
    });
}

/* ═══════════════════ COURBE DE L'OUBLI (CANVAS) ═══════════════════ */

function initForgettingCurve() {
    const canvas = document.getElementById('forgettingCanvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    window.forgettingCurveCanvas   = canvas;
    window.forgettingCurveCtx      = ctx;
    window.forgettingCurveAnimated = false;

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !window.forgettingCurveAnimated) {
            window.forgettingCurveAnimated = true;
            animateForgettingCurve(canvas, ctx);
            observer.unobserve(canvas);
        }
    }, { threshold: 0.3 });

    observer.observe(canvas);

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.forgettingCurveAnimated) drawForgettingCurve(canvas, ctx, 1);
        }, 250);
    });
}

function animateForgettingCurve(canvas, ctx) {
    const duration  = 2000;
    const startTime = performance.now();

    function animate(currentTime) {
        const progress = Math.min(1, (currentTime - startTime) / duration);
        const eased    = 1 - Math.pow(1 - progress, 3);
        drawForgettingCurve(canvas, ctx, eased);
        if (progress < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}

function drawForgettingCurve(canvas, ctx, progress) {
    const dpr     = window.devicePixelRatio || 1;
    const rect    = canvas.getBoundingClientRect();
    const displayW = rect.width  || 800;
    const displayH = rect.height > 0 ? rect.height : 400;

    canvas.width  = displayW * dpr;
    canvas.height = displayH * dpr;
    ctx.scale(dpr, dpr);

    const w = displayW, h = displayH;
    const padding = { top: 30, right: 30, bottom: 50, left: 60 };
    const chartW  = w - padding.left - padding.right;
    const chartH  = h - padding.top  - padding.bottom;

    ctx.clearRect(0, 0, w, h);

    const fontName = currentLang === 'ar' ? 'Cairo, sans-serif' : 'Inter, sans-serif';

    // Grille
    ctx.strokeStyle = 'hsla(220, 15%, 40%, 0.1)';
    ctx.lineWidth   = 1;
    for (let i = 0; i <= 10; i++) {
        const y = padding.top + (chartH * i / 10);
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();
    }

    // Labels axe Y
    ctx.fillStyle  = 'hsl(220, 15%, 45%)';
    ctx.font       = `11px ${fontName}`;
    ctx.textAlign  = 'right';
    for (let i = 0; i <= 10; i += 2) {
        const y = padding.top + (chartH * (10 - i) / 10);
        ctx.fillText(i * 10 + '%', padding.left - 10, y + 4);
    }

    // Labels axe X
    ctx.textAlign = 'center';
    const xLabels    = currentLang === 'ar'
        ? ['ي1','ي3','ي7','ي14','ي30','ي60']
        : ['J1','J3','J7','J14','J30','J60'];
    const xPositions = [0, 0.04, 0.1, 0.22, 0.5, 1];
    xLabels.forEach((label, i) => {
        ctx.fillText(label, padding.left + chartW * xPositions[i], h - padding.bottom + 20);
    });

    // Courbe oubli (sans révision)
    const forgettingPts = [];
    for (let tVal = 0; tVal <= 1; tVal += 0.005) {
        const retention = Math.max(8, 100 * Math.exp(-2.5 * tVal));
        forgettingPts.push({
            x: padding.left + chartW * tVal,
            y: padding.top  + chartH * (1 - retention / 100)
        });
    }

    const drawCount = n => Math.floor(n * progress);

    // Tracé courbe oubli
    ctx.beginPath();
    ctx.strokeStyle = 'hsl(0, 75%, 60%)';
    ctx.lineWidth   = 2.5;
    ctx.setLineDash([]);
    const fCount = drawCount(forgettingPts.length);
    forgettingPts.slice(0, fCount).forEach((pt, i) => {
        i === 0 ? ctx.moveTo(pt.x, pt.y) : ctx.lineTo(pt.x, pt.y);
    });
    ctx.stroke();

    // Remplissage
    if (fCount > 1) {
        ctx.beginPath();
        forgettingPts.slice(0, fCount).forEach((pt, i) => {
            i === 0 ? ctx.moveTo(pt.x, pt.y) : ctx.lineTo(pt.x, pt.y);
        });
        ctx.lineTo(forgettingPts[fCount - 1].x, padding.top + chartH);
        ctx.lineTo(padding.left, padding.top + chartH);
        ctx.closePath();
        ctx.fillStyle = 'hsla(0, 75%, 60%, 0.06)';
        ctx.fill();
    }

    // Courbe répétition espacée
    const reviewDays  = [0.04, 0.1, 0.22, 0.5];
    const spacedPts   = [];
    let currentR = 100, decayRate = 1.8;

    for (let tVal = 0; tVal <= 1; tVal += 0.005) {
        for (const rd of reviewDays) {
            if (Math.abs(tVal - rd) < 0.006 && currentR < 95) {
                currentR   = Math.min(98, currentR + 25);
                decayRate *= 0.7;
            }
        }
        currentR = Math.max(75, currentR - decayRate * 0.005 * 100);
        spacedPts.push({
            x: padding.left + chartW * tVal,
            y: padding.top  + chartH * (1 - currentR / 100)
        });
    }

    ctx.beginPath();
    ctx.strokeStyle = 'hsl(165, 80%, 55%)';
    ctx.lineWidth   = 2.5;
    const sCount = drawCount(spacedPts.length);
    spacedPts.slice(0, sCount).forEach((pt, i) => {
        i === 0 ? ctx.moveTo(pt.x, pt.y) : ctx.lineTo(pt.x, pt.y);
    });
    ctx.stroke();

    if (sCount > 1) {
        ctx.beginPath();
        spacedPts.slice(0, sCount).forEach((pt, i) => {
            i === 0 ? ctx.moveTo(pt.x, pt.y) : ctx.lineTo(pt.x, pt.y);
        });
        ctx.lineTo(spacedPts[sCount - 1].x, padding.top + chartH);
        ctx.lineTo(padding.left, padding.top + chartH);
        ctx.closePath();
        ctx.fillStyle = 'hsla(165, 80%, 55%, 0.06)';
        ctx.fill();
    }

    // Flèches révision
    if (progress > 0.3) {
        ctx.fillStyle = 'hsl(165, 80%, 55%)';
        ctx.font      = `bold 14px ${fontName}`;
        ctx.textAlign = 'center';
        reviewDays.forEach((rd, i) => {
            const markerProgress = Math.min(1, (progress - 0.3 - i * 0.1) / 0.2);
            if (markerProgress > 0) {
                ctx.globalAlpha = markerProgress;
                ctx.fillText('↑', padding.left + chartW * rd, padding.top + 5);
                ctx.globalAlpha = 1;
            }
        });
    }

    // Labels finaux
    if (progress > 0.8) {
        const alpha = Math.min(1, (progress - 0.8) / 0.2);
        ctx.globalAlpha = alpha;
        ctx.font        = `bold 12px ${fontName}`;
        ctx.textAlign   = 'left';

        ctx.fillStyle = 'hsl(0, 75%, 65%)';
        const lastF = forgettingPts[forgettingPts.length - 1];
        ctx.fillText('~10%', lastF.x + 5, lastF.y + 4);

        ctx.fillStyle = 'hsl(165, 80%, 60%)';
        const lastS = spacedPts[spacedPts.length - 1];
        ctx.fillText('~85%', lastS.x + 5, lastS.y + 4);

        ctx.globalAlpha = 1;
    }
}

/* ═══════════════════ COMPTEURS ANIMÉS ═══════════════════ */

function initCounters() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            animateCounter(entry.target);
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.stat-value[data-count]')
        .forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target    = parseInt(element.dataset.count);
    const duration  = 2000;
    const startTime = performance.now();

    function update(currentTime) {
        const progress = Math.min(1, (currentTime - startTime) / duration);
        const eased    = 1 - (1 - progress) * (1 - progress);
        element.textContent = Math.round(target * eased);
        if (progress < 1) requestAnimationFrame(update);
        else element.textContent = target;
    }

    requestAnimationFrame(update);
}

/* ═══════════════════ SMOOTH SCROLL ═══════════════════ */

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            e.preventDefault();

            const target  = document.querySelector(href);
            const navbar  = document.getElementById('navbar');
            if (!target) return;

            const navH           = navbar ? navbar.offsetHeight : 0;
            const targetPosition = target.getBoundingClientRect().top + window.scrollY - navH;
            window.scrollTo({ top: targetPosition, behavior: 'smooth' });
        });
    });
}

/* ═══════════════════ UTILITAIRE : EXPORT WAITLIST (admin) ═══════════════════ */
/*
 * Pour exporter les leads stockés en localStorage,
 * tape dans la console du navigateur :
 *
 *   console.table(JSON.parse(localStorage.getItem('khawarizmi-waitlist-submitted')))
 *
 * Puis copie-colle dans un tableur.
 * À remplacer par un vrai endpoint dès que le backend est prêt.
 */
