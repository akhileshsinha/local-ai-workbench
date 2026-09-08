from transformers import pipeline

MODEL_NAME = "Qwen/Qwen3-VL-2B-Instruct"

print("Loading vision model...")

pipe = pipeline(
    "image-text-to-text",
    model=MODEL_NAME,
    device="cpu",
)

print("Vision model loaded successfully.")

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "url": "test-image.png",
            },
            {
                "type": "text",
                "text": "Describe this image and identify the main elements you can see.",
            },
        ],
    }
]

result = pipe(
    text=messages,
    max_new_tokens=256,
    do_sample=False,
)

print("\nResponse:")
print(result[0]["generated_text"][-1]["content"])