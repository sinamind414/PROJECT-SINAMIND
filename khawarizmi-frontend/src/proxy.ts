// src/proxy.ts
// Protection routes désactivée — auth gérée côté client par AuthProvider.
// Le JWT est stocké dans un cookie HttpOnly et validé par le backend.
// Convention Next 16 : proxy remplace middleware.

export function proxy() {
  return undefined
}

export const config = {
  matcher: []
}
