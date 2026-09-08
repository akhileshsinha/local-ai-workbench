import gc
import torch
from diffusers import FluxPipeline


class FluxModel:

    def __init__(self):
        self.pipe = None

    def load(self):
        print("Loading FLUX.1-schnell...")

        self.pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=torch.bfloat16,
        )

        self.pipe.enable_model_cpu_offload()

        print("FLUX.1-schnell loaded.")

    def generate(
        self,
        prompt: str,
        output_path: str,
    ):
        if self.pipe is None:
            self.load()

        print("Generating image...")

        result = self.pipe(
            prompt=prompt,
            num_inference_steps=4,
            guidance_scale=0.0,
        )

        image = result.images[0]

        image.save(output_path)

        print(
            f"Image generated: {output_path}"
        )

        return image

    def unload(self):
        if self.pipe is None:
            return

        print("Unloading FLUX.1-schnell...")

        del self.pipe
        self.pipe = None

        gc.collect()

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()