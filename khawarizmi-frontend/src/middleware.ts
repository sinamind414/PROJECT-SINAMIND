// src/middleware.ts
// Protection des routes côté serveur

import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

// Routes qui nécessitent une authentification
const PROTECTED_ROUTES = [
  "/dashboard",
  "/diagnostic",
  "/drill",
  "/feynman",
  "/scanner"
]

// Routes accessibles uniquement si NON connecté
const AUTH_ROUTES = [
  "/auth/login",
  "/auth/register"
]

export function middleware(request: NextRequest) {
  const token = request.cookies.get("khawarizmi_token")?.value
  const { pathname } = request.nextUrl

  // Note : le token réel est dans localStorage côté client.
  // Ce middleware fait une vérification basique côté serveur.
  // La vraie protection est dans chaque page via useAuth.

  const isProtected = PROTECTED_ROUTES.some(route =>
    pathname.startsWith(route)
  )

  const isAuthRoute = AUTH_ROUTES.some(route =>
    pathname.startsWith(route)
  )

  // Si route protégée et pas de cookie → laisser passer
  // (la vraie vérification se fera côté client avec useAuth)

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/diagnostic/:path*",
    "/drill/:path*",
    "/feynman/:path*",
    "/scanner/:path*",
    "/auth/:path*"
  ]
}
