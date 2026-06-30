# Dashboard Orchestrator Feature

## Rôle
Ce dossier contient la logique non visuelle du dashboard orchestrateur.

## Structure
- `types.ts` : contrats TypeScript du feature layer
- `mappers.ts` : transformation backend/local -> UI dashboard
- `fallback.ts` : résolution locale + fallback hors API
- `presentation.ts` : helpers de présentation réutilisables (badges, labels)
- `index.ts` : point d'entrée unique du feature

## Règle d'architecture
- `components/dashboard/orchestrator/` = rendu UI uniquement
- `features/dashboard/orchestrator/` = logique d'assemblage, types, mapping, fallback, helpers de présentation
- `hooks/useDriveDashboard.ts` = hook mince, orchestration de chargement seulement

## Convention
Toute nouvelle logique métier du dashboard doit entrer ici avant d'être consommée par un composant.
