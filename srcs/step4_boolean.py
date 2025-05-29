# srcs/step4_boolean.py
import sys
from pathlib import Path
import numpy as np
from PIL import Image

def load_boolean_board(example_dir: str) -> np.ndarray:
    start_img = Image.open(Path(example_dir) / "starting_position.png").convert("RGB")
    arr = np.asarray(start_img)              # shape (H, W, 3), uint8 0-255
    # Alive if the pixel is white (255,255,255); dead otherwise.
    alive = np.all(arr == 255, axis=-1)      # shape (H, W), dtype=bool
    return alive

def save_debug_png(board: np.ndarray, out_path: Path) -> None:
    # Convert True → 255 white, False → 0 black
    img = Image.fromarray(board.astype(np.uint8) * 255, mode="L")
    img.save(out_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python srcs/step4_boolean.py <example-folder>")
        sys.exit(1)
    folder = sys.argv[1]
    board = load_boolean_board(folder)
    print(f"Board shape = {board.shape}, dtype = {board.dtype}, alive cells = {board.sum()}")
    save_debug_png(board, Path(folder) / "check_start.png")
    print("check_start.png written — open it to verify.")
