# CONCEPTS.md — my CS/AI handbook (AI Creator Studio flavored)

Plain-English explanations of what I've learned, tied to *how it shows up in this project*.
Not Wikipedia — just enough to understand and explain it.

## Environment & tooling
- **Virtual environment (`.venv`)** — a private box of libraries per project, so versions don't
  clash. A "mini-fridge" just for this project. Ours holds groq/dotenv/edge-tts locally.
- **`requirements.txt`** — the recipe: exact pinned libraries so anyone rebuilds the same env.
  "Commit the recipe, not the meal" (we ignore heavy `.venv`, commit the list).
- **Git: staging → commit → push** — staging area = packing a box (`git add`); commit = sealing it
  locally; push = sending a copy to GitHub (the cloud). Commit ≠ push.
- **`.gitignore`** — a "do-not-save" list Git reads automatically. Trailing `/` = folder-only. We
  ignore `.venv/`, `outputs/`, model weights, and `.env` (secrets).

## Software architecture
- **Module / package / library / framework** — module = one `.py`; package = folder + `__init__.py`
  (our `src/persona`); library = a toolbox *you* call; framework = calls *your* code ("don't call
  us, we'll call you").
- **Separation of concerns / fault isolation** — each module owns one job; a bug's blast radius
  stays contained. Change the voice → touch only `src/voice`.
- **DRY** — one source of truth. Changing `Persona`'s fields updates `__init__`, printing, equality
  automatically (dataclass).
- **Abstraction / encapsulation** — hide messy detail behind a simple interface. `text_to_speech()`
  wraps the async `_speak()` so callers never touch async.

## Python
- **Class vs object / instance** — class = cookie cutter; object = a stamped cookie. `aria` and
  `leo` are instances of `Persona`.
- **`@dataclass`** — auto-writes `__init__`/`__repr__`/`__eq__` from a field list.
- **`__init__`, `self`, methods, attributes** — constructor, "this object", functions on the class,
  the object's stored data.
- **`@classmethod` / factory** — a method on the *class* (`cls`) that builds an instance;
  `Persona.load(path)` is an alternative constructor.
- **JSON / serialization** — turn an object into text to save/send (`asdict` + `json.dump`) and back
  (`json.load` + `cls(**data)`). `**` unpacks a dict into keyword args.
- **`sys.path`** — the list of folders Python searches for imports ("front doors"). Run
  `python -m pkg.mod` from the repo root so `src` is importable (see PROBLEM_LOG P7).
- **Default args & falsy values** — `scene: str = ""`; `if scene:` skips empty strings.
- **Async / `await` / `asyncio.run`** — code that can pause for I/O (e.g., network) without
  freezing. We wrap it so callers stay synchronous.

## Generative AI — images
- **Embedding** — numbers that capture meaning; similar things get similar vectors. Text and images
  both become embeddings.
- **CLIP** — the text encoder that turns a prompt into a text embedding (and can encode images too).
- **Latent space** — a compressed "map of meaning"; SDXL works here (~45× smaller than pixels) for
  speed. Not human-readable until decoded.
- **VAE** — a learned compressor: encoder (image→latent) + decoder (latent→image). Lossy, like a
  smart JPEG. SDXL's VAE is fp16-unstable → run it in fp32.
- **Diffusion** — start from random noise; a network removes a little noise each step (~30 steps),
  guided by the text embedding, until an image emerges. Hard problem split into easy steps.
- **U-Net** — the denoiser; each step it *predicts the noise* to subtract (conditioned on the text
  embedding via cross-attention + the timestep).
- **Scheduler / steps** — how denoising is paced; quality vs steps flattens out (diminishing
  returns).
- **Seed** — the random starting noise. Same prompt + same seed = identical image (reproducible);
  different seed = different image. A persona's canonical face = (prompt + seed).
- **Guidance scale** — how strongly to obey the prompt.
- **Pretrained / foundation model, inference vs training** — someone paid the huge training cost; we
  only *use* the finished weights (inference). `from_pretrained` downloads them from the HF Hub.
- **fp16 vs fp32 (mixed precision)** — 16-bit = half the memory/faster (big UNet); 32-bit where
  numerically fragile (VAE). fp16 halved SDXL so it fit a 16 GB GPU.
- **Identity conditioning / IP-Adapter** — feed a *reference image* → image embedding → guides the
  UNet toward *that* face. Fixes identity drift that text alone can't.

## Hardware / infra
- **GPU VRAM vs system RAM** — two separate memories. CPU offload saves VRAM but costs system RAM;
  attention slicing saves VRAM without touching RAM (PROBLEM_LOG P5).
- **CUDA / compute capability** — a GPU architecture version; PyTorch must ship kernels for it.
  P100 (Pascal 6.0) unsupported by modern torch; T4 (Turing 7.5) is safe (P10).
- **CPU offload / attention slicing / VAE slicing** — techniques to fit big models on small GPUs,
  each with different trade-offs.

## LLM & audio
- **LLM / orchestration** — an LLM predicts the next word; *orchestration* = using it as a
  programmable component (build prompt → call API → use output), not manual chatting.
- **Chat roles** — `system` sets persistent behavior/guardrails (wins conflicts); `user` is the
  request; `assistant` is the reply.
- **Secrets / `.env`** — API keys live in `.env` (gitignored), loaded at runtime via
  `python-dotenv`; never printed in full.
- **Prompt engineering** — positive prompt (subject + style + quality tokens) + **negative prompt**
  (artifacts to avoid). Fights "plastic" look from both sides. Mind CLIP's ~77-token limit.
- **TTS** — text → spoken audio; neural voices (edge-tts) sound natural.

## To learn next (not yet covered)
Lip-sync/Wav2Lip internals · video assembly (ffmpeg/moviepy) · REST/HTTP/FastAPI · queues ·
caching · production logging/config.
