# # srcs/step4_boolean.py
# import sys
# from pathlib import Path
# import numpy as np
# from PIL import Image

# def load_boolean_board(example_dir: str) -> np.ndarray:
#     start_img = Image.open(Path(example_dir) / "starting_position.png").convert("RGB")
#     arr = np.asarray(start_img)              # shape (H, W, 3), uint8 0-255
#     # Alive if the pixel is white (255,255,255); dead otherwise.
#     alive = np.all(arr == 255, axis=-1)      # shape (H, W), dtype=bool
#     return alive

# def save_debug_png(board: np.ndarray, out_path: Path) -> None:
#     # Convert True → 255 white, False → 0 black
#     img = Image.fromarray(board.astype(np.uint8) * 255, mode="L")
#     img.save(out_path)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python srcs/step4_boolean.py <example-folder>")
#         sys.exit(1)
#     folder = sys.argv[1]
#     board = load_boolean_board(folder)
#     print(f"Board shape = {board.shape}, dtype = {board.dtype}, alive cells = {board.sum()}")
#     save_debug_png(board, Path(folder) / "check_start.png")
#     print("check_start.png written — open it to verify.")


# srcs/step4_boolean.py
"""
Utilities for loading the starting board and (optionally) the universe mask
from starting_position.png.

Functions
---------
load_boolean_board(example_dir) -> np.ndarray[bool]
    True where the pixel is ≥ “white-threshold” (default 200).

load_board_and_mask(example_dir) -> (board, mask)
    Returns both the initial board *and* the mask so the simulation
    can clip births with  `next_board &= mask`.

Command-line mode:
    python -m srcs.step4_boolean <example-folder>
    Writes check_start.png for visual inspection.
"""

from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image

# Pixels whose average RGB ≥ THRESH are treated as “white / in-universe”
THRESH = 200


def _white_mask(img_path: Path) -> np.ndarray:
    """Return bool array: True where pixel average ≥ THRESH."""
    arr = np.asarray(Image.open(img_path).convert("RGB"), dtype=np.uint8)
    return arr.mean(axis=-1) >= THRESH     # shape (H, W) bool


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def load_board_and_mask(example_dir: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns
    -------
    board : bool ndarray  (H, W)   – initial live cells (all True inside mask)
    mask  : bool ndarray  (H, W)   – universe; births must stay inside mask
    """
    img_path = Path(example_dir) / "starting_position.png"
    mask = _white_mask(img_path)
    board = mask.copy()                   # initial live cells = white pixels
    return board, mask


def load_boolean_board(example_dir: str) -> np.ndarray:
    """
    Backward-compat wrapper used by older code/tests.
    Simply returns the initial board of live cells.
    """
    board, _ = load_board_and_mask(example_dir)
    return board


# ---------------------------------------------------------------------------
# CLI mode for a quick sanity check
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python -m srcs.step4_boolean <example-folder>")
        raise SystemExit(1)

    folder = sys.argv[1]
    bd, ms = load_board_and_mask(folder)
    print(f"shape={bd.shape},  initial_live={bd.sum()},  mask_pix={ms.sum()}")

    # Write debug PNG
    Image.fromarray(bd.astype(np.uint8) * 255, mode="L").save(
        Path(folder) / "check_start.png"
    )
    print("check_start.png written – open to verify.")
