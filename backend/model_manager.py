import gc
import torch

from models.qwen_model import QwenModel
from models.qwen_coder_model import QwenCoderModel
from models.qwen_vision_model import QwenVisionModel
from models.flux_model import FluxModel


class ModelManager:

    def __init__(self):

        self.current_model_name = None
        self.current_model = None

        self.models = {
            "qwen": QwenModel(),
            "qwen-vision": QwenVisionModel(),
            "qwen-coder": QwenCoderModel(),
            "flux": FluxModel(),
        }

    def load(self, model_name):

        if model_name not in self.models:
            raise ValueError(
                f"Unknown model: {model_name}"
            )

        model = self.models[model_name]

        print(
            f"Loading model: {model_name}"
        )

        model.load()

        self.current_model_name = model_name
        self.current_model = model

    def unload(self):

        if self.current_model is None:
            return

        print(
            f"Unloading model: "
            f"{self.current_model_name}"
        )

        self.current_model.unload()

        self.current_model = None
        self.current_model_name = None

        gc.collect()

        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        print(
            "Model memory released."
        )

    def switch(self, model_name):

        if self.current_model_name == model_name:
            return

        self.unload()
        self.load(model_name)

    def generate(self, prompt):

        if self.current_model is None:
            self.load("qwen")

        return self.current_model.generate(
            prompt
        )

    def generate_image(prompt):

        self.switch("flux")

        return self.models["flux"].generate(
            prompt
        )

    def generate_project(
            self,
            prompt,
            workspace=None,
    ):
        self.switch("qwen-coder")

        return self.models["qwen-coder"].generate_project(
            prompt,
            workspace
        )

    def get_status(self):

        return {
            "active_model": self.current_model_name,
            "loaded": self.current_model is not None,
            "available_models": list(
                self.models.keys()
            ),
        }