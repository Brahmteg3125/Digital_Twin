# 🎬 AI Creator Studio

Turn a fictional creator into an identity-consistent face, an LLM-written script, a spoken voice, a
lip-synced talking video, and a captioned social clip — an **end-to-end generative-AI content
pipeline**, exposed over a REST API.

> A learning-first portfolio project. The full engineering journey — every real bug, decision, and
> lesson — is documented in [`docs/learning/`](docs/learning).

## ✨ What it does
- **Persona** — define a creator (name, age, personality, appearance, voice) as a typed data model.
- **Image** — generate a face with **SDXL** (Diffusers); keep it identity-consistent with **IP-Adapter**.
- **Script** — an **LLM (Groq · Llama 3.3)** writes a short script in the persona's voice.
- **Voice** — **edge-tts** turns the script into natural speech.
- **Lip-sync** — **Wav2Lip** makes the face speak the audio (1024px talking head).
- **Video** — **moviepy** assembles a captioned, vertical (9:16) social clip.
- **API** — a **FastAPI** endpoint runs the pipeline over HTTP and returns JSON.

## 🗺️ Architecture
```
       POST /create {topic}
 client ─────► FastAPI (src/api) ─────► Orchestrator (src/orchestrator)
                                            ├─► Script  (LLM · Groq)
                                            └─► Voice   (TTS · edge-tts)
                                        returns JSON { script, audio_path }

 Heavy GPU workers (cloud · Kaggle/Colab):  Image (SDXL) → Identity (IP-Adapter) → Lip-sync (Wav2Lip)
```
Light stages (script, voice, video, API) run **locally, no GPU**. Heavy stages (image, lip-sync) run
on a **cloud GPU** — a real "light API + GPU worker" split.

## 🛠️ Tech stack
Python · SDXL / Diffusers · HuggingFace · IP-Adapter · Wav2Lip · edge-tts · Groq (LLM) · FastAPI ·
moviepy · Git

## 🚀 Run it (local pipeline + API)
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

echo GROQ_API_KEY=your_key_here > .env   # your Groq API key (kept out of git)

python main.py                        # run the pipeline once (script + voice)
uvicorn src.api.app:app --reload      # or serve the API → http://localhost:8000/docs
```
The GPU stages (image generation, lip-sync) run in a cloud notebook (Kaggle T4) — see
[`docs/learning/LEARNING_LOG.md`](docs/learning/LEARNING_LOG.md).

## 📁 Structure
```
src/
├── persona/       data model (+ JSON save/load)
├── image/         SDXL generation + prompt engineering
├── script/        LLM script generation (Groq)
├── voice/         text-to-speech (edge-tts)
├── video/         captioned video assembly (moviepy)
├── orchestrator/  pipeline coordinator
└── api/           FastAPI layer
docs/learning/     the engineering journey (problems, decisions, concepts, stories)
main.py            entry point
```

## 📓 Engineering journey
Documented *as it was built* — see [`docs/learning/`](docs/learning):
- **PROBLEM_LOG.md** — real bugs with full reasoning journeys (CUDA OOM, VRAM vs system RAM, GPU
  compatibility, legacy-dependency patching, a subtle grayscale-prompt bug, …).
- **DECISIONS.md** — architecture decisions with trade-offs.
- **ARCHITECTURE.md** · **CONCEPTS.md** · **PROJECT_STORY.md** · **INTERVIEW_STORIES.md**.

## 📌 Status
Functional MVP: the full pipeline works (persona → image → script → voice → lip-sync → video),
exposed via an API. Identity preservation is proven and documented; further polish (video quality,
an output manager) is future work.
