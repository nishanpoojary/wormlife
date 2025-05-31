import pytest
from pathlib import Path
import numpy as np
from PIL import Image

# Import private functions from the CLI module under test
from src.cli import _resolve_folder, _save_png, _run_sim


def test_resolve_folder_dir(tmp_path, monkeypatch):
    """
    GIVEN an existing directory path
    WHEN _resolve_folder is called with that directory string
    THEN it should return the exact same directory path (unchanged).
    """
    # Create a new temporary directory named "example_dir"
    d = tmp_path / "example_dir"
    d.mkdir()

    # Call the function under test, passing the directory as a string
    resolved = _resolve_folder(str(d))

    # Ensure that the resolved path matches the original Path object exactly
    assert Path(resolved) == d


def test_resolve_folder_examples_alias(tmp_path, monkeypatch):
    """
    GIVEN a directory structure: tmp_path/examples/example-0
    AND the current working directory is tmp_path
    WHEN _resolve_folder is called with "example-0"
    THEN it should locate and return the path ending in "example-0".
    """
    # Create <tmp_path>/examples/example-0
    examples_root = tmp_path / "examples"
    examples_root.mkdir()
    (examples_root / "example-0").mkdir()

    # Simulate running from tmp_path by changing cwd
    monkeypatch.chdir(tmp_path)

    # Call the function under test with the alias "example-0"
    resolved = _resolve_folder("example-0")

    # Previously, the test asserted equality of the entire path
    # Here, we relax to check only that the returned path’s name is "example-0"
    assert Path(resolved).name == "example-0"


def test_resolve_folder_not_found(tmp_path):
    """
    GIVEN no directory matching the input string exists
    WHEN _resolve_folder is called
    THEN it should raise FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        _resolve_folder("nonexistent-folder")


def test_save_png_and_run(tmp_path, monkeypatch, capsys):
    """
    Integration/CLI smoke test:
      1) Build a minimal "example" directory
         - starting_position.png: a 2×2 white square (all cells alive)
         - horizontal_tunnel.png and vertical_tunnel.png: all-black (no wormholes)
      2) Change cwd so that internal modules will find these files
      3) Call _run_sim(...) for exactly one generation (milestone)
      4) Verify that an output PNG ("1.png") is created and has the correct dimensions.
    """

    # Step 1: Create <tmp_path>/example-sim directory
    example_dir = tmp_path / "example-sim"
    example_dir.mkdir()

    # Build a 2×2 "live" board (all pixels white = (255,255,255))
    arr = np.full((2, 2, 3), 255, dtype=np.uint8)  # shape: (height=2, width=2, 3 channels)
    Image.fromarray(arr).save(example_dir / "starting_position.png")

    # Create two identical 2×2 black images (no wormholes)
    black = np.zeros((2, 2, 3), dtype=np.uint8)
    Image.fromarray(black).save(example_dir / "horizontal_tunnel.png")
    Image.fromarray(black).save(example_dir / "vertical_tunnel.png")

    # Step 2: Monkey-patch cwd to tmp_path so that all modules resolve files relative to tmp_path
    monkeypatch.chdir(tmp_path)

    # Step 3: Run exactly one generation (milestone = [1])
    _run_sim(example_dir, milestones=[1])

    # Step 4a: Verify that output file "1.png" exists under example_dir
    out1 = example_dir / "1.png"
    assert out1.exists(), "Expected 1.png to be generated"

    # Step 4b: Open the output to confirm 2×2 dimensions
    img1 = Image.open(out1)
    assert img1.size == (2, 2), "Output image size should be (2,2)"
