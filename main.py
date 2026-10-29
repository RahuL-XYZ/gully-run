"""
main.py
Entry-point for Gully Run.
"""
import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct script execution
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from gully_run.game import GullyRun


def main() -> None:
    app = GullyRun()
    app.run()


if __name__ == "__main__":
    main()

