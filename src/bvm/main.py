"""Command-line entry point for Bee Vision Movement."""

from argparse import ArgumentParser
from collections.abc import Sequence


def _build_parser() -> ArgumentParser:
    return ArgumentParser(
        prog="bvm",
        description="Analyze bee vision and movement from video.",
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return its exit code."""
    parser = _build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
