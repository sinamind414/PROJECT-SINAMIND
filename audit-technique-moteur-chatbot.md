# Audit technique ciblé — moteur chatbot

## Fichiers audités
- `khawarizmi-backend/routes/chatbot.py`
- `khawarizmi-backend/services/chat_service.py`
- `khawarizmi-backend/services/chat_prompt.py`
- `khawarizmi-backend/prompts/free_chat_prompt.py`

## Objectif
Optimiser le moteur chatbot sans casser l'expérience existante, en le rendant plus direct, plus contextuel, plus utile pour un élève BAC SVT algérien Gen Z.

---

# 1. Diagnostic franc

Le chatbot est déjà utilisable, mais il souffre de 4 faiblesses :
1. pas assez d'intention explicite ;
2. historique encore trop verbeux pour certains cas ;
3. pas de cache simple visible sur l'endpoint principal ;
4. quelques cartes d'aide trop génériques.

## Ce qu'il fait bien
- RAG intégré ;
- fallback propre ;
- historique borné ;
- prompt libre déjà structuré ;
- surface API simple.

## Ce qu'il fait mal
- le mode reste surtout "question libre" ;
- les cartes sont statiques et peu contextuelles ;
- le même traitement s'applique à beaucoup de cas ;
- pas de cache basique sur l'endpoint `/api/chatbot/ask`.

---

# 2. Changements sûrs appliqués

## A. Cache léger sur `/api/chatbot/ask`
- Clé basée sur : langue + mode + chapitre + message normalisé
- TTL : 900 secondes (15 min)
- Stockage après réponse LLM succès
- Fallback silencieux si cache échoue

## B. Instruction par mode (`_mode_instruction`)
- `quick` → réponse rapide et claire
- `tutor` → posture de professeur personnel, étape par étape
- `bac` → focalisation sur ce qu'attend le correcteur

## C. Cartes d'aide actionnables
- `quick` : "اشرح لي بسرعة" / "أعطني الأهم للبكالوريا"
- `tutor` : "شرح خطوة بخطوة" / "ساعدني بدون الجواب"
- `bac` : "ماذا ينتظر المصحح؟" / "أين أخطئ عادة؟"

## D. Historique réduit
- 500 → 300 chars par message d'historique

---

# 3. Ce qu'on ne touche pas
- route publique ;
- structure de réponse ;
- fallback principal ;
- intégration RAG ;
- widget frontend.

---

# 4. Résultat attendu
- moins de coût sur questions répétées ;
- mode plus lisible ;
- suggestions plus utiles ;
- historique moins gras ;
- route plus intelligente sans changer son interface.
