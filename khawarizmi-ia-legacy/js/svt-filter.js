const SVTFilter = {
    // 1. REGEX MATHÉMATIQUES (Priorité absolue)
    mathRegex: [
        /\d+\s*[\+\-\*\/\×\÷]\s*\d+/,             // 1+1, 11+23, etc.
        /^[0-9\s\+\-\*\/\=\(\)\.\,]+$/,            // Que des chiffres et symboles (ex: 123 + 456)
        /كم\s+(يساوي|تساوي|يعمل|نتيجة)/,            // كم يساوي
        /(احسب|حساب|calculer|calcule)\s+\d+/i,    // احسب 50
        /résous\s+l'équation/i                    // résous l'équation
    ],

    // 2. MOTS CLÉS SVT (Pour autoriser)
    svtKeywords: [
        'adn', 'arn', 'atp', 'نواة', 'خلية', 'بروتين', 'إنزيم', 'مناعة', 'عصب', 'زلزال', 'صفيحة', 'جيولوجيا', 'تركيب ضوئي', 'تنفس'
    ],

    // 3. SALUTATIONS ET SUIVI (Pour autoriser)
    allowedShort: ['سلام', 'مرحبا', 'شكرا', 'نعم', 'لا', 'merci', 'ok', 'hi', 'hello'],

    checkQuestion(message, hasContext) {
        const clean = message.trim().toLowerCase();

        // --- RÈGLE 1 : DÉTECTION MATHÉMATIQUE (BLOQUAGE IMMÉDIAT) ---
        // On vérifie si le message contient un calcul
        const isMath = this.mathRegex.some(regex => regex.test(clean));
        
        // Si c'est du math ET que ça ne contient PAS un mot clé SVT important (ex: "calculer atp")
        if (isMath && !this.containsSVT(clean)) {
            return {
                accepted: false,
                redirect: this.getMathRedirect()
            };
        }

        // --- RÈGLE 2 : MOTS CLÉS SVT ---
        if (this.containsSVT(clean)) return { accepted: true };

        // --- RÈGLE 3 : SALUTATIONS / RÉACTIONS ---
        if (this.allowedShort.some(word => clean.includes(word))) return { accepted: true };

        // --- RÈGLE 4 : SUIVI COURT ---
        if (hasContext && clean.length < 15) return { accepted: true };

        // --- RÈGLE 5 : HORS SUJET GÉNÉRAL ---
        if (this.isClearlyOffTopic(clean)) {
            return { accepted: false, redirect: this.getDefaultRedirect() };
        }

        // Par défaut, on accepte pour ne pas frustrer, sauf si c'est du pur math
        return { accepted: true };
    },

    containsSVT(message) {
        return this.svtKeywords.some(kw => message.includes(kw));
    },

    isClearlyOffTopic(message) {
        const offTopic = [/code|html|python|cuisine|recette|match|score|film/i];
        return offTopic.some(regex => regex.test(message));
    },

    getMathRedirect() {
        return `🧮 **عذراً، أنا متخصص في العلوم الطبيعية (SVT) فقط.**

أنا أستاذ خوارزمي، لا يمكنني حل المسائل الرياضية البسيطة، لكن يمكنني مساعدتك في:
• حساب طاقة ATP 🔋
• حساب عدد النيوكليوتيدات 🧬
• تفسير المنحنيات البيانية 📊

**جرب سؤالاً في العلوم!**`;
    },

    getDefaultRedirect() {
        return `🧬 **أنا أستاذ خوارزمي لعلوم الطبيعة والحياة.**
سؤالك يبدو خارج تخصصي. يرجى طرح سؤال متعلق ببرنامج العلوم للبكالوريا.`;
    }
};
