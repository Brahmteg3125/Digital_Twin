"""Entry point: run the pipeline so far — persona -> script -> voice."""
from src.persona.persona import Persona
from src.script.generator import generate_script
from src.voice.tts import text_to_speech

# 1. Who she is
aria = Persona("Aria", 24, "cheerful", "warm smile and freckles")

# 2. She writes her own script
script = generate_script(aria, "a 30-second travel tip about Ludhiana")

# 3. Clean stray quotes/whitespace the LLM may add (TTS wants clean text)
script = script.strip().strip('"').strip()
print("SCRIPT:\n", script, "\n")

# 4. She speaks it
text_to_speech(script, "outputs/aria_ludhiana.mp3")
