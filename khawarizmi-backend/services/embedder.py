# -*- coding: utf-8 -*-
"""
services/embedder.py - Service d'embeddings unifié (Sentence-Transformers / ONNX quantizé).
"""

import os
import logging
import numpy as np
from typing import List

logger = logging.getLogger("khawarizmi.embedder")

class KhawarizmiEmbedder:
    """
    Abstraction unique : même interface, deux backends selon l'environnement.
    Sélection automatique via variable d'environnement USE_ONNX=1
    """
    
    def __init__(self):
        self.backend = os.getenv("USE_ONNX", "0") == "1"
        
        if self.backend:
            try:
                self._init_onnx()
            except Exception as e:
                logger.error(f"Impossible d'initialiser ONNX, repli vers sentence-transformers: {e}")
                self.backend = False
                self._init_sentence_transformers()
        else:
            self._init_sentence_transformers()
        
        logger.info(f"Embedder initialisé : {'ONNX INT8' if self.backend else 'sentence-transformers'}")
    
    def _init_onnx(self):
        from optimum.onnxruntime import ORTModelForFeatureExtraction
        from transformers import AutoTokenizer
        
        # On résout le chemin absolu du modèle ONNX
        model_path = os.getenv("ONNX_MODEL_PATH", "models/minilm_onnx_int8")
        if not os.path.isabs(model_path):
            # Prendre relativement à la racine du projet
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, model_path)
            
        logger.info(f"Initialisation ONNX avec le modèle à : {model_path}")
        
        # Décompresser le modèle zip s'il n'existe pas en tant qu'onnx
        onnx_file = os.path.join(model_path, "model_quantized.onnx")
        zip_file = os.path.join(model_path, "model_quantized.zip")
        if not os.path.exists(onnx_file) and os.path.exists(zip_file):
            logger.info(f"Décompression du modèle ONNX depuis {zip_file}...")
            import zipfile
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(model_path)
                logger.info("Décompression du modèle ONNX terminée.")
            except Exception as e:
                logger.error(f"Erreur lors de la décompression du modèle ONNX: {e}")
                
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = ORTModelForFeatureExtraction.from_pretrained(model_path, file_name="model_quantized.onnx")
    
    def _init_sentence_transformers(self):
        from sentence_transformers import SentenceTransformer
        logger.info("Initialisation de sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)...")
        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Interface identique quel que soit le backend"""
        if not texts:
            return np.empty((0, 384))
            
        if self.backend:
            return self._encode_onnx(texts)
        else:
            return self.model.encode(texts, normalize_embeddings=True)
    
    def _encode_onnx(self, texts: List[str]) -> np.ndarray:
        import torch
        
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=128,  # Suffisant pour les réponses SVT courtes
            return_tensors="pt"
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling (identique à sentence-transformers)
        attention_mask = inputs["attention_mask"]
        token_embeddings = outputs.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        embeddings = embeddings / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
        # Normalisation L2
        norms = torch.norm(embeddings, dim=1, keepdim=True)
        embeddings = embeddings / norms
        
        return embeddings.numpy()

# Lazy singleton — chargé à la première utilisation, pas à l'import
_embedder_instance = None

def get_embedder() -> "KhawarizmiEmbedder":
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = KhawarizmiEmbedder()
    return _embedder_instance

# Compatibilité backward : embedder.encode(...) continue de fonctionner
class _LazyEmbedder:
    def encode(self, texts):
        return get_embedder().encode(texts)

embedder = _LazyEmbedder()
