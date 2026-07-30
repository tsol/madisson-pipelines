#!/usr/bin/env python3
"""
ComfyUI API client for sequential pipeline execution.

Generates image via Z-Image-Turbo, then applies face swap externally.
Designed for 8GB VRAM where SDXL+IP-Adapter together cause OOM/black images.
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.request
from pathlib import Path

COMFY_API = os.getenv("COMFY_API", "http://host.docker.internal:8188")


def queue_prompt(workflow: dict, client_id: str = "pipeline") -> dict:
    payload = {"prompt": workflow, "client_id": client_id}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_API}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def get_image(prompt_id: str, filename: str, output_dir: str) -> str:
    url = f"{COMFY_API}/view?filename={filename}&subfolder=&type=output"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)
    with open(path, "wb") as f:
        f.write(data)
    return path


def poll_history(prompt_id: str, timeout: int = 120) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(f"{COMFY_API}/history/{prompt_id}")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                history = json.loads(resp.read())
        except Exception:
            time.sleep(2)
            continue
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError("Generation timed out")


def build_prompt_from_nodes(nodes: list) -> dict:
    """Convert ComfyUI node list to API prompt dict."""
    prompt = {}
    for node in nodes:
        nid = str(node["id"])
        prompt[nid] = {
            "inputs": {},
            "class_type": node["type"],
        }

    # Second pass — map widget values to inputs
    widget_map = {
        "CheckpointLoaderSimple": ["ckpt_name"],
        "CLIPTextEncode": ["text"],
        "KSampler": ["seed", "control_after_generate", "steps", "cfg", "sampler_name", "scheduler", "denoise"],
        "EmptyLatentImage": ["width", "height", "batch_size"],
        "VAEDecode": [],
        "SaveImage": ["filename_prefix"],
    }

    for node in nodes:
        nid = str(node["id"])
        node_type = node["type"]
        if node_type in widget_map:
            keys = widget_map[node_type]
            vals = node.get("widgets_values", [])
            for k, v in zip(keys, vals):
                prompt[nid]["inputs"][k] = v

        # Map linked inputs
        for inp in node.get("inputs", []):
            if len(inp) >= 3:
                inp_name, src_id, src_slot = inp[0], inp[1], inp[2]
                prompt[nid]["inputs"][inp_name] = [str(src_id), src_slot]

    return prompt


def generate(prompt_text: str, seed: int | None = None, output_dir: str = "./output") -> str:
    seed = seed or random.randint(1, 2**32)

    wf_path = Path(__file__).parent.parent / "workflows" / "sequential-face-pipeline.json"
    with open(wf_path) as f:
        wf = json.load(f)

    nodes = wf["nodes"] if isinstance(wf["nodes"], list) else []
    for node in nodes:
        if node["id"] == 7:
            node["widgets_values"][0] = prompt_text
        if node["id"] == 3:
            node["widgets_values"][0] = seed

    prompt = build_prompt_from_nodes(nodes)
    result = queue_prompt(prompt)
    prompt_id = result["prompt_id"]
    print(f"Queued: {prompt_id}")

    history = poll_history(prompt_id)
    outputs = history.get("outputs", {})

    for node_id, node_output in outputs.items():
        for img in node_output.get("images", []):
            filename = img["filename"]
            return get_image(prompt_id, filename, output_dir)

    raise RuntimeError("No output images found")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output", default="./output")
    args = parser.parse_args()

    path = generate(args.prompt, args.seed, args.output)
    print(f"Generated: {path}")


if __name__ == "__main__":
    main()
