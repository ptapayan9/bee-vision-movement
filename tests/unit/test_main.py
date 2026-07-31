"""Tests for the command-line entry point."""

from bvm.main import main


def test_main_without_arguments_prints_help(capsys) -> None:
    """Verify that invoking the CLI without arguments displays help."""
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: bvm" in captured.out
