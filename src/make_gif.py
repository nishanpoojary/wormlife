#!/usr/bin/env python3
"""
make_gif.py

Scan each subdirectory of 'examples/' (or a single example folder) for the four
generation images (1.png, 10.png, 100.png, 1000.png) and produce an animated
GIF named 'all_output.gif' in that same folder.

Usage:
    # To process all example‐N folders under examples/:
    python src/make_gif.py --examples-dir examples/

    # Or to process a single folder only (e.g. examples/example-2):
    python src/make_gif.py --folder examples/example-2
"""

import sys
import os
import argparse
from pathlib import Path
from PIL import Image

# The list of “milestone” filenames we expect to turn into a GIF.
DEFAULT_MILESTONES = ["1.png", "10.png", "100.png", "1000.png"]

def make_gif_from_folder(folder_path: Path, output_name: str = "all_output.gif", 
                         milestones=DEFAULT_MILESTONES, duration=500):
    """
    Given a folder containing {1.png,10.png,100.png,1000.png}, load them in that
    order and save an animated GIF called `output_name` in the same folder.

    - folder_path: Path to the directory with the PNG snapshots.
    - output_name: Name of the resulting GIF file (in the same folder).
    - milestones: List of filenames (as strings) to include in the GIF, in order.
    - duration: Time (in ms) each frame is displayed.
    """
    # 1) Check that each milestone file exists
    missing = [m for m in milestones if not (folder_path / m).is_file()]
    if missing:
        print(f"  ✗ Skipping {folder_path!s}: missing {missing}", file=sys.stderr)
        return False

    # 2) Open each image (Pillow.Image) and convert all to RGBA (or RGB)
    frames = []
    for fname in milestones:
        img_path = folder_path / fname
        try:
            im = Image.open(img_path).convert("RGBA")
            frames.append(im)
        except Exception as e:
            print(f"  ✗ Failed to open {img_path.name!r}: {e}", file=sys.stderr)
            return False

    # 3) Save as animated GIF (loop=0 means infinite loop)
    output_path = folder_path / output_name
    try:
        # The first frame .save() with save_all=True, append_images=...
        frames[0].save(
            output_path,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
        )
        print(f"✔ Created GIF: {output_path}")
        return True
    except Exception as e:
        print(f"  ✗ Failed to save GIF in {folder_path!s}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate an animated GIF (all_output.gif) from 1.png,10.png,100.png,1000.png"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--examples-dir",
        "-e",
        type=Path,
        help="Path to the top‐level 'examples/' directory. Will iterate over each subfolder."
    )
    group.add_argument(
        "--folder",
        "-f",
        type=Path,
        help="Path to a single example folder (e.g. examples/example-0)."
    )
    parser.add_argument(
        "--output-name",
        "-o",
        type=str,
        default="all_output.gif",
        help="Name of the generated GIF inside each folder (default: all_output.gif)."
    )
    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        default=500,
        help="Milliseconds per frame in the GIF (default: 500)."
    )

    args = parser.parse_args()

    if args.examples_dir:
        examples_root = args.examples_dir
        if not examples_root.is_dir():
            print(f"Error: {examples_root!s} is not a directory.", file=sys.stderr)
            sys.exit(1)

        # For each subdirectory directly under examples/
        for sub in sorted(examples_root.iterdir()):
            if sub.is_dir():
                print(f"Processing folder: {sub}")
                make_gif_from_folder(
                    sub,
                    output_name=args.output_name,
                    duration=args.duration,
                )

    else:
        # Single folder mode
        single = args.folder
        if not single.is_dir():
            print(f"Error: {single!s} is not a directory.", file=sys.stderr)
            sys.exit(1)
        print(f"Processing single folder: {single}")
        make_gif_from_folder(
            single,
            output_name=args.output_name,
            duration=args.duration,
        )


if __name__ == "__main__":
    main()
