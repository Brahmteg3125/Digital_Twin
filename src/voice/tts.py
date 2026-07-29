import asyncio
import os

import edge_tts


async def _speak(text: str, path: str, voice: str) -> None:
    """Async worker: fetch neural audio for `text` and save it."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


def text_to_speech(text: str, path: str = "outputs/voice.mp3",
                   voice: str = "en-US-MichelleNeural") -> str:
    """Turn text into spoken audio and save it as an MP3. Returns the file path."""
    os.makedirs("outputs", exist_ok=True)
    asyncio.run(_speak(text, path, voice))
    print(f"Saved audio: {path}")
    return path


if __name__ == "__main__":
    text_to_speech(
        "Hi, I'm Aria! This is my very first spoken sentence.",
        "outputs/aria_test.mp3",
    )
