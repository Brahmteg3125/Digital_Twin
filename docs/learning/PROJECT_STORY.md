# PROJECT_STORY.md — the engineering journey

A higher-level, technically-accurate narrative so I can *explain the whole project* naturally
(not recite features). Wrapped in our "Lumina Studios" frame, but every event is real.

## The premise
At the fictional startup **Lumina Studios**, founder **Maya** wants an "AI influencer" platform. I'm
the junior engineer; my mentor and I build **AI Creator Studio** one stage at a time. Our first
digital creator is **Aria**.

## Act 1 — Foundations before features
We *didn't* start with the exciting AI. We built a real project skeleton first: a virtual
environment, Git with small meaningful commits, a `.gitignore` (that even ignores `.env` for secrets
— a decision that paid off much later), a `src/` package, `README`, and a pinned `requirements.txt`.
The theme: **separation of concerns and reproducibility from day one.**

## Act 2 — Giving Aria an identity (data)
We modeled a creator as a `Persona`. First a plain class (to learn `__init__`/`self`), then we
*felt* the boilerplate and **refactored to a `@dataclass`**. We made her persist by saving/loading
JSON — learning serialization, `@classmethod` factories, and dict unpacking. Aria could now survive
program restarts.

## Act 3 — Aria gets a face (and the AI gets real)
We learned the theory *before* the code: embeddings, CLIP, latent space, the VAE, and diffusion
(noise → image in ~30 small steps). Because the laptop had **no GPU**, we moved heavy work to the
cloud (Colab), cloning our own GitHub repo to run it — the Day-1 GitHub setup paying off. We
generated Aria with SDXL, learned fp16/fp32 mixed precision and seeds/reproducibility, and even
watched diffusion happen frame by frame (debugging a real dtype error along the way).

## Act 4 — The hardest problem, and knowing when to stop
Two generations of the same prompt produced *different people* — **identity drift**. We reasoned to
the fix ourselves: condition on a **reference image** (IP-Adapter), mirroring how text conditioning
works. We proved it worked — then hit a **wall of infrastructure problems** on free hardware: CUDA
out-of-memory, a CPU-offload crash from exhausting *system* RAM, and attention slicing that was
fundamentally incompatible with IP-Adapter. We made a mature call: prove the concept, document the
lessons, and **not** burn days fighting free-tier limits. (Later we'd learn Kaggle's larger RAM
makes this feasible.)

## Act 5 — The pragmatic middle (all local, no GPU)
We regrouped on GPU-free work. **Prompt engineering**: a proper positive/negative prompt system,
split into a pure `prompts.py` so it's testable on any laptop (a refactor born from a real
"can't import torch locally" problem). **LLM scripts**: Aria writes her own content via the **Groq**
API — and the `.env` we set up on Day 1 finally held a real secret. **Voice**: **edge-tts** turns
her script into speech; we wrapped its async internals behind a simple function. Then `main.py`
wired it end-to-end: *topic → script → clean → voice → MP3*. Aria spoke.

## Act 6 — Talking on screen (in progress)
For lip-sync we moved to **Kaggle** (more RAM than Colab). A first GPU pick (P100) failed with
"no kernel image" — a compute-capability mismatch — so we switched to a **T4**. We regenerated
Aria's canonical face on Kaggle using our own repo… and she came out **black-and-white** (an open
bug). Wav2Lip integration is next.

## The meta-move
We turned the repository itself into the project's **durable memory** (`CLAUDE.md` +
`docs/learning/`) so the learning journey, decisions, and hard-won lessons persist across sessions —
and so the *reasoning*, not just the code, survives.

## Recurring themes (the real "design philosophy")
1. **Foundations and reproducibility before features.**
2. **Separation of concerns** everywhere (modules; pure logic vs heavy engine).
3. **Understand the theory** so tools stop being magic.
4. **Debug by reasoning** (observe → hypothesize → test), and **measure, don't guess**.
5. **Match tools to real constraints** (no GPU, low budget → cloud + free APIs).
6. **Know when to stop** fighting infrastructure and change the approach.
