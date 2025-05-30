# """
# Neighbour lookup-table builder for Wormhole Game of Life.

# Produces two int32 arrays

#     nbr_r[row, col, dir]  – neighbour’s row index
#     nbr_c[row, col, dir]  – neighbour’s col index

# dir = 0:Top, 1:Right, 2:Bottom, 3:Left

# Values of **-1** mark neighbours that are outside the universe
# (always dead).  Wormhole remaps and the precedence rule
# TOP > RIGHT > BOTTOM > LEFT are applied.
# """

# from typing import Dict, Tuple
# import numpy as np
# from .wormhole import PairMap

# DIR_IDX: Dict[str, int] = {"top": 0, "right": 1, "bottom": 2, "left": 3}
# INVALID = -1  # sentinel for off-board cells


# def build_tables(
#     height: int,
#     width: int,
#     horiz: PairMap,
#     vert: PairMap,
# ) -> Tuple[np.ndarray, np.ndarray]:
#     # ------------------------------------------------------------------
#     # 1. Classic neighbour grid (NO clamping, so off-board = −1 / width)
#     # ------------------------------------------------------------------
#     row_idx = np.repeat(np.arange(height)[:, None], width, axis=1)
#     col_idx = np.repeat(np.arange(width)[None, :], height, axis=0)

#     nbr_r = np.stack(
#         [row_idx - 1, row_idx, row_idx + 1, row_idx], axis=2
#     )
#     nbr_c = np.stack(
#         [col_idx, col_idx + 1, col_idx, col_idx - 1], axis=2
#     )

#     # Mark any coordinate that is outside [0, H-1] or [0, W-1] as INVALID
#     mask_out = (nbr_r < 0) | (nbr_r >= height) | (nbr_c < 0) | (nbr_c >= width)
#     nbr_r[mask_out] = INVALID
#     nbr_c[mask_out] = INVALID

#     # ------------------------------------------------------------------
#     # 2. Apply wormhole remaps with precedence
#     # ------------------------------------------------------------------
#     def _apply(pairs: PairMap, frm: str, to: str) -> None:
#         i_from, i_to = DIR_IDX[frm], DIR_IDX[to]
#         for (r1, c1), (r2, c2) in pairs.items():
#             nbr_r[r1, c1, i_from], nbr_c[r1, c1, i_from] = r2, c2
#             nbr_r[r2, c2, i_to],   nbr_c[r2, c2, i_to]   = r1, c1

#     _apply(horiz, "left",  "right")   # lowest precedence
#     _apply(vert,  "bottom","top")
#     _apply(horiz, "right", "left")
#     _apply(vert,  "top",   "bottom")  # highest precedence

#     return nbr_r.astype(np.int32), nbr_c.astype(np.int32)


# """
# Neighbour lookup-table builder for Wormhole Game of Life.

# Returns two int32 arrays

#     nbr_r[row, col, dir]  – row-index  of the neighbour
#     nbr_c[row, col, dir]  – column-index of the neighbour

# where dir = 0: Top, 1: Right, 2: Bottom, 3: Left.

# The tables already include wormhole teleporting and the spec’s
# precedence rule (TOP > RIGHT > BOTTOM > LEFT).
# """

# from typing import Dict, Tuple
# import numpy as np

# from .wormhole import PairMap

# INVALID = -1                           # sentinel for “no neighbour”
# DIR_IDX: Dict[str, int] = {"top": 0, "right": 1, "bottom": 2, "left": 3}


# def build_tables(
#     height: int,
#     width: int,
#     horiz: PairMap,
#     vert: PairMap,
# ) -> Tuple[np.ndarray, np.ndarray]:
#     """
#     Produce neighbour lookup tables incorporating wormholes.

#     Parameters
#     ----------
#     height, width : int
#         Dimensions of the board
#     horiz, vert : PairMap
#         Horizontal / vertical portal dictionaries from wormhole.load_wormholes

#     Returns
#     -------
#     nbr_r, nbr_c : int32 (H, W, 4)
#         Neighbour row / column indices or -1 if the neighbour is outside.
#     """

#     # ------------------------------------------------------------- #
#     # 1. Classic orthogonal neighbours on a finite grid (no wrap)   #
#     # ------------------------------------------------------------- #
#     row_idx = np.repeat(np.arange(height)[:, None], width, axis=1)
#     col_idx = np.repeat(np.arange(width)[None, :],  height, axis=0)

#     nbr_r = np.stack([row_idx - 1, row_idx, row_idx + 1, row_idx], axis=2)
#     nbr_c = np.stack([col_idx, col_idx + 1, col_idx, col_idx - 1], axis=2)

#     # mark out-of-bounds cells as INVALID (-1)
#     nbr_r = np.where((nbr_r < 0) | (nbr_r >= height), INVALID, nbr_r)
#     nbr_c = np.where((nbr_c < 0) | (nbr_c >= width),  INVALID, nbr_c)

#     # ------------------------------------------------------------- #
#     # 2. Patch in wormhole teleports                                #
#     # ------------------------------------------------------------- #
#     # → for each portal decide which endpoint is left/right or top/bottom
#     #   then overwrite only the direction that “faces” into the tunnel.
#     for (r1, c1), (r2, c2) in horiz.items():
#         if c1 < c2:
#             left, right = (r1, c1), (r2, c2)
#         else:
#             left, right = (r2, c2), (r1, c1)

#         nbr_r[left][DIR_IDX["right"]] = right[0]
#         nbr_c[left][DIR_IDX["right"]] = right[1]

#         nbr_r[right][DIR_IDX["left"]] = left[0]
#         nbr_c[right][DIR_IDX["left"]] = left[1]

#     for (r1, c1), (r2, c2) in vert.items():
#         if r1 < r2:
#             top, bottom = (r1, c1), (r2, c2)
#         else:
#             top, bottom = (r2, c2), (r1, c1)

#         nbr_r[top][DIR_IDX["bottom"]] = bottom[0]
#         nbr_c[top][DIR_IDX["bottom"]] = bottom[1]

#         nbr_r[bottom][DIR_IDX["top"]] = top[0]
#         nbr_c[bottom][DIR_IDX["top"]] = top[1]

#     return nbr_r.astype(np.int32), nbr_c.astype(np.int32)



"""
srcs/lookup.py
Build neighbour-lookup tables that include wormhole teleporting
and guarantee each cell has at most one neighbour per direction.

If two directions end up pointing to the same target, the lower-precedence
direction is invalidated so counts stay correct.

Precedence (high → low):  TOP, RIGHT, BOTTOM, LEFT
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------
# Types / constants
Coord   = Tuple[int, int]
PairMap = Dict[Coord, Coord]

DIRS        = ["top", "right", "bottom", "left"]
DIR_IDX     = {d: i for i, d in enumerate(DIRS)}
INVALID     = -1
PRECEDENCE  = [0, 1, 2, 3]           # indices of DIRS, high → low

# ---------------------------------------------------------------------
# Tunnel bitmaps  →  PairMap
# ---------------------------------------------------------------------
def _pairs_from_bitmap(path: Path, orient: str) -> PairMap:
    """
    Create portal pairs from a BMP/PNG.

    * Colours appear an even number of times.
    * Sequential pairing (0-1, 2-3, …) handles long border lines.
    """
    arr = np.asarray(Image.open(path).convert("RGB"))
    H, W, _ = arr.shape
    colour2coords: Dict[Tuple[int, int, int], List[Coord]] = {}

    for r in range(H):
        for c in range(W):
            colour = tuple(arr[r, c])
            if colour == (0, 0, 0):
                continue
            colour2coords.setdefault(colour, []).append((r, c))

    pairs: PairMap = {}
    for coords in colour2coords.values():
        if len(coords) % 2:
            raise ValueError(f"{path.name}: colour count must be even.")
        # order along tunnel direction
        coords.sort(key=lambda rc: (rc[0], rc[1]) if orient == "horizontal"
                    else (rc[1], rc[0]))
        for a, b in zip(coords[0::2], coords[1::2]):
            pairs[a] = b
            pairs[b] = a
    return pairs


def load_wormholes(example_dir: str | Path) -> Tuple[PairMap, PairMap]:
    p = Path(example_dir)
    horiz = _pairs_from_bitmap(p / "horizontal_tunnel.png", "horizontal")
    vert  = _pairs_from_bitmap(p / "vertical_tunnel.png",   "vertical")
    return horiz, vert

# ---------------------------------------------------------------------
# Build neighbour tables
# ---------------------------------------------------------------------
def build_tables(h: int, w: int,
                 horiz: PairMap, vert: PairMap
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """Return (nbr_r, nbr_c) each int32 (H,W,4)."""

    r_idx = np.repeat(np.arange(h)[:, None], w, axis=1)
    c_idx = np.repeat(np.arange(w)[None, :], h, axis=0)

    nbr_r = np.stack([r_idx-1, r_idx, r_idx+1, r_idx], axis=2)
    nbr_c = np.stack([c_idx, c_idx+1, c_idx, c_idx-1], axis=2)

    # clip to INVALID outside board
    mask = (nbr_r < 0) | (nbr_r >= h) | (nbr_c < 0) | (nbr_c >= w)
    nbr_r[mask] = INVALID
    nbr_c[mask] = INVALID

    # ---- apply wormholes  (LEFT < BOTTOM < RIGHT < TOP) -----------------
    def _patch(a: Coord, b: Coord, frm: str, to: str):
        fi, ti = DIR_IDX[frm], DIR_IDX[to]
        nbr_r[a][fi], nbr_c[a][fi] = b
        nbr_r[b][ti], nbr_c[b][ti] = a

    # horizontal
    for (r1, c1), (r2, c2) in horiz.items():
        if c1 < c2:  # left → right
            _patch((r1, c1), (r2, c2), "right", "left")
        else:
            _patch((r2, c2), (r1, c1), "right", "left")
    # vertical
    for (r1, c1), (r2, c2) in vert.items():
        if r1 < r2:  # top → bottom
            _patch((r1, c1), (r2, c2), "bottom", "top")
        else:
            _patch((r2, c2), (r1, c1), "bottom", "top")

    # ---- deduplicate per cell  (keep higher-precedence dir) -------------
    for d in PRECEDENCE[1:]:          # skip TOP, start with RIGHT
        same_r = nbr_r[:, :, d][..., None] == nbr_r[:, :, :d]
        same_c = nbr_c[:, :, d][..., None] == nbr_c[:, :, :d]
        dup = (same_r & same_c).any(axis=2)
        nbr_r[dup, d] = INVALID
        nbr_c[dup, d] = INVALID

    return nbr_r.astype(np.int32), nbr_c.astype(np.int32)
