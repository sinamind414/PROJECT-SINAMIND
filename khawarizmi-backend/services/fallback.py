import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger("khawarizmi.fallback")

def normalize_arabic(text: str) -> str:
    """
    Normalise le texte arabe pour éviter les échecs de matching liés 
    aux diacritiques (tashkeel), aux variantes de hamza, etc.
    """
    if not text:
        return ""
        
    # Supprimer les diacritiques (tashkeel)
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F]', '', text)
    # Normaliser les variantes de alef
    text = re.sub(r'[أإآا]', 'ا', text)
    # Normaliser les variantes de hamza
    text = re.sub(r'[ؤئ]', 'ء', text)
    # Normaliser ya finale et ta marbouta
    text = re.sub(r'[ىي]', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    # Minuscules pour les termes latins mélangés
    return text.lower().strip()

def fallback_evaluate(pattern: str, reponse: str) -> Dict[str, Any]:
    """
    Évaluation algorithmique de secours (Niveau 2).
    Utilise le pattern de recherche (mots-clés séparés par &&).
    Ne retourne JAMAIS CORRECT (score max 5/10).
    """
    if not pattern:
        # S'il n'y a pas de pattern, le fallback ne peut pas juger
        return {
            "score": 0,
            "statut": "FAUX",
            "feedback": "Impossible de valider automatiquement. (Évaluation rapide)",
            "manquant": []
        }

    termes = [t.strip() for t in pattern.split('&&') if t.strip()]
    if not termes:
        return {
            "score": 0,
            "statut": "FAUX",
            "feedback": "Critères d'évaluation absents. (Évaluation rapide)",
            "manquant": []
        }

    reponse_norm = normalize_arabic(reponse)
    manquant: List[str] = []
    
    for terme in termes:
        terme_norm = normalize_arabic(terme)
        # Gestion basique des OU dans le pattern (ex: ADN || مورثة)
        sub_terms = [t.strip() for t in terme.split('||')]
        found = False
        for st in sub_terms:
            st_norm = normalize_arabic(st)
            if st_norm in reponse_norm:
                found = True
                break
        
        if not found:
            # On ajoute le premier terme officiel comme manquant
            manquant.append(sub_terms[0])
    
    ratio = 1 - (len(manquant) / len(termes))
    
    if ratio < 0.5:
        return {
            "score": 2, 
            "statut": "FAUX",
            "feedback": "Des mots-clés essentiels manquent. (Évaluation rapide — précise ta réponse.)",
            "manquant": manquant
        }
    else:
        return {
            "score": 5, 
            "statut": "PARTIEL", 
            "feedback": "Mots-clés détectés. (Évaluation rapide — précise ta réponse complète.)",
            "manquant": manquant
        }

def fallback_safe_json() -> Dict[str, Any]:
    """
    Niveau 3 — Le JSON de secours absolu.
    """
    return {
        "score"   : 0,
        "statut"  : "ERREUR",
        "feedback": "L'algorithme de Khawarizmi est en cours de mise à jour. Réessaie dans quelques secondes.",
        "manquant": []
    }
