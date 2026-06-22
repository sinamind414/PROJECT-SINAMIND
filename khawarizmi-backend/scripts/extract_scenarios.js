// Extrait les scénarios et questions depuis methodology-documents.ts
// et génère un JSON pour le seed Python.
// Usage: node extract_scenarios.js

const fs = require("fs");
const path = require("path");

const src = fs.readFileSync(
  path.join(__dirname, "..", "..", "khawarizmi-frontend", "src", "lib", "methodology-documents.ts"),
  "utf-8"
);

// ── Extraction des scénarios par regex ──
// Chaque scénario commence par id: "xxx-v1" et se termine par le prochain id: ou la fin du tableau

const scenarioRegex = /id:\s*"([^"]+)".*?unitKey:\s*"([^"]+)".*?title:\s*"([^"]+)".*?subtitle:\s*"([^"]+)".*?contextAr:\s*\n?\s*"([^"]+)".*?(?:dominantSkills:\s*\[([^\]]*)\])?.*?questions:\s*readonly\s*\[([\s\S]*?)\]\s*\}/g;

const levelMap = {
  "analyse": "L1",
  "interpret": "L2",
  "deduce": "L2",
  "justify": "L2",
  "compare": "L2",
  "relationship": "L2",
  "hypothesis": "L3",
  "validate-hypothesis": "L3",
  "discuss": "L3",
  "scientific-text": "L3",
};

const scenarios = [];
let match;

// Approche plus simple : splitter par "id:" au niveau des scénarios
const lines = src.split("\n");
let currentScenario = null;
let currentQuestion = null;
let inQuestions = false;
let inDocuments = false;
let braceDepth = 0;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();

  // Détection d'un nouveau scénario (id se termine par -v1)
  const idMatch = line.match(/^id:\s*"([^"]+)"/);
  if (idMatch && idMatch[1].includes("-v1")) {
    if (currentScenario) {
      if (currentQuestion) {
        currentScenario.questions.push(currentQuestion);
        currentQuestion = null;
      }
      scenarios.push(currentScenario);
    }
    currentScenario = {
      slug: idMatch[1],
      unit_key: "",
      title_ar: "",
      subtitle_ar: "",
      context_ar: "",
      dominant_skills: [],
      questions: [],
    };
    inQuestions = false;
    inDocuments = false;
    continue;
  }

  if (!currentScenario) continue;

  // Extraction des champs du scénario
  const unitKeyMatch = line.match(/^unitKey:\s*"([^"]+)"/);
  if (unitKeyMatch) {
    currentScenario.unit_key = unitKeyMatch[1];
    continue;
  }

  const titleMatch = line.match(/^title:\s*"([^"]+)"/);
  if (titleMatch && !inQuestions && !inDocuments) {
    currentScenario.title_ar = titleMatch[1];
    continue;
  }

  const subtitleMatch = line.match(/^subtitle:\s*"([^"]+)"/);
  if (subtitleMatch) {
    currentScenario.subtitle_ar = subtitleMatch[1];
    continue;
  }

  const contextMatch = line.match(/^contextAr:\s*"([^"]+)"/);
  if (contextMatch) {
    currentScenario.context_ar = contextMatch[1];
    continue;
  }

  const domSkillsMatch = line.match(/^dominantSkills:\s*\[([^\]]*)\]/);
  if (domSkillsMatch) {
    currentScenario.dominant_skills = domSkillsMatch[1]
      .split(",")
      .map(s => s.trim().replace(/"/g, ""))
      .filter(s => s);
    continue;
  }

  // Détection du bloc documents
  if (line.match(/^documents:\s*\[/)) {
    inDocuments = true;
    inQuestions = false;
    continue;
  }

  // Détection du bloc questions
  if (line.match(/^questions:\s*readonly\s*\[/) || line.match(/^questions:\s*\[/)) {
    inQuestions = true;
    inDocuments = false;
    continue;
  }

  // Extraction des questions
  if (inQuestions) {
    const verbMatch = line.match(/^verbSlug:\s*"([^"]+)"/);
    if (verbMatch) {
      if (currentQuestion) {
        currentScenario.questions.push(currentQuestion);
      }
      currentQuestion = {
        verb_slug: verbMatch[1],
        level: levelMap[verbMatch[1]] || "L2",
        n: 0,
        title_ar: "",
        skill_ar: "",
        doc_ref: "",
        prompt_ar: "",
        placeholder_ar: "",
        model_answer_ar: "",
        learning_focus_ar: "",
      };
      continue;
    }

    if (!currentQuestion) continue;

    const nMatch = line.match(/^n:\s*(\d+)/);
    if (nMatch) { currentQuestion.n = parseInt(nMatch[1]); continue; }

    const qTitleMatch = line.match(/^title:\s*"([^"]+)"/);
    if (qTitleMatch) { currentQuestion.title_ar = qTitleMatch[1]; continue; }

    const skillMatch = line.match(/^skill:\s*"([^"]+)"/);
    if (skillMatch) { currentQuestion.skill_ar = skillMatch[1]; continue; }

    const docRefMatch = line.match(/^docRef:\s*"([^"]+)"/);
    if (docRefMatch) { currentQuestion.doc_ref = docRefMatch[1]; continue; }

    const promptMatch = line.match(/^prompt:\s*"([^"]+)"/);
    if (promptMatch) { currentQuestion.prompt_ar = promptMatch[1]; continue; }

    const placeholderMatch = line.match(/^placeholder:\s*"([^"]+)"/);
    if (placeholderMatch) { currentQuestion.placeholder_ar = placeholderMatch[1]; continue; }

    const modelAnswerMatch = line.match(/^modelAnswer:\s*"([^"]+)"/);
    if (modelAnswerMatch) { currentQuestion.model_answer_ar = modelAnswerMatch[1]; continue; }

    const learningFocusMatch = line.match(/^learningFocus:\s*"([^"]+)"/);
    if (learningFocusMatch) { currentQuestion.learning_focus_ar = learningFocusMatch[1]; continue; }
  }
}

// Dernier scénario
if (currentScenario) {
  if (currentQuestion) {
    currentScenario.questions.push(currentQuestion);
  }
  scenarios.push(currentScenario);
}

// Filtrer les scénarios valides (qui ont un slug en -v1)
const validScenarios = scenarios.filter(s => s.slug && s.slug.includes("-v1"));

// Output JSON
const outputPath = path.join(__dirname, "document_analysis_seed.json");
fs.writeFileSync(outputPath, JSON.stringify(validScenarios, null, 2), "utf-8");

console.log(`Extraction terminée : ${validScenarios.length} scénarios, ${validScenarios.reduce((sum, s) => sum + s.questions.length, 0)} questions`);
console.log(`Output : ${outputPath}`);
validScenarios.forEach(s => {
  console.log(`  - ${s.slug}: ${s.questions.length} questions`);
});
