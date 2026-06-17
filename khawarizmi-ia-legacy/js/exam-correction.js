/* ============================================
   CORRECTION AUTOMATIQUE - Système d'évaluation
   ============================================ */

const ExamCorrection = {

  /**
   * Corriger une réponse d'élève
   */
  correctAnswer(questionId, studentAnswer) {
    const question = BACQuestions.questions.find(q => q.id === questionId);
    if (!question) return null;

    const analysis = this.analyzeAnswer(studentAnswer, question);
    const score = this.calculateScore(analysis, question.points);
    const feedback = this.generateFeedback(analysis, question, score);

    return {
      questionId,
      score,
      maxPoints: question.points,
      percentage: Math.round((score / question.points) * 100),
      analysis,
      feedback
    };
  },

  /**
   * Analyser la réponse de l'élève
   */
  analyzeAnswer(studentAnswer, question) {
    if (!studentAnswer || studentAnswer.trim().length === 0) {
      return {
        isEmpty: true,
        foundKeywords: [],
        missingKeywords: question.keyWords,
        wordCount: 0,
        hasStructure: false,
        hasExamples: false,
        qualityLevel: 'empty'
      };
    }

    const cleanAnswer = studentAnswer.toLowerCase().trim();
    const words = cleanAnswer.split(/\s+/);

    // Vérifier les mots-clés trouvés
    const foundKeywords = [];
    const missingKeywords = [];

    question.keyWords.forEach(keyword => {
      const keywordLower = keyword.toLowerCase();
      // Vérification flexible
      const variations = this.getKeywordVariations(keywordLower);
      const found = variations.some(v => cleanAnswer.includes(v));

      if (found) {
        foundKeywords.push(keyword);
      } else {
        missingKeywords.push(keyword);
      }
    });

    // Vérifier la structure de la réponse
    const hasStructure = this.checkStructure(cleanAnswer);

    // Vérifier la présence d'exemples
    const hasExamples = this.checkExamples(cleanAnswer);

    // Vérifier la longueur
    const expectedMinWords = question.points * 8;
    const isLongEnough = words.length >= expectedMinWords;

    // Vérifier les erreurs courantes
    const commonErrors = this.checkCommonErrors(cleanAnswer, question);

    // Calculer le niveau de qualité
    const keywordRatio = foundKeywords.length / question.keyWords.length;
    let qualityLevel;

    if (keywordRatio >= 0.8 && hasStructure && isLongEnough) {
      qualityLevel = 'excellent';
    } else if (keywordRatio >= 0.6 && isLongEnough) {
      qualityLevel = 'good';
    } else if (keywordRatio >= 0.4) {
      qualityLevel = 'average';
    } else if (keywordRatio >= 0.2) {
      qualityLevel = 'weak';
    } else {
      qualityLevel = 'insufficient';
    }

    return {
      isEmpty: false,
      foundKeywords,
      missingKeywords,
      wordCount: words.length,
      expectedMinWords,
      isLongEnough,
      hasStructure,
      hasExamples,
      commonErrors,
      keywordRatio,
      qualityLevel
    };
  },

  /**
   * Obtenir les variations d'un mot-clé
   */
  getKeywordVariations(keyword) {
    const variations = [keyword];

    // Variations courantes
    const replacements = {
      'é': 'e', 'è': 'e', 'ê': 'e',
      'à': 'a', 'â': 'a',
      'î': 'i', 'ï': 'i',
      'ô': 'o', 'û': 'u',
      'ç': 'c'
    };

    let normalized = keyword;
    Object.entries(replacements).forEach(([from, to]) => {
      normalized = normalized.replace(new RegExp(from, 'g'), to);
    });

    if (normalized !== keyword) {
      variations.push(normalized);
    }

    // Ajout sans tirets et espaces
    variations.push(keyword.replace(/[-\s]/g, ''));
    variations.push(keyword.replace(/[أإآ]/g, 'ا'));

    return variations;
  },

  /**
   * Vérifier la structure de la réponse
   */
  checkStructure(answer) {
    const structureIndicators = [
      /[1-9][).\-]|[١-٩]/,
      /بما أن|وبالتالي|من ناحية|لذلك|إذن|نستنتج|يتبين|نلاحظ/,
      /أولا|ثانيا|ثالثا|أخيرا|بالإضافة|علاوة/,
      /•|→|←|-\s/
    ];

    let structureScore = 0;
    structureIndicators.forEach(pattern => {
      if (pattern.test(answer)) structureScore++;
    });

    return structureScore >= 2;
  },

  /**
   * Vérifier la présence d'exemples
   */
  checkExamples(answer) {
    const exampleIndicators = [
      /مثل|مثلا|على سبيل المثال|كـ|نذكر|من بين/,
      /exemple|par exemple|tel que/,
      /مثال/
    ];

    return exampleIndicators.some(pattern => pattern.test(answer));
  },

  /**
   * Vérifier les erreurs courantes
   */
  checkCommonErrors(answer, question) {
    const errors = [];

    // Erreurs par sujet
    if (question.topic === 'الاستنساخ') {
      if (answer.includes('هيولى') && !answer.includes('نواة')) {
        errors.push('⚠️ الاستنساخ يتم في النواة وليس في الهيولى');
      }
      if (answer.includes('t') && !answer.includes('u')) {
        errors.push('⚠️ تذكر: في ARN نستخدم U بدل T');
      }
    }

    if (question.topic === 'الترجمة') {
      if (answer.includes('نواة') && !answer.includes('هيولى')) {
        errors.push('⚠️ الترجمة تتم في الهيولى على الريبوزومات وليس في النواة');
      }
    }

    if (question.unit === 'المناعة') {
      if (answer.includes('lb') && answer.includes('تقتل')) {
        errors.push('⚠️ LB لا تقتل الخلايا! LB تنتج الأجسام المضادة. LTc هي التي تقتل');
      }
    }

    // Erreurs générales
    if (answer.length > 20 && !answer.includes('لأن') && !answer.includes('بسبب') && !answer.includes('يتم')) {
      if (question.type === 'explication') {
        errors.push('💡 حاول تفسير إجابتك بـ "لأن..." أو "بسبب..."');
      }
    }

    return errors;
  },

  /**
   * Calculer le score
   */
  calculateScore(analysis, maxPoints) {
    if (analysis.isEmpty) return 0;

    let score = 0;

    // Points pour les mots-clés (60% de la note)
    const keywordPoints = maxPoints * 0.6;
    score += keywordPoints * analysis.keywordRatio;

    // Points pour la structure (15%)
    if (analysis.hasStructure) {
      score += maxPoints * 0.15;
    }

    // Points pour la longueur (15%)
    if (analysis.isLongEnough) {
      score += maxPoints * 0.15;
    } else if (analysis.wordCount > analysis.expectedMinWords * 0.5) {
      score += maxPoints * 0.07;
    }

    // Points pour les exemples (10%)
    if (analysis.hasExamples) {
      score += maxPoints * 0.1;
    }

    // Pénalité pour erreurs courantes
    if (analysis.commonErrors.length > 0) {
      score -= maxPoints * 0.05 * analysis.commonErrors.length;
    }

    return Math.max(0, Math.min(maxPoints, Math.round(score * 10) / 10));
  },

  /**
   * Générer le feedback détaillé
   */
  generateFeedback(analysis, question, score) {
    if (analysis.isEmpty) {
      return {
        emoji: '📝',
        title: 'إجابة فارغة',
        message: 'لم تكتب أي إجابة! حاول كتابة شيء ما حتى لو لم تكن متأكداً. لا تترك سؤالاً فارغاً أبداً في البكالوريا!',
        details: [],
        tips: ['اكتب على الأقل تعريف المصطلحات المطلوبة', 'حاول ذكر الأفكار الرئيسية حتى لو بشكل مختصر'],
        grade: 'F'
      };
    }

    const percentage = Math.round((score / question.points) * 100);
    let emoji, title, grade;

    if (percentage >= 90) {
      emoji = '🏆';
      title = 'ممتاز! إجابة شاملة ودقيقة';
      grade = 'A+';
    } else if (percentage >= 80) {
      emoji = '🌟';
      title = 'جيد جداً! إجابة قوية';
      grade = 'A';
    } else if (percentage >= 70) {
      emoji = '✅';
      title = 'جيد! لكن يمكن تحسينها';
      grade = 'B';
    } else if (percentage >= 50) {
      emoji = '👍';
      title = 'مقبول. تحتاج لمزيد من التفصيل';
      grade = 'C';
    } else if (percentage >= 30) {
      emoji = '⚠️';
      title = 'ضعيف. معلومات ناقصة';
      grade = 'D';
    } else {
      emoji = '❌';
      title = 'غير كافٍ. يجب مراجعة الدرس';
      grade = 'F';
    }

    // Détails de la correction
    const details = [];

    // Mots-clés trouvés
    if (analysis.foundKeywords.length > 0) {
      details.push({
        type: 'success',
        icon: '✅',
        text: `مصطلحات صحيحة (${analysis.foundKeywords.length}/${question.keyWords.length}):`,
        items: analysis.foundKeywords
      });
    }

    // Mots-clés manquants
    if (analysis.missingKeywords.length > 0) {
      details.push({
        type: 'error',
        icon: '❌',
        text: `مصطلحات ناقصة (${analysis.missingKeywords.length}):`,
        items: analysis.missingKeywords
      });
    }

    // Structure
    details.push({
      type: analysis.hasStructure ? 'success' : 'warning',
      icon: analysis.hasStructure ? '✅' : '⚠️',
      text: analysis.hasStructure ?
        'إجابتك منظمة ومنطقية' :
        'إجابتك تفتقر للتنظيم. استخدم الترقيم والروابط المنطقية'
    });

    // Longueur
    details.push({
      type: analysis.isLongEnough ? 'success' : 'warning',
      icon: analysis.isLongEnough ? '✅' : '⚠️',
      text: analysis.isLongEnough ?
        `طول الإجابة مناسب (${analysis.wordCount} كلمة)` :
        `إجابتك قصيرة (${analysis.wordCount} كلمة). المطلوب ~${analysis.expectedMinWords}+ كلمة`
    });

    // Exemples
    if (analysis.hasExamples) {
      details.push({
        type: 'success',
        icon: '✅',
        text: 'أحسنت! أعطيت أمثلة لدعم إجابتك'
      });
    } else {
      details.push({
        type: 'warning',
        icon: '💡',
        text: 'أضف أمثلة محسوسة لتقوية إجابتك'
      });
    }

    // Erreurs courantes
    if (analysis.commonErrors.length > 0) {
      details.push({
        type: 'error',
        icon: '⚠️',
        text: 'أخطاء مكتشفة:',
        items: analysis.commonErrors
      });
    }

    // Conseils d'amélioration
    const tips = [];

    if (analysis.missingKeywords.length > 0) {
      tips.push(`أضف هذه المصطلحات المهمة: ${analysis.missingKeywords.slice(0, 3).join(', ')}`);
    }

    if (!analysis.hasStructure) {
      tips.push('نظّم إجابتك: استخدم 1) 2) 3) أو النقاط');
    }

    if (!analysis.isLongEnough) {
      tips.push('طوّر إجابتك أكثر: أضف تفسيرات وأمثلة');
    }

    if (!analysis.hasExamples) {
      tips.push('أعطِ مثالاً محسوساً يدعم شرحك');
    }

    if (question.type === 'comparaison') {
      tips.push('في المقارنة: ارسم جدولاً مقارناً لتنظيم الأفكار');
    }

    if (question.type === 'synthese') {
      tips.push('في النص العلمي: ابدأ بمقدمة وانتهِ بخاتمة');
    }

    return {
      emoji,
      title,
      message: `حصلت على ${score}/${question.points} (${percentage}%)`,
      details,
      tips,
      grade,
      modelAnswer: question.modelAnswer
    };
  },

  /**
   * Générer le HTML du feedback
   */
  renderFeedback(correction) {
    const fb = correction.feedback;
    const percentage = correction.percentage;

    let bgColor, borderColor;
    if (percentage >= 80) {
      bgColor = '#D1FAE5';
      borderColor = '#10B981';
    } else if (percentage >= 50) {
      bgColor = '#FEF3C7';
      borderColor = '#F59E0B';
    } else {
      bgColor = '#FEE2E2';
      borderColor = '#DC2626';
    }

    return `
      <div class="correction-result" style="background: ${bgColor}; border: 2px solid ${borderColor}; border-radius: 20px; padding: 30px; margin: 20px 0; animation: fadeIn 0.5s;">

        <div style="text-align: center; margin-bottom: 24px;">
          <div style="font-size: 3.5rem; margin-bottom: 8px;">${fb.emoji}</div>
          <h3 style="font-family: 'Cairo', sans-serif; color: ${borderColor}; font-size: 1.4rem; margin-bottom: 8px;">
            ${fb.title}
          </h3>
          <p style="font-size: 1.1rem; font-weight: 700; color: var(--bac-text);">
            ${fb.message}
          </p>

          <div style="margin: 16px auto; max-width: 400px;">
            <div style="background: rgba(0,0,0,0.1); height: 12px; border-radius: 6px; overflow: hidden;">
              <div style="background: ${borderColor}; height: 100%; width: ${percentage}%; border-radius: 6px; transition: width 1s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.85rem; color: var(--bac-text-light);">
              <span>0</span>
              <span style="font-weight: 800; color: ${borderColor};">${correction.score}/${correction.maxPoints}</span>
              <span>${correction.maxPoints}</span>
            </div>
          </div>
        </div>

        <div style="display: grid; gap: 10px; margin-bottom: 20px;">
          ${fb.details.map(d => `
            <div style="background: white; padding: 14px; border-radius: 12px; display: flex; align-items: flex-start; gap: 10px;">
              <span style="font-size: 1.3rem; flex-shrink: 0;">${d.icon}</span>
              <div>
                <strong style="color: var(--bac-text);">${d.text}</strong>
                ${d.items ? `
                  <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                    ${d.items.map(item => `
                      <span style="background: ${d.type === 'success' ? '#D1FAE5' : d.type === 'error' ? '#FEE2E2' : '#FEF3C7'};
                                     padding: 4px 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 600;">
                        ${item}
                      </span>
                    `).join('')}
                  </div>
                ` : ''}
              </div>
            </div>
          `).join('')}
        </div>

        ${fb.tips.length > 0 ? `
          <div style="background: white; padding: 20px; border-radius: 14px; margin-bottom: 20px;">
            <h4 style="font-family: 'Cairo', sans-serif; color: #3B82F6; margin-bottom: 12px;">
              💡 نصائح للتحسين:
            </h4>
            <ul style="list-style: none; display: grid; gap: 8px;">
              ${fb.tips.map(tip => `
                <li style="display: flex; align-items: flex-start; gap: 8px;">
                  <span style="color: #3B82F6;">→</span>
                  <span>${tip}</span>
                </li>
              `).join('')}
            </ul>
          </div>
        ` : ''}

        <details style="background: white; border-radius: 14px; overflow: hidden;">
          <summary style="padding: 16px; cursor: pointer; font-weight: 700; background: var(--bac-bg); display: flex; align-items: center; gap: 8px;">
            <span>📖</span>
            <span>عرض الإجابة النموذجية</span>
          </summary>
          <div style="padding: 20px; border-top: 2px solid var(--bac-bg); white-space: pre-line; line-height: 1.8;">
            ${fb.modelAnswer}
          </div>
        </details>

      </div>
    `;
  },

  /**
   * Corriger tout un examen
   */
  correctExam(answers) {
    const results = [];
    let totalScore = 0;
    let totalMaxPoints = 0;

    answers.forEach(item => {
      const correction = this.correctAnswer(item.questionId, item.answer);
      if (correction) {
        results.push(correction);
        totalScore += correction.score;
        totalMaxPoints += correction.maxPoints;
      }
    });

    const percentage = totalMaxPoints > 0 ? Math.round((totalScore / totalMaxPoints) * 100) : 0;

    let grade, comment;
    if (percentage >= 90) { grade = 'A+'; comment = 'ممتاز! أداء استثنائي'; }
    else if (percentage >= 80) { grade = 'A'; comment = 'جيد جداً! استمر'; }
    else if (percentage >= 70) { grade = 'B'; comment = 'جيد! يمكنك التحسن'; }
    else if (percentage >= 50) { grade = 'C'; comment = 'مقبول. راجع الدروس'; }
    else { grade = 'D'; comment = 'ضعيف. تحتاج مراجعة شاملة'; }

    return {
      results,
      totalScore,
      totalMaxPoints,
      percentage,
      grade,
      comment,
      questionsAnswered: results.filter(r => !r.analysis.isEmpty).length,
      questionsTotal: results.length
    };
  }
};

if (typeof window !== 'undefined') {
  window.ExamCorrection = ExamCorrection;
}
