#!/usr/bin/env python3
"""Vérifie que le frontend et le backend de production sont BRANCHÉS L'UN SUR L'AUTRE.

Pourquoi ce script (rapport §11 et §19, dette D1) : la panne n'était pas une exception, c'était un
silence. `connect-src` whitelistait un domaine qui ne sert pas ce dépôt, `NEXT_PUBLIC_API_URL` de Vercel
pointait un domaine Railway non provisionné, et comme la destination du rewrite était figée au build
pendant que la CI ne re-déploie que Railway, rien ne rougeait jamais.

Le script distingue les trois pannes par EMPREINTE, pas par code HTTP :
  A. l'amont n'est pas CE dépôt  → /health répond autre chose que l'objet de diagnostic de routes/health.py
  B. le proxy du front ne suit pas → /api/... ne répond pas comme l'amont
  C. les drapeaux de correction sont éteints → health.correction.local_rubric_grader est false

Usage :
  python3 scripts/verify_prod_api.py \\
      --front https://khawarizmi-ia-two.vercel.app \\
      --back https://<domaine-railway>            # optionnel : sans lui, seul le front est testé

Sortie : 0 si tout est cohérent, 1 sinon, avec la correction à appliquer pour chaque échec.
Aucune dépendance (urllib seul) : il doit tourner sur la machine du prof, pas seulement dans un conteneur.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request

TIMEOUT = 20
# Les formes d'erreur que CE dépôt produit (routes/errors.py). Toute autre forme = autre service.
NOTES = {
    "A": "L'amont interrogé ne court pas ce dépôt. Son /health ne renvoie pas l'objet de diagnostic "
         "(clés status/database/redis/correction). Vérifie le service Railway pointé.",
    "B": "Le proxy du front ne rejoint pas le backend. Depuis F32, le front appelle son propre /api "
         "(same-origin) et le handler lit API_ORIGIN À CHAQUE REQUÊTE : pose API_ORIGIN dans Vercel "
         "(sans /api), puis « Redeploy ». Un 501 {code: api_origin_non_configuré} = la variable est absente.",
    "C": "Le correcteur local est éteint côté backend : ajoute LOCAL_RUBRIC_GRADER=true (et "
         "SAVOIR_REMEDIATION_ENABLED=true si tu assumes les seuils) dans Railway, puis redémarre.",
}


def fetch(url: str) -> tuple[int | None, str, str]:
    """Retourne (status, body_texte, erreur). Ne lève jamais : un échec réseau EST le résultat attendu ici."""
    req = urllib.request.Request(url, headers={"user-agent": "khawarizmi-verify/1", "accept": "application/json"})
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            return r.status, r.read(200_000).decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as e:
        return e.code, e.read(200_000).decode("utf-8", "replace"), ""
    except Exception as e:  # DNS, TLS, timeout, egress bouché
        return None, "", f"{type(e).__name__}: {e}"


def as_json(body: str) -> dict | None:
    try:
        d = json.loads(body)
        return d if isinstance(d, dict) else None
    except Exception:
        return None


def is_this_repo_health(d: dict | None) -> bool:
    return bool(d) and {"status", "database", "redis"} <= set(d)


FAILURES: set[str] = set()


def check(name: str, ok: bool, note: str = "", detail: str = "") -> bool:
    print(f"  [{'✓' if ok else '✗'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.add(note)
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--front", required=True, help="URL publique du frontend Vercel, sans /api")
    ap.add_argument("--back", default="", help="URL publique du backend (optionnel, pour l'empreinte)")
    a = ap.parse_args()
    front = a.front.rstrip("/")
    back = a.back.rstrip("/")
    results: list[bool] = []

    print("1) Empreinte du backend (est-ce bien CE dépôt ?)")
    if back:
        st, body, err = fetch(f"{back}/health")
        d = as_json(body)
        results.append(check(f"GET {back}/health → {st or 'aucune réponse'}", is_this_repo_health(d), "A",
                             err or (d or {}).get("status", body[:60])))
        if is_this_repo_health(d):
            print(f"        database={d.get('database')} · redis={d.get('redis')} · env={d.get('environment')}")
            if d.get("status") != "healthy":
                print("        ⚠ c'est bien ce dépôt, mais il se déclare « degraded » : base ou cache HS.")
            corr = d.get("correction") or {}
            results.append(check("LOCAL_RUBRIC_GRADER=allumé", corr.get("local_rubric_grader") is True, "C",
                                  f"correction={corr or 'absent (backend antérieur à ce correctif)'}"))
        # Un 404 de CE dépôt a la forme de routes/errors.py ; `{"message","requestId"}` = autre service.
        st2, body2, _ = fetch(f"{back}/api/__inexistant__")
        d2 = as_json(body2)
        results.append(check(f"GET /api/__inexistant__ → {st2}", st2 == 404 and bool(d2) and "erreur" in d2, "A",
                             body2[:90]))
    else:
        print("  [–] --back non fourni : empreinte du backend ignorée")

    print("\n2) Le proxy du front atteint-il un backend vivant ?")
    st, body, err = fetch(f"{front}/api/manhadjiya/verbs")
    d = as_json(body)
    proxied = st == 200 or (st == 404 and bool(d) and "erreur" in d)
    results.append(check(f"GET {front}/api/manhadjiya/verbs → {st or 'aucune réponse'}", proxied, "B",
                         err or body[:90]))
    if isinstance(d, dict) and d.get("code") == "api_origin_non_configuré":
        print("        → le handler répond 501 : `API_ORIGIN` n'est pas posé dans Vercel (panne de config, pas réseau)")
    st_h, body_h, _ = fetch(f"{front}/health")
    results.append(check(f"GET {front}/health → {st_h}", is_this_repo_health(as_json(body_h)), "B", body_h[:90]))

    print("\n3) Verdict")
    if all(results):
        print("  ✓ front et backend branchés l'un sur l'autre, correcteur local allumé.")
        return 0
    print(f"  ✗ {sum(1 for r in results if not r)} vérification(s) en échec — {sorted(FAILURES)}")
    for k in sorted(FAILURES):
        print(f"\n  [{k}] {NOTES[k]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
