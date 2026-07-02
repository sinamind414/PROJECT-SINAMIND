# Tâche C — Brancher HighlightedAnswer dans le frontend

> Instructions pour Deepseek dans OpenCode.
> À faire APRÈS la Tâche B (RAG). Sinon, l'expérience visuelle sera moins riche
> mais le composant fonctionnera quand même.

**Objectif** : c'est LA fonctionnalité "stylo rouge" que l'utilisateur veut.
Actuellement le backend v2 renvoie déjà des `highlights[]`, mais le frontend
les jette et affiche l'ancien rendu (texte plat). Cette tâche les branche.

**Fichiers existants (déjà commités)** :
- `src/components/methodology/HighlightedAnswer.tsx` (composant + tests, prêt)
- `src/components/methodology/HighlightedAnswer.demo.html` (démo statique)

**Fichiers à modifier** :
- `src/components/methodology/ScenarioRunner.tsx` (3 lignes)
- `src/lib/methodology-evaluator.ts` (ajout 2 champs optionnels au type)
- `src/lib/api-client.ts` (nouvelle méthode `evaluateDaAnswersV2`)

**Interdit** : modifier `HighlightedAnswer.tsx` (fichier gelé, testé).

---

## Session 1 — Vérifier que le composant tourne (5 min)

```bash
cd khawarizmi-frontend
npx vitest run src/components/methodology/HighlightedAnswer.test.ts
```

**Attendu** : `14 passed`. Si un test échoue, `HighlightedAnswer.tsx` a
été touché par erreur — restaurer depuis le repo.

**Vérification visuelle** (utilisateur) :

Ouvrir `src/components/methodology/HighlightedAnswer.demo.html` dans un
vrai navigateur (double-clic). Doit montrer 4 cartes avec les surlignages
colorés selon le type. Si l'utilisateur signale un défaut RTL ou de
palette, **s'arrêter et demander** avant de continuer.

---

## Session 2 — Étendre le type `MethodologyEvaluation` (10 min)

**Fichier** : `khawarizmi-frontend/src/lib/methodology-evaluator.ts`

Ajouter en haut du fichier, après les imports existants :

```ts
import type { Highlight } from "@/components/methodology/HighlightedAnswer"
```

Puis modifier le type `MethodologyEvaluation` en ajoutant 2 champs
**optionnels** (backward compat totale) :

```ts
export type MethodologyEvaluation = {
  verbSlug: string
  score: number
  scoreMax: number
  percentage: number
  // ... champs existants inchangés ...

  // ── Nouveaux champs, présents uniquement quand la réponse vient de la route v2 ──
  highlights?: Highlight[]
  source?: "sanity" | "llm" | "llm_recovered" | "llm_error"
}
```

**Vérifier que TypeScript compile** :

```bash
cd khawarizmi-frontend
npx tsc --noEmit
```

**Attendu** : aucune erreur. Si erreur, c'est qu'un autre fichier construit
un `MethodologyEvaluation` sans ces champs — pas grave puisqu'ils sont
optionnels, mais vérifier qu'aucun cast forcé ne bloque.

---

## Session 3 — Nouvelle méthode `evaluateDaAnswersV2` dans l'API client (15 min)

**Fichier** : `khawarizmi-frontend/src/lib/api-client.ts`

Trouver la méthode existante `evaluateDaAnswers` (vers ligne 681).
**Ne PAS la modifier**. Ajouter juste après une nouvelle méthode :

```ts
async evaluateDaAnswersV2(payload: {
  scenario_id: string
  chapter_slug: string | null
  answers: Array<{ verb_slug: string; answer: string; question_id?: string }>
}) {
  return this.request<{
    session_id: string
    score_global: number
    score_max: number
    percentage: number
    evaluations: Array<{
      question_id: string
      verb_slug: string
      score: number
      score_max: number
      percentage: number
      highlights: Array<{
        start: number
        end: number
        type: "gibberish" | "off_topic" | "missing_link" |
              "wrong_formulation" | "irrelevant" | "good_element"
        message_ar: string
      }>
      matched_criteria: string[]
      unmatched_criteria: Array<{ criterion: string; why_ar: string; from_model_answer: string }>
      feedback_ar: string
      advice_ar: string
      source: "sanity" | "llm" | "llm_recovered" | "llm_error"
    }>
  }>("/api/document-analysis/evaluate-v2", {
    method: "POST",
    body: JSON.stringify(payload),
  })
},
```

**Point important** : ne PAS supprimer `evaluateDaAnswers` (v1). Les deux
coexistent. On basculera plus tard quand tout sera validé en prod.

**Vérifier que TypeScript compile toujours** :

```bash
npx tsc --noEmit
```

---

## Session 4 — Brancher dans `ScenarioRunner.tsx` (20 min)

**Fichier** : `khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx`

**Étape A — Ajouter l'import du composant** en haut du fichier :

```tsx
import { HighlightedAnswer } from "@/components/methodology/HighlightedAnswer"
```

**Étape B — Trouver le bloc actuel qui affiche la réponse de l'élève**
(vers ligne 73 selon le repo initial) :

```tsx
<div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
  <p className="text-gray-400 text-xs font-bold mb-2">إجابتك</p>
  <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
    {item.answer || "إجابة فارغة"}
  </p>
</div>
```

Le remplacer par :

```tsx
<div className="rounded-2xl p-4 bg-white/[0.03] border border-white/[0.05]">
  <p className="text-gray-400 text-xs font-bold mb-2">إجابتك</p>
  <HighlightedAnswer
    answer={item.answer}
    highlights={item.evaluation.highlights ?? []}
    emptyLabel="إجابة فارغة"
  />
</div>
```

**Étape C — Basculer l'appel API v1 → v2** dans le même fichier.

Trouver l'appel actuel (vers ligne 171) :

```tsx
const resp = await apiClient.evaluateDaAnswers(payload)
```

Le remplacer par :

```tsx
const resp = await apiClient.evaluateDaAnswersV2(payload)
```

Puis, dans la fonction qui construit `evaluations` depuis `resp` (ligne 173),
propager les 2 nouveaux champs :

```tsx
const evaluations = questions.map((question) => {
  const evalData = resp.evaluations.find((e) => e.verb_slug === question.verbSlug)
  // ... code existant qui construit un MethodologyEvaluation ...
  return {
    question,
    answer: answers[question.n] ?? "",
    evaluation: {
      // ... champs existants (score, scoreMax, percentage, etc.) ...
      highlights: evalData?.highlights ?? [],    // ← nouveau
      source: evalData?.source,                   // ← nouveau
    },
  }
})
```

**IMPORTANT** : conserver strictement le format existant des autres champs
pour ne pas casser la logique de `CorrectionCard`. On ajoute, on ne remplace pas.

---

## Session 5 — Test manuel bout en bout (utilisateur)

**Deepseek** : demander à l'utilisateur de lancer ces vérifications.

```bash
cd khawarizmi-frontend
npm run dev
# Ouvrir http://localhost:3000/diagnostic/chapters/<un-chapter-slug>
# Se connecter avec un compte de test
# Répondre aux 5 questions avec :
#   - 4 charabias (ERRETREZR, EREZREZT, ?KJ YBYUTIUJPO, BVCGGCVUVUY)
#   - 1 vraie réponse arabe (hypothèse par exemple)
# Cliquer "صحّح التشخيص وسجّل الأخطاء"
```

**Attendu** :
- Les 4 charabias : cartes rouges avec le texte entier surligné en rouge
  foncé, tooltip "غير مفهوم — نص غير مفهوم".
- La vraie réponse : score >= 60%, éventuellement des passages surlignés
  en vert (bons éléments) ou orange (liens manquants).
- Au survol des surlignages : tooltip arabe visible.
- Aucun crash JS dans la console navigateur.

**Points de vigilance visuels** :
- La ponctuation finale (`.` en fin de phrase arabe) ne doit pas se
  détacher visuellement du surlignage.
- Le RTL doit rester cohérent (les highlights suivent le texte de droite
  à gauche).
- Sur mobile (390px de large), les cartes ne débordent pas.

---

## Session 6 — Commit propre

```bash
cd PROJECT-SINAMIND
git status
# Doit montrer 3 fichiers modifiés :
#   khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx
#   khawarizmi-frontend/src/lib/methodology-evaluator.ts
#   khawarizmi-frontend/src/lib/api-client.ts

git add khawarizmi-frontend/src/components/methodology/ScenarioRunner.tsx \
        khawarizmi-frontend/src/lib/methodology-evaluator.ts \
        khawarizmi-frontend/src/lib/api-client.ts

git commit -m "feat(frontend): brancher HighlightedAnswer et route v2 dans ScenarioRunner

Le module de diagnostic SVT appelle maintenant /api/document-analysis/evaluate-v2
(hybride sanity + LLM) et rend la copie de l'élève avec les zones fautives
surlignées en couleur selon leur type, avec tooltip arabe explicatif au survol.

C'est la fonctionnalité 'stylo rouge' demandée : l'élève voit précisément
dans son propre texte ce qui cloche, avec un message pédagogique en arabe.

Changements :
* ScenarioRunner.tsx : remplace <p> par <HighlightedAnswer>, bascule
  l'appel API vers evaluateDaAnswersV2.
* methodology-evaluator.ts : ajoute 2 champs optionnels (highlights, source)
  au type MethodologyEvaluation. Rétrocompatible.
* api-client.ts : nouvelle méthode evaluateDaAnswersV2 typée strictement
  sur la réponse de la route v2. evaluateDaAnswers (v1) conservée.

Vérification manuelle : les 5 charabias d'origine sont maintenant rendus
avec un fond rouge foncé sur tout le texte + tooltip 'غير مفهوم'. Les vraies
réponses arabes reçoivent des surlignages verts/oranges selon les critères
matchés / manquants.

Le composant HighlightedAnswer et ses 14 tests vitest sont inchangés.
"

git push
```

---

## Ce qui doit rester intact après cette tâche

- `HighlightedAnswer.tsx` (composant gelé)
- `HighlightedAnswer.test.ts` (14 tests)
- `evaluateDaAnswers` v1 dans `api-client.ts` (méthode legacy conservée)
- Tous les autres endroits qui utilisent `MethodologyEvaluation` (les 2
  nouveaux champs sont optionnels)

## Cas d'arrêt — demander à l'utilisateur

1. Si `npx tsc --noEmit` renvoie des erreurs après ajout du type Highlight.
2. Si `ScenarioRunner.tsx` a une structure différente de ce que décrit ce
   document (le repo a peut-être évolué).
3. Si les tests vitest de `HighlightedAnswer` cassent (fichier gelé touché ?).
4. Si l'utilisateur signale un défaut visuel majeur (RTL cassé, ponctuation
   détachée, débordement mobile) après le test manuel.
5. Si l'utilisateur veut basculer complètement (supprimer v1) plutôt que
   coexistence — c'est une décision produit, pas technique.
