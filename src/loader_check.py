# src/loader_check.py

"""
Simple script to verify that the three required images exist and are loadable:

  • starting_position.png
  • horizontal_tunnel.png
  • vertical_tunnel.png
"""

import sys
from pathlib import Path
from PIL import Image

__all__ = ["main"]


def main(example_dir: str | Path) -> None:
    p = Path(example_dir)
    required = ["starting_position.png", "horizontal_tunnel.png", "vertical_tunnel.png"]
    for fname in required:
        try:
            img = Image.open(p / fname)
            print(f"{fname}: size={img.size}, mode={img.mode}")
        except Exception as e:
            print(f"✗ failed to load {fname}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m wormlife.loader_check <example-folder>")
        sys.exit(1)
    main(sys.argv[1])
