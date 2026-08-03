"""Prompt-building logic for image generation.

Pure Python (no torch / diffusers) so it can be tested LOCALLY without a GPU.
"""
from src.persona.persona import Persona

QUALITY = ("photorealistic, natural skin texture, "
           "soft natural lighting, high detail, sharp focus")

NEGATIVE = ("plastic skin, airbrushed, cgi, 3d render, cartoon, illustration, "
            "deformed, extra fingers, blurry, out of focus, "
            "watermark, text, low quality")


def build_prompt(persona: Persona, scene: str = "") -> str:
    """Positive prompt: subject + appearance + optional scene + quality tokens."""
    subject = (f"candid photo of a {persona.age}-year-old {persona.personality} person, "
               f"{persona.appearance}")
    if scene:
        subject += f", {scene}"
    return f"{subject}, {QUALITY}"


def build_negative_prompt() -> str:
    """What to steer AWAY from — fights the plastic/AI look."""
    return NEGATIVE


if __name__ == "__main__":
    aria = Persona("Aria", 24, "cheerful", "warm smile and freckles")
    print("NO SCENE:\n", build_prompt(aria))
    print("\nWITH SCENE:\n",
          build_prompt(aria, "on a busy Tokyo street at night, neon signs"))
    print("\nNEGATIVE:\n", build_negative_prompt())
