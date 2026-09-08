from transformers import pipeline
from PIL import Image


class QwenVisionModel:
    def __init__(self):
        self.pipe = None

    def load(self):
        print("Loading Qwen3-VL-2B-Instruct...")

        self.pipe = pipeline(
            "image-text-to-text",
            model="Qwen/Qwen3-VL-2B-Instruct",
            device="cpu",
        )

        print("Qwen3-VL-2B-Instruct loaded.")

    def generate(self, image_path, prompt):
        if self.pipe is None:
            self.load()

        image = Image.open(image_path).convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        result = self.pipe(
            text=messages,
            max_new_tokens=512,
            do_sample=False,
        )

        return result[0]["generated_text"][-1]["content"]

    def unload(self):
        if self.pipe is None:
            return

        print("Unloading Qwen3-VL-2B-Instruct...")

        del self.pipe
        self.pipe = None