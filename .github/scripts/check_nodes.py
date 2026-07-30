#!/usr/bin/env python3
"""Validate ComfyUI workflow JSON has required node types."""

import glob
import json
import sys

REQUIRED = {"CheckpointLoaderSimple", "KSampler", "SaveImage"}
errors = 0

for path in glob.glob("workflows/*.json"):
    with open(path) as f:
        wf = json.load(f)

    nodes = wf.get("nodes", [])
    types = {n.get("type") for n in nodes}
    missing = REQUIRED - types

    if missing:
        print(f"{path}: missing {missing}")
        errors += 1
    else:
        print(f"{path}: OK")

sys.exit(1 if errors else 0)
