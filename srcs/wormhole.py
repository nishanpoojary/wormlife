# srcs/wormhole.py
"""
Utilities to parse wormhole PNGs and build neighbour-lookup tables.

A colour ≠ black (0,0,0) means “this pixel is a tunnel end”.
Each colour appears **exactly twice** (PDF spec) :contentReference[oaicite:0]{index=0}.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

Coord = Tuple[int, int]  # (row, col)
PairMap = Dict[Coord, Coord]


def _pairs_from_bitmap(path: Path, orientation: str) -> PairMap:
    """
    Build {endpoint_a: endpoint_b, endpoint_b: endpoint_a} for every colour.

    orientation = "horizontal"  -> endpoints chosen by min/max COL (same row)
                 = "vertical"    -> endpoints chosen by min/max ROW (same col)
    """
    assert orientation in {"horizontal", "vertical"}
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img)  # (H, W, 3)
    h, w, _ = arr.shape

    colour_to_coords: Dict[Tuple[int, int, int], List[Coord]] = {}
    for r in range(h):
        for c in range(w):
            colour = tuple(arr[r, c])
            if colour == (0, 0, 0):  # background
                continue
            colour_to_coords.setdefault(colour, []).append((r, c))

    pairs: PairMap = {}
    for colour, coords in colour_to_coords.items():
        # Pick extreme points depending on orientation
        if orientation == "horizontal":
            # All coords should share the same row; pick leftmost & rightmost
            left = min(coords, key=lambda t: t[1])
            right = max(coords, key=lambda t: t[1])
            a, b = left, right
        else:  # vertical
            # All coords share same col; pick topmost & bottommost
            top = min(coords, key=lambda t: t[0])
            bottom = max(coords, key=lambda t: t[0])
            a, b = top, bottom

        pairs[a] = b
        pairs[b] = a

    return pairs


def load_wormholes(example_dir: str) -> Tuple[PairMap, PairMap]:
    p = Path(example_dir)
    horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
    vert = _pairs_from_bitmap(p / "vertical_tunnel.png", "vertical")
    return horiz, vert
