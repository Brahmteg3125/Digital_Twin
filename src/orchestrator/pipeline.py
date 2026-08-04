"""The pipeline coordinator ("conductor").

Turns a persona + topic into a script and spoken audio by running the stages
in order. Only the CPU/API stages (script, voice) run here — the GPU stages
(image, lip-sync) run as separate cloud workers and plug in where a GPU exists.
"""
import os

from src.persona.persona import Persona
from src.script.generator import generate_script
from src.voice.tts import text_to_speech


def create_content(persona: Persona, topic: str, output_dir: str = "outputs") -> dict:
    """Run the pipeline: persona + topic -> script -> audio. Returns a result dict."""
    # 1. the LLM writes the script; clean stray quotes/whitespace for the TTS
    script = generate_script(persona, topic).strip().strip('"').strip()

    # 2. turn the script into spoken audio
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"{persona.name.lower()}_voice.mp3")
    text_to_speech(script, audio_path)

    # 3. hand back a structured summary of what we produced
    return {
        "persona": persona.name,
        "topic": topic,
        "script": script,
        "audio_path": audio_path,
    }
