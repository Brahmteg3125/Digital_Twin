# INTERVIEW_STORIES.md — raw material for interview answers

Capture the **evidence now**, polish into STAR / engineering-story answers near the end.
Each story is REAL (cross-referenced to PROBLEM_LOG / DECISIONS). Don't over-polish yet.

Rating: ⭐ useful · ⭐⭐ strong · ⭐⭐⭐ headline.

---

## S1 — The two-kinds-of-memory debugging saga ⭐⭐⭐
*(refs: PROBLEM_LOG P4, P5, P6)* — best "hardest problem / first approach failed" story.
- **Situation:** running SDXL + IP-Adapter (identity preservation) on a free 15 GB T4.
- **Task:** make it fit and run.
- **Actions / reasoning journey:**
  1. Hit **CUDA out of memory** → tried `enable_model_cpu_offload()`.
  2. That **silently killed the kernel**. Key insight: a *kill* (not a Python exception) means the
     **OS** ran out of **system RAM** — offload parks the model in CPU RAM, and Colab has only
     ~13 GB.
  3. Switched to **attention slicing** → it was **incompatible with IP-Adapter** (both rewrite the
     UNet's attention processors → `'tuple' object has no attribute 'shape'`).
  4. Realized both easy levers were ruled out; the fix space was `expandable_segments` + VAE slicing
     + lower resolution, or a bigger machine.
- **Result:** proved identity conditioning works, then made the *engineering call* to move heavy
  work to **Kaggle** (~30 GB RAM) and stop fighting free-tier limits.
- **Lessons:** VRAM ≠ system RAM; optimizations trade against *different* memories; know when to
  stop patching and change the environment.
- **Maps to:** "Tell me about a difficult technical problem." / "A time your first fix made things
  worse." / "How do you debug resource issues?"

## S2 — "The data corrected my hypothesis" (dtype leak) ⭐⭐
*(refs: PROBLEM_LOG P2, P3)*
- Recurring `Half vs float` error during IP-Adapter generation. I *assumed* the image encoder was
  fp32. Instead of guessing, I **printed every component's dtype** — it was the **VAE** (fp32),
  leaked from an earlier experiment because we reused the pipeline object.
- **Lesson:** measure, don't guess; state leaks across notebook cells; restart clean when messy.
- **Maps to:** "A time you were wrong." / "How do you approach debugging?"

## S3 — "No kernel image": a GPU/software compatibility bug ⭐⭐
*(refs: PROBLEM_LOG P10, DECISIONS D6)*
- On Kaggle's **P100**, SDXL threw `cudaErrorNoKernelImageForDevice`. Root cause: the P100's
  **compute capability (Pascal 6.0)** wasn't in the installed PyTorch build; switching to a **T4
  (Turing 7.5)** fixed it.
- **Lesson:** this class of error means "software wasn't built for this exact hardware," not a code
  bug. Newer GPU architectures are safer defaults.
- **Maps to:** "A tricky environment/infra issue." / "Something that wasn't your code's fault."

## S4 — Refactor for testability: splitting pure logic from heavy deps ⭐⭐
*(refs: PROBLEM_LOG P8, DECISIONS D5)*
- Prompt logic was trapped in a module that imported torch, so it couldn't run on a GPU-less laptop.
  Split it into a pure `prompts.py` → instantly testable locally.
- **Lesson:** isolate business logic from heavy infrastructure → fast feedback loops; concrete
  separation-of-concerns win.
- **Maps to:** "A refactor you're proud of." / "How do you make code testable?"

## S5 — Solving identity drift (design decision) ⭐⭐
*(refs: DECISIONS D7)*
- Same prompt → different faces, because text describes a *type*, not an *individual*. Reasoned to
  the fix (condition on a **reference image** → image embedding guides the UNet, mirroring how text
  → CLIP → text embedding works). Chose IP-Adapter; understood the whole-image vs face-specific
  trade-off.
- **Lesson:** know *why* a technique is needed, not just how to call it; text is low-bandwidth for
  identity.
- **Maps to:** "A design decision and its trade-offs." / "Explain a model/technique you used."

## S6 — Engineering under constraints (free, GPU-less tooling) ⭐
*(refs: DECISIONS D6, D8, D9)*
- No local GPU + cost-sensitive → chose Colab/Kaggle for GPU, **Groq** (free LLM) and **edge-tts**
  (free neural TTS) for the GPU-free stages, keeping the pipeline runnable and cheap.
- **Lesson:** match tooling to real constraints; the API *pattern* generalizes across providers.
- **Maps to:** "A pragmatic trade-off you made." / "Working within limitations."

## S7 — Building for durable memory (this system) ⭐
- Turned the repo itself into the project's persistent memory (`CLAUDE.md` + `docs/learning/`) so no
  context is lost between sessions and the reasoning journey is preserved.
- **Maps to:** "How do you manage knowledge / onboarding / documentation?"

---
### Candidate one-liners to expand later
- "Tell me about a hard bug" → **S1** (memory saga).
- "A time you were wrong" → **S2** (dtype).
- "A design decision" → **S5** (identity) or **D4** (class vs function).
- "A refactor" → **S4** (prompts split).
- "Infra pain" → **S3** (P100).
