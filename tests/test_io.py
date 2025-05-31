import numpy as np
import pytest
from pathlib import Path
from PIL import Image

# Import only the function under test
from src.io import load_boolean_board


def test_load_boolean_board_simple(tmp_path):
    """
    Create a 3×3 RGB image:
      - Set pixel (1,1) to exactly white (255,255,255) → interpreted as True ("alive")
      - All other pixels are black → interpreted as False ("dead")
    Then call load_boolean_board and verify the returned boolean array shape and contents.
    """
    # Build a 3×3 image using NumPy
    arr = np.zeros((3, 3, 3), dtype=np.uint8)
    arr[1, 1] = [255, 255, 255]  # Single live (center) pixel
    img = Image.fromarray(arr, mode="RGB")

    # Save the image to the temporary directory as "starting_position.png"
    img_path = tmp_path / "starting_position.png"
    img.save(img_path)

    # Call the function under test
    board = load_boolean_board(tmp_path)

    # Confirm board shape is (3,3)
    assert board.shape == (3, 3)

    # Build expected boolean array: only (1,1) is True
    expected = np.zeros((3, 3), dtype=bool)
    expected[1, 1] = True

    # Compare elementwise
    assert np.array_equal(board, expected), "Only exact-white pixel should map to True"


def test_load_boolean_board_non_exact_white(tmp_path):
    """
    Create a 2×2 image where one pixel is nearly white (254,255,255), and one pixel is exact white.
    In load_boolean_board, only exact (255,255,255) → True; other colors are False.
    """
    # Build a 2×2 RGB image
    arr = np.zeros((2, 2, 3), dtype=np.uint8)
    arr[0, 0] = [254, 255, 255]  # Nearly white, should remain False
    arr[1, 1] = [255, 255, 255]  # Exact white, should become True
    img = Image.fromarray(arr, mode="RGB")

    # Save as "starting_position.png"
    img_path = tmp_path / "starting_position.png"
    img.save(img_path)

    # Call load_boolean_board
    board = load_boolean_board(tmp_path)

    # Build expected result
    expected = np.zeros((2, 2), dtype=bool)
    expected[1, 1] = True  # Only exact white at (1,1)

    assert np.array_equal(board, expected), "Only exact-white pixel should map to True"


def test_load_boolean_board_missing_file(tmp_path):
    """
    If "starting_position.png" is missing entirely, load_boolean_board should raise FileNotFoundError.
    This tests that the function does not swallow a missing file error.
    """
    with pytest.raises(FileNotFoundError):
        # Passing a non-existent directory to force a missing file
        load_boolean_board(tmp_path / "nonexistent_folder")
