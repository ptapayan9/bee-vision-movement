"""Tests for the command-line entry point."""

from bvm.main import main


def test_main_without_arguments_prints_help(capsys) -> None:
    """Verify that invoking the CLI without arguments displays help."""
    exit_code = main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: bvm" in captured.out


def test_main_accepts_existing_video(tmp_path, capsys) -> None:
    """Verify that the CLI accepts a existing path."""
    video_path = tmp_path / "existing,mp4"
    video_path.touch()

    exit_code = main([str(video_path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert str(video_path) in captured.out


def test_main_rejects_missing_video(tmp_path, capsys) -> None:
    """Verify that the CLI rejects a non-existing path."""
    video_path = tmp_path / "missing.mp4"
    try:
        main([str(video_path)])
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("Expected the CLI to reject a missing file")

    captured = capsys.readouterr()
    assert "video path is not a file" in captured.err


def test_main_rejects_directory(tmp_path, capsys) -> None:
    """Verify if the CLI rejects a directory"""
    try:
        main([str(tmp_path)])
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("Expected CLI to reject a directory")

    captured = capsys.readouterr()
    assert "video path is not a file" in captured.err
