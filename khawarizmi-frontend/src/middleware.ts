// src/middleware.ts
// Protection stricte des routes côté serveur

import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const PROTECTED_ROUTES = [
  "/dashboard",
  "/diagnostic",
  "/drill",
  "/feynman",
  "/scanner",
  "/exercises",
  "/mindmap",
  "/progress"
]

const AUTH_ROUTES = [
  "/auth/login",
  "/auth/register"
]

export function middleware(request: NextRequest) {
  const tokenCookie = request.cookies.get("khawarizmi_token")?.value
  const { pathname } = request.nextUrl

  const isProtected = PROTECTED_ROUTES.some(route => pathname.startsWith(route))
  const isAuthRoute = AUTH_ROUTES.some(route => pathname.startsWith(route))

  // 1. Visiteur anonyme tentant d'accéder à une page privée -> Redirect Login
  if (isProtected && !tokenCookie) {
    const loginUrl = new URL("/auth/login", request.url)
    loginUrl.searchParams.set("redirect", pathname)
    return NextResponse.redirect(loginUrl)
  }

  // 2. Utilisateur connecté tentant d'accéder à Login/Register -> Redirect Dashboard
  if (isAuthRoute && tokenCookie) {
    const dashboardUrl = new URL("/dashboard", request.url)
    return NextResponse.redirect(dashboardUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/diagnostic/:path*",
    "/drill/:path*",
    "/feynman/:path*",
    "/scanner/:path*",
    "/exercises/:path*",
    "/mindmap/:path*",
    "/progress/:path*",
    "/auth/:path*"
  ]
}
