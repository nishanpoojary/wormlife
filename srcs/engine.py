"""
Vectorised one-generation update for Wormhole Game of Life.

–  Treats neighbours with index −1 as dead.  
–  Casts board to uint8 so neighbour sums are correct (0/1 instead of True/False).
"""

import numpy as np

__all__ = ["step"]
INVALID = -1  # must match sentinel in lookup.py


def _gather(board8: np.ndarray, r: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Return neighbour values, 0 where r or c is INVALID."""
    mask = r != INVALID
    out = np.zeros_like(board8, dtype=np.uint8)
    out[mask] = board8[r[mask], c[mask]]
    return out


def _diag(board8: np.ndarray, nbr_r: np.ndarray, nbr_c: np.ndarray,
          vert_dir: int, horiz_dir: int) -> np.ndarray:
    """Two-step lookup to fetch diagonal neighbours."""
    r_mid = nbr_r[:, :, vert_dir]
    c_mid = nbr_c[:, :, vert_dir]
    r = np.where(r_mid != INVALID, nbr_r[r_mid, c_mid, horiz_dir], INVALID)
    c = np.where(r_mid != INVALID, nbr_c[r_mid, c_mid, horiz_dir], INVALID)
    return _gather(board8, r, c)


def step(board: np.ndarray,
         nbr_r: np.ndarray,
         nbr_c: np.ndarray) -> np.ndarray:
    board8 = board.astype(np.uint8)  # 0 / 1 integers

    # Orthogonals
    n_t = _gather(board8, nbr_r[:, :, 0], nbr_c[:, :, 0])
    n_r = _gather(board8, nbr_r[:, :, 1], nbr_c[:, :, 1])
    n_b = _gather(board8, nbr_r[:, :, 2], nbr_c[:, :, 2])
    n_l = _gather(board8, nbr_r[:, :, 3], nbr_c[:, :, 3])

    # Diagonals
    n_tl = _diag(board8, nbr_r, nbr_c, 0, 3)
    n_tr = _diag(board8, nbr_r, nbr_c, 0, 1)
    n_bl = _diag(board8, nbr_r, nbr_c, 2, 3)
    n_br = _diag(board8, nbr_r, nbr_c, 2, 1)

    neighbours = n_t + n_r + n_b + n_l + n_tl + n_tr + n_bl + n_br

    survive = board & ((neighbours == 2) | (neighbours == 3))
    born    = (~board) & (neighbours == 3)
    return survive | born
