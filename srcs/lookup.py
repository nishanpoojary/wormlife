"""
Neighbour lookup-table builder for Wormhole Game of Life.

Produces two int32 arrays

    nbr_r[row, col, dir]  – neighbour’s row index
    nbr_c[row, col, dir]  – neighbour’s col index

dir = 0:Top, 1:Right, 2:Bottom, 3:Left

Values of **-1** mark neighbours that are outside the universe
(always dead).  Wormhole remaps and the precedence rule
TOP > RIGHT > BOTTOM > LEFT are applied.
"""

from typing import Dict, Tuple
import numpy as np
from .wormhole import PairMap

DIR_IDX: Dict[str, int] = {"top": 0, "right": 1, "bottom": 2, "left": 3}
INVALID = -1  # sentinel for off-board cells


def build_tables(
    height: int,
    width: int,
    horiz: PairMap,
    vert: PairMap,
) -> Tuple[np.ndarray, np.ndarray]:
    # ------------------------------------------------------------------
    # 1. Classic neighbour grid (NO clamping, so off-board = −1 / width)
    # ------------------------------------------------------------------
    row_idx = np.repeat(np.arange(height)[:, None], width, axis=1)
    col_idx = np.repeat(np.arange(width)[None, :], height, axis=0)

    nbr_r = np.stack(
        [row_idx - 1, row_idx, row_idx + 1, row_idx], axis=2
    )
    nbr_c = np.stack(
        [col_idx, col_idx + 1, col_idx, col_idx - 1], axis=2
    )

    # Mark any coordinate that is outside [0, H-1] or [0, W-1] as INVALID
    mask_out = (nbr_r < 0) | (nbr_r >= height) | (nbr_c < 0) | (nbr_c >= width)
    nbr_r[mask_out] = INVALID
    nbr_c[mask_out] = INVALID

    # ------------------------------------------------------------------
    # 2. Apply wormhole remaps with precedence
    # ------------------------------------------------------------------
    def _apply(pairs: PairMap, frm: str, to: str) -> None:
        i_from, i_to = DIR_IDX[frm], DIR_IDX[to]
        for (r1, c1), (r2, c2) in pairs.items():
            nbr_r[r1, c1, i_from], nbr_c[r1, c1, i_from] = r2, c2
            nbr_r[r2, c2, i_to],   nbr_c[r2, c2, i_to]   = r1, c1

    _apply(horiz, "left",  "right")   # lowest precedence
    _apply(vert,  "bottom","top")
    _apply(horiz, "right", "left")
    _apply(vert,  "top",   "bottom")  # highest precedence

    return nbr_r.astype(np.int32), nbr_c.astype(np.int32)
