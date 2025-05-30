# tests/test_engine.py
import numpy as np
from srcs.lookup import build_tables
from srcs.engine import step

def test_blinker_flips_in_centre():
    """
    5×5 board so the lookup's clamped edges don't interfere.
    Vertical blinker at col 2 should flip to horizontal at row 2.
    """
    board = np.zeros((5, 5), dtype=bool)
    board[1:4, 2] = True                 # vertical blinker

    nbr_r, nbr_c = build_tables(5, 5, {}, {})
    nxt = step(board, nbr_r, nbr_c)

    expected = np.zeros_like(board)
    expected[2, 1:4] = True              # horizontal blinker

    assert np.array_equal(nxt, expected)
