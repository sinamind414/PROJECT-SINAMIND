/* ============================================
   GENETIC-CODE.JS - Interactive Codon Table
   ============================================ */

(function() {
  'use strict';
  
  // Build the codon table
  function buildCodonTable() {
    const tbody = document.getElementById('codonBody');
    if (!tbody) return;
    
    // Clear in case of re-init
    tbody.innerHTML = '';
    
    const codonsArray = Object.keys(codonTable);
    
    for (let i = 0; i < codonsArray.length; i += 4) {
      const tr = document.createElement('tr');
      for (let j = 0; j < 4; j++) {
        if (i + j >= codonsArray.length) break;
        const codon = codonsArray[i + j];
        const aa = codonTable[codon];
        
        const tdCodon = document.createElement('td');
        tdCodon.textContent = codon;
        
        if (codon === 'AUG') {
          tdCodon.classList.add('start');
        } else if (aa === 'STOP') {
          tdCodon.classList.add('stop');
        }
        
        const tdAA = document.createElement('td');
        tdAA.textContent = aa;
        
        // Add click handler to codon cell
        tdCodon.addEventListener('click', () => selectCodon(codon, aa));
        tdAA.addEventListener('click', () => selectCodon(codon, aa));
        
        tr.appendChild(tdCodon);
        tr.appendChild(tdAA);
      }
      tbody.appendChild(tr);
    }
  }
  
  function selectCodon(codon, aa) {
    const display = document.getElementById('codonDisplay');
    if (!display) return;
    
    // Clean amino acid name from start suffix
    const cleanAA = aa.replace(' (START)', '');
    const arabicName = aminoAcidsArabic[cleanAA] || cleanAA;
    
    // Get language for context if needed, but display both Arabic and English names
    display.innerHTML = `
      <div class="selected-codon">${codon}</div>
      <div class="selected-aa">${arabicName} (${cleanAA})</div>
    `;
  }
  
  document.addEventListener('DOMContentLoaded', buildCodonTable);
})();
