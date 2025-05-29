# srcs/loader_check.py
import sys
from pathlib import Path
from PIL import Image

def main(example_dir: str) -> None:
    p = Path(example_dir)
    files = ["starting_position.png", "horizontal_tunnel.png", "vertical_tunnel.png"]
    for fname in files:
        img = Image.open(p / fname)
        print(f"{fname}: size={img.size}, mode={img.mode}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python srcs/loader_check.py <example-folder>")
        sys.exit(1)
    main(sys.argv[1])
