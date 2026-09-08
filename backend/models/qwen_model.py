import torch
from transformers import pipeline


class QwenModel:

    def __init__(self):
        self.pipe = None

    def load(self):
        print("Loading Qwen3-4B...")

        self.pipe = pipeline(
            "text-generation",
            model="Qwen/Qwen3-4B",
            device="mps",
        )

        print("Qwen3-4B loaded.")

    def generate(self, prompt):
        if self.pipe is None:
            self.load()

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        prompt_text = self.pipe.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )

        # Keep the RAG context within a safe size.
        inputs = self.pipe.tokenizer(
            prompt_text,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )

        input_ids = inputs["input_ids"].to("mps")
        attention_mask = inputs["attention_mask"].to("mps")

        with torch.no_grad():
            output_ids = self.pipe.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=2048,
                do_sample=False,
                use_cache=True,
            )

        generated_ids = output_ids[0][input_ids.shape[-1]:]

        # Move generated token IDs to CPU before decoding.
        generated_ids = generated_ids.detach().cpu()

        response = self.pipe.tokenizer.decode(
            generated_ids,
            skip_special_tokens=True,
        )

        return response.strip()

    def unload(self):
        if self.pipe is None:
            return

        print("Unloading Qwen3-4B...")

        del self.pipe
        self.pipe = None