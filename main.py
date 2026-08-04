"""Entry point: run the pipeline through the orchestrator."""
from src.persona.persona import Persona
from src.orchestrator.pipeline import create_content

aria = Persona("Aria", 24, "cheerful", "warm smile and freckles")
result = create_content(aria, "a 30-second travel tip about Ludhiana")

print("SCRIPT:\n", result["script"])
print("\nAUDIO:", result["audio_path"])
