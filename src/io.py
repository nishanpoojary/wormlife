# src/io.py

"""
Loading utilities for the Wormhole Game of Life.

Provides:
  • load_boolean_board(): read 'starting_position.png' and return a boolean mask of live cells.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

__all__ = ["load_boolean_board"]


def load_boolean_board(example_dir: str | Path) -> np.ndarray:
    """
    Load 'starting_position.png' from the given directory and interpret
    every white pixel (RGB == (255,255,255)) as a live cell (True). All
    other pixels are considered dead (False).

    Parameters
    ----------
    example_dir : str | Path
        Path to the example folder containing 'starting_position.png'.

    Returns
    -------
    board : np.ndarray[bool] with shape (H, W)
        True where starting_position.png is exactly white, False elsewhere.
    """
    path = Path(example_dir) / "starting_position.png"
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img)  # shape (H, W, 3), dtype=uint8

    # White pixel ↦ (255,255,255) exactly
    board = np.all(arr == 255, axis=-1)
    return board
