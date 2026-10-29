"""
main.py
Entry-point for Gully Run.
"""
from gully_run.game import GullyRun


def main() -> None:
    app = GullyRun()
    app.run()


if __name__ == "__main__":
    main()

