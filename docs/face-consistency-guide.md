# Face Consistency Guide

## Goal

All generated images of Madisson must show the same identifiable person across different lighting, poses, and contexts.

## Methods

### Method A: IP-Adapter (SDXL) — 12GB+ VRAM

```
Load Checkpoint (SDXL) → Load IPAdapter Model → IPAdapterUnifiedLoader
                                              ↓
CLIP Vision Load → IPAdapterAdvanced → KSampler
```

Requires:
- `ip-adapter-plus-face_sdxl_vit-h.bin`
- `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` (must be renamed from HF default name)

**Blocker:** On 8GB VRAM this produces black images. Only viable on 12GB+.

### Method B: InsightFace Swap (8GB VRAM)

```
Z-Image-Turbo generates base image → InsightFace extracts face from reference
                                    → inswapper_128.onnx replaces face
                                    → Optional: Real-ESRGAN upscale
```

**Reference image:** `consistency-reference.png` — one high-quality frontal face, good lighting, neutral expression.

**Process:**
1. Detect face in reference → get embedding
2. Detect face in generated image → get largest face bbox
3. Run inswapper_128 with paste_back=True
4. Review output manually

### Method C: Hybrid (Best Quality on Low VRAM)

1. Generate batch of 10 with Z-Turbo
2. Face-swap all 10
3. Pick best 3 by eye
4. Optional upscale + inpaint

## Selfie Realism Checklist

Every generated selfie must show **one** of:
- Mirror reflection (phone visible, reversed text/room)
- Front camera POV (extended arm, slight wide-angle distortion)
- Candid mirror (phone on counter, timer shot)

**Fails:** Phone in hand without mirror/camera visible — implies someone else took the photo, breaks immersion.

## Quality Gates

1. Face identifiable as same person?
2. Lighting direction consistent with scene?
3. Pose looks physically possible?
4. No extra fingers / deformed joints?
5. POV believable?

## Tools

- `scripts/faceswap.py` — CLI face swap
- `scripts/comfy_generate.py` — ComfyUI generation then auto-swap
- `scripts/pipeline_orchestrator.py` — Full sequential pipeline
