#!/usr/bin/env python3
"""Double-clickable launcher for the GrabBox app. Works on all OSes."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grabbox.server import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
