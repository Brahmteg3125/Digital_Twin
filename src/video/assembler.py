"""Video assembly: combine audio + a caption into a vertical social-media clip.

Pure local (no GPU) — uses moviepy. The orchestrator can call this as the final
stage to produce a shareable video from the generated audio + script.
"""
import os

from moviepy import AudioFileClip, ColorClip, TextClip, CompositeVideoClip

# A font that ships with Windows (bold, readable). Override if on another OS.
FONT = "C:/Windows/Fonts/arialbd.ttf"


def assemble_video(audio_path: str, caption: str,
                   output_path: str = "outputs/video.mp4",
                   size=(720, 1280)) -> str:
    """Build a vertical (9:16) video: dark background + caption + the audio."""
    audio = AudioFileClip(audio_path)

    # 1. a solid background for the length of the audio
    background = ColorClip(size, color=(18, 18, 28)).with_duration(audio.duration)

    # 2. the caption (the script), wrapped to fit, centered
    text = (TextClip(text=caption, font=FONT, font_size=46, color="white",
                     size=(size[0] - 100, None), method="caption")
            .with_position("center").with_duration(audio.duration))

    # 3. stack them and attach the audio
    video = CompositeVideoClip([background, text]).with_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    video.write_videofile(output_path, fps=24)
    return output_path
