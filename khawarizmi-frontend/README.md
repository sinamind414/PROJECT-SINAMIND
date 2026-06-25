# Khawarizmi Frontend

Interface utilisateur de la plateforme IA Khawarizmi Pro — Bac SVT Algérie.

## Stack technique

- **Framework** : Next.js 16 (App Router)
- **UI** : React 19 + TailwindCSS 4
- **Animations** : Framer Motion
- **Langue** : Arabe (RTL)
- **Design system** : Glassmorphism, mint/orange palette

## Structure

```
src/
├── app/           → Pages (dashboard, cours, mindmap, exercises...)
├── components/    → Composants réutilisables (layout, ui, features)
├── lib/           → Auth context, API client, hooks
├── styles/        → Globaux CSS
└── public/        → Assets statiques
```

## Commandes

```bash
npm run dev       # Développement
npm run build     # Production
npm run lint      # Linting
npm run typecheck # TypeScript
```

## Design system

Le projet utilise :
- `mint` / `mint-soft` / `teal` — Couleurs primaires (vert scientifique)
- `orange` — Accents et alertes
- `slate-deep` / `slate-300` — Fonds et textes
- RTL (`dir="rtl"`) — Arabe comme langue principale

## Références

- `AGENTS.md` — Règles et conventions du projet

---

**Projet :** IA Khawarizmi Pro — Bac Sciences Naturelles Algérie
