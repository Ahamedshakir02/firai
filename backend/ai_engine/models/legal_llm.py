"""
Legal LLM Service
-----------------
Local generative AI for conversational legal answers.
Uses Qwen2.5-0.5B-Instruct running on CPU.
"""

import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

_model = None
_tokenizer = None
_pipe = None

def warmup():
    global _model, _tokenizer, _pipe
    if _model is not None:
        return
    
    print("[Legal LLM] Loading Qwen2.5-0.5B-Instruct for conversational answers...")
    model_id = "Qwen/Qwen2.5-0.5B-Instruct"
    
    try:
        # Run on CPU. 
        _tokenizer = AutoTokenizer.from_pretrained(model_id)
        _model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            torch_dtype=torch.float32, 
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        
        _pipe = pipeline(
            "text-generation",
            model=_model,
            tokenizer=_tokenizer,
            max_new_tokens=256,
            temperature=0.3,
            do_sample=True,
            repetition_penalty=1.1,
        )
        print("[Legal LLM] Generative model loaded successfully.")
    except Exception as e:
        print(f"[Legal LLM] Error loading model: {e}")

def is_ready():
    return _pipe is not None

def generate_answer(question: str, context: str) -> str:
    if not is_ready():
        return "I'm currently loading my advanced conversational models. I'll be ready in just a moment!"
        
    system_prompt = (
        "You are an expert AI Legal Assistant for the Kerala Police. "
        "Your task is to answer legal questions accurately based ONLY on the provided context. "
        "Do not invent or guess any legal information. If the context does not contain the answer, "
        "politely inform the user. Keep your answer conversational, concise, and professional."
    )
    
    user_prompt = f"Context from Knowledge Base:\n{context}\n\nQuestion:\n{question}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Use chat template
        prompt = _tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        outputs = _pipe(prompt)
        generated_text = outputs[0]["generated_text"]
        
        # Extract only the assistant's reply (Qwen uses <|im_start|> and <|im_end|>)
        if "<|im_start|>assistant" in generated_text:
            reply = generated_text.split("<|im_start|>assistant\n")[-1].split("<|im_end|>")[0].strip()
        else:
            reply = generated_text[len(prompt):].strip()
            
        return reply
    except Exception as e:
        print(f"[Legal LLM] Generation error: {e}")
        return "I encountered an error while generating a response. Please check the backend logs."
