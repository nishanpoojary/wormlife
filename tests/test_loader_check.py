from pathlib import Path
from PIL import Image
import numpy as np

# Import the main entry function from loader_check
from src.loader_check import main


def make_dummy_image(tmp_path: Path, name: str, size=(2, 2), color=(0, 0, 0)):
    """
    Helper to create a small PNG file of specified width×height (size) and fill color (RGB tuple).
    Returns the Path to the saved image.
    """
    # NumPy expects shape in (height, width, 3)
    arr = np.full((size[1], size[0], 3), color, dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    out = tmp_path / name
    img.save(out)
    return out


def test_loader_check_reports_sizes(capsys, tmp_path):
    """
    GIVEN three valid PNGs named starting_position.png, horizontal_tunnel.png, vertical_tunnel.png
    WHEN main(dir_path) is invoked
    THEN it should print exactly three lines, each containing "size=(width, height), mode=" for each file.
    """
    # Create starting_position.png (3×4) all white
    make_dummy_image(tmp_path, "starting_position.png", size=(3, 4), color=(255, 255, 255))
    # Create horizontal_tunnel.png (5×6) all dark color
    make_dummy_image(tmp_path, "horizontal_tunnel.png", size=(5, 6), color=(10, 20, 30))
    # Create vertical_tunnel.png (2×2)
    make_dummy_image(tmp_path, "vertical_tunnel.png", size=(2, 2), color=(50, 50, 50))

    # Invoke the main function which prints each filename with its size and mode
    main(str(tmp_path))

    # Capture stdout
    captured = capsys.readouterr()
    out = captured.out.strip().splitlines()

    # Expect exactly three lines, each referencing the correct filename and containing "size="
    assert any("starting_position.png: size=(3, 4), mode=" in line for line in out)
    assert any("horizontal_tunnel.png: size=(5, 6), mode=" in line for line in out)
    assert any("vertical_tunnel.png: size=(2, 2), mode=" in line for line in out)
    assert len(out) == 3, f"Expected exactly 3 lines of output, got {len(out)}"


def test_loader_check_missing_file_prints_error(capsys, tmp_path):
    """
    GIVEN only starting_position.png exists
    WHEN main(dir_path) is called
    THEN it should print at least one line containing "✗ failed to load horizontal_tunnel.png"
         or "✗ failed to load vertical_tunnel.png" to indicate missing image errors.
    """
    # Create only starting_position.png, omit the other two
    make_dummy_image(tmp_path, "starting_position.png", size=(2, 2), color=(255, 255, 255))

    # Run the loader_check main function against tmp_path
    main(str(tmp_path))

    # Capture stdout
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()

    # Verify that at least one missing-file error was printed
    assert any("✗ failed to load horizontal_tunnel.png" in line for line in lines) or \
           any("✗ failed to load vertical_tunnel.png" in line for line in lines), \
           "Expected an error line for missing tunnel image"
