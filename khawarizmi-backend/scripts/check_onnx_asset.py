#!/usr/bin/env python3
"""Vérification de l'asset modèle ONNX (embeddings) — diagnostic + récupération.

Usage (depuis khawarizmi-backend/) :
    python scripts/check_onnx_asset.py

Sorties possibles :
    OK        : modèle valide et chargeable
    LFS       : pointeur Git LFS non téléchargé (récupération : git lfs pull)
    CORROMPU  : fichier présent mais illisible par onnxruntime
    MANQUANT  : ni .onnx ni .zip présents
    ZIP       : .onnx absent mais model_quantized.zip présent (décompression auto
                au démarrage par services/embedder.py)
"""
from __future__ import annotations

import os
import pathlib
import sys

BACKEND = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = BACKEND / "models" / "minilm_onnx_int8"
ONNX = MODEL_DIR / "model_quantized.onnx"
ZIP = MODEL_DIR / "model_quantized.zip"


def is_lfs_pointer(path: pathlib.Path) -> bool:
    try:
        head = path.read_bytes()[:64]
    except OSError:
        return False
    return head.startswith(b"version https://git-lfs.github.com/spec/")


def onnx_loadable(path: pathlib.Path) -> bool:
    try:
        import onnxruntime as ort  # noqa: PLC0415

        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        ort.InferenceSession(str(path), opts)
        return True
    except Exception:
        return False


def main() -> int:
    print(f"Modèle : {ONNX}")
    if ONNX.exists() and is_lfs_pointer(ONNX):
        print("STATUT : LFS — pointeur Git LFS non téléchargé.")
        print(f"  taille du fichier : {ONNX.stat().st_size} octets (un modèle réel fait ~118 Mo).")
        print("  RÉCUPÉRATION :")
        print("    git lfs pull --include 'khawarizmi-backend/models/minilm_onnx_int8/*'")
        print("    (puis redémarrer le backend — l'embedder repassera en mode sémantique)")
        return 1
    if ONNX.exists() and onnx_loadable(ONNX):
        print(f"STATUT : OK — modèle valide et chargeable ({ONNX.stat().st_size / 1e6:.1f} Mo).")
        return 0
    if ONNX.exists():
        print(f"STATUT : CORROMPU — fichier présent ({ONNX.stat().st_size} octets) mais illisible par onnxruntime.")
        print("  RÉCUPÉRATION : remplacer le fichier (git lfs pull ou model_quantized.zip).")
        return 2
    if ZIP.exists():
        print("STATUT : ZIP — .onnx absent mais model_quantized.zip présent.")
        print("  L'embedder décompressera automatiquement au prochain démarrage.")
        return 3
    print("STATUT : MANQUANT — ni .onnx ni .zip dans models/minilm_onnx_int8/.")
    print("  RÉCUPÉRATION : git lfs pull (voir scripts/convert_to_onnx.py pour la régénération).")
    return 4


if __name__ == "__main__":
    sys.exit(main())
