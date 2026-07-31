"""Package import smoke tests."""

import bvm


def test_package_imports() -> None:
    """Verify that the installed package can be imported."""
    assert bvm is not None
