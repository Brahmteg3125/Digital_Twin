# ARCHITECTURE.md — current system

Update this whenever the system meaningfully changes.

## Vision (final target)
```
USER ──> API (FastAPI) ──> ORCHESTRATOR ──> {Persona, Image, Script, Voice, Lip-sync, Video}
                                                          └──> Output Manager ──> short video
```

## What exists TODAY (built + committed, M1–M7)
```
                 topic string + Persona
                          │
   ┌──────────────────────┼───────────────────────────┐
   ▼                      ▼                             ▼
Persona (data)   Script (LLM/Groq)               Image (SDXL)         [cloud/GPU]
src/persona      src/script/generator.py         src/image/
  persona.py       build_script_prompt()           prompts.py  build_prompt/negative
  - dataclass      generate_script()  ──text──┐    generator.py ImageGenerator.generate()
  - save/load JSON                            │      (identity/IP-Adapter = concept only)
                                              ▼
                                     clean text (strip quotes)
                                              │
                                              ▼
                                   Voice (TTS/edge-tts)   src/voice/tts.py
                                     text_to_speech()  ──> outputs/*.mp3

   main.py = temporary orchestrator wiring Persona → Script → Voice
```

## Components & responsibilities
| Module | File(s) | Responsibility | Runs where |
|---|---|---|---|
| Persona | `src/persona/persona.py` | data model (name/age/personality/appearance/voice_style) + JSON save/load | local |
| Image | `src/image/prompts.py`, `generator.py` | prompt building (pure) + SDXL generation (heavy) | **cloud GPU** |
| Script | `src/script/generator.py` | LLM prompt + Groq call → script text | local (API) |
| Voice | `src/voice/tts.py` | text → MP3 via edge-tts (async wrapped) | local (internet) |
| Video | `src/video/assembler.py` | audio + caption → captioned vertical MP4 (moviepy) | local |
| Orchestrator | `src/orchestrator/pipeline.py` | coordinate the pipeline (recipe card) → result dict | local |
| API | `src/api/app.py` | FastAPI front door (`GET /`, `POST /create`) → JSON | local |
| Entry | `main.py` | quick local run via the orchestrator | local |
| Data | `data/personas/aria.json` | saved sample persona | local (committed) |

## Data flow (today)
`Persona + topic → generate_script() [Groq] → clean text → text_to_speech() [edge-tts] → outputs/*.mp3`
Image path (separate, cloud): `Persona → build_prompt() → ImageGenerator.generate() [SDXL] → PNG`.

## Storage
- `data/personas/*.json` — persona definitions (committed sample).
- `outputs/` — generated media (gitignored; regenerable). Includes seed in filenames for repro.
- `.env` — API keys (gitignored).
- Model weights — downloaded from HF Hub at runtime in the cloud (never committed).

## Key dependencies
- Local: `groq`, `python-dotenv`, `edge-tts`.
- Cloud/GPU: `torch` (provided by Colab/Kaggle), `diffusers`, `transformers`, `accelerate`.
- Cloud GPU host: **Kaggle** (T4, ~30 GB RAM) preferred over Colab. GPU work is not in the repo.

## Boundaries / notes
- Pure logic (`prompts.py`, `persona.py`) is torch-free → testable locally.
- Heavy engine (`generator.py`) is quarantined; runs only where a GPU exists.
- Cross-module imports require the repo root on `sys.path` (`python -m ...` or `main.py` at root).

## Not built yet
Done since: lip-sync (M8) ✅ · orchestrator (M12) ✅ · API (M11) ✅.
Remaining: video assembly (M9) · output manager (M10) · production hardening (M13) ·
docs/polish (M14) · interview packaging (M15).
