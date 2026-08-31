import type { NextConfig } from "next";
import path from "path";

/**
 * Origine de l'API, dérivée de la MÊME variable que les rewrites ci-dessous.
 *
 * Mesure du 2026-08-31 (rapport §11) : `connect-src` Contenait un domaine écrit en dur qui ne sert
 * pas ce dépôt (son `/health` répond « OK », ses 404 `{"message","requestId"}` — deux formes
 * qu'aucun fichier de ce repo ne produit), pendant que le `NEXT_PUBLIC_API_URL` réellement
 * configuré sur Vercel pointait vers un domaine Railway non provisionné. Résultat : changer l'URL
 * côté env sans toucher la CSP laissait le site cassé — le navigateur bloquant l'origine callée.
 * Une seule source de vérité, donc, et aucun hôte en dur.
 */
function apiOrigin(raw?: string): string | null {
  if (!raw) return null
  try {
    const u = new URL(raw)
    return u.protocol === "http:" || u.protocol === "https:" ? u.origin : null
  } catch {
    return null
  }
}

const nextConfig: NextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  // Security headers — audit technique 2026-08-18 (avant : aucun).
  // La CSP est appliquée en production uniquement : en dev, Next/Turbopack
  // injecte des scripts inline incompatibles avec une CSP stricte.
  async headers() {
    const isProd = process.env.NODE_ENV === "production"
    const origin = apiOrigin(process.env.NEXT_PUBLIC_API_URL)
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
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/health`,
      },
    ];
  },
};

export default nextConfig;
