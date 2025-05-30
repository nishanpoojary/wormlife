# tests/conftest.py
"""
Ensures the project root (parent of 'tests') is on sys.path so tests can
import `srcs.*` without needing editable installs or PYTHONPATH tweaks.
"""
import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
