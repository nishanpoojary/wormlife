# src/wormhole.py

"""
Wormhole tunnel parser for Game of Life.

Given two PNG bitmaps named:
  • 'horizontal_tunnel.png'
  • 'vertical_tunnel.png'

this module will locate all coloured pixels (non-black) and pair them up
according to the specification:

  • If exactly two pixels share the same colour, they form a two-pixel portal.
  • If a colour appears >2 times only along one border (top+bottom or left+right),
    pair the extreme endpoints per row (for vertical) or per column (for horizontal).

Every colour must appear an even number of times or a ValueError is raised.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

Coord = Tuple[int, int]
PairMap = Dict[Coord, Coord]


def _extreme_pairs(coords: List[Coord], pair_by_row: bool) -> PairMap:
    """
    Given a list of coordinates all sharing the same colour, form pairs of
    (leftmost ↔ rightmost) if pair_by_row=True (vertical tunnel)
    or (topmost ↔ bottommost) if pair_by_row=False (horizontal tunnel).

    Returns a dict mapping each endpoint to its partner.
    """
    buckets: Dict[int, List[int]] = {}
    for r, c in coords:
        key = r if pair_by_row else c
        val = c if pair_by_row else r
        buckets.setdefault(key, []).append(val)

    pairs: PairMap = {}
    for k, vs in buckets.items():
        if len(vs) < 2:
            # fewer than 2 endpoints on this row/column: ignore
            continue
        a, b = min(vs), max(vs)
        if pair_by_row:
            pairs[(k, a)] = (k, b)
            pairs[(k, b)] = (k, a)
        else:
            pairs[(a, k)] = (b, k)
            pairs[(b, k)] = (a, k)
    return pairs


def _pairs_from_bitmap(img_path: Path, orient: str) -> PairMap:
    """
    Read one tunnel bitmap and return a mapping {coord → paired_coord}.

    orient must be either "vertical" or "horizontal":

    • vertical   → link LEFT edge ↔ RIGHT edge, pairing extremes on each row
    • horizontal → link TOP edge ↔ BOTTOM edge, pairing extremes on each column

    Any colour that appears exactly twice becomes a simple 2-pixel portal.
    If a colour appears more than twice, we invoke _extreme_pairs().

    Raises
    ------
    ValueError
        if any colour appears an odd number of times.
    """
    arr = np.asarray(Image.open(img_path).convert("RGB"))
    H, W, _ = arr.shape

    # Group every non-black pixel by its RGB colour
    colour2coords: Dict[Tuple[int, int, int], List[Coord]] = {}
    for r in range(H):
        for c in range(W):
            col = tuple(arr[r, c])
            if col == (0, 0, 0):
                continue
            colour2coords.setdefault(col, []).append((r, c))

    pairs: PairMap = {}
    for col, coords in colour2coords.items():
        n = len(coords)
        if n % 2 != 0:
            raise ValueError(f"{img_path.name}: colour {col} occurs {n} times (must be even)")

        if n == 2:
            a, b = coords
            pairs[a] = b
            pairs[b] = a
        else:
            # Must be a border-line tunnel: pair extremes
            if orient == "vertical":
                # leftmost ↔ rightmost on each row
                pairs.update(_extreme_pairs(coords, pair_by_row=True))
            elif orient == "horizontal":
                # topmost ↔ bottommost on each column
                pairs.update(_extreme_pairs(coords, pair_by_row=False))
            else:
                raise ValueError(f"Unknown orientation '{orient}' for {img_path.name}")

    return pairs


def load_wormholes(example_dir: str | Path) -> Tuple[PairMap, PairMap]:
    """
    Return two dictionaries (horiz_pairs, vert_pairs) corresponding to
    the portals found in 'horizontal_tunnel.png' and 'vertical_tunnel.png'.

    Parameters
    ----------
    example_dir : str | Path
        Directory containing the two tunnel PNG files.

    Returns
    -------
    (horiz_pairs, vert_pairs)
        Each is a dict: {(r, c) → (r2, c2)}.
    """
    p = Path(example_dir)
    horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
    vert = _pairs_from_bitmap(p / "vertical_tunnel.png", "vertical")
    return horiz, vert
