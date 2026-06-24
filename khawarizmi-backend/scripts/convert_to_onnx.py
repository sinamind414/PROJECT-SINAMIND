"""
scripts/convert_to_onnx.py - Export et quantification INT8 du modèle d'embeddings pour la production.
"""

import os
import sys

# Ajouter le répertoire parent au path pour les imports si nécessaire
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
OUTPUT_DIR = "models/minilm_onnx_int8"


def main():
    print("Export vers ONNX...")
    # Étape 1 : Export ONNX
    model = ORTModelForFeatureExtraction.from_pretrained(MODEL_NAME, export=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    # Étape 2 : Quantisation INT8
    print("Quantisation INT8...")
    qconfig = AutoQuantizationConfig.avx512_vnni(
        is_static=False,  # Quantisation dynamique
        per_channel=False,
    )

    quantizer = ORTQuantizer.from_pretrained(model)
    quantizer.quantize(save_dir=OUTPUT_DIR, quantization_config=qconfig)

    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"ONNX INT8 model saved in {OUTPUT_DIR}/")

    # Calcul de la taille finale
    total_size = sum(
        os.path.getsize(os.path.join(OUTPUT_DIR, f))
        for f in os.listdir(OUTPUT_DIR)
        if os.path.isfile(os.path.join(OUTPUT_DIR, f))
    )
    print(f"Final size: {total_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
