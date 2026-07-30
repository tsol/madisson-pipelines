#!/usr/bin/env python3
"""
Pipeline orchestrator for sequential AI image generation on constrained VRAM.

Stages:
    1. Generate base image via ComfyUI (Z-Image-Turbo)
    2. Apply face consistency via InsightFace (CPU)
    3. (Optional) Upscale via Real-ESRGAN
    4. (Optional) Refine face via SD 1.5 inpainting

Usage:
    python pipeline_orchestrator.py \
        --prompt "mirror selfie, morning light, cozy apartment" \
        --face-ref assets/reference.png \
        --output ./final/
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def stage_generate(prompt: str, output_dir: str, seed: int | None = None) -> str:
    """Stage 1: Generate base image via ComfyUI."""
    gen_script = Path(__file__).parent / "comfy_generate.py"
    cmd = [
        sys.executable, str(gen_script),
        "--prompt", prompt,
        "--output", output_dir,
    ]
    if seed is not None:
        cmd += ["--seed", str(seed)]

    print(f"[Stage 1] Generating: {prompt[:50]}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Generation failed:", result.stderr)
        sys.exit(1)

    # Parse output path from last line
    for line in result.stdout.strip().split("\n"):
        if line.startswith("Generated: "):
            return line.replace("Generated: ", "").strip()

    raise RuntimeError("Could not parse generated file path")


def stage_faceswap(source: str, target: str, output_dir: str) -> str:
    """Stage 2: Apply face consistency."""
    swap_script = Path(__file__).parent / "faceswap.py"
    cmd = [
        sys.executable, str(swap_script),
        "--source", source,
        "--target", target,
        "--output", output_dir,
    ]

    print(f"[Stage 2] Face swap: {source} → {target}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Face swap failed:", result.stderr)
        sys.exit(1)

    for line in result.stdout.strip().split("\n"):
        if line.startswith("Saved: "):
            return line.replace("Saved: ", "").strip()

    raise RuntimeError("Could not parse swapped file path")


def run_pipeline(prompt: str, face_ref: str, output_dir: str, seed: int = None) -> dict:
    """Execute full sequential pipeline."""
    os.makedirs(output_dir, exist_ok=True)

    generated = stage_generate(prompt, output_dir, seed)
    swapped = stage_faceswap(face_ref, generated, output_dir)

    # Stage 3+ can be added here: upscale, inpaint, etc.

    return {
        "generated": generated,
        "final": swapped,
    }


def main():
    parser = argparse.ArgumentParser(description="Sequential AI image pipeline")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--face-ref", required=True, help="Reference face image")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--seed", type=int, default=None, help="Generation seed")
    args = parser.parse_args()

    if not os.path.exists(args.face_ref):
        print(f"Face reference not found: {args.face_ref}")
        sys.exit(1)

    results = run_pipeline(args.prompt, args.face_ref, args.output, args.seed)
    print(f"\nPipeline complete:")
    print(f"  Generated: {results['generated']}")
    print(f"  Final:     {results['final']}")


if __name__ == "__main__":
    main()
