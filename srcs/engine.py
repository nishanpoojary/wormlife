# srcs/engine.py
"""
Vectorised one-generation update for Wormhole Game of Life.
Now casts the board to uint8 so neighbour counts are correct.
"""

import numpy as np

__all__ = ["step"]


def _diag(
    board8: np.ndarray,
    nbr_r: np.ndarray,
    nbr_c: np.ndarray,
    vert_dir: int,
    horiz_dir: int,
) -> np.ndarray:
    """Helper to fetch diagonal neighbours via two look-ups."""
    r = nbr_r[nbr_r[:, :, vert_dir], nbr_c[:, :, vert_dir], horiz_dir]
    c = nbr_c[nbr_r[:, :, vert_dir], nbr_c[:, :, vert_dir], horiz_dir]
    return board8[r, c]


def step(board: np.ndarray, nbr_r: np.ndarray, nbr_c: np.ndarray) -> np.ndarray:
    """
    Parameters
    ----------
    board : bool (H, W)
    nbr_r / nbr_c : int32 (H, W, 4) – output of lookup.build_tables()

    Returns
    -------
    next_board : bool (H, W)
    """
    board8 = board.astype(np.uint8)  # 0 / 1  – prevents “True+True = True”

    # Orthogonals
    n_t = board8[nbr_r[:, :, 0], nbr_c[:, :, 0]]
    n_r = board8[nbr_r[:, :, 1], nbr_c[:, :, 1]]
    n_b = board8[nbr_r[:, :, 2], nbr_c[:, :, 2]]
    n_l = board8[nbr_r[:, :, 3], nbr_c[:, :, 3]]

    # Diagonals via two-step look-up
    n_tl = _diag(board8, nbr_r, nbr_c, 0, 3)
    n_tr = _diag(board8, nbr_r, nbr_c, 0, 1)
    n_bl = _diag(board8, nbr_r, nbr_c, 2, 3)
    n_br = _diag(board8, nbr_r, nbr_c, 2, 1)

    neighbour_sum = n_t + n_r + n_b + n_l + n_tl + n_tr + n_bl + n_br

    survive = board & ((neighbour_sum == 2) | (neighbour_sum == 3))
    born = (~board) & (neighbour_sum == 3)
    return survive | born
