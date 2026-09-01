import { NextResponse } from "next/server"
import { configuredApiOrigin, resolvedApiOrigin } from "@/lib/api-origin"

/**
 * Proxy d'API **résolu à la requête** (et non au build).
 *
 * Le problème que ce fichier règle (rapport §11, dette D1) : `next.config.ts` construit ses `rewrites`
 * au **build**. Sur Vercel, `NEXT_PUBLIC_API_URL` est donc figée dans le bundle de déploiement — et la CI
 * (`.github/workflows/ci.yml`, job `deploy-railway`) ne re-déploie que Railway. Chaque changement de
 * domaine du backend re-casse donc la production **sans commit et sans CI rouge** : c'est la raison pour
 * laquelle cette panne a survécu à huit audits.
 *
 * Ici l'origine est lue à chaque requête : changer `API_ORIGIN` dans Vercel → Environment Variables,
 * puis « Redeploy » (ou même simplement relancer, la variable étant lue au runtime), suffit. Le front
 * appelle toujours `/api/...` en same-origin : ni CORS, ni CSP à retoucher.
 *
 * `NEXT_PUBLIC_API_URL` reste acceptée en repli pour ne rien casser pour les devs qui l'ont déjà en `.env`.
 */
export const runtime = "nodejs"
export const dynamic = "force-dynamic"

const UPSTREAM_HEADERS_DROP = new Set([
  "host",
  "connection",
  "keep-alive",
  "upgrade",
  "proxy-authorization",
  "proxy-connection",
  "transfer-encoding",
  "content-length",
  "content-encoding",
  "accept-encoding",
])

const RESPONSE_HEADERS_DROP = new Set(["content-encoding", "content-length", "transfer-encoding", "connection", "keep-alive"])

/** Origine du backend, par requête. Repli de dev partagé avec `next.config.ts` (même module). */
export function apiOrigin(): string {
  return resolvedApiOrigin()
}

function buildTarget(req: Request, segments: string[] | undefined): URL {
  const here = new URL(req.url)
  const path = (segments ?? []).map(encodeURIComponent).join("/")
  const target = new URL(`${apiOrigin()}/api/${path}`)
  // La query string est conservée telle quelle (`/api/x?page=2&tri=desc`).
  if (here.search) target.search = here.search
  return target
}

/** En-têtes transmis : tout sauf ce qui est propre au saut de transport. Le cookie passe (session élève). */
function forwardHeaders(req: Request): Headers {
  const out = new Headers()
  req.headers.forEach((value, key) => {
    if (!UPSTREAM_HEADERS_DROP.has(key.toLowerCase())) out.set(key, value)
  })
  return out
}

async function handle(req: Request, ctx: { params: Promise<{ path?: string[] }> }): Promise<Response> {
  const { path } = await ctx.params
  const target = buildTarget(req, path)
  const method = req.method.toUpperCase()
  const body = method === "GET" || method === "HEAD" ? undefined : await req.arrayBuffer()

  // Cas n°1 traité AVANT tout appel réseau : rien n'est configuré, en prod → 501 de configuration.
  if (!configuredApiOrigin() && process.env.NODE_ENV === "production") {
    return NextResponse.json(
      {
        erreur: "Configuration manquante côté serveur : API_ORIGIN n'est pas défini.",
        status: 501,
        code: "api_origin_non_configuré",
        attendu: "API_ORIGIN = l'origine publique du backend, sans /api",
        path: `/api/${(path ?? []).join("/")}`,
        method,
      },
      { status: 501 },
    )
  }

  let upstream: Response
  try {
    upstream = await fetch(target, {
      method,
      headers: forwardHeaders(req),
      body,
      redirect: "manual",
      cache: "no-store",
    })
  } catch (err) {
    // Forme d'erreur du backend (`routes/errors.py`) : un message arabe élève + un identifiant, jamais
    // une stack trace. 502 et non 500 : c'est le pont qui est cassé, pas la requête de l'élève.
    const requestId = `proxy-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
    console.error(`[api-proxy] ${requestId} ${method} ${target.pathname} → ${String(err)}`)
    return NextResponse.json(
      {
        erreur: "Le serveur de correction est injoignable. Réessaie dans un instant.",
        status: 502,
        path: `/api/${(path ?? []).join("/")}`,
        method,
        requestId,
      },
      { status: 502 },
    )
  }

  const headers = new Headers()
  upstream.headers.forEach((value, key) => {
    if (!RESPONSE_HEADERS_DROP.has(key.toLowerCase())) headers.set(key, value)
  })
  // Corps passé en flux : `/api/chatbot/ask/stream` (SSE) doit continuer à arriver par morceaux.
  return new Response(upstream.body, { status: upstream.status, statusText: upstream.statusText, headers })
}

export const GET = handle
export const POST = handle
export const PUT = handle
export const PATCH = handle
export const DELETE = handle
export const HEAD = handle
export const OPTIONS = handle
