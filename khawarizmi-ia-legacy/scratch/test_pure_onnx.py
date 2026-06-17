import os
import sys
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

def test_pure_onnx():
    model_path = r"c:\Users\zakaria\Documents\PROJET KHAWARIZMI IA\khawarizmi-backend\models\minilm_onnx_int8"
    
    # 1. Load tokenizer
    tokenizer_file = os.path.join(model_path, "tokenizer.json")
    print(f"Loading tokenizer from {tokenizer_file}...")
    tokenizer = Tokenizer.from_file(tokenizer_file)
    
    # Configure padding and truncation (optional, but good practice)
    tokenizer.enable_truncation(max_length=128)
    tokenizer.enable_padding(direction="right", pad_id=0, pad_type_id=0, pad_token="[PAD]")
    
    # 2. Load ONNX model
    onnx_file = os.path.join(model_path, "model_quantized.onnx")
    print(f"Loading ONNX model from {onnx_file}...")
    session = ort.InferenceSession(onnx_file)
    
    # 3. Encode texts
    texts = ["تركيب البروتين في الخلية", "La transcription de l'ADN"]
    print(f"Encoding texts: {texts}")
    
    encodings = tokenizer.encode_batch(texts)
    
    # Prepare inputs for ONNX session
    input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
    token_type_ids = np.array([e.type_ids for e in encodings], dtype=np.int64)
    
    # Run session
    inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids
    }
    
    outputs = session.run(None, inputs)
    last_hidden_state = outputs[0]  # Shape: (batch_size, seq_len, hidden_dim)
    print("Last hidden state shape:", last_hidden_state.shape)
    
    # 4. Mean Pooling in numpy
    input_mask_expanded = np.expand_dims(attention_mask, axis=-1).astype(float)
    sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
    sum_mask = np.sum(input_mask_expanded, axis=1)
    sum_mask = np.clip(sum_mask, 1e-9, None)
    embeddings = sum_embeddings / sum_mask
    
    # L2 Normalization
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-9, None)
    embeddings = embeddings / norms
    
    print("Embedded successfully!")
    print("Embeddings shape:", embeddings.shape)
    print("Sample embedding prefix:", embeddings[0][:5])

if __name__ == "__main__":
    test_pure_onnx()
