/* ============================================
   DATA.JS - Scientific Data (Codon Table)
   ============================================ */

const codonTable = {
  // Phenylalanine & Leucine
  'UUU': 'Phe', 'UUC': 'Phe', 'UUA': 'Leu', 'UUG': 'Leu',
  // Serine
  'UCU': 'Ser', 'UCC': 'Ser', 'UCA': 'Ser', 'UCG': 'Ser',
  // Tyrosine & STOP
  'UAU': 'Tyr', 'UAC': 'Tyr', 'UAA': 'STOP', 'UAG': 'STOP',
  // Cysteine, STOP, Tryptophan
  'UGU': 'Cys', 'UGC': 'Cys', 'UGA': 'STOP', 'UGG': 'Trp',
  // Leucine
  'CUU': 'Leu', 'CUC': 'Leu', 'CUA': 'Leu', 'CUG': 'Leu',
  // Proline
  'CCU': 'Pro', 'CCC': 'Pro', 'CCA': 'Pro', 'CCG': 'Pro',
  // Histidine & Glutamine
  'CAU': 'His', 'CAC': 'His', 'CAA': 'Gln', 'CAG': 'Gln',
  // Arginine
  'CGU': 'Arg', 'CGC': 'Arg', 'CGA': 'Arg', 'CGG': 'Arg',
  // Isoleucine & Methionine (START)
  'AUU': 'Ile', 'AUC': 'Ile', 'AUA': 'Ile', 'AUG': 'Met (START)',
  // Threonine
  'ACU': 'Thr', 'ACC': 'Thr', 'ACA': 'Thr', 'ACG': 'Thr',
  // Asparagine & Lysine
  'AAU': 'Asn', 'AAC': 'Asn', 'AAA': 'Lys', 'AAG': 'Lys',
  // Serine & Arginine
  'AGU': 'Ser', 'AGC': 'Ser', 'AGA': 'Arg', 'AGG': 'Arg',
  // Valine
  'GUU': 'Val', 'GUC': 'Val', 'GUA': 'Val', 'GUG': 'Val',
  // Alanine
  'GCU': 'Ala', 'GCC': 'Ala', 'GCA': 'Ala', 'GCG': 'Ala',
  // Aspartate & Glutamate
  'GAU': 'Asp', 'GAC': 'Asp', 'GAA': 'Glu', 'GAG': 'Glu',
  // Glycine
  'GGU': 'Gly', 'GGC': 'Gly', 'GGA': 'Gly', 'GGG': 'Gly'
};

// Amino acid full names (Arabic)
const aminoAcidsArabic = {
  'Phe': 'فينيل ألانين',
  'Leu': 'ليوسين',
  'Ser': 'سيرين',
  'Tyr': 'تيروزين',
  'Cys': 'سيستيين',
  'Trp': 'تريبتوفان',
  'Pro': 'برولين',
  'His': 'هيستيدين',
  'Gln': 'غلوتامين',
  'Arg': 'أرجينين',
  'Ile': 'إيزولوسين',
  'Met': 'ميثيونين',
  'Thr': 'ثريونين',
  'Asn': 'أسبارجين',
  'Lys': 'ليزين',
  'Val': 'فالين',
  'Ala': 'ألانين',
  'Asp': 'أسبارتات',
  'Glu': 'غلوتامات',
  'Gly': 'جلايسين',
  'STOP': 'توقف'
};
