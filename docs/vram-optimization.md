# VRAM Optimization for 8GB GPUs

## The Problem

Running SDXL + IP-Adapter + CLIP Vision simultaneously on an RTX 4060 Laptop (8GB VRAM) reliably produces black images or CUDA OOM. Peak VRAM usage exceeds 9GB.

## Verified Solutions

### 1. Sequential Pipeline (Recommended)

Instead of loading all models at once, split into independent stages with model unloading between calls.

| Stage | Model | Peak VRAM | Duration |
|-------|-------|-----------|----------|
| Base generation | Z-Image-Turbo (SDXL-based) | ~6GB | 6s |
| Face consistency | InsightFace inswapper_128 (ONNX, CPU) | 0GB | 5s |
| Upscale | Real-ESRGAN 4x+ | ~4GB | 10s |
| Face inpaint | SD 1.5 inpainting | ~4GB | 8s |

ComfyUI's `--lowvram` flag is essential. It unloads models between API calls.

### 2. Z-Image-Turbo Batching

When face consistency is not critical (e.g., mood shots, landscapes):
- Generate 10-20 images with Z-Turbo
- Select best by aesthetic score or manual review
- No face swap needed

### 3. Face Swap vs IP-Adapter

| Approach | VRAM | Quality | Speed | Use Case |
|----------|------|---------|-------|----------|
| IP-Adapter (SDXL) | 12GB+ | Excellent | 15s | 16GB+ GPUs |
| IP-Adapter (SD 1.5) | 6GB | Mediocre | 8s | Not recommended — 2022 quality |
| InsightFace swap | 0GB (CPU) | Good | 5s | **8GB GPUs** |

### 4. Quality Hacks

- Hide hands/feet with props (coffee cup, blanket, high heels) to avoid generation artifacts
- Use extended-arm POV or mirror reflection for selfie realism
- Apply film grain / Portra LUT in post for cohesive look

## ComfyUI Launch Flags

```bash
python main.py --lowvram --disable-xformers --normalvram
```

For headless servers:
```bash
python main.py --lowvram --disable-xformers --cpu-vae --listen 0.0.0.0
```

## Reference

- [ComfyUI lowvram docs](https://github.com/comfyanonymous/ComfyUI#how-to-show-high-quality-previews)
- InsightFace models: `buffalo_l` pack (~500MB)
