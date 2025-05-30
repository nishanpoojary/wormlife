# srcs/lookup.py
"""
Neighbour lookup-table builder for Wormhole Game of Life.

Returns two int32 arrays:

    nbr_r[row, col, dir]  – row-index of the neighbour
    nbr_c[row, col, dir]  – col-index of the neighbour

where dir = 0:Top, 1:Right, 2:Bottom, 3:Left.

The tables already include wormhole teleporting and the spec’s
precedence rule (TOP > RIGHT > BOTTOM > LEFT).
"""

from typing import Dict
from typing import Tuple
import numpy as np

from .wormhole import PairMap

DIR_IDX: Dict[str, int] = {"top": 0, "right": 1, "bottom": 2, "left": 3}


def build_tables(
    height: int,
    width: int,
    horiz: PairMap,
    vert: PairMap,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Produce neighbour lookup tables incorporating wormholes.

    Parameters
    ----------
    height, width : int
        Dimensions of the board.
    horiz, vert : PairMap
        Horizontal and vertical portal pair dictionaries produced by
        wormhole.load_wormholes().

    Returns
    -------
    nbr_r, nbr_c : np.ndarray
        int32 arrays of shape (H, W, 4) giving the row / col index of the
        neighbour in the directions Top, Right, Bottom, Left.
    """

    # ------------------------------------------------------------------
    # 1. Classic orthogonal neighbours on a finite grid (no wrap-around)
    # ------------------------------------------------------------------
    # Build full H×W index grids
    row_idx = np.repeat(np.arange(height)[:, None], width, axis=1)
    col_idx = np.repeat(np.arange(width)[None, :], height, axis=0)

    # Stack into (H, W, 4) direction planes
    nbr_r = np.stack([row_idx - 1, row_idx, row_idx + 1, row_idx], axis=2)  # T, R, B, L
    nbr_c = np.stack([col_idx, col_idx + 1, col_idx, col_idx - 1], axis=2)

    # Clamp edges so we stay in-bounds (effectively fixed-dead border)
    nbr_r = np.clip(nbr_r, 0, height - 1)
    nbr_c = np.clip(nbr_c, 0, width - 1)

    # ------------------------------------------------------------------
    # 2. Apply wormhole remaps with precedence
    # ------------------------------------------------------------------
    def _apply(pairs: PairMap, frm: str, to: str) -> None:
        """Overwrite direction `frm` so that endpoint A's frm-neighbour is B,
        and endpoint B's to-neighbour is A."""
        i_from, i_to = DIR_IDX[frm], DIR_IDX[to]
        for (r1, c1), (r2, c2) in pairs.items():
            nbr_r[r1, c1, i_from], nbr_c[r1, c1, i_from] = r2, c2
            nbr_r[r2, c2, i_to], nbr_c[r2, c2, i_to] = r1, c1

    # Apply in REVERSE precedence so later calls overwrite earlier ones
    _apply(horiz, "left", "right")  # lowest
    _apply(vert, "bottom", "top")
    _apply(horiz, "right", "left")
    _apply(vert, "top", "bottom")  # highest

    return nbr_r.astype(np.int32), nbr_c.astype(np.int32)
