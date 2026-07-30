# madisson-pipelines

AI image generation pipelines — ComfyUI workflows, face consistency systems, and agent orchestration for creative production.

> Personal portfolio of production-ready AI pipelines built on 8GB VRAM (RTX 4060 Laptop), proving that constrained hardware is not a blocker for professional output.

---

## Pipelines

### 1. Sequential Face Pipeline (8GB VRAM)

**Problem:** SDXL + IP-Adapter + CLIP Vision together exceed 8GB VRAM, producing black images.

**Solution:** Split into sequential GPU-then-CPU steps with model auto-unloading between calls.

```
Z-Image-Turbo generation (6s, GPU)
  → InsightFace swap (5s, CPU)
  → Real-ESRGAN upscale (10s, GPU)
  → SD 1.5 face inpaint (8s, GPU)
```

| Stage | Tool | VRAM | Purpose |
|-------|------|------|---------|
| Generate | Z-Image-Turbo | ~6GB | High-quality base image |
| Consistency | InsightFace inswapper_128.onnx | 0GB (CPU) | Face identity transfer from reference |
| Upscale | Real-ESRGAN 4x+ | ~4GB | Resolution boost |
| Refine | SD 1.5 inpainting | ~4GB | Seamless face integration |

[workflow JSON](workflows/sequential-face-pipeline.json)

### 2. Hermes Agent Orchestration

Automated creative production using Hermes Agent (Nous Research) with scheduled pipelines:

- **Daily selfie generation** — contextual, POV-aware (mirror / front camera / extended arm)
- **Dream pipeline** — nightly compression of action logs → memory merge
- **Kanban-driven output** — tasks → execution → review cycle

[see scripts/](scripts/)

### 3. Face Consistency Reference System

Single reference image (`consistency-reference.png`) drives all generated content.

- **IP-Adapter approach** (SDXL, 12GB+ VRAM): IPAdapterUnifiedLoader + IPAdapterAdvanced
- **Fallback approach** (8GB VRAM): Z-Turbo batch → InsightFace face swap
- **Quality gate**: Face similarity scoring + manual review

### 4. ComfyUI MCP Integration

Remote ComfyUI control via MCP server:
```bash
python scripts/comfy_generate.py \
  --prompt "mirror selfie, morning light, soft tones" \
  --face-ref assets/reference.png \
  --output out/
```

---

## Repository Structure

```
madisson-pipelines/
├── workflows/              # ComfyUI workflow JSONs
│   ├── sequential-face-pipeline.json
│   └── z-image-batch.json
├── scripts/                # Automation & utilities
│   ├── faceswap.py         # InsightFace CLI wrapper
│   ├── comfy_generate.py   # ComfyUI API client
│   └── pipeline_orchestrator.py
├── docs/                   # Write-ups & methodology
│   ├── vram-optimization.md
│   └── face-consistency-guide.md
├── .github/workflows/      # CI for workflow validation
│   └── validate-json.yml
└── README.md
```

---

## Requirements

- Python 3.10+
- ComfyUI with `--lowvram` flag
- `insightface`, `onnxruntime`, `requests`
- Z-Image-Turbo (local or via API)
- Hermes Agent (for orchestration scripts)

## Quick Start

```bash
# Clone with ComfyUI workflows
git clone https://github.com/tsol/madisson-pipelines.git
cd madisson-pipelines

# Install face swap dependencies
pip install insightface onnxruntime requests pillow

# Run face swap pipeline
python scripts/faceswap.py \
  --source assets/reference.png \
  --target generated/morning_selfie.png \
  --output final/
```

---

## Topics

`comfyui` · `stable-diffusion` · `ai-pipeline` · `face-swap` · `insightface` · `agent-orchestration` · `generative-ai`

---

## License

MIT

---

Built by [Madisson](https://t.me/madissonwaves) · [Telegram Channel](https://t.me/madissonwaves) · [Bot](https://t.me/madissonwaves_bot)
