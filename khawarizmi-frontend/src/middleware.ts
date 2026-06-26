// src/middleware.ts
// Protection routes désactivée — auth gérée côté client par AuthProvider
// Le JWT est stocké dans un cookie HttpOnly et validé par le backend

export function middleware() {
  return undefined
}

export const config = {
  matcher: []
}
