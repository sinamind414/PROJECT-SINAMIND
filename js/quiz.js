/* ============================================
   QUIZ.JS - Interactive MCQ Quiz System
   ============================================ */

const quizData = {
  transcription: [
    {
      q: "أين تحدث عملية الاستنساخ في الخلية حقيقية النواة؟",
      options: ["الهيولى", "النواة", "الميتوكوندري", "جهاز غولجي"],
      correct: 1,
      explanation: "تحدث عملية الاستنساخ داخل النواة لأن جزيئة ADN موجودة هناك."
    },
    {
      q: "ما هو الإنزيم المسؤول عن عملية الاستنساخ؟",
      options: ["ADN بوليمراز", "ARN بوليمراز", "الليغاز", "الهيليكاز"],
      correct: 1,
      explanation: "إنزيم ARN بوليمراز يقوم ببناء جزيئة ARNm من قالب ADN."
    },
    {
      q: "ماذا يحدث للقطع غير الدالة (Introns) أثناء نضج ARNm؟",
      options: ["تُترجم إلى بروتين", "تُحذف", "تُضاعف", "تبقى كما هي"],
      correct: 1,
      explanation: "تُحذف القطع غير الدالة (Introns) ويتم الإبقاء على القطع الدالة (Exons) فقط."
    }
  ],
  
  code: [
    {
      q: "كم عدد الرامزات الإجمالي في الشفرة الوراثية؟",
      options: ["20", "61", "64", "100"],
      correct: 2,
      explanation: "هناك 64 رامزة: 61 رامزة تشفير + 3 رامزات توقف."
    },
    {
      q: "ما هي رامزة الانطلاق في الشفرة الوراثية؟",
      options: ["AUG", "UAA", "UAG", "UGA"],
      correct: 0,
      explanation: "AUG هي رامزة الانطلاق وتُشفِّر أيضاً للحمض الأميني الميثيونين (Met)."
    },
    {
      q: "أيٌّ من التالي ليس من رامزات التوقف؟",
      options: ["UAA", "UAG", "UGA", "AUG"],
      correct: 3,
      explanation: "AUG هي رامزة الانطلاق وليست توقف. رامزات التوقف هي: UAA, UAG, UGA."
    },
    {
      q: "ما المقصود بـ 'تنكُّس' الشفرة الوراثية؟",
      options: [
        "كل رامزة تشفر لعدة أحماض",
        "عدة رامزات تشفر لنفس الحمض",
        "الشفرة تتغير بمرور الوقت",
        "الشفرة مختلفة بين الكائنات"
      ],
      correct: 1,
      explanation: "التنكُّس يعني أن عدة رامزات مختلفة يمكنها تشفير نفس الحمض الأميني."
    }
  ],
  
  translation: [
    {
      q: "أين تحدث عملية الترجمة؟",
      options: ["النواة", "الهيولى (على الريبوزومات)", "الميتوكوندري", "جهاز غولجي"],
      correct: 1,
      explanation: "تحدث الترجمة في الهيولى على مستوى الريبوزومات."
    },
    {
      q: "ما دور ARNt في عملية الترجمة؟",
      options: [
        "حمل المعلومة الوراثية",
        "نقل الأحماض الأمينية",
        "تركيب الريبوزوم",
        "حذف Introns"
      ],
      correct: 1,
      explanation: "ARNt (الناقل) ينقل الأحماض الأمينية إلى الريبوزوم لربطها بالسلسلة الببتيدية."
    },
    {
      q: "متى تنتهي عملية الترجمة؟",
      options: [
        "عند رامزة الانطلاق",
        "بعد 100 حمض أميني",
        "عند رامزة التوقف",
        "بعد ساعة من البدء"
      ],
      correct: 2,
      explanation: "تنتهي الترجمة عند وصول الريبوزوم لإحدى رامزات التوقف (UAA, UAG, UGA)."
    },
    {
      q: "ما هو الـ Polysome؟",
      options: [
        "نوع من البروتينات",
        "عدة ريبوزومات تقرأ نفس ARNm",
        "إنزيم خاص",
        "نوع من ARN"
      ],
      correct: 1,
      explanation: "Polysome هو تجمع عدة ريبوزومات تقرأ نفس جزيئة ARNm في نفس الوقت."
    }
  ],
  
  fate: [
    {
      q: "ماذا يجب أن يحدث للبروتين بعد تركيبه؟",
      options: [
        "يُهضم مباشرة",
        "يكتسب بنية فراغية وظيفية",
        "يعود إلى النواة",
        "يتحول إلى ADN"
      ],
      correct: 1,
      explanation: "يجب أن يخضع البروتين للطي (Folding) ليكتسب بنيته الفراغية الوظيفية."
    },
    {
      q: "أي البروتينات التالية يُفرز خارج الخلية؟",
      options: ["الهيموغلوبين", "الأنسولين", "إنزيمات الهيولى", "بروتينات النواة"],
      correct: 1,
      explanation: "الأنسولين هرمون يُفرز من خلايا البنكرياس إلى مجرى الدم."
    }
  ]
};

(function() {
  'use strict';
  
  let currentQuiz = null;
  let currentQuestionIndex = 0;
  let score = 0;
  let answered = false;
  
  window.startQuiz = function(quizId) {
    currentQuiz = quizData[quizId];
    currentQuestionIndex = 0;
    score = 0;
    answered = false;
    
    if (!currentQuiz) return;
    
    showQuestion(quizId);
  };
  
  function showQuestion(quizId) {
    const container = document.getElementById(`quiz-${quizId}`);
    if (!container) return;
    
    if (currentQuestionIndex >= currentQuiz.length) {
      showResults(quizId);
      return;
    }
    
    const question = currentQuiz[currentQuestionIndex];
    const progress = ((currentQuestionIndex) / currentQuiz.length) * 100;
    
    container.innerHTML = `
      <div class="quiz-progress">
        <div class="quiz-progress-bar" style="width: ${progress}%"></div>
      </div>
      <div class="quiz-counter">السؤال ${currentQuestionIndex + 1} من ${currentQuiz.length}</div>
      
      <div class="quiz-question">
        <h4>${question.q}</h4>
        <div class="quiz-options" id="options-${quizId}">
          ${question.options.map((opt, i) => `
            <button class="quiz-option" onclick="checkAnswer('${quizId}', ${i})">
              <span class="option-letter">${String.fromCharCode(65 + i)}</span>
              <span>${opt}</span>
            </button>
          `).join('')}
        </div>
      </div>
    `;
    
    answered = false;
  }
  
  window.checkAnswer = function(quizId, selectedIndex) {
    if (answered) return;
    answered = true;
    
    const question = currentQuiz[currentQuestionIndex];
    const options = document.querySelectorAll(`#options-${quizId} .quiz-option`);
    
    options.forEach((opt, i) => {
      opt.disabled = true;
      if (i === question.correct) {
        opt.classList.add('correct');
      } else if (i === selectedIndex && i !== question.correct) {
        opt.classList.add('wrong');
      }
    });
    
    if (selectedIndex === question.correct) {
      score++;
    }
    
    // Show explanation
    const questionDiv = document.querySelector(`#quiz-${quizId} .quiz-question`);
    const explanationHTML = `
      <div class="quiz-explanation">
        <strong>${selectedIndex === question.correct ? '✅ إجابة صحيحة!' : '❌ إجابة خاطئة'}</strong>
        ${question.explanation}
      </div>
      <div class="quiz-controls">
        <button class="quiz-btn quiz-btn-next" onclick="nextQuestion('${quizId}')">
          ${currentQuestionIndex + 1 >= currentQuiz.length ? '🏆 رؤية النتيجة' : '➡️ السؤال التالي'}
        </button>
      </div>
    `;
    questionDiv.insertAdjacentHTML('beforeend', explanationHTML);
  };
  
  window.nextQuestion = function(quizId) {
    currentQuestionIndex++;
    showQuestion(quizId);
  };
  
  function showResults(quizId) {
    const container = document.getElementById(`quiz-${quizId}`);
    const percentage = Math.round((score / currentQuiz.length) * 100);
    
    // Save score automatically
    if (typeof Storage !== 'undefined') {
      Storage.saveQuizScore(quizId, score, currentQuiz.length);
    }
    
    let emoji, message;
    if (percentage === 100) {
      emoji = '🏆';
      message = 'ممتاز! أداء استثنائي!';
    } else if (percentage >= 75) {
      emoji = '🌟';
      message = 'جيد جداً! استمر هكذا';
    } else if (percentage >= 50) {
      emoji = '👍';
      message = 'لا بأس! راجع الدرس وحاول مرة أخرى';
    } else {
      emoji = '📚';
      message = 'يجب مراجعة الدرس جيداً';
    }
    
    container.innerHTML = `
      <div class="quiz-results">
        <div class="quiz-emoji">${emoji}</div>
        <div class="quiz-score">${score} / ${currentQuiz.length}</div>
        <div class="quiz-score-text">${percentage}% — ${message}</div>
        <div class="quiz-controls">
          <button class="quiz-btn quiz-btn-restart" onclick="startQuiz('${quizId}')">
            🔄 إعادة الاختبار
          </button>
        </div>
      </div>
    `;
  }
})();
