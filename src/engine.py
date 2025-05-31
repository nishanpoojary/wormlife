# src/engine.py

"""
One‐step update for Wormhole Game of Life.

Counts *unique* neighbours (so that if two directions map to the same cell,
it is only counted once).  Note that lookup.build_tables() has already
ensured no cell has duplicate orthogonal references of the same target.

All arithmetic is done in uint8 for speed:

  • _gather() returns 0 if (r,c) == INVALID, otherwise board8[r,c].
  • _diag() performs a two‐hop index to fetch diagonal neighbours.

Usage:
    next_board = step(current_board, nbr_r, nbr_c)
"""

from __future__ import annotations

import numpy as np

INVALID = -1  # sentinel from lookup.py

__all__ = ["step"]


def _gather(board8: np.ndarray, r: np.ndarray, c: np.ndarray) -> np.ndarray:
    """
    Return a uint8 array of 0/1 neighbour values for each (r,c).  If r or c is INVALID,
    that position yields 0.
    """
    out = np.zeros_like(board8, dtype=np.uint8)
    mask = (r != INVALID) & (c != INVALID)
    out[mask] = board8[r[mask], c[mask]]
    return out


def _diag(board8: np.ndarray, nbr_r: np.ndarray, nbr_c: np.ndarray, vdir: int, hdir: int) -> np.ndarray:
    """
    Two‐hop diagonal gather:

    1. Step in vertical direction 'vdir' (0=Top, 2=Bottom), producing intermediate coords (rm, cm).
    2. From (rm, cm), step in horizontal direction 'hdir' (1=Right, 3=Left).
    3. Gather neighbour from final (r2, c2) via _gather().

    Positions where any intermediate = INVALID yield 0.
    """
    rm, cm = nbr_r[:, :, vdir], nbr_c[:, :, vdir]
    mask_mid = (rm != INVALID) & (cm != INVALID)

    # Prepare empty invalid arrays
    r2 = np.full_like(rm, INVALID)
    c2 = np.full_like(cm, INVALID)

    # Fill valid two‐hop coordinates
    r2[mask_mid] = nbr_r[rm[mask_mid], cm[mask_mid], hdir]
    c2[mask_mid] = nbr_c[rm[mask_mid], cm[mask_mid], hdir]

    return _gather(board8, r2, c2)


def step(board: np.ndarray, nbr_r: np.ndarray, nbr_c: np.ndarray) -> np.ndarray:
    """
    Advance one generation of Wormhole Game of Life.

    Parameters
    ----------
    board : np.ndarray[bool], shape = (H, W)
        Current generation (True = live, False = dead)
    nbr_r, nbr_c : np.ndarray[int32], shape = (H, W, 4)
        Orthogonal neighbour indices from lookup.build_tables().

    Returns
    -------
    next_board : np.ndarray[bool], shape = (H, W)
        Next generation after applying the 8‐neighbour Conway rules.
    """
    board8 = board.astype(np.uint8)

    # Orthogonal neighbours (0=top,1=right,2=bottom,3=left)
    n_t = _gather(board8, nbr_r[:, :, 0], nbr_c[:, :, 0])
    n_r = _gather(board8, nbr_r[:, :, 1], nbr_c[:, :, 1])
    n_b = _gather(board8, nbr_r[:, :, 2], nbr_c[:, :, 2])
    n_l = _gather(board8, nbr_r[:, :, 3], nbr_c[:, :, 3])

    # Diagonal neighbours via two‐hop (Top-Left, Top-Right, Bottom-Left, Bottom-Right)
    n_tl = _diag(board8, nbr_r, nbr_c, 0, 3)
    n_tr = _diag(board8, nbr_r, nbr_c, 0, 1)
    n_bl = _diag(board8, nbr_r, nbr_c, 2, 3)
    n_br = _diag(board8, nbr_r, nbr_c, 2, 1)

    # Sum all 8 neighbours (each entry is 0 or 1)
    neighbour_sum = n_t + n_r + n_b + n_l + n_tl + n_tr + n_bl + n_br

    # Apply standard Conway's Game of Life rules
    survive = board & ((neighbour_sum == 2) | (neighbour_sum == 3))
    born = (~board) & (neighbour_sum == 3)

    return survive | born
