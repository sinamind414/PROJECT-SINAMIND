const PrintHelper = {
  printPage(title) {
    this.addPrintHeader(title);
    this.addPrintFooter();
    document.querySelectorAll('details').forEach(d => d.open = true);
    document.querySelectorAll('.question-card').forEach(c => c.classList.add('open'));
    setTimeout(() => {
      window.print();
      setTimeout(() => this.removePrintElements(), 1000);
    }, 300);
  },

  printExamResults() {
    this.addPrintHeader('نتائج الامتحان التجريبي');
    this.addPrintFooter();
    setTimeout(() => window.print(), 300);
  },

  printStats() {
    this.addPrintHeader('إحصائياتي - تقرير الأداء');
    this.addPrintFooter();
    setTimeout(() => window.print(), 300);
  },

  printMethodologie() {
    this.addPrintHeader('منهجية البكالوريا - العلوم الطبيعية');
    this.addPrintFooter();
    setTimeout(() => window.print(), 300);
  },

  printErrors() {
    this.addPrintHeader('الأخطاء الشائعة في البكالوريا');
    this.addPrintFooter();
    setTimeout(() => window.print(), 300);
  },

  addPrintHeader(title) {
    this.removePrintElements();
    const header = document.createElement('div');
    header.className = 'print-header';
    header.id = 'printHeader';
    header.innerHTML = `
      <h1>🧠 خوارزمي IA</h1>
      <p>${title || 'منصة البكالوريا الذكية'}</p>
      <p style="font-size: 9pt; margin-top: 5px;">التاريخ: ${new Date().toLocaleDateString('ar-DZ')}</p>
    `;
    document.body.insertBefore(header, document.body.firstChild);
  },

  addPrintFooter() {
    const existing = document.getElementById('printFooter');
    if (existing) existing.remove();
    const footer = document.createElement('div');
    footer.className = 'print-footer';
    footer.id = 'printFooter';
    footer.innerHTML = `
      <p>🧠 خوارزمي IA — منصة البكالوريا الذكية الأولى في الجزائر</p>
      <p>khawarizmi-ia.com | ${new Date().getFullYear()}</p>
    `;
    document.body.appendChild(footer);
  },

  removePrintElements() {
    document.getElementById('printHeader')?.remove();
    document.getElementById('printFooter')?.remove();
  },

  generatePDF(title) {
    this.printPage(title);
  }
};

if (typeof window !== 'undefined') {
  window.PrintHelper = PrintHelper;
}
