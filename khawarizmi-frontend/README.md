# Khawarizmi Pro — Frontend

Interface utilisateur de la plateforme éducative IA, construite avec Next.js 16.

## Stack

- **Framework** : Next.js 16 + React 19
- **Style** : TailwindCSS 4
- **Langue** : Arabe (RTL) / Français
- **API** : Axios vers backend FastAPI
- **Mobile** : React Native + Expo 56 (projet séparé)

## Structure

```
src/
├── app/          ← Pages (App Router)
├── components/   ← Composants réutilisables
├── lib/          ← Utilitaires, API client
├── hooks/        ← Custom hooks
└── styles/       ← Styles globaux
```

## Commandes

```bash
npm install       # Installer les dépendances
npm run dev       # Lancement développement (port 3000)
npm run build     # Build production
npm run lint      # ESLint
npx tsc --noEmit  # TypeScript check
```

## Design

- Support RTL (arabe)
- Thème sombre/clair via TailwindCSS
- Composants réutilisables dans `components/`
- Page d'accueil avec étapes pédagogiques (Feynman → FSRS → Bac)

## Documentation

Voir `AGENTS.md` pour les règles de contribution.
