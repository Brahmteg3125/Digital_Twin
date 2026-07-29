from src.voice.tts import text_to_speech
line = "Hey, I'm Aria! Heading to Ludhiana? Try the famous sarson ka saag!"
for v in ["en-US-AriaNeural", "en-US-JennyNeural", "en-US-MichelleNeural"]:
    text_to_speech(line, f"outputs/voice_{v}.mp3", voice=v)