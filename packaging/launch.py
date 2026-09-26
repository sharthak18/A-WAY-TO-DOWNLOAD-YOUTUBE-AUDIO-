#!/usr/bin/env python3
"""Entry point for the PyInstaller build (see grabbox.spec next to this file).

From a source checkout you do not need it - run `python3 -m grabbox` from the
repo root, or double-click one of the launchers in scripts/.
"""

import os
import sys

# Make the repo root importable so `grabbox` resolves when run as a plain file.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grabbox.server import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
