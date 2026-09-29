"""
Explanation Module for EduGenie
Uses MBZUAI/LaMini-Flan-T5-783M to explain educational concepts in simple, student-friendly terms.
Implements single-instance lazy loading, thread-safety, and robust error handling.
"""

import os
import logging
import threading
from typing import Optional, Tuple, Any

logger = logging.getLogger("EduGenie.Explanation")

MODEL_NAME = os.getenv("EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M")

_model_lock = threading.Lock()
_tokenizer = None
_model = None
_device = -1
_model_load_error: Optional[str] = None
_is_loading = False

def get_model_and_tokenizer() -> Tuple[Any, Any, int]:
    """
    Loads and caches the MBZUAI/LaMini-Flan-T5-783M model and tokenizer.
    Ensures model is loaded once into memory and reused across requests.
    """
    global _tokenizer, _model, _device, _model_load_error, _is_loading

    if _model is not None and _tokenizer is not None:
        return _model, _tokenizer, _device

    with _model_lock:
        if _model is not None and _tokenizer is not None:
            return _model, _tokenizer, _device

        _is_loading = True
        logger.info(f"Loading explanation model '{MODEL_NAME}'... (runs once)")
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

            # Determine device (CUDA if GPU is available, else CPU)
            _device = 0 if torch.cuda.is_available() else -1
            logger.info(f"Using device: {'CUDA' if _device == 0 else 'CPU'}")

            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            _model = AutoModelForSeq2SeqLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float32 if _device == -1 else torch.float16,
                low_cpu_mem_usage=True
            )

            if _device == 0:
                _model = _model.cuda()

            _model_load_error = None
            logger.info(f"Model '{MODEL_NAME}' successfully loaded into memory.")
            return _model, _tokenizer, _device
        except Exception as e:
            _model_load_error = str(e)
            logger.error(f"Failed to load explanation model '{MODEL_NAME}': {e}", exc_info=True)
            raise RuntimeError(
                f"Failed to load explanation model '{MODEL_NAME}'. "
                f"Ensure internet connectivity for the initial download and sufficient memory. Details: {e}"
            )
        finally:
            _is_loading = False

def explain_topic(topic: str) -> str:
    """
    Generates a simple, student-friendly explanation of a concept using MBZUAI/LaMini-Flan-T5-783M.
    
    Args:
        topic: The topic or concept to explain (e.g. 'Pythagoras theorem').
        
    Returns:
        A concise, clear explanation string.
        
    Raises:
        ValueError: If topic is empty.
        RuntimeError: If model loading or inference fails.
    """
    cleaned_topic = topic.strip() if topic else ""
    if not cleaned_topic:
        raise ValueError("Topic cannot be empty. Please provide a topic to explain.")

    model, tokenizer, device = get_model_and_tokenizer()

    prompt = f"Please explain the concept of '{cleaned_topic}' in simple, clear, and beginner-friendly terms suitable for a school student."

    try:
        logger.info(f"Generating explanation for topic: '{cleaned_topic}'")
        import torch

        inputs = tokenizer(prompt, return_tensors="pt")
        if device == 0:
            inputs = {k: v.cuda() for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.2
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        if not generated_text:
            raise RuntimeError("Model returned empty text.")

        return generated_text
    except Exception as e:
        logger.error(f"Inference error while explaining '{cleaned_topic}': {e}")
        raise RuntimeError(f"Failed to generate explanation: {e}")
