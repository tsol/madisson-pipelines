#!/usr/bin/env python3
"""
Face swap pipeline using InsightFace.

Usage:
    python faceswap.py --source reference.png --target input.jpg --output out/

Requirements:
    pip install insightface onnxruntime pillow numpy

Models (~530MB):
    ~/.insightface/models/buffalo_l/inswapper_128.onnx
    ~/.insightface/models/buffalo_l/det_10g.onnx
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import cv2
    import insightface
    from insightface.app import FaceAnalysis
except ImportError:
    print("Install dependencies: pip install insightface onnxruntime pillow")
    sys.exit(1)


def swap_faces(source_path: str, target_path: str, output_path: str) -> str:
    app = FaceAnalysis(name="buffalo_l", root=os.path.expanduser("~/.insightface"))
    app.prepare(ctx_id=-1, det_size=(640, 640))

    source_img = cv2.imread(source_path)
    target_img = cv2.imread(target_path)

    if source_img is None:
        raise FileNotFoundError(f"Source not found: {source_path}")
    if target_img is None:
        raise FileNotFoundError(f"Target not found: {target_path}")

    source_faces = app.get(source_img)
    target_faces = app.get(target_img)

    if not source_faces:
        raise ValueError("No face detected in source image")
    if not target_faces:
        raise ValueError("No face detected in target image")

    source_face = sorted(source_faces, key=lambda x: x.bbox[3] - x.bbox[1])[-1]
    target_face = sorted(target_faces, key=lambda x: x.bbox[3] - x.bbox[1])[-1]

    swapper = insightface.model_zoo.get_model(
        os.path.expanduser("~/.insightface/models/buffalo_l/inswapper_128.onnx")
    )

    result = swapper.get(target_img, target_face, source_face, paste_back=True)

    os.makedirs(output_path, exist_ok=True)
    outfile = os.path.join(output_path, f"swapped_{Path(target_path).name}")
    cv2.imwrite(outfile, result)

    return outfile


def main():
    parser = argparse.ArgumentParser(description="InsightFace face swap CLI")
    parser.add_argument("--source", required=True, help="Reference face image")
    parser.add_argument("--target", required=True, help="Image to swap face into")
    parser.add_argument("--output", default="./output", help="Output directory")
    args = parser.parse_args()

    try:
        result = swap_faces(args.source, args.target, args.output)
        print(f"Saved: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
