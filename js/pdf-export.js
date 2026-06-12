/* ============================================
   PDF-EXPORT.JS - PDF Generation System
   ============================================ */

const pdfContent = {
  transcription: {
    title: 'الاستنساخ (Transcription)',
    content: `
      <h2>المفهوم</h2>
      <p>الاستنساخ هو نسخ المعلومة الوراثية من ADN إلى ARNm داخل النواة بواسطة إنزيم ARN بوليمراز.</p>
      
      <h2>المتطلبات</h2>
      <ul>
        <li>إنزيم ARN بوليمراز</li>
        <li>النيوكليوتيدات (A, U, G, C)</li>
        <li>طاقة (ATP)</li>
        <li>قالب ADN</li>
      </ul>
      
      <h2>المراحل</h2>
      <ol>
        <li><strong>الانطلاق:</strong> ارتباط الإنزيم ببداية المورثة</li>
        <li><strong>الاستطالة:</strong> قراءة وبناء خيط ARN</li>
        <li><strong>النهاية:</strong> انفصال الإنزيم وتحرر ARNm</li>
      </ol>
      
      <h2>النضج</h2>
      <p>قبل خروج ARNm من النواة، تُحذف القطع غير الدالة (Introns) ويتم الإبقاء على Exons.</p>
    `
  },
  code: {
    title: 'الشفرة الوراثية (Genetic Code)',
    content: `
      <h2>المفهوم</h2>
      <p>نظام مراسلة بين 4 قواعد نووية و20 حمض أميني. الوحدة هي الرامزة (3 نيوكليوتيدات).</p>
      
      <h2>الأرقام المهمة</h2>
      <ul>
        <li>64 رامزة إجمالاً</li>
        <li>61 رامزة تشفير</li>
        <li>3 رامزات توقف: UAA, UAG, UGA</li>
        <li>1 رامزة انطلاق: AUG (Met)</li>
      </ul>
      
      <h2>الخصائص</h2>
      <ul>
        <li><strong>عالمية:</strong> نفسها في كل الكائنات</li>
        <li><strong>تنكُّسية:</strong> عدة رامزات لنفس الحمض</li>
        <li><strong>غير متراكبة:</strong> قراءة متتالية</li>
        <li><strong>محددة:</strong> كل رامزة لحمض واحد</li>
      </ul>
    `
  },
  translation: {
    title: 'الترجمة (Translation)',
    content: `
      <h2>المفهوم</h2>
      <p>تحويل المعلومة من ARNm إلى سلسلة ببتيدية في الهيولى على الريبوزومات.</p>
      
      <h2>المتطلبات</h2>
      <ul>
        <li>ARNm (الرسالة)</li>
        <li>الريبوزومات (المقر)</li>
        <li>ARNt (الناقل)</li>
        <li>الأحماض الأمينية</li>
        <li>إنزيمات وطاقة (GTP)</li>
      </ul>
      
      <h2>بنية الريبوزوم</h2>
      <p>وحدتان: كبيرة وصغيرة. موقعان: P (الببتيد) و A (الحمض).</p>
      
      <h2>المراحل</h2>
      <ol>
        <li><strong>الانطلاق:</strong> تشكل معقد الانطلاق عند AUG</li>
        <li><strong>الاستطالة:</strong> تشكل الروابط الببتيدية</li>
        <li><strong>النهاية:</strong> وصول رامزة توقف وتحرر البروتين</li>
      </ol>
    `
  },
  fate: {
    title: 'مصير البروتين',
    content: `
      <h2>المفهوم</h2>
      <p>بعد التركيب، يكتسب البروتين بنية فراغية ووظيفة محددة.</p>
      
      <h2>المراحل</h2>
      <ol>
        <li>الطي (Folding)</li>
        <li>التعديلات</li>
        <li>التوجيه</li>
        <li>اكتساب الوظيفة</li>
      </ol>
      
      <h2>الوجهات</h2>
      <ul>
        <li><strong>داخل الخلية:</strong> الإنزيمات الخلوية</li>
        <li><strong>خارج الخلية:</strong> الأنسولين، الأجسام المضادة</li>
        <li><strong>الغشاء:</strong> المستقبلات والقنوات</li>
      </ul>
      
      <h2>أمراض الطي</h2>
      <p>خلل الطي يسبب: الزهايمر، باركنسون.</p>
    `
  }
};

(function() {
  'use strict';
  
  window.generatePDF = function(type) {
    if (type === 'dashboard') {
      generateDashboardPDF();
      return;
    }
    
    const data = pdfContent[type];
    if (!data) return;
    
    openPrintWindow(data.title, data.content);
  };
  
  function generateDashboardPDF() {
    const user = Storage.getUser();
    const progress = Storage.getProgress();
    const scores = Storage.getAllScores();
    
    const content = `
      <h2>معلومات الطالب</h2>
      <p><strong>الاسم:</strong> ${user.name}</p>
      <p><strong>تاريخ التسجيل:</strong> ${new Date(user.joinDate).toLocaleDateString('ar-DZ')}</p>
      
      <h2>الإحصائيات</h2>
      <ul>
        <li>التقدم العام: ${progress.progressPercent}%</li>
        <li>الأقسام المكتملة: ${progress.sectionsVisited}/${progress.totalSections}</li>
        <li>الاختبارات: ${progress.quizzesCompleted}/${progress.totalQuizzes}</li>
        <li>المعدل العام: ${progress.avgScore}%</li>
      </ul>
      
      <h2>نتائج الاختبارات</h2>
      <table style="width:100%;border-collapse:collapse;margin-top:15px;">
        <thead>
          <tr style="background:#2C5F8D;color:white;">
            <th style="padding:10px;border:1px solid #ddd;">القسم</th>
            <th style="padding:10px;border:1px solid #ddd;">النتيجة</th>
            <th style="padding:10px;border:1px solid #ddd;">المحاولات</th>
          </tr>
        </thead>
        <tbody>
          ${Object.entries(scores).map(([id, s]) => `
            <tr>
              <td style="padding:10px;border:1px solid #ddd;">${id === 'transcription' ? 'الاستنساخ' : id === 'code' ? 'الشفرة الوراثية' : id === 'translation' ? 'الترجمة' : id === 'fate' ? 'مصير البروتين' : id}</td>
              <td style="padding:10px;border:1px solid #ddd;text-align:center;"><strong>${s.percentage}%</strong></td>
              <td style="padding:10px;border:1px solid #ddd;text-align:center;">${s.attempts}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    
    openPrintWindow('تقرير الطالب', content);
  }
  
  function openPrintWindow(title, content) {
    const win = window.open('', '_blank');
    win.document.write(`
      <!DOCTYPE html>
      <html lang="ar" dir="rtl">
      <head>
        <meta charset="UTF-8">
        <title>${title} - علوم وحياة BAC</title>
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&family=Cairo:wght@800&display=swap');
          
          body {
            font-family: 'Tajawal', sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            color: #1A2942;
          }
          
          .header {
            text-align: center;
            border-bottom: 4px solid #2C5F8D;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          
          .header h1 {
            font-family: 'Cairo', sans-serif;
            color: #2C5F8D;
            font-size: 2.5rem;
          }
          
          .header .subtitle {
            color: #7FBFA8;
            font-size: 1.1rem;
            margin-top: 8px;
          }
          
          h2 {
            font-family: 'Cairo', sans-serif;
            color: #2C5F8D;
            border-right: 5px solid #7FBFA8;
            padding-right: 15px;
            margin-top: 30px;
          }
          
          ul, ol { padding-right: 30px; }
          li { margin: 8px 0; }
          
          strong { color: #2C5F8D; }
          
          .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #E8F0F9;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
          }
          
          @media print {
            body { padding: 20px; }
            .no-print { display: none; }
          }
          
          .print-btn {
            position: fixed;
            top: 20px;
            left: 20px;
            background: #2C5F8D;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 50px;
            font-weight: 700;
            cursor: pointer;
            font-family: 'Tajawal', sans-serif;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
          }
          
          .print-btn:hover { background: #7FBFA8; }
        </style>
      </head>
      <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ طباعة / حفظ PDF</button>
        
        <div class="header">
          <h1>🧬 ${title}</h1>
          <div class="subtitle">علوم وحياة BAC - الوحدة 1: تركيب البروتين</div>
        </div>
        
        ${content}
        
        <div class="footer">
          <p>© 2025 علوم وحياة BAC — منصة تعليمية للطالب الجزائري</p>
          <p>تاريخ الإصدار: ${new Date().toLocaleDateString('ar-DZ')}</p>
        </div>
      </body>
      </html>
    `);
    win.document.close();
  }
})();
