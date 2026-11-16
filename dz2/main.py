import sys

from src.container import build_container
from src.infrastructure.console_app import ConsoleApp


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    app = build_container().resolve(ConsoleApp)
    app.run()


if __name__ == "__main__":
    main()
