# """
# Vectorised one-generation update for Wormhole Game of Life.

# –  Treats neighbours with index −1 as dead.  
# –  Casts board to uint8 so neighbour sums are correct (0/1 instead of True/False).
# """

# import numpy as np

# __all__ = ["step"]
# INVALID = -1  # must match sentinel in lookup.py


# def _gather(board8: np.ndarray, r: np.ndarray, c: np.ndarray) -> np.ndarray:
#     """Return neighbour values, 0 where r or c is INVALID."""
#     mask = r != INVALID
#     out = np.zeros_like(board8, dtype=np.uint8)
#     out[mask] = board8[r[mask], c[mask]]
#     return out


# def _diag(board8: np.ndarray, nbr_r: np.ndarray, nbr_c: np.ndarray,
#           vert_dir: int, horiz_dir: int) -> np.ndarray:
#     """Two-step lookup to fetch diagonal neighbours."""
#     r_mid = nbr_r[:, :, vert_dir]
#     c_mid = nbr_c[:, :, vert_dir]
#     r = np.where(r_mid != INVALID, nbr_r[r_mid, c_mid, horiz_dir], INVALID)
#     c = np.where(r_mid != INVALID, nbr_c[r_mid, c_mid, horiz_dir], INVALID)
#     return _gather(board8, r, c)


# def step(board: np.ndarray,
#          nbr_r: np.ndarray,
#          nbr_c: np.ndarray) -> np.ndarray:
#     board8 = board.astype(np.uint8)  # 0 / 1 integers

#     # Orthogonals
#     n_t = _gather(board8, nbr_r[:, :, 0], nbr_c[:, :, 0])
#     n_r = _gather(board8, nbr_r[:, :, 1], nbr_c[:, :, 1])
#     n_b = _gather(board8, nbr_r[:, :, 2], nbr_c[:, :, 2])
#     n_l = _gather(board8, nbr_r[:, :, 3], nbr_c[:, :, 3])

#     # Diagonals
#     n_tl = _diag(board8, nbr_r, nbr_c, 0, 3)
#     n_tr = _diag(board8, nbr_r, nbr_c, 0, 1)
#     n_bl = _diag(board8, nbr_r, nbr_c, 2, 3)
#     n_br = _diag(board8, nbr_r, nbr_c, 2, 1)

#     neighbours = n_t + n_r + n_b + n_l + n_tl + n_tr + n_bl + n_br

#     survive = board & ((neighbours == 2) | (neighbours == 3))
#     born    = (~board) & (neighbours == 3)
#     return survive | born


"""
srcs/engine.py
Vectorised one-generation update for Wormhole Game of Life.

Key feature: counts *unique* neighbours, so if two directions map to
the same cell that live cell contributes only 1 to the neighbour-sum.
"""

from __future__ import annotations

import numpy as np

__all__ = ["step"]

INVALID = -1  # must match sentinel in lookup.py


# ---------------------------------------------------------------------------
# Helper: gather neighbour values (and optionally coords) safely
# ---------------------------------------------------------------------------
def _gather(board8: np.ndarray,
            r: np.ndarray,
            c: np.ndarray,
            return_key: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """
    Parameters
    ----------
    board8 : uint8 (H, W)    – 0/1 board
    r, c   : int32   (H, W)  – neighbour coordinates
    return_key : bool        – also return key = r*W + c

    Returns
    -------
    val : uint8 (H, W)       – 0/1 (dead/live), INVALID → 0
    key : int32 (H, W)       – flattened index or -1  (only if return_key)
    """
    mask = (r != INVALID) & (c != INVALID)
    val = np.zeros_like(board8, dtype=np.uint8)
    val[mask] = board8[r[mask], c[mask]]
    if return_key:
        W = board8.shape[1]
        key = np.where(mask, r * W + c, INVALID)
        return val, key
    else:
        return val, None  # type: ignore


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def step(board: np.ndarray,
         nbr_r: np.ndarray,
         nbr_c: np.ndarray) -> np.ndarray:
    """
    board  : bool   (H, W)
    nbr_r,
    nbr_c  : int32  (H, W, 4) – orthogonal neighbour indices, plus
              diagonal indices are fetched via two-hop lookup.
    Returns
    -------
    next_board : bool (H, W)
    """
    board8 = board.astype(np.uint8)  # 0 / 1  (faster sums)

    # ---- orthogonals (val + key) ----------------------------------------
    v_t, k_t = _gather(board8, nbr_r[:, :, 0], nbr_c[:, :, 0], True)
    v_r, k_r = _gather(board8, nbr_r[:, :, 1], nbr_c[:, :, 1], True)
    v_b, k_b = _gather(board8, nbr_r[:, :, 2], nbr_c[:, :, 2], True)
    v_l, k_l = _gather(board8, nbr_r[:, :, 3], nbr_c[:, :, 3], True)

    # ---- diagonals (two-hop) -------------------------------------------
    def diag(vert_dir: int, horiz_dir: int):
        rm = nbr_r[:, :, vert_dir]
        cm = nbr_c[:, :, vert_dir]
        mask_mid = (rm != INVALID) & (cm != INVALID)
        r = np.full_like(rm, INVALID)
        c = np.full_like(cm, INVALID)
        r[mask_mid] = nbr_r[rm[mask_mid], cm[mask_mid], horiz_dir]
        c[mask_mid] = nbr_c[rm[mask_mid], cm[mask_mid], horiz_dir]
        return _gather(board8, r, c, True)

    v_tl, k_tl = diag(0, 3)
    v_tr, k_tr = diag(0, 1)
    v_bl, k_bl = diag(2, 3)
    v_br, k_br = diag(2, 1)

    # ---- stack keys & values (H, W, 8) ----------------------------------
    vals = np.stack([v_t, v_r, v_b, v_l, v_tl, v_tr, v_bl, v_br], axis=2)
    keys = np.stack([k_t, k_r, k_b, k_l, k_tl, k_tr, k_bl, k_br], axis=2)

    # ---- sort by key so duplicates become adjacent ----------------------
    idx_sort = np.argsort(keys, axis=2)
    keys_sorted = np.take_along_axis(keys, idx_sort, axis=2)
    vals_sorted = np.take_along_axis(vals, idx_sort, axis=2)

    # ---- zero-out duplicate neighbour contributions ---------------------
    dup = (keys_sorted == np.roll(keys_sorted, shift=1, axis=2))
    dup[:, :, 0] = False                     # first entry never duplicate
    vals_sorted[dup] = 0                    # count only unique neighbours

    neighbour_sum = vals_sorted.sum(axis=2)  # uint8

    # ---- apply Game of Life rules ---------------------------------------
    survive = board & ((neighbour_sum == 2) | (neighbour_sum == 3))
    born    = (~board) & (neighbour_sum == 3)
    return survive | born
