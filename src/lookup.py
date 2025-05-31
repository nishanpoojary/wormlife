# src/lookup.py

"""
Build neighbour lookup tables for the Wormhole Game of Life.

After loading the wormhole portal pairs, we build two integer arrays:

    nbr_r[row, col, dir]  – row index  of the neighbour
    nbr_c[row, col, dir]  – column index of the neighbour

Directions are ordered as follows:
    0: Top, 1: Right, 2: Bottom, 3: Left

Cells that fall outside the board or are “blocked” by wormhole duplication
are set to -1 (INVALID).  This module also enforces the spec’s precedence:
    TOP  > RIGHT  > BOTTOM  > LEFT

If two directions end up pointing to the same target, the lower‐precedence
direction is invalidated (→ -1) so that live cells are not double‐counted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

Coord = Tuple[int, int]
PairMap = Dict[Coord, Coord]

DIRS = ["top", "right", "bottom", "left"]
DIR_IDX = {d: i for i, d in enumerate(DIRS)}
INVALID = -1
PRECEDENCE = [0, 1, 2, 3]  # indices: TOP (0), RIGHT (1), BOTTOM (2), LEFT (3)


def _pairs_from_bitmap(path: Path, orient: str) -> PairMap:
    """
    Internal helper: identical to wormhole._pairs_from_bitmap,
    but inlined here so lookup.py can be standalone if desired.
    """
    arr = np.asarray(Image.open(path).convert("RGB"))
    H, W, _ = arr.shape

    colour2coords: Dict[Tuple[int, int, int], List[Coord]] = {}
    for r in range(H):
        for c in range(W):
            col = tuple(arr[r, c])
            if col == (0, 0, 0):
                continue
            colour2coords.setdefault(col, []).append((r, c))

    pairs: PairMap = {}
    for coords in colour2coords.values():
        if len(coords) % 2 != 0:
            raise ValueError(f"{path.name}: colour count must be even.")
        coords.sort(key=lambda rc: (rc[0], rc[1]) if orient == "horizontal"
                    else (rc[1], rc[0]))
        for a, b in zip(coords[0::2], coords[1::2]):
            pairs[a] = b
            pairs[b] = a
    return pairs


def load_wormholes(example_dir: str | Path) -> Tuple[PairMap, PairMap]:
    """
    Return (horiz_pairs, vert_pairs) by reading
    'horizontal_tunnel.png' and 'vertical_tunnel.png' from example_dir.
    """
    p = Path(example_dir)
    horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
    vert = _pairs_from_bitmap(p / "vertical_tunnel.png", "vertical")
    return horiz, vert


def build_tables(h: int, w: int, horiz: PairMap, vert: PairMap) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build and return (nbr_r, nbr_c), both int32 arrays of shape (h, w, 4).

    1. Start with classic neighbours on a finite h×w grid:
         top    = (row−1, col)
         right  = (row, col+1)
         bottom = (row+1, col)
         left   = (row, col−1)
       Any index outside [0..h−1] or [0..w−1] is set to INVALID (-1).

    2. Patch in wormhole remaps in four passes, following the PDF’s precedence:
         (a) horiz: “left→right” (lowest precedence)
         (b) vert:  “bottom→top”
         (c) horiz: “right→left”
         (d) vert:  “top→bottom” (highest precedence)

       For each portal endpoint (r1,c1) ↔ (r2,c2):
         • a “→” direction cell’s neighbour index is replaced with the other endpoint.
         • the return direction on (r2,c2) likewise points back to (r1,c1).

    3. If any two directions for the same cell resolve to the same target (r,c),
       drop the lower‐precedence direction (set to INVALID) so it is not double‐counted.

    Parameters
    ----------
    h : int
        Number of rows in the board.
    w : int
        Number of columns in the board.
    horiz : PairMap
        Portal pairs from horizontal_tunnel.png.
    vert : PairMap
        Portal pairs from vertical_tunnel.png.

    Returns
    -------
    nbr_r, nbr_c : np.ndarray[int32], shape = (h, w, 4)
        The row and column indices of each of the 4 orthogonal neighbours
        for every cell (r,c).  INVALID = -1 marks “no neighbour”.
    """
    # Step 1: Basic orthogonal neighbours on a finite grid
    row_idx = np.repeat(np.arange(h)[:, None], w, axis=1)
    col_idx = np.repeat(np.arange(w)[None, :], h, axis=0)

    nbr_r = np.stack([row_idx - 1, row_idx, row_idx + 1, row_idx], axis=2)
    nbr_c = np.stack([col_idx, col_idx + 1, col_idx, col_idx - 1], axis=2)

    # Mark any out-of-bounds as INVALID
    mask_oob = (nbr_r < 0) | (nbr_r >= h) | (nbr_c < 0) | (nbr_c >= w)
    nbr_r[mask_oob] = INVALID
    nbr_c[mask_oob] = INVALID

    # Step 2: Apply wormhole patches (in order of increasing precedence)
    def _patch(a: Coord, b: Coord, frm: str, to: str) -> None:
        fi, ti = DIR_IDX[frm], DIR_IDX[to]
        nbr_r[a][fi], nbr_c[a][fi] = b
        nbr_r[b][ti], nbr_c[b][ti] = a

    # (a) horizontal “left→right”
    for (r1, c1), (r2, c2) in horiz.items():
        # determine which is truly “left” vs “right”
        if c1 < c2:
            _patch((r1, c1), (r2, c2), "right", "left")
        else:
            _patch((r2, c2), (r1, c1), "right", "left")

    # (b) vertical “bottom→top”
    for (r1, c1), (r2, c2) in vert.items():
        if r1 < r2:
            # r2,c2 is “bottom”, r1,c1 is “top”
            _patch((r2, c2), (r1, c1), "top", "bottom")
        else:
            _patch((r1, c1), (r2, c2), "top", "bottom")

    # (c) horizontal “right→left”
    for (r1, c1), (r2, c2) in horiz.items():
        if c1 > c2:
            _patch((r1, c1), (r2, c2), "left", "right")
        else:
            _patch((r2, c2), (r1, c1), "left", "right")

    # (d) vertical “top→bottom”
    for (r1, c1), (r2, c2) in vert.items():
        if r1 < r2:
            _patch((r1, c1), (r2, c2), "bottom", "top")
        else:
            _patch((r2, c2), (r1, c1), "bottom", "top")

    # Step 3: Deduplicate: if two directions point to the same (r,c), drop lower precedence
    for d in PRECEDENCE[1:]:
        same_r = nbr_r[:, :, d][..., None] == nbr_r[:, :, :d]
        same_c = nbr_c[:, :, d][..., None] == nbr_c[:, :, :d]
        dup_mask = (same_r & same_c).any(axis=2)
        nbr_r[dup_mask, d] = INVALID
        nbr_c[dup_mask, d] = INVALID

    return nbr_r.astype(np.int32), nbr_c.astype(np.int32)
