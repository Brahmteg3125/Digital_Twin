# LEARNING_LOG.md — compact session continuity

Newest entries at the bottom. Keep entries SHORT. This is the fastest way to answer
"where are we and what's next?" Reconstructed from git history + our conversation.

Template:
`### <milestone/session> — <title>` · Built · Learned · Files · Decisions · Problems · State · Next

---

### M1 — Foundations
- Built: `.venv`, `git init`, root `.gitignore`, `src/` package, `README.md`, `requirements.txt`;
  GitHub remote (repo later renamed **Digital_Twin**).
- Learned: venv, git staging/commit/push, gitignore semantics, modular architecture, DRY,
  requirements round-trip.
- Problems: P1 (venv self-ignore). State: ✅ committed.

### M2 — Persona data model
- Built: `src/persona/persona.py` — `Persona` dataclass + JSON `save()`/`load()`; `data/personas/aria.json`.
- Learned: classes/objects, `@dataclass`, refactoring, `@classmethod` factory, JSON/serialization,
  `**` unpacking, default args, `__eq__`.
- Decisions: D2. State: ✅ committed.

### M3 — SDXL image generation
- Built: `src/image/generator.py` (`ImageGenerator`, `build_prompt`). Ran SDXL on Colab via cloning
  our repo. Generated Aria (seed 42).
- Learned: embeddings, CLIP, latent space, VAE, diffusion, U-Net, seeds, fp16/fp32, pretrained/
  inference, HF Hub, `sys.path`.
- Decisions: D1, D3, D4, D6. Problems: P2 (dtype), P7 (`sys.path`). State: ✅ code committed
  (images are cloud-only, not in repo).

### M4 — Identity preservation (concept proven, build skipped)
- Did: IP-Adapter on Colab — Aria on a "Tokyo street" clearly resembled her reference → identity
  conditioning WORKS. Then hit a memory wall.
- Learned: identity drift, image conditioning (image encoder → image embedding), IP-Adapter, VRAM vs
  system RAM, CPU offload / attention slicing trade-offs, canonical face = (prompt + seed).
- Decisions: D7. Problems: **P3, P4, P5, P6** (⭐ the memory saga). State: ⚠️ **not committed**
  (Colab only); user chose to move on.

### M5 — Prompt engineering (all local)
- Built: `src/image/prompts.py` (pure) with `QUALITY`/`NEGATIVE` + `build_prompt(persona, scene="")`
  + `build_negative_prompt()`; wired into `generator.py`.
- Learned: prompt engineering, positive/negative prompts, CLIP token limit, separation of pure logic
  from heavy deps (testability), falsy values.
- Decisions: D5. Problems: P8. State: ✅ committed.

### M6 — LLM script generation (Groq)
- Built: `src/script/generator.py` — `build_script_prompt`, `generate_script` (Groq
  `llama-3.3-70b-versatile`); `.env` + `python-dotenv`. Aria wrote a real Ludhiana script.
- Learned: LLMs, orchestration, secrets/.env, chat roles (system/user), API clients.
- Decisions: D8, D10. State: ✅ committed.

### M7 — Text-to-speech (edge-tts)
- Built: `src/voice/tts.py` (`text_to_speech` wrapping async `_speak`, voice=`en-US-MichelleNeural`);
  `main.py` wiring persona→script→voice → `outputs/aria_ludhiana.mp3`. Aria spoke.
- Learned: TTS, async + `asyncio.run`, abstraction/encapsulation, cleaning LLM output.
- Decisions: D9, D11. Problems: P9 (wrong-env pins). State: ✅ committed. (`requirements.txt` pin
  fix was still uncommitted at handoff — commit it.)

### M8 — Lip-sync (Wav2Lip) — ✅ WORKING
- Did: moved cloud host to **Kaggle** (more RAM). P100 failed ("no kernel image") → **T4**. Fixed the
  B&W bug (P11). Used a Kaggle dataset for the Wav2Lip repo + `wav2lip_gan.pth`; downloaded
  `s3fd.pth`; patched `audio.py` for modern librosa (P12); freed SDXL VRAM before inference (P13);
  idempotent setup cell for the ephemeral env (P14). **Produced `aria_talking.mp4` (1024px, ~11.8s)
  — Aria lip-syncs her Ludhiana script!**
- Learned: Wav2Lip pipeline (face-detect → mouth-sync → composite), GPU compute capability (P10),
  legacy-dep patching (P12), multi-model GPU memory handoff (P13), idempotent setup (P14),
  read-only-input vs writable-workbench, keyword-only args.
- Problems: P10, P11, P12, P13, P14 — all ✅. State: ✅ lip-sync works (in the Kaggle notebook; not
  committed to the repo).
- **NEXT:** Milestone 9 — video assembly (stitch clip + captions into a polished short). Consider
  saving the Kaggle lip-sync steps as a notebook in the repo for reproducibility.

### Meta — Persistence system
- Built: `CLAUDE.md` + `docs/learning/` (this system). Removed junk `temp.py`.
- Purpose: repo = durable memory across sessions.
