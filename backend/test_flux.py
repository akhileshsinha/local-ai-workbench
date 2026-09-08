from models.flux_model import FluxModel


model = FluxModel()

model.generate(
    prompt=(
        "A futuristic software development office, "
        "large transparent screens displaying AI code, "
        "modern cinematic lighting, highly detailed"
    ),
    output_path="test_flux.png",
)

model.unload()