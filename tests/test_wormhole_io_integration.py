import numpy as np
from pathlib import Path
from PIL import Image

# Import functions for end-to-end integration
from src.io import load_boolean_board
from src.wormhole import load_wormholes
from src.lookup import build_tables
from src.engine import step


def test_full_pipeline_single_iteration(tmp_path):
    """
    End-to-end integration test for one iteration of Game of Life with no wormholes:
      1) Create a 3×3 starting_position.png with center pixel white (alive).
      2) Create empty (black) horizontal_tunnel.png and vertical_tunnel.png (no wormholes).
      3) Load boolean board, wormhole maps, and neighbor tables.
      4) Perform one step; the single live cell should die (underpopulation).
    """
    # Step 1: Create a 3×3 RGBA array, only the center (1,1) is white
    arr = np.zeros((3, 3, 3), dtype=np.uint8)
    arr[1, 1] = [255, 255, 255]  # Mark center as alive
    Image.fromarray(arr).save(tmp_path / "starting_position.png")

    # Step 2: Create black images for wormhole inputs (no tunnels appear)
    black = np.zeros((3, 3, 3), dtype=np.uint8)
    Image.fromarray(black).save(tmp_path / "horizontal_tunnel.png")
    Image.fromarray(black).save(tmp_path / "vertical_tunnel.png")

    # Step 3: Load board and wormhole maps
    board = load_boolean_board(tmp_path)
    horiz, vert = load_wormholes(tmp_path)       # Expect empty dicts
    nbr_r, nbr_c = build_tables(3, 3, horiz, vert)

    # Step 4: Execute one step of the Game of Life
    new_board = step(board, nbr_r, nbr_c)

    # After one iteration, the lone center cell should die
    assert not new_board.any(), "Single live cell should die after one iteration"
