import React, { useState } from 'react';
import { 
  StyleSheet, 
  Text, 
  View, 
  SafeAreaView, 
  TouchableOpacity, 
  StatusBar,
  ScrollView,
  Animated
} from 'react-native';

// Mock QCM Diagnostic (Sciences & Maths)
const QUESTIONS = [
  {
    id: 1,
    matiere: "Sciences Expérimentales",
    chapitre: "Immunologie",
    texte: "Quel est le rôle principal des lymphocytes T8 (LT8) ?",
    options: [
      "Produire des anticorps circulants",
      "Phagocyter les bactéries",
      "Se différencier en cellules cytotoxiques (LTc)",
      "Sécréter des interleukines pour activer les LB"
    ],
    correctIndex: 2
  },
  {
    id: 2,
    matiere: "Mathématiques",
    chapitre: "Suites Numériques",
    texte: "Si une suite (Un) est croissante et majorée, alors...",
    options: [
      "Elle diverge vers +∞",
      "Elle converge vers une limite finie l",
      "Elle est constante à partir d'un certain rang",
      "Elle n'admet pas de limite"
    ],
    correctIndex: 1
  },
  {
    id: 3,
    matiere: "Sciences Expérimentales",
    chapitre: "Génétique",
    texte: "La transcription de l'ADN en ARNm se déroule dans :",
    options: [
      "Le cytoplasme",
      "Le réticulum endoplasmique",
      "L'appareil de Golgi",
      "Le noyau"
    ],
    correctIndex: 3
  },
  {
    id: 4,
    matiere: "Mathématiques",
    chapitre: "Fonctions",
    texte: "La limite de x*e^x quand x tend vers -∞ est :",
    options: [
      "-∞",
      "+∞",
      "0",
      "1"
    ],
    correctIndex: 2
  }
];

export default function App() {
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  
  const question = QUESTIONS[currentQIndex];

  const handleAnswer = (index) => {
    if (selectedAnswer !== null) return; // Prevent multiple clicks
    
    setSelectedAnswer(index);
    if (index === question.correctIndex) {
      setScore(score + 1);
    }

    setTimeout(() => {
      setSelectedAnswer(null);
      if (currentQIndex < QUESTIONS.length - 1) {
        setCurrentQIndex(currentQIndex + 1);
      } else {
        setShowResults(true);
      }
    }, 1200); // Wait 1.2s to show correct/incorrect color
  };

  const resetDiagnostic = () => {
    setCurrentQIndex(0);
    setScore(0);
    setShowResults(false);
    setSelectedAnswer(null);
  };

  if (showResults) {
    const percentage = (score / QUESTIONS.length) * 100;
    let feedback = "";
    if (percentage === 100) feedback = "Excellent niveau ! Le moteur FSRS va te proposer des exercices complexes.";
    else if (percentage >= 50) feedback = "Bonnes bases. On va consolider ça avec la répétition espacée.";
    else feedback = "Parfait. On sait exactement par où commencer le mode Feynman.";

    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" />
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>Diagnostic Terminé</Text>
          <Text style={styles.scoreText}>{score} / {QUESTIONS.length}</Text>
          <Text style={styles.percentageText}>{percentage}% de précision</Text>
          
          <View style={styles.feedbackCard}>
            <Text style={styles.feedbackText}>{feedback}</Text>
          </View>
          
          <TouchableOpacity style={styles.buttonMain} onPress={resetDiagnostic}>
            <Text style={styles.buttonText}>Lancer Khawarizmi IA</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Khawarizmi</Text>
        <Text style={styles.headerSubtitle}>Test de Positionnement</Text>
        
        {/* Progress Bar */}
        <View style={styles.progressContainer}>
          <View style={[styles.progressBar, { width: `${((currentQIndex + 1) / QUESTIONS.length) * 100}%` }]} />
        </View>
        <Text style={styles.progressText}>Question {currentQIndex + 1} / {QUESTIONS.length}</Text>
      </View>

      <ScrollView style={styles.scrollContent} contentContainerStyle={{ paddingBottom: 40 }}>
        
        <View style={styles.tagsContainer}>
          <View style={styles.tag}>
            <Text style={styles.tagText}>{question.matiere}</Text>
          </View>
          <View style={[styles.tag, styles.tagChapitre]}>
            <Text style={styles.tagText}>{question.chapitre}</Text>
          </View>
        </View>

        <Text style={styles.questionText}>{question.texte}</Text>

        <View style={styles.optionsContainer}>
          {question.options.map((option, index) => {
            let bgColor = '#1E1E2D';
            let borderColor = '#2B2B40';
            
            if (selectedAnswer !== null) {
              if (index === question.correctIndex) {
                bgColor = 'rgba(0, 200, 83, 0.2)'; // Correct (Green)
                borderColor = '#00C853';
              } else if (index === selectedAnswer) {
                bgColor = 'rgba(255, 59, 48, 0.2)'; // Wrong (Red)
                borderColor = '#FF3B30';
              }
            }

            return (
              <TouchableOpacity 
                key={index} 
                activeOpacity={0.7}
                style={[styles.optionButton, { backgroundColor: bgColor, borderColor: borderColor }]}
                onPress={() => handleAnswer(index)}
              >
                <Text style={styles.optionText}>{option}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D0D14', // Deep dark theme
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#151521',
    borderBottomWidth: 1,
    borderBottomColor: '#2B2B40',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#E0E0FF',
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#8A8A9D',
    textAlign: 'center',
    marginTop: 5,
    marginBottom: 20,
  },
  progressContainer: {
    height: 6,
    backgroundColor: '#2B2B40',
    borderRadius: 3,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#6C5DD3', // Brand purple
    borderRadius: 3,
  },
  progressText: {
    color: '#8A8A9D',
    fontSize: 12,
    textAlign: 'right',
  },
  scrollContent: {
    flex: 1,
    padding: 20,
  },
  tagsContainer: {
    flexDirection: 'row',
    marginBottom: 20,
    flexWrap: 'wrap',
  },
  tag: {
    backgroundColor: 'rgba(108, 93, 211, 0.15)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 10,
    marginBottom: 10,
  },
  tagChapitre: {
    backgroundColor: 'rgba(255, 140, 0, 0.15)',
  },
  tagText: {
    color: '#E0E0FF',
    fontSize: 12,
    fontWeight: '600',
  },
  questionText: {
    fontSize: 22,
    color: '#FFFFFF',
    fontWeight: '600',
    lineHeight: 32,
    marginBottom: 30,
  },
  optionsContainer: {
    gap: 15,
  },
  optionButton: {
    borderWidth: 1.5,
    borderRadius: 12,
    padding: 18,
    minHeight: 60,
    justifyContent: 'center',
  },
  optionText: {
    color: '#E0E0FF',
    fontSize: 16,
    lineHeight: 24,
  },
  resultContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
  },
  resultTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 20,
  },
  scoreText: {
    fontSize: 64,
    fontWeight: '800',
    color: '#6C5DD3',
  },
  percentageText: {
    fontSize: 18,
    color: '#8A8A9D',
    marginBottom: 40,
  },
  feedbackCard: {
    backgroundColor: '#151521',
    padding: 25,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#2B2B40',
    marginBottom: 50,
    width: '100%',
  },
  feedbackText: {
    color: '#E0E0FF',
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 24,
  },
  buttonMain: {
    backgroundColor: '#6C5DD3',
    paddingVertical: 18,
    paddingHorizontal: 40,
    borderRadius: 30,
    width: '100%',
    shadowColor: '#6C5DD3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  }
});
