import psutil
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "Qwen/Qwen3-4B"


pipe = pipeline(
    "text-generation",
    model=MODEL_NAME,
    device="mps"
)

class RequestBody(BaseModel):
    prompt: str

@app.post("/generate")
def generate(request: RequestBody):
    messages = [
        {
            "role": "system",
            "content": "Answer the user's question directly and clearly. Decide the appropriate response length based on the question. Give only the final answer; do not include your reasoning or thinking process."
        },
        {
            "role": "user",
            "content": request.prompt
        }
    ]

    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )

    result = pipe(
        prompt,
        max_new_tokens=1024
    )

    return {
        "response": result[0]["generated_text"][len(prompt):].strip()
    }

@app.get("/model-info")
def model_info():
    return {
        "name": "Qwen/Qwen3-4B",
        "type": "causal-language-model",
        "parameters": "4B",
        "license": "Apache-2.0",
        "capabilities": {
            "text_generation": True,
            "summarization": True,
            "translation": True,
            "reasoning": True,
            "coding": True,
            "tool_usage": True,
            "image_generation": False,
            "image_understanding": False,
            "text_to_speech": False,
            "speech_to_text": False,
            "text_to_video": False
        }
    }

@app.get("/system/memory")
def memory_info():

    memory = psutil.virtual_memory()

    return {
        "total_gb": round(memory.total / (1024 ** 3), 2),
        "available_gb": round(memory.available / (1024 ** 3), 2),
        "used_gb": round(memory.used / (1024 ** 3), 2),
        "usage_percent": memory.percent,
    }
