// src/middleware.ts
// Protection routes désactivée — auth gérée côté client par AuthProvider
// Le token est dans localStorage (invisible pour le middleware server-side)

export function middleware() {
  return undefined
}

export const config = {
  matcher: []
}
