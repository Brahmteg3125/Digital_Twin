# PROBLEM_LOG.md — real problems + reasoning journeys

Our most valuable file. Only **real** problems that actually happened. Each entry preserves the
*reasoning* (observation → hypothesis → experiment → result → root cause → fix), not just
"error → fix". This is what interviewers care about and what the user wants to learn.

Legend: ✅ solved · 🟡 worked-around · 🔴 OPEN

---

## P1 — "Where did `.venv` go?" (git ignored it invisibly) ✅  · Milestone 1
- **Symptom:** after `git init`, `.venv/` did **not** appear in `git status` untracked list.
- **Reasoning:** expected it to show → ran `git check-ignore -v .venv` → output pointed at
  `.venv/.gitignore:2:*`.
- **Root cause:** Python's `venv` auto-creates a `.gitignore` **inside** `.venv/` containing `*`.
- **Fix:** none needed; we also added `.venv/` to the *root* `.gitignore` so the repo is
  self-documenting.
- **Lesson:** `git check-ignore -v <path>` tells you *which rule* ignores a file. Tools sometimes
  pre-solve problems for you.
- **Interview value:** small, but shows fluency with git internals.

## P2 — fp16 vs fp32 VAE dtype mismatch ✅  · Milestone 3 (denoising visualization)
- **Symptom:** `RuntimeError: Input type (c10::Half) and bias type (float) should be the same`,
  raised in a Conv2d during our manual per-step latent decode.
- **Observation → hypothesis:** "Half vs float" = a layer's weights are fp32 but the input tensor is
  fp16 → a dtype mismatch inside the VAE decode.
- **Experiment:** we had called `pipe.upcast_vae()` which does a *partial* upcast (some VAE layers
  stay fp16). Feeding an fp16 latent hit an fp32 layer.
- **Root cause:** SDXL's VAE is numerically unstable in fp16, so the pipeline upcasts it — but our
  *manual* decode bypassed the pipeline's automatic handling and produced mixed precision.
- **Fix:** make the whole VAE one precision and match the input: `pipe.vae.to(torch.float32)` and
  `latents.to(torch.float32)` before decode.
- **Why it worked:** every op in the decode path then shared one dtype; no mixed-precision op.
- **Lesson:** the rule is "make them agree." Mixed precision (fp16 for the big repeated UNet, fp32
  for the fragile once-run VAE) is deliberate, not an accident.
- **Interview value:** ⭐ good "explain a precision/numerical-stability bug" story.

## P3 — State leakage: an fp32 VAE followed us into a new build ✅  · Milestone 4
- **Symptom:** the *same* Half-vs-float error appeared during IP-Adapter generation, even after a
  "clean" attempt.
- **Debugging (measure, don't guess):** printed each component's dtype →
  `unet=float16, vae=float32, image_encoder=float16`. I had *guessed* `image_encoder` was the
  culprit; the measurement proved it was the **VAE**.
- **Root cause:** the fp32 VAE from P2's experiment persisted because we **reused the same pipe
  object** (skipped re-creating it). Leftover state from one experiment corrupted the next.
- **Fix:** `pipe.vae.to(torch.float16)` (or re-create the pipeline fresh).
- **Lesson:** in long-lived notebook sessions, **state leaks across cells**. When a session is a
  mess, restart clean instead of patching. And always **inspect actual values** rather than trusting
  a hunch.
- **Interview value:** ⭐⭐ "a time your first hypothesis was wrong and the data corrected you."

## P4 — CUDA out of memory (SDXL + IP-Adapter @1024) ✅→led to P5  · Milestone 4
- **Symptom:** `CUDA out of memory. Tried to allocate ... GPU has 14.56 GiB ... 247 MiB free`.
- **Reasoning:** base SDXL generation fit, but adding the IP-Adapter's large image encoder (ViT-bigG
  ~2.5 GB) on top of SDXL @1024 pushed a 15 GB T4 over the edge.
- **First fix attempt:** `enable_model_cpu_offload()` → *created a new problem* (P5).
- **Lesson:** big-model-on-small-GPU is a real constraint; peak VRAM is the enemy.

## P5 — CPU offload CRASHED the kernel (system RAM, not VRAM) ✅  · Milestone 4
- **Symptom:** the kernel silently **restarted** ("restarting kernel (1/5)") — *not* a Python
  `OutOfMemoryError`.
- **Key observation:** a silent kernel *kill* (vs a Python exception) = the **OS** killed the
  process → **system RAM** exhaustion, not GPU VRAM.
- **Root cause:** `enable_model_cpu_offload()` parks the ~9 GB model in **CPU/system RAM** to save
  VRAM — but Colab's free tier has only ~12.7 GB system RAM, so it overflowed.
- **Fix (attempted):** switch to attention slicing instead of offload → led to P6.
- **Lesson:** ⭐ **VRAM ≠ system RAM.** Different optimizations trade against different memories:
  CPU offload saves VRAM but *costs* RAM; attention slicing saves VRAM without touching RAM.
- **Prevention:** on RAM-limited machines, prefer slicing/lower-res over CPU offload. (Kaggle has
  ~30 GB RAM, which is why we later moved there.)
- **Interview value:** ⭐⭐⭐ excellent "two kinds of memory / debugging a resource limit" story.

## P6 — Attention slicing is incompatible with IP-Adapter 🟡  · Milestone 4
- **Symptoms (two, in sequence):**
  1. at `load_ip_adapter`: `SlicedAttnProcessor.__init__() missing 1 required positional argument:
     'slice_size'`.
  2. after loading first, at inference: `'tuple' object has no attribute 'shape'`.
- **Root cause:** both `enable_attention_slicing()` and IP-Adapter **replace the UNet's attention
  processors**. IP-Adapter needs its own processors that accept `encoder_hidden_states` as a *tuple*
  (text + image embeds); the sliced processor expects a plain tensor → conflict either way. Loading
  order didn't save us.
- **Fix / decision:** don't use attention slicing with IP-Adapter. Use `expandable_segments` +
  `vae_slicing` + reduced resolution instead.
- **Lesson:** when two features modify the *same* internal machinery, they can be mutually
  exclusive; order of operations matters, but sometimes incompatibility is fundamental.
- **Status:** identity build was ultimately **skipped on free hardware** (see DECISIONS). Concept
  was proven working before the memory wall.
- **Interview value:** ⭐⭐ "an integration/compatibility problem between two libraries/features."

## P7 — `ModuleNotFoundError: No module named 'src'` ✅  · Milestone 3 (Colab) & local
- **Symptom:** importing `from src.image.generator import ...` failed on Colab after `%cd` into the
  repo; also fails locally with `python src/image/generator.py`.
- **Root cause:** Python finds modules via a list of directories called **`sys.path`** ("front
  doors"). Neither `%cd` nor running a file *inside* `src/` puts the **repo root** on `sys.path`.
- **Fix:** run as a module from the root (`python -m src.image.generator`) or, in a notebook,
  `sys.path.insert(0, "<repo-root>")`. `python main.py` works because `main.py` sits at the root.
- **Lesson:** ⭐ imports resolve relative to `sys.path`, not to your current folder. `-m` from the
  project root (and root-level `main.py`) puts the root on the path.
- **Interview value:** ⭐ Python packaging / import-system understanding.

## P8 — Couldn't test prompt logic locally (torch import blocked it) ✅  · Milestone 5
- **Symptom:** running the prompt code locally failed to import — `generator.py` imports `torch` at
  the top, and torch isn't installed on the laptop (GPU work is cloud-only).
- **Root cause:** pure string logic (`build_prompt`) lived in the same module as heavy
  torch/diffusers code, so the whole file was un-importable without a GPU stack.
- **Fix:** split `src/image/prompts.py` (pure Python, no torch) from `src/image/generator.py` (heavy
  engine). `prompts.py` is testable anywhere.
- **Lesson:** ⭐⭐ **isolate pure logic from heavy dependencies** → testability + fast local
  iteration. A concrete case of separation of concerns.
- **Interview value:** ⭐⭐ "a refactor that improved testability."

## P9 — Wrong dependency versions pinned (wrong environment) ✅  · Milestone 7
- **Symptom:** I pinned `groq==1.0.0` / `python-dotenv==1.2.1` in `requirements.txt`; the user's
  actual venv had `groq==1.5.0` / `python-dotenv==1.2.2` / `edge-tts==7.2.8`.
- **Root cause:** the versions were read from a shell that was **not** the user's activated `.venv`.
- **Fix:** read versions straight from the venv (`.venv/Scripts/python.exe -m pip freeze`) and pin
  those.
- **Lesson:** ⭐ **pin dependencies from the environment that actually runs the code**, never from
  memory or a different machine. Stale pins cause "works on my machine" bugs.
- **Interview value:** ⭐ reproducibility / environment hygiene.

## P10 — "no kernel image is available for execution on the device" (Kaggle P100) ✅  · Milestone 8
- **Symptom:** `AcceleratorError: CUDA error: no kernel image is available for execution on the
  device (cudaErrorNoKernelImageForDevice)` while running SDXL on a Kaggle **P100**.
- **Root cause:** a GPU's **compute capability** (architecture) must be supported by the installed
  PyTorch build. **P100 = Pascal (6.0)**, older; the modern torch had **no compiled kernels** for
  it. **T4 = Turing (7.5)** is universally supported.
- **Fix:** switch Kaggle accelerator from P100 to **T4** (fixed SDXL *and* Wav2Lip in one move).
- **Lesson:** ⭐⭐ "no kernel image" ≈ *the software wasn't built to talk to this specific GPU*, not a
  code bug. Newer GPU architectures have broader/longer software support; a T4 is a safe default.
- **Interview value:** ⭐⭐ "a hardware/software compatibility issue and how you diagnosed it."

## P11 — SDXL generated a BLACK-AND-WHITE Aria ✅  · Milestone 8 (Kaggle, T4)
- **Symptom:** regenerating Aria's seed-42 face on Kaggle produced a **grayscale** image (the rest
  of the image was fine — a narrow, color-only failure).
- **UNDERSTAND ("what changed?"):** last color image was Colab/M3 with a simple prompt; M5 added
  quality tokens + a negative prompt. Prime suspect = the prompt.
- **HYPOTHESES:** (a) positive token `film grain` biases toward black-and-white film; (b) negative
  `oversaturated, unnatural colors` overshoots away from color into grey.
- **TEST (bisection, seed 42, 4 variants):** A=both, B=no film grain, C=no color-negatives,
  D=neither. **Result: only D produced color** → *both* tokens independently desaturate; each alone
  is enough to grey the image.
- **ROOT CAUSE:** two color-draining prompt tokens introduced in M5 — `film grain` (positive) and
  `oversaturated, unnatural colors` (negative).
- **FIX:** removed both from `src/image/prompts.py` (`QUALITY` + `NEGATIVE`). Verify by regenerating.
- **LESSON:** ⭐⭐ prompt tokens have side effects — "quality" words carry aesthetic baggage
  (`film grain`→mono), and **negative-prompting color can overshoot into grayscale**. Isolate one
  variable at a time (bisection) to find the offending token.
- **Interview value:** ⭐⭐ "a well-intentioned change caused a subtle regression; I isolated it with
  a controlled bisection experiment." (INTERVIEW_STORIES S8)

## P12 — Wav2Lip broke on modern librosa (`mel()` keyword-only args) ✅  · Milestone 8
- **Symptom:** `TypeError: mel() takes 0 positional arguments but 2 positional arguments ... given`
  at `audio.py:100`, calling `librosa.filters.mel(hp.sample_rate, hp.n_fft, ...)`.
- **Root cause:** modern librosa (≥0.10) made `sr`/`n_fft` **keyword-only**; Wav2Lip's 2020 code
  passes them **positionally**.
- **Fix:** patched `audio.py` → `librosa.filters.mel(sr=..., n_fft=..., ...)` (in our writable copy).
- **Lesson:** ⭐ legacy code breaks when a library tightens its signature (keyword-only args). Patch
  the exact call the traceback points to.
- **Interview value:** ⭐⭐ "integrating a 2020 codebase with modern dependencies."

## P13 — Wav2Lip OOM because SDXL was still resident (two processes, one GPU) ✅  · Milestone 8
- **Symptom:** `CUDA out of memory` in Wav2Lip's face detector; GPU showed ~14 GiB used, ~35 MiB
  free — even though Wav2Lip's models are small.
- **Root cause:** the notebook still held the **SDXL pipeline** (`gen`) from regenerating Aria's
  face. The `!python inference.py` **subprocess** shares the same physical GPU and had no room.
- **Fix:** free SDXL first — `del gen; gc.collect(); torch.cuda.empty_cache()`. Inference then ran at
  full 1024px (no `--resize_factor` needed).
- **Lesson:** ⭐⭐ on ONE GPU running a multi-model pipeline, **release each stage's memory before the
  next**; `empty_cache()` returns reserved VRAM so other processes can use it. 🔗 same theme as P4/P5.
- **Interview value:** ⭐⭐⭐ "fitting multiple large models on a single GPU / memory handoff."

## P14 — Kaggle kept wiping /kaggle/working → idempotent setup ✅  · Milestone 8
- **Symptom:** across kernel restarts, `/kaggle/working` (Wav2Lip copy, s3fd, Aria's face) kept
  getting wiped, forcing painful piece-by-piece rebuilds.
- **Fix / practice:** consolidated all fragile setup (locate code → copy → download s3fd → patch
  audio.py) into ONE **idempotent** cell that rebuilds a clean state on demand.
- **Lesson:** ⭐⭐ in ephemeral cloud environments, encode setup as a single re-runnable script.
  Durable state = files/datasets + reproducible seeds + the repo, never RAM.
- **Interview value:** ⭐⭐ "reproducible/idempotent setup for ephemeral compute."
