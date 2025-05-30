# srcs/run_sim.py
import sys
from pathlib import Path
import numpy as np
from PIL import Image

from srcs.step4_boolean import load_boolean_board
from srcs.wormhole import load_wormholes
from srcs.lookup import build_tables
from srcs.engine import step

MILESTONES = [1, 10, 100, 1000]

def save_png(board: np.ndarray, outfile: Path) -> None:
    """White = live, Black = dead"""
    Image.fromarray(board.astype(np.uint8) * 255, mode="L").save(outfile)

def main(folder: str) -> None:
    p = Path(folder)
    board = load_boolean_board(folder)
    h, w = board.shape

    horiz, vert = load_wormholes(folder)
    nbr_r, nbr_c = build_tables(h, w, horiz, vert)

    current = board
    for gen in range(1, max(MILESTONES) + 1):
        current = step(current, nbr_r, nbr_c)
        if gen in MILESTONES:
            out = p / f"{gen}.png"
            save_png(current, out)
            print("✓", out)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m srcs.run_sim <example-folder>")
        sys.exit(1)
    main(sys.argv[1])
