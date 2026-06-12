/* ============================================
   TRANSLATION-SIM.JS - Interactive Translation Simulator
   ============================================ */

window.translateMRNA = function() {
  const input = document.getElementById('mrnaInput');
  const mrnaDisplay = document.getElementById('mrnaDisplay');
  const proteinOutput = document.getElementById('proteinOutput');
  
  if (!input || !mrnaDisplay || !proteinOutput) return;
  
  let seq = input.value.trim().toUpperCase().replace(/\s/g, '');
  
  // Basic validation: must contain only A, U, G, C
  if (!/^[AUGC]+$/.test(seq)) {
    alert('الرجاء إدخال تتابع يحتوي فقط على القواعد A, U, G, C\nPlease enter a sequence containing only A, U, G, C');
    return;
  }
  
  // Must start with AUG
  if (!seq.startsWith('AUG')) {
    alert('يجب أن يبدأ تتابع ARNm برامزة الانطلاق AUG لتبدأ الترجمة!\nThe mRNA sequence must start with the start codon AUG!');
    return;
  }
  
  // Show mRNA sequence
  mrnaDisplay.innerHTML = 'ARNm: ';
  proteinOutput.innerHTML = '';
  
  // Group into codons
  const codons = [];
  for (let i = 0; i < seq.length; i += 3) {
    if (i + 3 <= seq.length) {
      codons.push(seq.substring(i, i + 3));
    }
  }
  
  // Animate codon by codon translation
  let index = 0;
  
  function stepTranslation() {
    if (index >= codons.length) {
      proteinOutput.insertAdjacentHTML('beforeend', '<div style="margin-top:10px; font-weight:bold; color:var(--red-stop);">⚠️ انتهت القراءة (نهاية الشريط) / End of strand</div>');
      return;
    }
    
    const codon = codons[index];
    const aa = codonTable[codon] || '???';
    
    // Highlight mRNA codon
    mrnaDisplay.innerHTML = 'ARNm: ' + codons.map((c, idx) => {
      if (idx === index) {
        return `<span class="codon" style="background:var(--purple); color:white; padding: 2px 6px; border-radius: 4px;">${c}</span>`;
      }
      return `<span class="codon" style="padding: 2px 6px;">${c}</span>`;
    }).join(' ');
    
    if (aa === 'STOP') {
      proteinOutput.insertAdjacentHTML('beforeend', `<span class="aa-bead" style="background:var(--red-stop);">${aa}</span>`);
      proteinOutput.insertAdjacentHTML('beforeend', '<div style="margin-top:10px; font-weight:bold; color:var(--red-stop);">🏁 رامزة توقف: انتهت الترجمة! / STOP codon: Translation finished!</div>');
      return;
    }
    
    // Add amino acid bead
    const cleanAA = aa.replace(' (START)', '');
    const arabicName = aminoAcidsArabic[cleanAA] || cleanAA;
    proteinOutput.insertAdjacentHTML('beforeend', `<span class="aa-bead" title="${arabicName} (${cleanAA})" style="display: inline-block; padding: 8px 12px; background: var(--green-fresh); color: white; border-radius: 50%; margin: 3px; font-weight: 700; animation: popIn 0.5s;">${cleanAA}</span>`);
    
    index++;
    setTimeout(stepTranslation, 1000); // 1 second delay per codon for simulation effect
  }
  
  stepTranslation();
};
