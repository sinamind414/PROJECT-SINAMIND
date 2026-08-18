"use client"

// global-error.tsx — remplace le layout racine en cas d'erreur fatale
// (audit technique 2026-08-18). Obligatoirement client et DOIT rendre
// ses propres <html>/<body>.
export default function GlobalError({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html lang="ar" dir="rtl">
      <body style={{ background: "#0C151A", color: "#fff", fontFamily: "system-ui, sans-serif" }}>
        <div
          style={{
            minHeight: "100vh",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            textAlign: "center",
            padding: "24px",
          }}
        >
          <div style={{ fontSize: 56 }}>⚠️</div>
          <h1 style={{ fontSize: 22, fontWeight: 900 }}>خطأ حرج</h1>
          <p style={{ color: "rgba(255,255,255,0.6)", fontSize: 14, maxWidth: 420 }}>
            وقع خطأ على مستوى التطبيق. أعد المحاولة.
          </p>
          <button
            onClick={reset}
            style={{
              marginTop: 20,
              minHeight: 48,
              padding: "12px 24px",
              borderRadius: 12,
              background: "#2DD4BF",
              color: "#0C151A",
              fontWeight: 800,
              border: "none",
              cursor: "pointer",
            }}
          >
            إعادة المحاولة
          </button>
        </div>
      </body>
    </html>
  )
}
