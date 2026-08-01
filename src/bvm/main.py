"""Command-line entry point for Bee Vision Movement."""

from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path


def _build_parser() -> ArgumentParser:

    parser = ArgumentParser(
        prog="bvm",
        description="Analyze bee vision and movement from video.",
    )

    # check if file path can be opened
    parser.add_argument(
        "video",
        nargs="?",  # allows zero or one video path
        type=Path,  # converts the input string to a PathLib
        help="Path to the video to analyze",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return its exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    video_path: Path | None = args.video
    if video_path is None:
        parser.print_help()
        return 0

    if not video_path.is_file():
        parser.error(f"video path is not a file: {video_path}")

    print(f"selected video: {video_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
