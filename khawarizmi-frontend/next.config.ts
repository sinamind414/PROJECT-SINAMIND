import type { NextConfig } from "next";
import path from "path";
// Une seule implémentation de la résolution d'origine pour la CSP, le rewrite /health et le proxy
// runtime (`src/app/api/[...path]/route.ts`). Deux lecteurs = deux sources de vérité = la panne de §11.
import { cspApiOrigin, resolvedApiOrigin } from "./src/lib/api-origin";

/**
 * Mesure du 2026-08-31 (rapport §11) : `connect-src` contenait un domaine écrit en dur qui ne sert
 * pas ce dépôt (son `/health` répond « OK », ses 404 `{"message","requestId"}` — deux formes
 * qu'aucun fichier de ce repo ne produit), pendant que le `NEXT_PUBLIC_API_URL` réellement
 * configuré sur Vercel pointait vers un domaine Railway non provisionné. Résultat : changer l'URL
 * côté env sans toucher la CSP laissait le site cassé — le navigateur bloquant l'origine callée.
 * Depuis F32, le cas normal est `connect-src 'self'` seul : le proxy runtime est same-origin.
 */

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  // Security headers — audit technique 2026-08-18 (avant : aucun).
  // La CSP est appliquée en production uniquement : en dev, Next/Turbopack
  // injecte des scripts inline incompatibles avec une CSP stricte.
  async headers() {
    const isProd = process.env.NODE_ENV === "production"
    const origin = cspApiOrigin()
    const csp = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob:",
      "font-src 'self' data:",
      // 'self' suffit quand le client passe par le proxy /api (rewrites) ; l'origine n'est ajoutée
      // que si l'appel part vraiment en cross-origin (API_BASE_URL = NEXT_PUBLIC_API_URL).
      `connect-src 'self'${origin ? ` ${origin}` : ""}`,
      "frame-ancestors 'none'",
      "base-uri 'self'",
      "form-action 'self'",
    ].join("; ")
    const headers: { key: string; value: string }[] = [
      { key: "X-Frame-Options", value: "DENY" },
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
    ]
    if (isProd) headers.push({ key: "Content-Security-Policy", value: csp })
    return [{ source: "/:path*", headers }]
  },
  async rewrites() {
    return [
      // ⚠ Le rewrite `/api/:path*` a été RETIRÉ (mesure du 2026-08-31) : la documentation de Next place
      // les rewrites « afterFiles » **avant** les routes dynamiques — donc tant qu'il existait, il servait
      // toutes les requêtes `/api/*` et masquait complètement le proxy runtime `src/app/api/[...path]/route.ts`.
      // Preuve : avec `API_ORIGIN=http://127.0.0.1:8999` (port mort) et l'amont vivant sur :8000, la
      // requête répondait quand même le JSON de :8000 — c'était le rewrite, figé au build, qui parlait.
      // L'appel `/api/...` passe donc désormais par le handler, qui lit l'origine **à chaque requête**.
      {
        source: "/health",
        // Même résolveur que le proxy runtime : une variable (`API_ORIGIN`) gouverne tout.
        destination: `${resolvedApiOrigin()}/health`,
      },
    ];
  },
};

export default nextConfig;
