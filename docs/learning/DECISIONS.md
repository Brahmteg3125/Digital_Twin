# DECISIONS.md — architecture & technology decisions

Why we chose what we chose. Enough to *defend* the architecture in an interview.
Format: Context · Options · Chosen · Why · Trade-offs · Revisit if.

---

## D1 — Modular `src/` package layout (separation of concerns)
- **Context:** avoid the "everything in one 2000-line file" trap.
- **Options:** monolith vs. one module per pipeline stage.
- **Chosen:** `src/persona`, `src/image`, `src/script`, `src/voice`, … each owns one job.
- **Why:** separation of concerns → fault isolation, parallel work, independent testing, fewer merge
  conflicts. Built incrementally (YAGNI) — a module folder is created only when we reach its stage.
- **Trade-offs:** more files to navigate; cross-module imports need correct `sys.path` (see P7).
- **Revisit if:** the app grows enough to warrant packages-of-packages or a plugin system.

## D2 — `Persona` as a `@dataclass`
- **Options:** plain class with hand-written `__init__` vs. `@dataclass`.
- **Chosen:** `@dataclass` (after first building the plain class to learn the mechanics).
- **Why:** auto-generates `__init__`/`__repr__`/`__eq__` from one field list (DRY); adding a field
  is one line. We felt the boilerplate pain first, then removed it (a real refactor).
- **Trade-offs:** slight "magic"; fields need type annotations.
- **Revisit if:** we need heavy validation/serialization logic → consider `pydantic`.

## D3 — Prompt-building lives in the image module, NOT on `Persona` ("Option B")
- **Options:** A) `persona.to_prompt()` method; B) `build_prompt(persona)` in `src/image`.
- **Chosen:** B.
- **Why:** keep `Persona` as pure data (single source of truth); each consumer (image, script,
  voice) decides how to *use* it. `Persona.to_prompt()` would bloat the model with image concerns.
- **Trade-offs:** slightly less "OO convenient."
- **Revisit if:** many modules need identical prompt logic → shared prompt service.

## D4 — `ImageGenerator` is a class, but `generate_script` is a plain function
- **Why:** `ImageGenerator.__init__` loads SDXL **once** (expensive) and reuses it → "load once,
  generate many." The Groq client is cheap to create, so script generation needs **no class** — a
  function is the right, simpler tool. *Choose the tool that fits the resource.*
- **Revisit if:** script generation needs cached/expensive state (e.g., a persistent session).

## D5 — Split `prompts.py` (pure logic) from `generator.py` (heavy engine)
- **Context:** torch import at module top made prompt logic un-testable on a GPU-less laptop (P8).
- **Chosen:** `src/image/prompts.py` = pure Python; `generator.py` imports from it.
- **Why:** isolate pure logic from heavy deps → test/iterate locally in milliseconds.
- **Trade-offs:** one more file.
- **Revisit if:** prompt logic grows into a full templating system → its own subpackage.

## D6 — Cloud GPU: Colab first, then **Kaggle**; use **T4**, not P100
- **Context:** user's laptop has no CUDA GPU (Intel iGPU, 32 GB RAM).
- **Options:** Colab (free T4, ~13 GB RAM), Kaggle (free T4×2/P100, ~30 GB RAM), paid GPU, local CPU.
- **Chosen:** Colab initially; **switched to Kaggle** for its larger **system RAM**; pick **T4**.
- **Why:** Kaggle's ~30 GB RAM avoids the CPU-offload kernel crash (P5); **T4 (Turing)** is
  supported by modern PyTorch, **P100 (Pascal) is not** (P10).
- **Trade-offs:** cloud sessions are ephemeral; inputs/outputs must be uploaded or regenerated.
- **Revisit if:** we need reliable long runs → paid GPU (Colab Pro / cloud instance / A100).

## D7 — Identity preservation via IP-Adapter (reference-image conditioning)
- **Context:** text prompts fix a *type*, not a specific *person* → identity drifts across images.
- **Options:** better text prompts (insufficient), seed-only (only reproduces one exact image),
  IP-Adapter (image embedding conditioning), face-specific (IP-Adapter FaceID / InstantID).
- **Chosen:** IP-Adapter (concept proven); **build polishing skipped on free hardware.**
- **Why:** an image carries identity that text can't ("a picture is worth a thousand words").
  Standard IP-Adapter worked (clear resemblance) but hit memory limits (P4–P6) on the free T4.
- **Trade-offs:** whole-image adapter also imports composition; face-specific variants need more
  setup. Free hardware couldn't run SDXL+IP-Adapter@1024 reliably.
- **Revisit if:** on a 24 GB+/A100 GPU → finish with IP-Adapter FaceID/InstantID for tighter faces.

## D8 — LLM provider: **Groq** (free)
- **Options:** Google Gemini (free), Anthropic Claude (paid, top quality), Groq (free, fast, open
  models), local Ollama (free, offline, slow on CPU).
- **Chosen:** Groq — free, fast, no GPU, easy key; model `llama-3.3-70b-versatile`.
- **Why:** cost-sensitive learning project; the API *pattern* transfers to any provider.
- **Revisit if:** need higher quality/safety → Claude; need offline/private → Ollama.

## D9 — TTS: **edge-tts** (free neural voices), voice = `en-US-MichelleNeural`
- **Options:** edge-tts (free, neural, needs internet), pyttsx3 (offline, robotic), ElevenLabs/
  OpenAI (paid, excellent).
- **Chosen:** edge-tts; user compared 3 voices and picked Michelle.
- **Why:** free + natural + no GPU + no key. Async wrapped behind a simple sync function.
- **Trade-offs:** needs internet; free TTS still sounds a bit synthetic.
- **Revisit if:** portfolio demo needs truly human/expressive voice → ElevenLabs.

## D10 — Secrets in `.env` + `python-dotenv`; pin deps from the real venv
- **Why:** never hardcode API keys (they get scraped from GitHub within minutes; also decouples
  secrets from code). `.env` is gitignored (verified Day 1 with `git check-ignore`). Pins must come
  from the environment that runs the code (see P9).

## D11 — `main.py` as a temporary orchestrator
- **Why:** a root entry point wires `persona → script → voice` today; a robust orchestrator module
  comes later (Milestone 12). `python main.py` works because the root is on `sys.path`.
- **Revisit at:** Milestone 12 — extract into `src/orchestrator/`.
