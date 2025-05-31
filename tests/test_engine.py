import numpy as np

# Import the step function (Core Game of Life logic) and build_tables for neighbor lookup
from src.engine import step
from src.lookup import build_tables


def make_empty_board(h: int, w: int):
    """
    Create and return an all-False ("dead") boolean board of shape (h, w).
    """
    return np.zeros((h, w), dtype=bool)


def make_vertical_blinker(h: int, w: int, center_row: int, center_col: int):
    """
    Create a 5×5 (for example) vertical 3-cell blinker (oscillator) centered at (center_row, center_col).
    Specifically, set three consecutive cells in the same column to True. All other cells remain False.
    """
    board = make_empty_board(h, w)

    # Turn on cells in a vertical line: (center_row-1, center_col), (center_row, center_col), (center_row+1, center_col)
    board[center_row - 1 : center_row + 2, center_col] = True
    return board


def test_step_blinker_flips():
    """
    A vertical blinker (3 cells in a column) should become a horizontal blinker (3 cells in a row) after one step,
    and then return to vertical after a second step. This verifies basic Game-of-Life oscillation behavior.
    """
    h, w = 5, 5

    # Build neighbor tables with no wormholes (all interneighbor links are orthogonal grid adjacency)
    nbr_r, nbr_c = build_tables(h, w, horiz={}, vert={})

    # Initial board: vertical blinker at center (2,2) for a 5×5 board
    board0 = make_vertical_blinker(h, w, 2, 2)

    # Step 1: expect the board to become a horizontal line at row=2, columns 1,2,3
    board1 = step(board0, nbr_r, nbr_c)

    # Build the expected horizontal blinker
    expected1 = make_empty_board(h, w)
    expected1[2, 1:4] = True  # cells (2,1),(2,2),(2,3)

    # Assert correctness of the flip
    assert np.array_equal(board1, expected1), "Vertical blinker did not flip to horizontal."

    # Step 2: apply one more generation, should revert to original vertical orientation
    board2 = step(board1, nbr_r, nbr_c)
    expected2 = board0.copy()
    assert np.array_equal(board2, expected2), "Horizontal blinker did not flip back to vertical."


def test_step_edge_cell_dies():
    """
    A single live cell on the edge or corner should die in the next generation (underpopulation).
    Here, test with a board of shape 3×3 and a lone live cell at (0, 0).
    """
    h, w = 3, 3
    nbr_r, nbr_c = build_tables(h, w, horiz={}, vert={})

    board = make_empty_board(h, w)
    board[0, 0] = True  # Single live cell at top-left
    new_board = step(board, nbr_r, nbr_c)

    # No cells should survive; new_board.any() must be False
    assert not new_board.any(), "Single live cell at edge should die (underpopulation)."


def test_step_full_block_survives():
    """
    A 2×2 block of live cells is a "still life" in Conway's Game of Life.
    Test on a 4×4 board: block located at rows (1,2), cols (1,2) should remain unchanged after stepping.
    """
    h, w = 4, 4
    nbr_r, nbr_c = build_tables(h, w, horiz={}, vert={})

    board = make_empty_board(h, w)
    # Turn on the 2×2 block at center: positions (1,1),(1,2),(2,1),(2,2)
    board[1, 1] = True
    board[1, 2] = True
    board[2, 1] = True
    board[2, 2] = True

    new_board = step(board, nbr_r, nbr_c)

    # Assert that the resulting board is identical to the input (block remains unchanged)
    assert np.array_equal(new_board, board), "2×2 block should be a still life (remain unchanged)."
