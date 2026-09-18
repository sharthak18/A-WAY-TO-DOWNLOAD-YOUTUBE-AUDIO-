"""Entry point for ``python3 -m grabbox``."""

import sys

from .server import main

if __name__ == "__main__":
    sys.exit(main())
