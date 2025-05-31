# conftest.py
import sys
from pathlib import Path

# Assume this conftest.py lives in the project root (wormlife/).
# We want to ensure that “wormlife/” is on sys.path so that
# “import src.some_module” works.

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    # prepend the root folder to sys.path
    sys.path.insert(0, str(project_root))
